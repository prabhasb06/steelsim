# 45. Testing

The SteelSim platform maintains continuous quality verification through a multi-tier test matrix covering backend unit tests, frontend component utilities, static analysis, and headless browser automation.

## Test suite execution

### 1. Backend tests (Pytest)
```powershell
# Run from repository root (using root pytest.ini)
python -m pytest backend/tests -v
```
- **Coverage:** **72 passing tests** across 4 dedicated test suites:
  - `backend/tests/test_topology.py` (Task 1: Topology graph, port validation, auto-setup)
  - `backend/tests/test_simulation.py` (Task 2: Deterministic engine, material balance, utility capacity, WebSocket auth)
  - `backend/tests/test_acamis.py` (Task 3: 8-stage evaluator, scenario injection, autonomous mitigation, risk gates, gateway key isolation)
  - `backend/tests/test_monitoring.py` (Task 3.1: Automatic throughput anomaly detection, 3-tick rule, evidence payload, synthetic drift)
- **Configuration:** Root `pytest.ini` specifies `pythonpath = backend` and `testpaths = backend/tests`, ensuring clean discovery from any terminal context.
- **Dedicated Task 3 Guide:** See [ACAMIS Testing & Verification Suite](/task-3-acamis/testing) for detailed test breakdown.

### 2. Frontend unit tests (Node Test Runner)
```powershell
npm --prefix frontend test
```
- **Coverage:** 4 tests in `frontend/tests/simulation-utils.test.ts`.
- **Validation scopes:** Topological process ordering, cross-simulation snapshot rejection, monotonic version guards preventing state rewind, and layout-only edit preservation.

### 3. Static analysis & compilation
```powershell
npm --prefix frontend run lint    # Oxlint static analysis (0 errors, 0 warnings across 20 files)
npm --prefix frontend run build   # TypeScript strict type checking & Vite bundle
```

### 4. Documentation site static build
```powershell
npm --prefix docs-site run docs:build
```
- Compiles all 53+ documentation pages, styles, search index, and Mermaid diagrams with zero syntax errors or broken links.

### 5. Headless browser E2E smoke test (Puppeteer)
```powershell
npm --prefix frontend run test:e2e
```
- Validates the complete 18-step user journey from demo load through simulation run, pause, reset, canvas clear, ACAMIS operations console inspection, and obsolete simulation cleanup, ensuring zero console errors.

