# 50. Roadmap

Development of the SteelSim ecosystem is organized into sequential industrial milestones:

## Horizon 1 — SteelSim Foundation (Completed · Task 1 & 2)
- **Visual Plant Builder:** Visual drag-and-drop canvas with typed industrial ports (`MATERIAL`, `ELECTRICAL`, `WATER`, `SIGNAL`, `AIR`).
- **Engineering Validation:** Multi-tier metallurgical sequence checks and aggregate utility capacity enforcement.
- **Deterministic Simulation Engine:** Monotonic state versioning, 1 Hz discrete tick loop, and sub-second WebSocket streaming.
- **Process Flow Diagram (PFD):** Dynamic SVG process flow rendering and real-time Simulation Control Center.
- **Standard Baseline:** 10-node verified 25 t/h TMT induction melting and rebar manufacturing line.

## Horizon 2 — ACAMIS Operational Intelligence (Completed · Task 3 & 3.1)
- **Specialist Evaluators:** 6 deterministic categories: Safety, Maintenance, Quality, Production, Energy, and Logistics.
- **Three Autonomy Modes:** `OBSERVE` (passive audit), `ADVISORY` (operator recommendation), and `AUTONOMOUS_SIMULATION` (closed-loop automated execution).
- **Controlled Scenarios:** 5 reproducible industrial failure modes (`cooling_water_degradation`, `furnace_instability`, `rolling_mill_slowdown`, `substation_capacity_constraint`, `raw_material_disruption`).
- **Automatic Telemetry Anomaly Detection (Task 3.1):** Defined rolling-throughput threshold with a 3-tick persistence rule.
- **Advisory Model Gateway:** BYOK connection to Gemini or an OpenAI-compatible provider, with generation verification and credentials held in backend memory for the simulation.
- **Operations Console & Safety Gates:** Dual-mode manual/autonomous procedures, cross-navigation to canvas and simulation, and alertdialog confirmation gates.

## Horizon 3 — Deployment and measured-data integration (Next)
- **Durable Hosting:** Add a persistent store, backup procedure, retention policy, and restore checks for Task 4 recordings.
- **Access Control:** Add individual accounts, authorization, and per-user model-key handling before shared public use.
- **Read-only Plant Data:** Design a separate adapter for authenticated SCADA or historian data. Validate quality, units, timestamps, and mapping before using it in analysis.
- **Model Validation:** Calibrate thresholds and simulation assumptions against approved plant datasets before drawing operational conclusions.

## Horizon 4 — Enterprise Fleet Coordination (Future)
- **Dynamic Energy Tariff Shaving:** Real-time day-ahead spot market optimization, automatically scheduling furnace tap-to-tap cycles during off-peak windows.
- **Multi-Facility Logistics:** Synchronized billet yard allocation across regional rolling mills.
- **Scope 1 / Scope 2 Decarbonization Auditing:** Automated real-time carbon intensity telemetry per finished rebar heat.
