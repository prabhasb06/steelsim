# 50. Roadmap

Development of the SteelSim ecosystem is organized into sequential industrial milestones:

## Horizon 1 — SteelSim Foundation (Completed · Task 1 & 2)
- **Visual Plant Builder:** Visual drag-and-drop canvas with typed industrial ports (`MATERIAL`, `ELECTRICAL`, `WATER`, `SIGNAL`, `AIR`).
- **Engineering Validation:** Multi-tier metallurgical sequence checks and aggregate utility capacity enforcement.
- **Deterministic Simulation Engine:** Monotonic state versioning, 1 Hz discrete tick loop, and sub-second WebSocket streaming.
- **Process Flow Diagram (PFD):** Dynamic SVG process flow rendering and real-time Simulation Control Center.
- **Standard Baseline:** 10-node verified 25 t/h TMT induction melting and rebar manufacturing line.

## Horizon 2 — ACAMIS Operational Intelligence (Completed · Task 3 & 3.1)
- **8-Stage Specialist Pipeline:** 6 independent engineering evaluators (Mechanical, Electrical, Thermal, Utility, Casting, Raw Material).
- **Three Autonomy Modes:** `OBSERVE` (passive audit), `ADVISORY` (operator recommendation), and `AUTONOMOUS_SIMULATION` (closed-loop automated execution).
- **Controlled Scenarios:** 5 reproducible industrial failure modes (`cooling_water_degradation`, `furnace_instability`, `rolling_mill_slowdown`, `substation_capacity_constraint`, `raw_material_disruption`).
- **Automatic Telemetry Anomaly Detection (Task 3.1):** Statistical drift detection ($A_T < 0.75 \times E_T$, 3-tick persistence rule, 5 lifecycle states).
- **Advisory Model Gateway:** Air-gapped BYOK integration for Google Gemini models with transient in-memory credentials.
- **Operations Console & Safety Gates:** Dual-mode manual/autonomous procedures, cross-navigation to canvas and simulation, and alertdialog confirmation gates.

## Horizon 3 — SCADA & Physical Field Connectivity (Next)
- **Industrial Protocol Gateways:** OPC UA and Modbus TCP southbound adapters for hardware SCADA/DCS data ingestion.
- **Shadow Digital Twin Mode:** Mirroring physical sensor streams side-by-side with deterministic simulation predictions to isolate sensor drift.
- **Hardware-in-the-Loop (HIL) Safety Interlocks:** Hardened safety PLC watchdog timers preventing autonomous simulation overrides on physical actuators.
- **Time-Series Telemetry Archiving:** High-throughput columnar storage (TimescaleDB / InfluxDB) for multi-shift historical replay.

## Horizon 4 — Enterprise Fleet Coordination (Future)
- **Dynamic Energy Tariff Shaving:** Real-time day-ahead spot market optimization, automatically scheduling furnace tap-to-tap cycles during off-peak windows.
- **Multi-Facility Logistics:** Synchronized billet yard allocation across regional rolling mills.
- **Scope 1 / Scope 2 Decarbonization Auditing:** Automated real-time carbon intensity telemetry per finished rebar heat.

