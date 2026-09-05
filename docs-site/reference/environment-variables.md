# 31. Environment variables

SteelSim is configured through environment variables on both the backend service and the frontend Vite build.

## Configuration variables reference

| Variable Name | Component | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **`STEELSIM_API_KEY`** | Backend | `""` (Disabled) | Optional shared secret. When set, enforces API-key authentication across all HTTP and WebSocket endpoints. |
| **`VITE_STEELSIM_API_KEY`**| Frontend | `""` (Disabled) | Matching client secret. Injected by Vite into the frontend bundle to authenticate API calls. |
| **`STEELSIM_ALLOWED_ORIGINS`**| Backend | `http://127.0.0.1:5173,http://localhost:5173` | Comma-separated list of allowed CORS origins for browser security. |
| **`VITE_API_PROXY_TARGET`** | Frontend | `http://127.0.0.1:8000` | Backend upstream target URL used by the Vite development proxy. |
| **`STEELSIM_BASE_URL`** | E2E Tests | `http://127.0.0.1:5173/` | Target frontend URL evaluated during Puppeteer browser test execution. |

## Secure deployment example

```powershell
# Set shared secret in PowerShell before launching services
$env:STEELSIM_API_KEY="c8a9f4e2b1d34a78bc901ef23456789a"
$env:VITE_STEELSIM_API_KEY=$env:STEELSIM_API_KEY

# Set custom CORS origin if hosting on a staging server
$env:STEELSIM_ALLOWED_ORIGINS="https://demo.steelsim.internal"
```
