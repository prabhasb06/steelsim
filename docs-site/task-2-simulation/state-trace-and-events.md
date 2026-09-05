# 24. State trace and events

SteelSim maintains an authoritative event journal and bounded historical snapshot trace for operational auditing and diagnostics.

## Event logging system

The simulation engine emits structured events (`SimulationEvent`) on state transitions, speed adjustments, and operational alarms:

```json
{
  "id": "evt_4f89a1c2",
  "simulation_id": "sim_9a7d3b2e",
  "simulation_time": "2026-01-01T08:02:22Z",
  "type": "EQUIPMENT_INTERLOCKED",
  "severity": "WARNING",
  "source": "InductionFurnace",
  "message": "Cooling-water flow restricted below safe operating limit (90.0 m³/h < 120.0 m³/h)."
}
```

### Event severity levels
- **`INFO`:** Normal lifecycle events (simulation started, paused, speed changed, reset).
- **`WARNING`:** Operational restrictions, material starvation, and capacity bottlenecks.
- **`ERROR`:** Equipment interlocks, aggregate utility trips, or fatal invariant violations.

## Bounded history governance

To prevent memory leaks during long-running sessions, the engine enforces strict memory boundaries:
- **Event history buffer:** Fixed-size ring buffer retaining the last **500 events** (FIFO eviction).
- **Snapshot trace buffer:** Fixed-size deque retaining the last **120 snapshots** for client charting.
- Historical snapshots can be retrieved via `GET /api/simulations/{id}/snapshots`.
