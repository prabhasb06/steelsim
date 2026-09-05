# 31. Incident Response & Recovery Workflow

When an anomaly is flagged—either automatically by the telemetry detector or manually through Scenario Control—ACAMIS executes a structured response lifecycle that prioritizes asset safety before restoring production pace.

---

## Response Sequence Diagram

<pre class="mermaid">
sequenceDiagram
    autonumber
    participant Sensor as Digital Twin Telemetry
    participant Monitor as Telemetry Detector
    participant Specialist as Specialist Evaluators
    participant Plan as Central Recovery Plan
    participant Gate as Policy & Autonomy Gate
    participant Engine as Simulation Runtime
    participant Audit as Audit Timeline

    Sensor->>Monitor: Tick telemetry (t/h, kW, m3/h, °C)
    Monitor->>Monitor: Verify deviation (>25% for 3 ticks)
    Monitor->>Specialist: Publish incident evidence
    Specialist->>Plan: Multi-domain assessment & procedures
    Plan->>Gate: Evaluate operating mode & risk level
    alt Low-risk procedure (Autonomous mode)
        Gate->>Engine: Schedule simulated recovery (T+12 ticks)
        Engine->>Monitor: Telemetry restored (>75% baseline)
        Monitor->>Audit: Record INCIDENT_RECOVERED
    else High-risk procedure (Furnace/Cooling)
        Gate-->>Plan: Escalate: HUMAN_VERIFICATION_REQUIRED
        Note over Gate: Operator confirms in dialog modal
        Gate->>Engine: Apply approved procedure
        Engine->>Audit: Record HUMAN_VERIFICATION_CONFIRMED
    end
</pre>

---

## 1. Incident Origins & Visual Differentiation

The console and Process Flow Diagram explicitly identify where an incident originated:

* **Telemetry detector:** Triggered by numerical deviation during runtime evaluation. Carries numerical deviation evidence, first detected tick, and persistence count.
* **Manual scenario:** Injected by operator command. Highlights pre-configured equipment groups and associated operational risks.

---

## 2. Affected-Asset Visualization & Cross-Navigation

Both the ACAMIS Console and the Simulation Control Center render the **Incident Impact** deck:
* Displays each affected node with baseline vs. actual telemetry (e.g., `throughput_tph: 70.0 ➔ 35.0 t/h`).
* Provides instant **Locate in plant** action (switches to Plant Builder, centers canvas, and highlights the asset) and **Inspect simulation** action (switches to Simulation Control and scrolls the process card into view).

---

## 3. Autonomous Scheduling & Recovery Verification

For low-risk incidents in Autonomous Simulation mode:
1. **Clock-Synchronized Scheduling:** Recovery is scheduled for `sim.tick + 12`.
2. **Deterministic Advance:** The simulation clock must advance 12 running ticks for the simulated inspection to conclude.
3. **Verification Before Closure:** When tick $T + 12$ is reached, `_resolve_incident()` verifies that live readings on all affected assets have returned to $\ge 75\%$ of expected baseline:
   ```python
   recovered = actual >= expected * detector.LIMIT
   ```
   If verified, the incident is closed, plant health returns to `NORMAL`, and an immutable `INCIDENT_RECOVERED` event is logged.

---

## 4. Human Intervention for Severe Incidents

When high-risk scenarios occur in Autonomous Simulation mode:
* The Central Recovery Plan transitions to:
  ```json
  "status": "HUMAN_VERIFICATION_REQUIRED"
  ```
* An **alert dialog modal** is presented in the user interface:
  * Outlines the contained state of the plant.
  * Specifies the high-risk action required (e.g., `stabilize_furnace`, `activate_standby_cooling`).
  * Requires the operator to click **Apply human intervention**, which dispatches the request with flag `human_verified: true`.
* The audit trail permanently captures `HUMAN_VERIFICATION_CONFIRMED`.\n