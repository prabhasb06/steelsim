# 41. WebSocket API

The WebSocket API streams live, backend-authoritative telemetry snapshots directly to connected clients on every discrete simulation tick.

## Connection specification

- **URL:** `ws://127.0.0.1:8000/api/simulations/{sim_id}/stream` (or `wss://` in production)
- **Subprotocols:**
  - Standard: `steelsim`
  - Authenticated (when API key is set): `steelsim-key.<base64url-encoded-key>`

## Streaming behavior

1. **Initial handshake:** Immediately upon connection, the server sends the current snapshot representing the existing state.
2. **Tick broadcasting:** While the simulation is `RUNNING`, the server emits a full snapshot on every clock tick.
3. **Keep-alive ping:** If the simulation is paused or waiting, a snapshot heartbeat is sent at least once every 15 seconds to prevent network timeouts.
4. **Disconnection codes:**
   - `4401:` Invalid or missing API key.
   - `4404:` Simulation ID not found or evicted from memory.

## ACAMIS telemetry payload extensions

In Task 3, every broadcast `SimulationSnapshot` includes ACAMIS operational impact metadata:
- `expected_throughput_tph` (`float | null`): Nominal baseline capacity calculated from active nodes ($25.0\text{ t/h}$ in standard TMT baseline).
- `acamis_impact` (`AcamisImpactSummary | null`): Present during active incidents or scenarios, reporting:
  - `active_scenario`: Identifier of active scenario (`cooling_water_degradation`, etc.) or `null`.
  - `mitigation_in_progress`: Boolean flag indicating if autonomous or manual mitigation is active.
  - `mitigation_procedure`: Identifier of executing procedure or `null`.
  - `operational_mode`: Current autonomy mode (`OBSERVE`, `ADVISORY`, `AUTONOMOUS_SIMULATION`).
  - `safety_gate_active`: Boolean flag indicating if a human approval safety gate is holding actions.

## Client message handler example

```typescript
const socket = new WebSocket('ws://127.0.0.1:8000/api/simulations/sim_123/stream', ['steelsim']);

socket.onmessage = (event) => {
  const snapshot = JSON.parse(event.data);
  // Enforce monotonic state versioning
  if (snapshot.state_version >= currentVersion) {
    currentVersion = snapshot.state_version;
    renderControlCenter(snapshot);
    // Task 3: Render ACAMIS operational telemetry
    if (snapshot.acamis_impact) {
      renderAcamisOverlay(snapshot.acamis_impact);
    }
  }
};
```

