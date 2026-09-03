# CONTEXT HANDOFF FOR CODEX — STEELSIM & ACAMIS UNIFIED ENGINE

## 1. Project Overview & Architecture
* **Mission**: Industrial digital twin and AI decision-support system for MSME Induction Furnace & TMT Rebar Rolling Mills (MSME Idea Hackathon 6.0).
* **Two Core Repositories in Workspace**:
  1. `C:\Users\prabh\steelsim`: Interactive visual Factory Builder + Deterministic Simulation Engine (React 19 + TypeScript + Vite + Tailwind + React Flow + FastAPI).
  2. `C:\Users\prabh\acamis`: ACAMIS multi-agent intelligence layer (FastAPI + 6 deterministic domain agents: Production, Maintenance, Safety, Quality, Energy, Logistics).
* **Core Goal**: Unify **Task 1 (Factory Builder)** and **Task 2 (Simulation Engine)** into a **single, non-disjoint industrial workspace** where users visually construct/wire a plant and simulate it live on the same canvas with real-time machine telemetry.

---

## 2. Work Accomplished & Root-Cause Fixes (`C:\Users\prabh\steelsim`)

### A. Backend API & Engine Enhancements
1. **Unified Command Endpoint (`backend/app/api/routes.py`)**:
   - Implemented `POST /api/simulations/{sim_id}/command` accepting `{ command: "start" | "pause" | "resume" | "reset" | "set_speed", payload: { speed?: string } }`.
   - Updated `GET /api/simulations/{sim_id}` and `POST /api/simulations` to return full snapshots containing live telemetry.
   - Added `WS /api/simulations/{sim_id}/stream` for backend-authoritative live snapshots and `GET /api/simulations/{sim_id}/snapshots` for bounded trace history.
   - Start, run, and resume all reject non-empty plants with blocking topology issues; simulations also have explicit deletion and bounded manager retention.
2. **Schema Resilience & Pydantic Validation (`backend/app/models/schemas.py`)**:
   - Added `node_telemetry: Dict[str, Any]` and `plant_summary: Dict[str, Any]` to both `SimulationState` and `SimulationSnapshot`.
   - Added a Pydantic `model_validator` to `SimulationConfiguration` that automatically aliases `{ plant_graph: ... }` to `plant`, resolving a critical bug where simulations were running with an empty 0-node plant.
   - Added an `id` fallback validator for `SimulationSnapshot` to satisfy legacy test assertions.
3. **Telemetry Computation Engine (`backend/app/engine/simulator.py`)**:
   - Added `_calculate_telemetry()` executed on every clock tick and lifecycle transition.
   - Computes machine operating states (`IDLE`, `RUNNING`), real-time power (MW / kW), operating temperatures (°C), cooling water circulation (m³/h), and throughput (t/h) based on equipment specifications (`RAW_MATERIAL_STORAGE`, `INDUCTION_FURNACE`, `LADLE_REFINING_FURNACE`, `CONTINUOUS_CASTING_MACHINE`, `REHEATING_FURNACE`, `ROLLING_MILL`, `TMT_QUENCHING_BOX`, `COOLING_BED`, `UTILITY_SUBSTATION`, `WATER_COOLING_SYSTEM`).
   - Computes plant-wide totals (`total_power_mw`, `total_water_m3h`, `active_nodes`, `interlocked_nodes`, `total_nodes`).
   - Maintains a monotonic state version, bounded snapshot history, live subscribers, utility-aware equipment interlocks, bottleneck-propagated material flow, aggregate utility-capacity enforcement, and a CPU-safe capped `MAX` speed.
4. **Backend Test Suite**:
   - All **43/43 tests pass (100%)** via `pytest` (`test_simulation.py` and `test_topology.py`), including HTTP/WebSocket access protection, lifecycle cleanup, material-flow bounds, aggregate utility capacity, history, monotonic versioning, safety gating, and the full melt-shop baseline.

### B. Frontend Clean Single-Interface Architecture
1. **Master Simulation Deck in App Header (`frontend/src/App.tsx`)**:
   - Moved simulation controls out of the cramped 48px canvas bar up to the top application header.
   - **Status Pill:** `READY` (blue) ➔ `RUNNING` (emerald with active pulse) ➔ `PAUSED` (amber).
   - **Controls:** **Run ▶**, **Pause ⏸**, **Reset ↺**, and Speed buttons (`1x`, `5x`, `10x`, `60x`).
   - **Real-Time KPIs:** Live `Tick` counter, `Power (MW)`, `Water (m³/h)`, and `Active Machines (N/M)`.
   - **Graph Synchronization:** Added `currentGraph` state and `onGraphChange` listener to ensure `handleStart` sends the actual live canvas nodes/edges directly to `/api/simulations`.
   - Physics-relevant graph edits retire stale backend simulations automatically, while layout-only movement preserves the active run.
   - Removed dead duplicate views where the canvas and an old static HUD table were stacked on top of each other.
2. **Restored, Clean Canvas Toolbar (`frontend/src/components/PlantBuilder/Blueprint.tsx`)**:
   - Canvas toolbar restored to spacious, uncluttered engineering actions:
     - *Left:* Library toggle, Inspector toggle, Issues/Events drawer toggle, Select mode.
     - *Center:* Auto Connect, Auto Layout, Auto Setup, Validate.
     - *Right:* Undo, Redo, Zoom In/Out, Fit Plant, Focus Mode, Demo Template, Save, Load, Clear.
   - Saves template to `localStorage` on Demo load as a fallback.
3. **Live Machine Cards (`frontend/src/components/PlantBuilder/CustomNode.tsx`)**:
   - Nodes on the canvas visually respond to simulation ticks:
     - Emerald status badge with glowing pulse dot when `RUNNING`.
     - Real-time power draw (MW/kW), temperatures (°C), throughput (t/h), and water flow (m³/h) display dynamically on each equipment card.
4. **Inspector Telemetry Card (`frontend/src/components/PlantBuilder/Inspector.tsx`)**:
   - Displays a dedicated "Live Telemetry" card in the right sidebar when any node is inspected during an active run.
5. **Dual-Tab Slide-up Drawer (`frontend/src/components/PlantBuilder/ValidationPanel.tsx`)**:
   - Toggles cleanly between **Topology Issues** (design/port errors) and the live **Event Console** (timestamped simulation event journal).
6. **Frontend Build Verification**:
   - `npm run lint`, four Node unit tests, the production build, and a Puppeteer browser workflow all pass. The browser regression covers Demo → Simulation → Run → Pause → Reset → topology invalidation → Overview with zero console errors.
7. **Task 2 Control Center (`frontend/src/App.tsx`)**:
   - Restored the strongest parts of the original standalone Task 2 UI inside the unified React application: live connection status, lifecycle/version/time/utilization KPIs, process-flow diagram, utility lane, clickable equipment inspector, authoritative state trace, and event journal.
   - WebSocket streaming is primary; a slower HTTP snapshot poll remains as a resilient fallback.
   - The builder stays mounted while switching views, so the current plant is never lost during navigation.

---

## 3. Work Accomplished in `C:\Users\prabh\acamis`
* **Deterministic Component Catalog (`backend/simulator/components.py`)**: 10 typed equipment models with typed directional ports (`MATERIAL`, `ELECTRICAL`, `WATER`, `SIGNAL`), rated specs, and deterministic state machines.
* **Typed Topology Validator (`backend/simulator/topology.py`)**: Strict physical connection validation and baseline 25 t/h TMT line with 22 connections (7 material, 9 electrical, 6 water).
* **Multi-Agent Decision Support (`backend/agents/`)**: 6 domain agents with strict priority hierarchies (`safety` = 1, `quality` = 2, `maintenance` = 3, `production` = 4, `energy` = 5, `logistics` = 6).

---

## 4. Current Operational Endpoints & Ports

* **Frontend**: `http://localhost:5173/` (Vite dev server running via `cmd /c "npm run dev"`)
* **Backend**: `http://127.0.0.1:8000/` (Uvicorn running via `python -m uvicorn main:app --port 8000`)
* **Key API Contracts**:
  * `POST /api/simulations`: Creates simulation instance with `{ plant: { nodes: [...], edges: [...] } }`.
  * `POST /api/simulations/{id}/command`: Accepts `{ command: "start" | "pause" | "resume" | "reset" | "set_speed", payload: {} }`.
  * `GET /api/simulations/{id}`: Returns `SimulationState` / `SimulationSnapshot` with `node_telemetry` and `plant_summary`.
  * `WS /api/simulations/{id}/stream`: Streams authoritative snapshots after every lifecycle change and deterministic tick.
  * `GET /api/simulations/{id}/snapshots`: Returns the bounded state-trace history.
  * `DELETE /api/simulations/{id}`: Cancels and removes an obsolete simulation.
  * `GET /api/plant/template/tmt`: Loads 10-node verified baseline TMT plant topology.

* **Optional Demo Protection**:
  * Set `STEELSIM_API_KEY` on the backend and matching `VITE_STEELSIM_API_KEY` on the frontend.
  * CORS defaults to the two local Vite origins and can be overridden with `STEELSIM_ALLOWED_ORIGINS`.

---

## 5. Next Steps for Codex / Developer Roadmap
1. **Integrate ACAMIS through a boundary adapter**: Keep ACAMIS as a separate decision-support product and let its 6 domain agents consume approved SteelSim telemetry contracts without merging either codebase or enabling machinery control.
2. **Dynamic Fault Injection**: Add interactive fault injection from the UI (e.g. tripping a cooling water pump or cutting an electrical line) to test how the plant state and agents react.
3. **Final Unified Documentation**: Produce consolidated documentation unifying SteelSim (Plant Builder + Simulation) and ACAMIS (Decision Intelligence).
