# 27. ACAMIS Architecture & Data Flow

ACAMIS evaluates backend SteelSim state as simulation ticks advance. Each tick represents one simulated second; wall-clock frequency changes with the selected speed. Its detectors and responses are deterministic and operate only on simulated equipment.

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
    Audit["8. Audit Trail Recording<br/>(Bounded live audit and local SQLite history)"]

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
7. **Recovery Verification:** For the rolling-throughput detector incident, the engine checks affected mills against the expected throughput bound before closure. Manual scenarios use configured simulated procedures.
8. **Audit Trail Recording:** Policy events appear in the live audit and are archived with the run in Task 4's local SQLite history.

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

The central plan exposes a priority order and procedures registered for the active primary incident. The six domain assessments are deterministic rule outputs; they do not perform independent model-based optimization or prove root cause. Signal-review cases carry measured evidence but no mapped automatic repair. If an external model is connected, its response remains advisory and cannot execute a procedure or bypass the policy gate.
