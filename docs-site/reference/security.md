# 44. Security

SteelSim implements a lightweight, secure perimeter designed for engineering demonstrations, industrial testbeds, and protected investor previews.

## Security architecture

<pre class="mermaid">
flowchart LR
    Client["Browser Client"]
    Middleware["CORS & Auth Middleware<br/>• secrets.compare_digest()"]
    Endpoints["FastAPI Endpoints"]

    Client -->|"X-SteelSim-API-Key Header"| Middleware
    Middleware -->|"Constant-Time Digest Verified"| Endpoints
</pre>

### 1. Constant-time API key verification
When `STEELSIM_API_KEY` is configured, incoming requests are checked using `secrets.compare_digest`. This prevents timing side-channel attacks that could infer secret keys by measuring microsecond differences in string comparisons.

### 2. WebSocket authentication
WebSockets cannot send custom HTTP headers during the browser handshake. SteelSim passes the API key through the standard `Sec-WebSocket-Protocol` header using a URL-safe Base64 token:
```
Sec-WebSocket-Protocol: steelsim, steelsim-key.<base64url-token>
```
The server extracts, decodes, and validates the token before accepting the connection.

### 3. Public endpoints
The health check endpoint (`GET /api/health`) and `OPTIONS` pre-flight requests bypass API-key checks, allowing container orchestrators and load balancers to perform health probes without credentials.

### 4. Advisory Model Gateway key isolation (Task 3)
In Task 3, SteelSim supports external LLM advisory analysis via the [Advisory Model Gateway](/task-3-acamis/model-gateway). To maintain strict industrial compliance:
- **In-memory transient storage:** API keys supplied via `POST /api/simulations/{id}/acamis/model/connect` are held strictly in process memory keyed to the active simulation ID.
- **Never written to disk or logs:** Keys are never serialized to database tables, `.env` files, or server logs.
- **Masked representation:** Status endpoints (`GET /api/simulations/{id}/acamis/status`) only return masked identifiers (e.g., `AIzaSy...****`).
- **Immediate revocation:** Invoking `POST /model/disconnect` or terminating the simulation (`DELETE /api/simulations/{id}`) immediately purges the key from memory.

## Security boundaries and limitations
- API-key authentication is a shared-secret gate, not a multi-tenant role-based access control (RBAC) system.
- In-flight telemetry is unencrypted over plain `ws://` and `http://`. When deployed outside localhost, the application must be fronted by a reverse proxy terminating HTTPS and WSS.
- The external Model Gateway sends anonymized plant snapshots to Google AI Studio. In classified or high-security air-gapped facilities, the Model Gateway can remain completely disconnected without impeding core deterministic simulation or rule-based incident mitigation.

