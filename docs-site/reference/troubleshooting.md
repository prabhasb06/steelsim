# 34. Troubleshooting

Common setup, connectivity, and simulation issues and their resolutions.

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
