# 33. Testing

The SteelSim platform maintains continuous quality verification through a multi-tier test matrix covering backend unit tests, frontend component utilities, static analysis, and headless browser automation.

## Test suite execution

### 1. Backend tests (Pytest)
```powershell
cd backend
python -m pytest -v
```
- **Coverage:** 43 tests across `tests/test_simulation.py` and `tests/test_topology.py`.
- **Validation scopes:** Lifecycle state transitions, command endpoints, monotonic versioning, aggregate utility capacity enforcement, material flow boundaries, and WebSocket token authentication.

### 2. Frontend unit tests (Node Test Runner)
```powershell
cd frontend
npm test
```
- **Coverage:** 4 tests in `tests/simulation-utils.test.ts`.
- **Validation scopes:** Topological process ordering, cross-simulation snapshot rejection, monotonic version guards preventing state rewind, and layout-only edit preservation.

### 3. Static analysis & compilation
```powershell
cd frontend
npm run lint    # Oxlint static analysis (0 errors, 0 warnings)
npm run build   # TypeScript strict type checking & Vite bundle
```

### 4. Headless browser E2E smoke test (Puppeteer)
```powershell
cd frontend
npm run test:e2e
```
- Validates the complete 18-step user journey from demo load through simulation run, pause, reset, canvas clear, and obsolete simulation cleanup, ensuring zero console errors.
