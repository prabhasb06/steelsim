# 37. ACAMIS Limitations & Engineering Roadmap

While ACAMIS establishes a sophisticated operational intelligence and policy-governance layer, clear engineering boundaries separate the current digital-twin MVP from physical production plant controllers.

---

## Digital Twin Capabilities vs. Physical Production

| Verified Digital Twin Capability (Task 3 & 3.1) | Physical Production Scope Boundary (Horizon 3 Roadmap) |
| :--- | :--- |
| **Pure Software Simulation Model:** Runs deterministic mass/energy balance in Python runtime | **No Direct Hardware Coupling:** Does not communicate directly with physical PLCs or field sensors |
| **In-Memory Telemetry & Audit History:** Retains monotonic snapshots and incident logs in memory | **No Industrial Time-Series Historian:** Multi-month archiving requires enterprise TimescaleDB/InfluxDB |
| **Deterministic Anomaly Detector:** Fast, explainable rule checking ($A_T < 0.75 \times E_T$) | **Not Safety-Instrumented System (SIS):** Does not replace SIL-3 / IEC 61508 emergency shutdown hardware |
| **Advisory BYOK Model Gateway:** Air-gapped transient API key held in process memory | **No Cloud Multi-Tenant Key Vault:** Enterprise deployment requires AWS KMS or HashiCorp Vault |
| **Simulated Closed-Loop Actuation:** Intervenes directly into digital twin engine parameters | **No Southbound SCADA Control:** Cannot send 4-20mA or fieldbus signals to physical actuators |

---

## Engineering Roadmap

<pre class="mermaid">
timeline
    title ACAMIS Engineering Horizons
    section Horizon 1 (Completed)
        Task 1 Plant Builder : Visual Canvas : Typed Industrial Ports : Validation Engine
        Task 2 Simulation    : Deterministic Engine : Discrete Ticks : WebSocket Stream
    section Horizon 2 (Completed)
        Task 3 ACAMIS Base  : 8-Stage Pipeline : 6 Specialist Evaluators : 3 Autonomy Modes
        Task 3.1 Monitoring : Telemetry Anomaly Detector : 3-Tick Rule : Evidence Payload
    section Horizon 3 (Next)
        Physical Connectors  : OPC UA Southbound Adapter : Modbus TCP Bridge : MQTT Sparkplug B
        Digital Shadow Mode  : Parallel Physical Mirroring : Sensor Drift Analytics
        Safety PLC Gate      : Hardware Interlock Watchdog : SIL-3 Air-Gap Verification
    section Horizon 4 (Future)
        Fleet Optimization   : Multi-Mill Meltshop Balancer : Dynamic Spot-Tariff Scheduling
        Decarbonization      : Automated Scope 1 & 2 Carbon Intensity Telemetry
</pre>

---

## Technical Debt & Boundary Summary

1. **Southbound Actuation Protocol:** Currently, ACAMIS procedures modify simulation state through in-process method calls (`engine.apply_throttling()`). In physical deployments, these calls must map to an OPC UA client writing to PLC DataBlocks.
2. **Model Gateway Isolation:** External LLMs operate purely as read-only consultants. They cannot directly execute operational procedures; their suggestions must be parsed into deterministic procedure candidates and evaluated against safety gates.
3. **Audit Persistence:** The audit timeline holds the last 100 incident records in process RAM. Production installations require an append-only, tamper-proof database log.\n