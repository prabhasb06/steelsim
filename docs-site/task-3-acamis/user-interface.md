# 33. ACAMIS Intelligence User Interface

The ACAMIS Console (`frontend/src/components/AcamisConsole.tsx`) presents monitoring, controlled scenarios, policy decisions, and review evidence from the SteelSim backend. It is a simulation interface, not a physical plant-control system.

---

## Console Layout & Component Architecture

<pre class="mermaid">
flowchart TD
    subgraph Header ["1. Executive Header Bar"]
        HealthBadge["Plant Health Badge<br/>(NORMAL · INCIDENT · STABILIZED)"]
        AutonomySelect["Operating Mode Selector<br/>(Observe · Advisory · Autonomous)"]
        SafetyIndicator["Safety Gate Alert Indicator"]
    end

    subgraph TopGrid ["2. Primary Diagnostic Grid"]
        IncidentDeck["Incident Impact Deck<br/>• Baseline vs Actual Metrics<br/>• Locate in Plant Cross-Navigation<br/>• Inspect Simulation Action"]
        MonitoringPanel["Automatic Monitoring Panel<br/>• Live Equipment Telemetry<br/>• 3-Tick Persistence Bar<br/>• Synthetic Anomaly Demo Button"]
    end

    subgraph MiddleGrid ["3. Operations & Advisory Grid"]
        ScenarioToolbar["Scenario Control Toolbar<br/>• 5 Controlled Failure Triggers<br/>• Reset Active Scenario"]
        ModelPanel["Advisory Model Gateway<br/>• BYOK Key Input & Masking<br/>• Model Status & Verification<br/>• Advisory AI Chat Console"]
    end

    subgraph BottomGrid ["4. Governance & Audit Grid"]
        SpecialistDeck["Specialist Intelligence<br/>• 6 Deterministic Domain Assessments"]
        RecoveryPlan["Central Recovery Plan<br/>• Containment Actions<br/>• Scheduled Procedures<br/>• Human Risk Authorization Modal"]
        AuditLog["Operations Audit Timeline<br/>• Recorded Events & Details"]
    end

    Header --> TopGrid --> MiddleGrid --> BottomGrid
</pre>

---

## Primary UI Panels & Modules

### 1. Plant Health & Executive Header
Displays real-time operational status at a glance:
* **Health Badges:**
  * `NORMAL` (Green): All equipment operating within nominal bounds.
  * `INCIDENT` (Amber / Red): Active scenario or telemetry anomaly detected.
  * `STABILIZED` (Blue): Containment action active; awaiting final recovery.
* **Autonomy Selector:** Instant dropdown switching between `OBSERVE`, `ADVISORY`, and `AUTONOMOUS SIMULATION`.

### 2. Incident Impact Deck
When an incident is active, displays the quantitative physical impact:
* Baseline throughput vs. actual degraded throughput.
* Aggregate plant power demand and cooling-water readings where available in the current snapshot.
* **Cross-Navigation Buttons:**
  * **Locate in plant:** Opens the Plant Builder with the affected equipment selected.
  * **Inspect simulation:** Opens the Simulation Control Center with the affected equipment selected.

### 3. Automatic Monitoring Card
Visualizes the real-time status of the Task 3.1 throughput anomaly detector:
* Rolling-mill actual and expected throughput, detector state, and persistence count.
* **Demo Button:** Injects a bounded simulated throughput restriction so the backend detector can observe a persistent deviation. This is a controlled demo input, not an unknown real-world fault.

### 4. Specialist Intelligence (6 Domains)
Displays findings from the 6 diagnostic rule evaluators:
* Safety, Maintenance, Quality, Production, Energy, and Logistics.
* Each card reports a deterministic severity, summary, and confidence value. The summaries are rule-based assessments, not proven root-cause diagnoses.

### 5. Central Recovery Plan
Presents actionable mitigation procedures:
* Procedure name and current step status.
* In Advisory mode: Clickable **Apply** buttons for operator-guided remediation.
* In Autonomous Simulation mode: Eligible low-risk rolling-mill recovery can be scheduled after the configured running-tick window; high-risk actions require human verification.

### 6. Human Intervention Alert Dialog
When an incident recovery plan requires human verification:
* ACAMIS triggers a high-priority modal dialog (`role="alertdialog"`).
* Displays safety warnings, affected machinery, and required confirmation.
* Provides **Review plan** and an explicit **Apply human intervention** action when the selected mode permits it. Reviewing or dismissing the prompt does not apply a procedure. This is a simulated authorization gate, not certified industrial safety control.

### 7. Advisory Model Gateway Panel
Enables operators to connect an external Google Gemini or OpenAI-compatible provider:
* Input field with key masking (`••••••••••••`).
* Connection verification through a provider request; provider charges may apply.
* An advisory review channel with relevant simulation context. Model replies cannot directly issue SteelSim commands, and the deterministic core works without an API key.

### 8. Audit Timeline
Backend-recorded events and details for scenarios, mode changes, signal reviews, and simulated procedures. The UI does not display a cryptographic operator signature or claim that the audit is tamper-proof. See [Signal Review Cases](../task-4-history/signal-review-cases.md) for the separate telemetry-evidence workflow.
