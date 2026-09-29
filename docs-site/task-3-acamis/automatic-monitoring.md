# 30. Automatic Monitoring & Telemetry Detector

Introduced in **Task 3.1**, Automatic Monitoring evaluates simulated rolling-mill throughput against the backend's expected baseline on each running tick. It is a deterministic threshold rule, not a statistical model or a detector of unknown physical faults. The separate temperature, cooling, and power rules are documented under [Telemetry review cases](/task-4-history/signal-review-cases).

---

## Detection Mechanism & Formula

The rolling throughput monitor evaluates all equipment nodes classified under:
`{"ROLLING_MILL", "ROUGHING_MILL", "INTERMEDIATE_MILL", "FINISHING_MILL"}`.

Every running tick, the detector reads actual node throughput from the SteelSim snapshot and expected throughput from its deterministic baseline. The baseline reflects the configured plant and simulated upstream material flow. It is not a calibrated physical sensor reference.

An anomaly is flagged when actual output drops more than **25%** below expected baseline:

$$A_T < 0.75 \times E_T$$

### Telemetry Detector Evaluation Window

| Timeline Stage | Tick Count | Measured Output ($A_T$) | Persistence Counter | Detector State | System Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial drift** | Tick 10 | 35.0 t/h (illustrative) | 1 / 3 ticks | `Watching` | Counter starts; no incident or audit alarm |
| **Sustained deficit** | Tick 11 | 35.0 t/h (illustrative) | 2 / 3 ticks | `Watching` | Counter increments; no incident |
| **Incident confirmation** | Tick 12 | 35.0 t/h (illustrative) | 3 / 3 ticks | `Detected` | `telemetry_rolling_throughput_deviation` is created |
| **Scheduled recovery** | Later running ticks | Depends on simulation | — | `Recovering` | Only in Autonomous Simulation mode; simulated inspection is scheduled 12 running ticks later |
| **Verified recovery** | After procedure | At least 75% of expected | 0 / 3 ticks | `Recovered` | Live throughput is checked before the incident closes |

---

## The 3-Tick Persistence Rule

The persistence window suppresses short simulated transients:
1. **Single-Tick Immunity:** A single-tick or two-tick drop below 75% will **not** trigger an alarm. The detector simply enters `Watching` state.
2. **Persistence Requirement:** The shortfall must strictly persist for **three consecutive running simulation ticks** (`WINDOW = 3`) on the same equipment node.
3. **Reset on Recovery:** If throughput recovers before reaching 3 ticks, the persistence counter resets to 0.

---

## Lifecycle States of the Detector

The monitor transitions through five distinct states:

| State | Definition & System Behavior |
| :--- | :--- |
| **Normal** | Live throughput across all rolling mills is within the normal operating band ($A_T \ge 0.75 \times E_T$). |
| **Watching** | A deficit exceeds 25%, but persistence count is less than 3 ticks. No incident is created; monitoring continues. |
| **Detected** | The deviation persisted for 3 running ticks. Incident `telemetry_rolling_throughput_deviation` is registered with origin `Telemetry detector`. |
| **Recovering** | In Autonomous Simulation mode, an inspection schedule is running. |
| **Recovered** | Throughput has been verified to return above the lower bound. Historical evidence is retained for review. |

---

## Structured Evidence Payload

When an incident is declared, ACAMIS retains structured evidence in the live monitor and run history. This is an MVP SQLite record, **not** an immutable or tamper-evident evidence store. A representative evidence item is:

```json
{
  "equipment_id": "mill_01",
  "actual_tph": 31.5,
  "expected_tph": 70.0,
  "deviation_percent": 55.0,
  "first_detected_tick": 40,
  "persistence_count": 3
}
```

---

## Synthetic Anomaly Demo Injection

For live demonstrations, the ACAMIS console and REST API provide a controlled disturbance. No probabilistic or external sensor source is involved:

```bash
curl -X POST http://127.0.0.1:8000/api/simulations/{id}/acamis/monitoring/demo
```

**Execution sequence:**
1. Applies a 50% capacity factor to the first configured rolling-mill node.
2. The simulation engine runs ticks: Tick 1 (Watching 1/3) $\rightarrow$ Tick 2 (Watching 2/3) $\rightarrow$ Tick 3 (Detected).
3. Origin badge displays `Telemetry detector` (proving the incident was detected by automated telemetry rather than a manual scenario injection).
4. In Autonomous Simulation mode, demonstrates approved low-risk simulated recovery after 12 further running ticks. Observe mode detects and explains without executing a procedure.
