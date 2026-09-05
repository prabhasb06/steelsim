# 46. Troubleshooting

Common setup, connectivity, simulation, and ACAMIS operations issues and their resolutions.

## Diagnostic guide

### 1. Simulation blocked on start
- **Symptom:** Clicking **Run** displays `Simulation blocked: resolve N topology issues first`.
- **Cause:** One or more placed equipment nodes lack a connected power or cooling water supply, or the material line has an invalid metallurgical sequence.
- **Resolution:** Open the **Topology Issues** drawer at the bottom of the canvas. Click **Auto Setup** to automatically wire missing utility lines and sort the sequence.

### 2. WebSocket connection status shows RECONNECTING
- **Symptom:** Top bar shows amber pulse and `RECONNECTING`.
- **Cause:** Backend service is stopped, running on a non-standard port, or blocked by a firewall.
- **Resolution:** Verify the backend is running at `http://127.0.0.1:8000/api/health`. If using an alternate port, set `VITE_API_PROXY_TARGET` in `frontend/.env`.

### 3. API key mismatch (HTTP 401 / WS 4401)
- **Symptom:** UI displays `Invalid or missing SteelSim API key`.
- **Cause:** `STEELSIM_API_KEY` is set on the backend, but `VITE_STEELSIM_API_KEY` is missing or mismatched in the frontend.
- **Resolution:** Ensure both environment variables contain identical values, or clear both to run in unauthenticated local mode.

### 4. Plant Builder elements visible on Simulation view
- **Symptom:** Equipment cards or port handles appear overlaid on the Simulation Control Center.
- **Cause:** Canvas layer visibility styles failed to apply.
- **Resolution:** Verified fixed in commit `e1dad6e`. The canvas layer receives `opacity: 0` and `pointer-events: none` whenever viewMode is not `BUILDER`.

### 5. ACAMIS scenario controls disabled or unresponsive
- **Symptom:** Clicking scenario triggers (`Cooling Water Degradation`, etc.) has no effect or buttons are disabled.
- **Cause:** Simulation is in `READY` or `PAUSED` state. The ACAMIS evaluation loop requires advancing simulation ticks to process degradation and compute specialist findings.
- **Resolution:** Ensure the simulation clock is actively `RUNNING` before triggering controlled scenarios or synthetic drift.

### 6. ACAMIS procedure not executing automatically
- **Symptom:** Recommended procedure remains pending despite autonomy being enabled.
- **Cause:** System is in `ADVISORY` or `OBSERVE` mode, or the recommended procedure carries `HIGH` risk triggering the mandatory safety gate.
- **Resolution:** Verify autonomy mode is set to `AUTONOMOUS_SIMULATION`. If risk is `HIGH`, an operator must manually review and confirm the action in the safety dialog.

### 7. Advisory Model Gateway connection failure (HTTP 400 / 403)
- **Symptom:** Model status shows `Connection Failed` or chat requests fail with an API error.
- **Cause:** Invalid Google AI Studio key, IP quota limit exceeded, or network restriction blocking `generativelanguage.googleapis.com`.
- **Resolution:** Verify your Gemini API key format (`AIzaSy...`) in Google AI Studio. Note that model keys are transient and held only in process memory; reconnecting requires re-entering the key.

