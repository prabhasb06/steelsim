# 35. ACAMIS Testing & Verification Suite

The SteelSim repository maintains comprehensive automated test coverage for both the core simulation engine and the ACAMIS operational-intelligence layer.

---

## Running Backend Tests from Repository Root

Backend tests can be executed directly from the repository root:

```powershell
python -m pytest backend/tests
```

### Root-Level Discovery via pytest.ini
Repository-root execution is powered by `pytest.ini` located at the root of the project:

```ini
[pytest]
pythonpath = backend
testpaths = backend/tests
asyncio_mode = strict
```

This configuration ensures Python automatically adds `backend/` to `sys.path`, resolving imports like `from app.acamis import service` without requiring manual environment exports.

---

## Verified Test Results

| Test Module | Tests | Passing | Focus Area |
| :--- | :---: | :---: | :--- |
| `test_acamis.py` | 18 | 18 | Scenarios, autonomy modes, human approval gates, procedure gating |
| `test_monitoring_api.py` | 1 | 1 | End-to-end REST monitoring demo trigger & status contract |
| `test_rolling_detector.py` | 10 | 10 | 3-tick persistence, 25% threshold, recovery verification, pause freezing |
| `test_simulation.py` | 32 | 32 | Tick engine, material flow, electrical/cooling models, WebSocket snapshot |
| `test_topology.py` | 11 | 11 | Industrial ports, syntax validation, graph connectivity |
| **Total Backend Suite** | **72** | **72** | **100% Passing (2.79s execution)** |

---

## Verified Behavioral Assertions

The test suite systematically enforces the following architectural invariants:

1. **Baseline Immunity:** Normal steady-state throughput produces zero automatic incidents.
2. **Persistence Guard:** A 1-tick or 2-tick drop below the 75% threshold produces no incident; the detector enters Watching and resets if throughput recovers.
3. **Deterministic Trigger:** An unmitigated deficit lasting $\ge 3$ consecutive ticks triggers exactly one `telemetry_rolling_throughput_deviation` incident.
4. **Pause Invariance:** Pausing the simulation engine freezes the persistence counter and autonomous recovery clock.
5. **Reset Idempotency:** Invoking scenario reset or simulation reset completely flushes detector samples and restores Normal monitoring state.
6. **Autonomy Safety Gating:** Autonomous Simulation mode schedules recovery only for approved low-risk procedures (12-tick duration). High-risk procedures (e.g., furnace repairs) strictly reject automated completion until explicit human verification is confirmed.
7. **Zero Model Dependency:** All core detector, specialist evaluation, and recovery behaviors pass without an external LLM API key.

---

## Frontend Test & Verification Suite

Frontend verification commands run via npm from the project root:

```powershell
# Run Node test runner for simulation client guards
npm --prefix frontend test

# Run strict TypeScript compiler check
npx --prefix frontend tsc --noEmit

# Run fast code linter across all components
npx --prefix frontend oxlint
```

* **Frontend Unit Tests:** 4 of 4 passed (validates process card topological ordering, WebSocket payload guards, monotonic version checks, and layout-only edit preservation).
* **Linter & Typecheck:** 0 errors and 0 warnings across 20 source files.\n