# 26. ACAMIS Overview

**ACAMIS** (Autonomous Cyber-Physical Agentic Manufacturing Intelligence System) is the operational-intelligence, monitoring, and policy-governance layer for the SteelSim digital twin. 

The deterministic simulation engine (Task 2) calculates plant telemetry. ACAMIS reads backend snapshots from that engine, applies defined detection and review rules, evaluates six operational domains, and gates approved simulated procedures. It is integrated with SteelSim; it is not a separate physical control system.

<pre class="mermaid">
graph TB
    subgraph ACAMIS ["ACAMIS Operational Intelligence Layer"]
        Monitoring["Automatic Monitoring & Telemetry Detector"]
        Specialists["6 Specialist Domain Evaluators"]
        Recovery["Central Recovery & Mitigation Planner"]
    end

    subgraph Core ["SteelSim Core Simulation Runtime"]
        Ticks["Discrete Simulation Ticks"]
        Flow["Mass & Energy Flow Network"]
        Utilities["Aggregate Utility Balance"]
    end

    Core -->|"Authoritative Snapshots (state_version)"| ACAMIS
    ACAMIS -->|"Approved Mitigations & Throttling"| Core
</pre>

---

## Core Purpose & Architectural Role

The MVP demonstrates how an operational-intelligence workflow can connect simulator readings, rule-based assessments, review evidence, and bounded recovery actions. These simulated behaviors must not be interpreted as validated predictions of an actual steel plant.

ACAMIS addresses this operational bottleneck by:
1. **Consuming Backend-Authoritative State:** Rather than scraping the user interface, ACAMIS reads authoritative, monotonic simulation snapshots directly from the simulation engine runtime (`sim.get_snapshot()`).
2. **Complementing the Simulator:** ACAMIS does not replace the simulation runtime. The engine provides the numerical simulation state; ACAMIS adds bounded incident rules, specialist summaries, signal-review cases, and approved simulated procedures.
3. **Enforcing Policy & Risk Gates:** Procedure execution passes through backend state and policy checks. High-risk simulated actions in Autonomous Simulation require human verification.

---

## Two Incident Types: Scenarios vs. Telemetry Incidents

ACAMIS handles two distinct classes of operational incidents:

| Dimension | Controlled Manual Scenarios (Task 3.0) | Automatic Telemetry Incidents (Task 3.1) |
| :--- | :--- | :--- |
| **Origin Badge** | `Manual scenario` | `Telemetry detector` |
| **Trigger Mechanism** | Operator clicks a pre-configured scenario button (e.g., *Cooling-water degradation*, *Furnace instability*) | Autonomous backend detector continuously checks measured mill throughput against expected baseline |
| **Activation Window** | Instantaneous upon operator injection | Requires continuous persistence (shortfall > 25% for 3 running ticks) |
| **Primary Purpose** | Guided demonstrations and deterministic regression testing | Detecting a defined rolling-throughput deviation from backend simulation telemetry |
| **Identifier Format** | `cooling_water_degradation`, `furnace_instability`, `rolling_mill_slowdown`, etc. | `telemetry_rolling_throughput_deviation` |

> [!NOTE]
> Manual scenarios take priority over automatic telemetry detection. When a manual scenario is injected, the automatic rolling monitor is suspended and labeled accordingly in the console.

---

## MVP Scope & Boundaries

To preserve industrial credibility, ACAMIS operates under strict engineering boundaries:

* **Digital Twin Only:** Procedures affect the SteelSim simulated runtime only. ACAMIS does not communicate with physical PLCs, DCS controllers, or live machinery.
* **Local History:** Task 4 records supported run snapshots, audit entries, and signal cases in local SQLite. Active runtime state and transient model keys are not a durable hosted service; the current Render deployment has no persistent disk.
* **Single Operational Incident:** At any given tick, only one primary operational incident can be active.
* **Additional Review Cases:** Persistent furnace-temperature, cooling-flow, and power-demand deviations can create evidence cases for review without automatically creating a repair procedure.
* **No Black-Box Control:** Detectors and specialist evaluations are deterministic. Optional external models return advisory text and cannot directly execute procedures.
