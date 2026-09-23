# 44. Security

SteelSim has a lightweight shared-key gate intended for controlled demonstrations. It has no accounts, role-based permissions, or per-user isolation.

## Security architecture

<pre class="mermaid">
flowchart LR
    Client["Browser Client"]
    Middleware["CORS & Auth Middleware<br/>• secrets.compare_digest()"]
    Endpoints["FastAPI Endpoints"]

    Client -->|"X-SteelSim-API-Key Header"| Middleware
    Middleware -->|"Constant-Time Digest Verified"| Endpoints
</pre>

### 1. Shared API key verification
When `STEELSIM_API_KEY` is configured, incoming requests are checked using `secrets.compare_digest`. The browser copy of this key is embedded in its built JavaScript bundle through `VITE_STEELSIM_API_KEY`, so it is visible to anyone who can load that bundle. It is a demo gate, not private user authentication.

### 2. WebSocket authentication
WebSockets cannot send custom HTTP headers during the browser handshake. SteelSim passes the API key through the standard `Sec-WebSocket-Protocol` header using a URL-safe Base64 token:
```
Sec-WebSocket-Protocol: steelsim, steelsim-key.<base64url-token>
```
The server extracts, decodes, and validates the token before accepting the connection.

### 3. Public endpoints
The health check endpoint (`GET /api/health`) and `OPTIONS` pre-flight requests bypass API-key checks, allowing container orchestrators and load balancers to perform health probes without credentials.

### 4. Advisory Model Gateway key isolation (Task 3)
SteelSim supports external advisory analysis via the [Advisory Model Gateway](/task-3-acamis/model-gateway):
- Keys supplied through `POST /api/simulations/{id}/acamis/model/connect` are held in process memory for that simulation. History excludes keys, prompts, and model replies.
- Status responses omit the API key entirely. They do not return a masked fragment.
- Disconnecting or deleting the simulation removes the in-memory connection. A backend restart also clears it.
- Connecting a cloud model sends simulated plant context to that provider. SteelSim does not claim air-gapped operation while that connection is active.

## Security boundaries and limitations
- API-key authentication is a shared-secret gate, not a multi-tenant role-based access control (RBAC) system.
- In-flight telemetry is unencrypted over plain `ws://` and `http://`. When deployed outside localhost, the application must be fronted by a reverse proxy terminating HTTPS and WSS.
- The external Model Gateway sends equipment IDs, simulated telemetry, incidents, and policy context to the selected provider. Do not connect it where that data must stay within an isolated network.
- Public demo users share the same backend process and can enumerate simulation sessions through the current API. Do not enter personal paid-provider keys into a shared public session. Multi-user authentication and authorization are future work.

