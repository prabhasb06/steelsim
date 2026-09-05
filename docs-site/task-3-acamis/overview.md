# 26. ACAMIS Overview

**ACAMIS** (Autonomous Cyber-Physical Agentic Manufacturing Intelligence System) is the operational-intelligence, monitoring, and policy-governance layer for the SteelSim digital twin. 

While the deterministic simulation engine (Task 2) calculates discrete, physics-based mass balances, electrical loads, and cooling water flows across the plant topology, ACAMIS sits directly above it to observe operating health, detect anomalies, evaluate multi-domain risk, coordinate containment, and schedule recovery procedures.

<pre class="mermaid">
graph TB
    subgraph ACAMIS ["ACAMIS Operational Intelligence Layer"]
        Monitoring["Automatic Monitoring & Telemetry Detector"]
        Specialists["6 Specialist Domain Evaluators"]
        Recovery["Central Recovery & Mitigation Planner"]
    end

    subgraph Core ["SteelSim Core Simulation Runtime"]
        Ticks["Discrete 1-Second Ticks (1 Hz)"]
        Flow["Mass & Energy Flow Network"]
        Utilities["Aggregate Utility Balance"]
    end

    Core -->|"Authoritative Snapshots (state_version)"| ACAMIS
    ACAMIS -->|"Approved Mitigations & Throttling"| Core
</pre>

---

## Core Purpose & Architectural Role

Traditional industrial plants rely on disjointed SCADA alarms, spreadsheets, and human memory to diagnose cascading production halts. In an induction-furnace mini-mill, a secondary slowdown downstream (e.g., in a rolling mill) causes liquid steel to back up into the Ladle Refining Furnace (LRF), threatening refractory wear or thermal freezing.

ACAMIS addresses this operational bottleneck by:
1. **Consuming Backend-Authoritative State:** Rather than scraping the user interface, ACAMIS reads authoritative, monotonic simulation snapshots directly from the simulation engine runtime (`sim.get_snapshot()`).
2. **Complementing the Simulator:** ACAMIS does not re-implement physics or replace the simulation runtime. The simulation engine remains the sole source of numerical truth for physical quantities (tonnage, MW, m³/h, °C). ACAMIS provides diagnostic interpretation, multi-disciplinary impact analysis, and approved simulated remediation.
3. **Enforcing Policy & Risk Gates:** Every remediation procedure passes through deterministic state-machine gates. High-risk physical repairs strictly mandate human verification, preventing autonomous runaway actions.

---

## Two Incident Types: Scenarios vs. Telemetry Incidents

ACAMIS handles two distinct classes of operational incidents:

| Dimension | Controlled Manual Scenarios (Task 3.0) | Automatic Telemetry Incidents (Task 3.1) |
| :--- | :--- | :--- |
| **Origin Badge** | `Manual scenario` | `Telemetry detector` |
| **Trigger Mechanism** | Operator clicks a pre-configured scenario button (e.g., *Cooling-water degradation*, *Furnace instability*) | Autonomous backend detector continuously checks measured mill throughput against expected baseline |
| **Activation Window** | Instantaneous upon operator injection | Requires continuous persistence (shortfall > 25% for 3 running ticks) |
| **Primary Purpose** | Investor demonstrations, operator training, and deterministic regression testing | Unprompted anomaly detection mimicking live industrial sensor drift |
| **Identifier Format** | `cooling_water_degradation`, `furnace_instability`, `rolling_mill_slowdown`, etc. | `telemetry_rolling_throughput_deviation` |

> [!NOTE]
> Manual scenarios take priority over automatic telemetry detection. When a manual scenario is injected, the automatic rolling monitor is suspended and labeled accordingly in the console.

---

## MVP Scope & Boundaries

To preserve industrial credibility, ACAMIS operates under strict engineering boundaries:

* **Digital Twin Only:** All actions, procedures, and mitigations modify only the in-memory SteelSim simulated runtime. ACAMIS does not currently communicate with physical PLCs, DCS controllers, or live plant machinery.
* **In-Memory Volatility:** All incident evidence, active mitigations, and audit entries reside in backend memory. A process restart resets active sessions to initial baseline.
* **Single Operational Incident:** At any given tick, only one primary operational incident can be active.
* **No Black-Box Control:** The core detector and specialist evaluations are fully deterministic algorithms. Optional external LLMs operate strictly in an advisory capacity behind deterministic safety gates.\n