# 43. Environment variables

SteelSim is configured through environment variables on both the backend service and the frontend Vite build.

## Configuration variables reference

| Variable Name | Component | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **`STEELSIM_API_KEY`** | Backend | `""` (Disabled) | Optional shared secret. When set, enforces API-key authentication across all HTTP and WebSocket endpoints. |
| **`VITE_STEELSIM_API_KEY`**| Frontend | `""` (Disabled) | Matching client secret. Injected by Vite into the frontend bundle to authenticate API calls. |
| **`STEELSIM_ALLOWED_ORIGINS`**| Backend | `http://127.0.0.1:5173,http://localhost:5173` | Comma-separated list of allowed CORS origins for browser security. |
| **`VITE_API_PROXY_TARGET`** | Frontend | `http://127.0.0.1:8000` | Backend upstream target URL used by the Vite development proxy. |
| **`STEELSIM_BASE_URL`** | E2E Tests | `http://127.0.0.1:5173/` | Target frontend URL evaluated during Puppeteer browser test execution. |
| **`STEELSIM_HISTORY_DB`** | Backend | `data/operations.sqlite3` | SQLite operations journal path. Use a persistent volume for durable hosted history. |
| **`STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS`** | Backend | `""` (Disabled) | Local development only: set to `1` to permit loopback HTTP model servers. Keep disabled on a public deployment. |

## BYOK model keys (Task 3 design rule)

> [!NOTE]
> **No Environment Variables for LLM Credentials:**
> External model credentials are supplied in the ACAMIS interface and held in backend memory for the active simulation. Connecting an external provider sends the selected simulated plant context over the network. See [Advisory Model Gateway](/task-3-acamis/model-gateway) and [Security](/reference/security).

## Shared demo key example

```powershell
# Set shared secret in PowerShell before launching services
$env:STEELSIM_API_KEY="c8a9f4e2b1d34a78bc901ef23456789a"
$env:VITE_STEELSIM_API_KEY=$env:STEELSIM_API_KEY

# Set custom CORS origin if hosting on a staging server
$env:STEELSIM_ALLOWED_ORIGINS="https://demo.steelsim.internal"
```

`VITE_STEELSIM_API_KEY` is embedded in the public frontend bundle at build time. It is not a private user credential or a substitute for accounts and authorization. Do not treat this shared-key setup as sufficient protection for a public multi-user service.
