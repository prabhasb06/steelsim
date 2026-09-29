# 28. Operating Modes & Risk Gates

ACAMIS enforces strict separation of operational permissions through three selectable autonomy levels: **Observe**, **Advisory**, and **Autonomous Simulation**.

## Operating Modes & Authorization Matrix

| Operational Feature / Permission | `OBSERVE` Mode | `ADVISORY` Mode | `AUTONOMOUS_SIMULATION` Mode |
| :--- | :---: | :---: | :---: |
| **Telemetry Anomaly Detection** | Active | Active | Active |
| **6 Specialist Domain Reviews** | Active | Active | Active |
| **Measured evidence and domain assessments** | Active | Active | Active |
| **Registered procedure recommendations for a primary incident** | Visible, not executable | Operator can apply | Low-risk recovery scheduled or high-risk containment applied |
| **Operator Manual Procedure Execution** | Blocked (HTTP 409) | Enabled (Operator-in-the-Loop) | Enabled (Manual Override) |
| **Autonomous low-risk recovery** | Disabled | Disabled | Scheduled after 12 running ticks |
| **High-risk final recovery** | Blocked by Observe mode | Operator can apply registered procedure | Requires explicit human verification |
| **Additional signal review cases** | Detect and acknowledge | Detect and acknowledge | Detect and acknowledge; no automatic repair mapped |

---

## Mode Comparison

### 1. Observe Mode (Default)
In Observe mode, ACAMIS monitors the digital twin passively:
* Continuously runs automatic detectors and calculates specialist domain evaluations.
* Flags anomalies, displays affected assets, and builds the Central Recovery Plan.
* **Prohibition:** Neither the system nor the operator can execute recovery procedures. Any attempt to invoke `/api/simulations/{id}/acamis/procedures/{name}` returns HTTP 409 Conflict:
  > *"Set ACAMIS to Advisory or Autonomous Simulation before applying a procedure."*

### 2. Advisory Mode (Operator-in-the-Loop)
Advisory mode empowers the human operator while maintaining absolute manual control:
* ACAMIS suggests prioritized containment and recovery actions.
* The operator evaluates the recommendations and clicks **Apply** on specific procedures.
* The system executes the simulated action, logs an audit entry, and recalculates telemetry.
* **Prohibition:** The system will not automatically apply procedures without operator input.

### 3. Autonomous Simulation Mode (Policy-Gated Closed Loop)
Autonomous Simulation mode acts only on registered procedures inside the virtual plant:
* **Safe Containment:** If a severe incident occurs, safe containment actions (such as `reduce_heat_load`) are triggered immediately by ACAMIS to prevent cascading plant stalls.
* **Low-Risk Recovery:** For low-risk incidents (such as `rolling_mill_slowdown` or `telemetry_rolling_throughput_deviation`), ACAMIS schedules a simulated inspection and recovery procedure after **12 running simulation ticks**.
* **High-Risk Human Gate:** For severe scenarios threatening physical equipment integrity (e.g., `furnace_instability`, `cooling_water_degradation`), autonomous recovery halts with:
  ```
  Status: HUMAN_VERIFICATION_REQUIRED
  ```
  The system displays an alert modal dialog requiring explicit human confirmation before the high-risk procedure can execute.

---

## Risk Tiering Matrix

ACAMIS uses the active scenario's registered procedure and escalation rules, rather than an open-ended list of generated repairs:

| Incident type | Registered procedure examples | Autonomous behavior |
| :--- | :--- | :--- |
| Rolling slowdown or rolling-throughput deviation | `pace_upstream_material`, `inspect_rolling_mill` | Schedule final simulated recovery after 12 running ticks. |
| Furnace instability | `reduce_heat_load`, `stabilize_furnace` | Apply containment; final recovery needs human verification. |
| Cooling-water degradation | `reduce_heat_load`, `activate_standby_cooling` | Apply containment; final recovery needs human verification. |
| Persistent temperature, cooling-flow, or power signal case without a primary incident | No recovery procedure mapped | Show evidence and require operator review; no automatic actuation. |

---

## Pause / Freeze Behavior

A critical industrial safety rule is enforced across all modes:

> [!IMPORTANT]
> **Deterministic Clock Synchronization:**
> When the simulation clock is paused (`POST /pause`), the entire ACAMIS operational engine freezes in lockstep:
> * Recovery countdown timers pause and hold their remaining ticks.
> * Telemetry persistence counters freeze without decay.
> * New manual scenario injection is rejected while paused. An operator acknowledgement records a review decision but does not advance telemetry or recovery. Resume the simulation to continue monitoring or a scheduled procedure.
