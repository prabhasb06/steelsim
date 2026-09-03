# SteelSim

SteelSim is an investor-ready industrial digital-twin MVP for MSME induction-furnace and TMT rebar plants. It combines the visual factory builder (Task 1) and the backend-authoritative deterministic simulation engine (Task 2) in one application.

## MVP capabilities

- React Flow plant builder with typed material, electrical, water, signal, and air ports
- Engineering topology validation, automatic connection, automatic layout, and browser-local save/load
- Verified 25 t/h baseline: raw-material yard, induction furnace, LRF, CCM, reheating furnace, rolling mill, Thermex quench, cooling bed, substation, and cooling-water station
- Deterministic run, pause, resume, reset, and 1×/5×/10×/60× speed controls
- Backend-authoritative telemetry streamed over WebSocket with polling fallback
- Bottleneck-aware material flow and aggregate electrical/cooling-water capacity gates
- Live process-flow diagram, equipment inspector, KPI deck, state trace, and event journal
- Topology safety gate across start, run, and resume; invalid non-empty plants cannot be started through the API
- Bounded simulation retention, explicit simulation cleanup, and an optional shared API key for protected demos

ACAMIS remains a separate, compatible decision-support product: **SteelSim creates the factory; ACAMIS understands the factory.** SteelSim does not control real machinery.

## Run locally

Open two terminals from the repository root.

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. The frontend proxies HTTP and WebSocket traffic under `/api` to the backend. To use another backend port, set `VITE_API_PROXY_TARGET`, for example `http://127.0.0.1:8002`.

For a protected remote demo, set the same secret before starting each service:

```powershell
$env:STEELSIM_API_KEY="replace-with-a-long-random-secret"
$env:VITE_STEELSIM_API_KEY=$env:STEELSIM_API_KEY
```

Allowed browser origins default to `http://127.0.0.1:5173` and `http://localhost:5173`. Override them with a comma-separated `STEELSIM_ALLOWED_ORIGINS` value. Use HTTPS/WSS whenever the application is accessed beyond localhost.

## Verify

```powershell
cd backend
python -m pytest -q

cd ../frontend
npm test
npm run build
npm run test:e2e
```

The E2E test expects the frontend and backend to be running. It uses installed Chrome or Edge when Puppeteer's bundled browser is unavailable.

Simulation instances are intentionally ephemeral in this MVP and are cleared when the backend restarts. Plant designs can be saved in the current browser. Persistent multi-user projects, role-based accounts, and ACAMIS optimization remain post-MVP capabilities and are not presented as finished controls.

The expected demo workflow is: open **Plant Builder**, click **Demo**, confirm the topology is valid, open **Simulation**, run the plant, inspect a process card, change speed, pause, and finish on **Overview**.
