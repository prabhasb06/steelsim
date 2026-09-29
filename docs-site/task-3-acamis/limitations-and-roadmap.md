# 37. ACAMIS Limitations & Engineering Roadmap

While ACAMIS establishes a sophisticated operational intelligence and policy-governance layer, clear engineering boundaries separate the current digital-twin MVP from physical production plant controllers.

---

## Digital Twin Capabilities vs. Physical Production

| Verified Digital Twin Capability (Task 3 & 3.1) | Physical Production Scope Boundary (Horizon 3 Roadmap) |
| :--- | :--- |
| **Pure Software Simulation Model:** Runs deterministic mass/energy balance in Python runtime | **No Direct Hardware Coupling:** Does not communicate directly with physical PLCs or field sensors |
| **Local Operations History:** Task 4 stores snapshots and policy audit in SQLite | **No Industrial Time-Series Historian:** Managed retention, backups, and multi-user access remain future work |
| **Deterministic Anomaly Detector:** Explainable rolling-throughput rule checking ($A_T < 0.75 \times E_T$) | **Not a Safety-Instrumented System (SIS):** Cannot replace a plant's independent protective controls |
| **Advisory BYOK Model Gateway:** Transient API key held in process memory; connected providers receive simulation context | **No Multi-User Key Vault:** Individual credentials and access control remain future work |
| **Simulated Procedures:** Registered procedures alter SteelSim's digital-twin state | **No Southbound SCADA Control:** Cannot command physical actuators |

---

## Engineering Roadmap

<pre class="mermaid">
timeline
    title ACAMIS Engineering Horizons
    section Horizon 1 (Completed)
        Task 1 Plant Builder : Visual Canvas : Typed Industrial Ports : Validation Engine
        Task 2 Simulation    : Deterministic Engine : Discrete Ticks : WebSocket Stream
    section Horizon 2 (Completed)
        Task 3 ACAMIS Base  : Deterministic Assessments : 6 Specialist Domains : 3 Operating Modes
        Task 3.1 Monitoring : Telemetry Anomaly Detector : 3-Tick Rule : Evidence Payload
        Task 4 Operations History : SQLite Run Journal : Replay : Paused Restore
    section Horizon 3 (Next)
        Plant Data Feeds  : Read-Only Adapter Design : Data Quality Checks
        Validation  : Plant-Specific Baselines : Controlled Pilot Evaluation
        Security  : Accounts : Access Control : Managed Credentials
    section Horizon 4 (Future)
        Fleet Optimization   : Multi-Mill Meltshop Balancer : Dynamic Spot-Tariff Scheduling
        Decarbonization      : Automated Scope 1 & 2 Carbon Intensity Telemetry
</pre>

---

## Technical Debt & Boundary Summary

1. **Industrial Integration:** Current procedures modify only simulation state. Any future connection to plant data should start read-only and require separate site-specific security, safety, and data-quality validation. Physical actuation is not on the MVP path.
2. **Model Gateway Isolation:** External models provide advisory text. They cannot directly execute operational procedures or bypass deterministic gates.
3. **Audit Persistence:** Task 4 writes policy audit to a local SQLite journal. The current hosted setup has no persistent disk; long-term retention, backups, and access control remain future work.
