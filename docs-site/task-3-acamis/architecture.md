# 27. ACAMIS Architecture & Data Flow

ACAMIS executes a deterministic pipeline that runs concurrently with the SteelSim simulation clock. Every second, the digital twin updates physical quantities, which ACAMIS ingests, evaluates, and acts upon according to configured operating policies.

---

## Implemented Processing Pipeline

The interaction between the simulation runtime and ACAMIS follows a strict eight-stage deterministic lifecycle:

<pre class="mermaid">
flowchart TD
    Snapshot["1. Simulation Snapshot<br/>(Versioned state, ticks, node telemetry)"]
    Detect["2. Detection & Verification<br/>(Automatic detector or manual scenario)"]
    Assess["3. Specialist Assessments<br/>(6 domain evaluations on shared snapshot)"]
    Plan["4. Central Recovery Plan<br/>(Prioritized procedures & containment steps)"]
    Gate["5. Policy & Risk Gating<br/>(Check autonomy mode & human approval rules)"]
    Execute["6. Simulated Execution<br/>(Apply mitigation / adjust plant throughput)"]
    Verify["7. Recovery Verification<br/>(Re-evaluate telemetry against baseline)"]
    Audit["8. Audit Trail Recording<br/>(Append immutable record with state version)"]

    Snapshot --> Detect
    Detect --> Assess
    Assess --> Plan
    Plan --> Gate
    Gate --> Execute
    Execute --> Verify
    Verify --> Audit
</pre>

1. **Simulation Snapshot:** The engine packages the authoritative `SimulationSnapshot` containing the current tick, version number, plant summary, and equipment telemetry map.
2. **Detection & Verification:** The active incident is checked—either from continuous telemetry monitoring (`telemetry_rolling_throughput_deviation`) or operator-injected manual scenarios.
3. **Specialist Assessments:** Six independent domain evaluations assess the active snapshot against defined industrial operating envelopes.
4. **Central Recovery Plan:** The central coordinator assembles recommended procedures into an ordered mitigation strategy based on severity and risk.
5. **Policy & Risk Gating:** Operating mode (`OBSERVE`, `ADVISORY`, `AUTONOMOUS_SIMULATION`) dictates whether containment or recovery can proceed automatically, or if human confirmation is mandatory.
6. **Simulated Execution:** Approved procedures modify internal digital-twin parameters (e.g., reducing heat load by 22%, pacing raw material to 80%, or clearing mill capacity constraints).
7. **Recovery Verification:** The detector evaluates live telemetry to ensure the asset has returned to normal operating bounds before closing the incident.
8. **Audit Trail Recording:** Every scenario, autonomy mode change, procedure execution, and approval is written to an in-memory chronological audit log.

---

## The Six Specialist Domains

ACAMIS models industrial expertise as six domain-specific evaluation categories. Rather than uncoordinated chatbots, these specialists are deterministic logic modules operating against the identical versioned snapshot:

<pre class="mermaid">
flowchart LR
    Snapshot["Shared Digital Twin Snapshot<br/>(Versioned, Monotonic)"]

    subgraph Specialists ["Specialist Domain Evaluators"]
        Safety["Safety Specialist<br/>• Operating limits<br/>• Thermal runaway risk"]
        Maintenance["Maintenance Specialist<br/>• Mechanical wear<br/>• Asset inspection order"]
        Quality["Quality Specialist<br/>• Solidification temps<br/>• Rebar metallurgy"]
        Production["Production Specialist<br/>• Mass flow balancing<br/>• Upstream backpressure"]
        Energy["Energy Specialist<br/>• Substation peak loads<br/>• MW/t optimization"]
        Logistics["Logistics Specialist<br/>• Scrap crane delivery<br/>• Billet yard buffer"]
    end

    Orchestrator["Central Orchestrator<br/>(Priority Order: Safety ➔ Limits ➔ Quality ➔ Maint ➔ Prod ➔ Energy ➔ Logistics)"]

    Snapshot --> Safety
    Snapshot --> Maintenance
    Snapshot --> Quality
    Snapshot --> Production
    Snapshot --> Energy
    Snapshot --> Logistics

    Safety --> Orchestrator
    Maintenance --> Orchestrator
    Quality --> Orchestrator
    Production --> Orchestrator
    Energy --> Orchestrator
    Logistics --> Orchestrator
</pre>

| Specialist Domain | Monitored Operating Scope | Escalation / Human Verification Trigger |
| :--- | :--- | :--- |
| **Safety** | Thermal envelopes, cooling-water flow margins, substation breaker limits | Escalates to mandatory human verification for severe furnace and cooling incidents |
| **Maintenance** | Rolling-mill load spikes, drive degradation, pump availability | Recommends asset physical inspection |
| **Quality** | Billet casting liquidus/solidus windows, rebar quench consistency | Flags risk of off-spec heats during temperature excursions |
| **Production** | Bottleneck detection, cascade interlocks, intermediate mill pacing | Computes required throughput reductions to prevent ladling stalls |
| **Energy** | Peak kVA demand, aggregate plant electrical capacity | Restricts full electrical load until substation constraints clear |
| **Logistics** | Raw-material scrap yard staging, finished goods dispatch pacing | Synchronizes incoming material feed with downstream mill capacity |

---

## Central Orchestrator & Policy Sovereignty

The central orchestrator resolves conflicts between specialist recommendations:
* **Strict Hierarchy:** Safety and physical equipment limits unconditionally override production pace.
* **Deterministic Sovereignty:** If an external LLM advisory model is connected, its suggestions are advisory only. The central orchestrator will reject any action not registered in the pre-approved procedure catalog (`acamis-simulation-policy.v1`).\n