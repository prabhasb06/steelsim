# SteelSim

SteelSim is an industrial plant-topology builder and deterministic simulation MVP.

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

Open `http://127.0.0.1:5173`. The frontend proxies `/api` to the backend. To use another backend port, set `VITE_API_PROXY_TARGET`, for example `http://127.0.0.1:8002`.

## Verify

```powershell
cd backend
python -m pytest -q

cd ../frontend
npm run build
```

The expected workflow is: load the TMT template, validate the topology, create a simulation, then run, pause, change speed, and reset it from the simulation console.
