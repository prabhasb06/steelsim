# 33. ACAMIS Intelligence User Interface

The ACAMIS Console (`frontend/src/components/AcamisConsole.tsx`) provides an integrated, single-pane-of-glass operations center designed for plant managers, metallurgical engineers, and shift operators.

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
        SpecialistDeck["Specialist Intelligence<br/>• 6 Domain Rule Evaluators<br/>• Severity & Root Cause"]
        RecoveryPlan["Central Recovery Plan<br/>• Containment Actions<br/>• Scheduled Procedures<br/>• Human Risk Authorization Modal"]
        AuditLog["Operations Audit Timeline<br/>• Monotonic Ticks & Timestamps<br/>• Origin Classification"]
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
* Aggregate plant power demand change (MW) and cooling water deficit ($	ext{m}^3/	ext{h}$).
* **Cross-Navigation Buttons:**
  * **Locate in plant:** Automatically jumps to the visual Plant Builder canvas and centers the camera on the affected equipment node.
  * **Inspect simulation:** Navigates directly to the Simulation Control Center process flow diagram.

### 3. Automatic Monitoring Card
Visualizes the real-time status of the Task 3.1 throughput anomaly detector:
* Rolling mill telemetry readings ($A_T$ vs. $E_T$).
* Persistence counter progress bar (`0/3`, `1/3`, `2/3`, `3/3`).
* **Demo Button:** "Inject throughput anomaly (demo)" sends a synthetic 50% capacity restriction to demonstrate detection and recovery without human scenario selection.

### 4. Specialist Intelligence (6 Domains)
Displays findings from the 6 diagnostic rule evaluators:
* Mechanical, Electrical, Thermal, Utility, Casting, and Raw Material.
* Each card reports domain health (`NORMAL`, `WARNING`, `CRITICAL`), primary diagnostic message, and identified root cause.

### 5. Central Recovery Plan
Presents actionable mitigation procedures:
* Procedure name, description, and risk level (`LOW`, `MEDIUM`, `HIGH`).
* In Advisory mode: Clickable **Apply** buttons for operator-guided remediation.
* In Autonomous mode: Live countdown display (*"Autonomous simulated recovery in N simulation ticks"*).

### 6. Human Intervention Alert Dialog
When a `HIGH`-risk procedure is scheduled in Autonomous mode:
* ACAMIS triggers a high-priority modal dialog (`role="alertdialog"`).
* Displays safety warnings, affected machinery, and required confirmation.
* Traps keyboard focus (`Tab`, `Escape`) and provides an explicit **Apply human intervention** button.

### 7. Advisory Model Gateway Panel
Enables operators to connect an external Google Gemini API key:
* Input field with key masking (`••••••••••••`).
* Live connection status probe.
* Interactive chat console allowing operators to ask questions regarding the live simulation state.

### 8. Audit Timeline
Chronological, append-only log of operational events:
* Displays tick index, event type (`INCIDENT_DECLARED`, `CONTAINMENT_APPLIED`, `PROCEDURE_EXECUTED`, `INCIDENT_RECOVERED`), origin (`Manual scenario` vs `Telemetry detector`), and operator signature.\n