# 30. Automatic Monitoring & Telemetry Detector

Introduced in **Task 3.1**, Automatic Monitoring provides continuous, non-intrusive surveillance of simulated plant sensor streams. Unlike manual scenarios, which require human activation, the automatic detector evaluates live numerical outputs against an expected baseline calculated on every simulation tick.

---

## Detection Mechanism & Formula

The rolling throughput monitor evaluates all equipment nodes classified under:
`{"ROLLING_MILL", "ROUGHING_MILL", "INTERMEDIATE_MILL", "FINISHING_MILL"}`.

Every running tick, the detector retrieves:
* **$A_T$ (Actual Throughput):** Live measured tonnage per hour ($	ext{t/h}$) from `sim.node_telemetry`.
* **$E_T$ (Expected Baseline):** Deterministic baseline from `sim.expected_telemetry`, reflecting upstream billet delivery, nominal motor speeds, and configured load factors.

An anomaly is flagged when actual output drops more than **25%** below expected baseline:

$$A_T < 0.75 \times E_T$$

### Telemetry Detector Evaluation Window

| Timeline Stage | Tick Count | Measured Output ($A_T$) | Persistence Counter | Detector State | System Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial Drift** | Tick 10 | $35.0\text{ t/h}$ (Deficit: 50%) | 1 / 3 ticks | `WATCHING` | Anomaly logged; transient timer begins; no alarm |
| **Sustained Deficit** | Tick 11 | $35.0\text{ t/h}$ (Deficit: 50%) | 2 / 3 ticks | `WATCHING` | Threshold timer increments; awaiting confirmation |
| **Incident Confirmation** | Tick 12 | $35.0\text{ t/h}$ (Deficit: 50%) | 3 / 3 ticks (Window Met) | `DETECTED` | Anomaly confirmed; `telemetry_rolling_throughput_deviation` declared |
| **Closed-Loop Action** | Tick 13+ | $35.0\text{ t/h} \rightarrow 70.0\text{ t/h}$ | — | `RECOVERING` | Autonomous inspection scheduled (12 ticks); mitigation executed |
| **Normal Restored** | Post-Recovery | $70.0\text{ t/h} \ge 0.75 \times E_T$ | 0 / 3 ticks | `RECOVERED` | Output verified restored; incident closed to audit log |

---

## The 3-Tick Persistence Rule

Industrial rolling mills routinely experience brief momentary load variations (e.g., billet inter-pass gap time). To eliminate false alarms:
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
| **Recovering** | In Autonomous Simulation mode, an inspection schedule is running, or an operator has applied a corrective procedure. |
| **Recovered** | Throughput has been verified to return above the lower bound. Historical evidence is retained for review. |

---

## Structured Evidence Payload

When an incident is declared, the detector captures an unalterable evidence record:

```json
{
  "incident_id": "inc_rolling_deviation_418",
  "origin": "Telemetry detector",
  "anomaly_type": "telemetry_rolling_throughput_deviation",
  "detected_at_tick": 42,
  "evidence_payload": {
    "target_component": "ROLLING_MILL",
    "actual_throughput_tph": 31.5,
    "expected_throughput_tph": 70.0,
    "ratio": 0.45,
    "threshold": 0.75,
    "consecutive_ticks": 3,
    "underperforming_nodes": ["node_rolling_mill_01"],
    "recent_trace": [
      { "tick": 40, "actual": 31.5, "expected": 70.0 },
      { "tick": 41, "actual": 31.5, "expected": 70.0 },
      { "tick": 42, "actual": 31.5, "expected": 70.0 }
    ]
  }
}
```

---

## Synthetic Anomaly Demo Injection

To facilitate live demonstrations without waiting for natural probabilistic drift, the ACAMIS console and REST API provide a synthetic injection hook:

```bash
curl -X POST http://127.0.0.1:8000/api/simulations/{id}/acamis/monitoring/demo
```

**Execution sequence:**
1. Injects a temporary 50% capacity constraint on active rolling mill nodes.
2. The simulation engine runs ticks: Tick 1 (Watching 1/3) $\rightarrow$ Tick 2 (Watching 2/3) $\rightarrow$ Tick 3 (Detected).
3. Origin badge displays `Telemetry detector` (proving the incident was detected by automated telemetry rather than a manual scenario injection).
4. Demonstrates the complete autonomous recovery pipeline.\n