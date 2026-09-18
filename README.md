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

Active simulation instances stop when the backend restarts. Task 4 records local run checkpoints, telemetry frames, incidents, and policy audit in SQLite. Open **Operations History** to inspect recordings or explicitly restore a run into a new **paused** session. Plant designs can also be saved in the current browser. Persistent multi-user projects, role-based accounts, and ACAMIS optimization remain post-MVP capabilities.

## Task 4: Operations History and signal monitoring

### Connecting an advisory model

Start a simulation, open ACAMIS Intelligence, select the provider, and paste your key into the transient API-key field. Gemini can automatically select a text-generation model from the key's current catalog. Compatible providers require their model ID and API base URL (typically ending in `/v1`). **Test & connect** makes a small generation request; provider charges or quota usage may apply. A green verified status means generation succeeded, not merely that the model catalog was reachable.

Use **Request model review** to send the current simulated telemetry, incident evidence, and approved recovery plan. Output remains advisory; it does not bypass the deterministic policy or approval gates. Connection errors identify key, permission, quota, or endpoint problems. Keys stay in server memory for that simulation and must be re-entered after disconnect, session replacement, or backend restart. Do not paste keys into chat, source files, or documentation.

Gemini transport follows Google's [generateContent API](https://ai.google.dev/api/generate-content) and [model catalog API](https://ai.google.dev/api/models).

- The backend checks temperature deviation (>40 °C), cooling flow (<75% of expected), and electrical demand (>112% of expected) for three consecutive running ticks. Baselines come from the simulator, not scenario labels or an external model. Concurrent deviations on one asset are grouped as correlated evidence, not a proven root cause.
- These additional signal findings are operator-review evidence only; they do not introduce autonomous repairs. Existing Task 3/3.1 procedures, approval gates, and rolling-throughput recovery remain unchanged. Pause freezes detection; Clear Scenario and Reset clear monitoring state.
- Operations History provides recorded-frame replay, a power trace, loaded-frame comparisons, policy audit, and a downloadable JSON incident report. Comparisons are sample summaries, not energy savings claims. The UI lists the most recent 100 runs and loads recordings in pages of 500 frames; the API also supports run pagination.
- Restore creates a new run, loads the saved plant into the builder, and keeps the clock paused until explicitly resumed. API keys and model replies are not archived; reconnect the provider separately. Old runs remain available after reset or deletion of a live simulation.

### Storage and deployment limits

Set `STEELSIM_HISTORY_DB` to a writable SQLite file on a persistent volume. The local default is `data/operations.sqlite3`, excluded from Git. The existing free Render deployment does not configure a persistent volume, so do **not** promise history survival across deployment or host replacement there. This change does not provision paid infrastructure.

This is a single-process MVP journal, not a production historian. Frames are written synchronously; accelerated runs may run more slowly with recording enabled. No automatic retention/deletion is configured: monitor disk usage and back up the SQLite database using SQLite-aware backup tools. Storage-write failures are surfaced in ACAMIS while the live simulation continues, and recordings can have gaps during an outage. Restart recovery is explicit, not unattended.

### Demo

Run the TMT plant, use Observe mode, inject Furnace Stability, and wait at least three running ticks. Inspect the thermal/power evidence. Pause, open Operations History, select that run, replay the recorded frames, and download its report. Restore as a paused session and verify the original plant and simulation tick before resuming. Real SCADA connections, physical control, learned anomaly detection, and arbitrary fault repair remain out of scope.

The expected demo workflow is: open **Plant Builder**, click **Demo**, confirm the topology is valid, open **Simulation**, run the plant, inspect a process card, change speed, pause, and finish on **Overview**.
