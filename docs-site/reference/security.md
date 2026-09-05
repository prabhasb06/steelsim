# 32. Security

SteelSim implements a lightweight, secure perimeter designed for engineering demonstrations and protected investor previews.

## Security architecture

```
[Browser Client] ──X-SteelSim-API-Key──> [CORS & Auth Middleware] ──> [FastAPI Endpoints]
                                                   │
                                          Constant-Time Digest
                                       secrets.compare_digest()
```

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

## Security boundaries and limitations
- API-key authentication is a shared-secret gate, not a multi-tenant role-based access control (RBAC) system.
- In-flight telemetry is unencrypted over plain `ws://` and `http://`. When deployed outside localhost, the application must be fronted by a reverse proxy terminating HTTPS and WSS.
