# 4. Quick start

This guide explains how to install, configure, verify, and run the SteelSim platform locally.

## Prerequisites

- **Python:** Version 3.10 or higher
- **Node.js:** Version 18.0 or higher with npm
- **Git:** Standard git client
- **Modern Web Browser:** Chrome, Edge, Firefox, or Safari

## Installation procedure

### 1. Clone the repository
```powershell
git clone https://github.com/prabhasb06/steelsim.git
cd steelsim
```

### 2. Configure and start the backend service
Open a terminal in the repository root:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend starts at `http://127.0.0.1:8000`. Verify service liveness:
```powershell
curl http://127.0.0.1:8000/api/health
# Returns: {"status":"ok","service":"steelsim-backend"}
```

### 3. Configure and start the frontend application
Open a second terminal:
```powershell
cd frontend
npm ci
npm run dev
```
The Vite development server starts at `http://127.0.0.1:5173`.

## Standard first-run workflow

<pre class="mermaid">
sequenceDiagram
    autonumber
    actor User
    participant Browser as Frontend (5173)
    participant Server as Backend (8000)

    User->>Browser: Navigate to http://127.0.0.1:5173/
    User->>Browser: Select "Plant Builder" from sidebar
    User->>Browser: Click "Demo" in canvas toolbar
    Browser->>Server: GET /api/plant/template/tmt
    Server-->>Browser: Return 10-node TMT baseline topology
    Browser->>Browser: Render nodes and auto-connect utilities
    User->>Browser: Switch to "Simulation" view
    User->>Browser: Click "Run Simulation"
    Browser->>Server: POST /api/simulations (Create)
    Server-->>Browser: Simulation Created (READY)
    Browser->>Server: POST /api/simulations/{id}/command (start)
    Server-->>Browser: State: RUNNING (Tick 1)
    Server-->>Browser: Stream WebSocket snapshots
    Browser->>Browser: Display live MW, m³/h, and equipment telemetry
</pre>

## Verification commands

Run the test suites to ensure the installation is fully verified:

```powershell
# Backend test suite (43 tests)
cd backend
python -m pytest -q

# Frontend unit tests (4 tests)
cd ..\frontend
npm test

# Linting & production build
npm run lint
npm run build

# Headless browser E2E smoke test (requires running backend and frontend)
npm run test:e2e
```
