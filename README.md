# SteelSim

SteelSim is an investor-ready industrial digital-twin MVP for MSME induction-furnace and TMT rebar plants. It combines the visual factory builder (Task 1) and the backend-authoritative deterministic simulation engine (Task 2) in one application.

## MVP capabilities

- React Flow plant builder with typed material, electrical, water, signal, and air ports
- Engineering topology validation, automatic connection, automatic layout, and local save/load
- Verified 25 t/h baseline: raw-material yard, induction furnace, LRF, CCM, reheating furnace, rolling mill, Thermex quench, cooling bed, substation, and cooling-water station
- Deterministic run, pause, resume, reset, and 1×/5×/10×/60× speed controls
- Backend-authoritative telemetry streamed over WebSocket with polling fallback
- Live process-flow diagram, equipment inspector, KPI deck, state trace, and event journal
- Topology safety gate: invalid non-empty plants cannot be started through the API

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

## Verify

```powershell
cd backend
python -m pytest -q

cd ../frontend
npm run build
```

The expected demo workflow is: open **Plant Builder**, click **Demo**, confirm the topology is valid, open **Simulation**, run the plant, inspect a process card, change speed, pause, and finish on **Overview**.
