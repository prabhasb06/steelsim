# 3. MVP scope

SteelSim is developed as a focused, investor-ready engineering demonstration. To preserve technical credibility, the scope of the current release (Task 1 and Task 2) is strictly demarcated from future roadmap items.

## Completed MVP capabilities

### Task 1 — Visual Plant Builder
- Infinite drag-and-drop engineering canvas powered by React Flow.
- Five typed industrial port domains: **Material**, **Electrical**, **Cooling Water**, **Signal**, and **Air**.
- Strict connection validation: port polarity, domain compatibility, duplicate detection, and self-connection rejection.
- Plant-wide graph rules: material acyclicity, metallurgical sequence enforcement, and missing utility detection.
- Aggregate utility sizing: verifies that total connected MW and m³/h do not exceed substation and pumping station ratings.
- Automated tools: Auto Connect Process, Auto Connect Utilities, Auto Layout, and combined Auto Setup.
- Browser-local storage persistence and pre-packaged 10-node TMT demo loading.
- Real-time diagnostics: Topology Issues panel, live Event Console, and node-level telemetry overlays.

### Task 2 — Deterministic Simulation Engine & Control Center
- Backend-authoritative Python/FastAPI execution loop with discrete clock ticks.
- Monotonic state versioning ensuring linear, tamper-resistant state progression.
- Reproducible seeded random variation for realistic but deterministic telemetry fluctuations.
- Five speed multipliers: 1×, 5×, 10×, 60×, and CPU-safe MAX mode.
- Topological mass-flow propagation: downstream throughput bounded by upstream output and rated node limits.
- Dynamic equipment interlocks triggered by utility starvation or upstream flow cessation.
- Real-time Simulation Control Center with dynamically generated Process Flow Diagram (PFD), KPI deck, equipment inspector, authoritative state trace, and event journal.
- Dual-transport client updates: sub-second WebSocket streaming with automatic HTTP snapshot polling fallback.
- Server-side safety gate: start, run, and resume commands strictly validate plant topology.

## Explicit non-scope boundaries

::: danger Not in MVP Scope
- **No real-time PLC/SCADA control:** SteelSim cannot actuate physical industrial machinery or read physical field sensors.
- **No industrial safety certification:** Not certified under IEC 61508, IEC 61511, or ISO 13849.
- **No finite-element or thermodynamic solver:** Uses discrete physics-based approximations, not computational fluid dynamics (CFD) or metallurgical phase-equilibrium engines.
- **No completed ACAMIS layer:** Multi-agent optimization, automated energy dispatch, and predictive maintenance are future roadmap items.
- **No multi-tenant cloud accounts:** Uses in-memory backend simulation states and browser-local design storage without multi-user authentication.
:::

## Completed MVP vs. future functionality

| Functional Area | Completed in SteelSim MVP | Future Capability / ACAMIS Layer |
| :--- | :--- | :--- |
| **Plant Modeling** | 10-node baseline TMT library, typed ports, auto-layout | Custom CAD/DXF import, multi-furnace parallel meltshops |
| **Topology Validation** | Port checks, process sequencing, aggregate utility capacity | Automated P&ID standards compliance checking |
| **Simulation Runtime** | Deterministic tick engine, mass balance, utility interlocks | Non-linear thermodynamic solvers, finite-element cooling models |
| **Telemetry Transport** | WebSockets with HTTP polling fallback, monotonic guards | OPC-UA, MQTT, and Modbus TCP industrial field protocols |
| **Plant Optimization** | Informational roadmap placeholder view | Multi-agent RL optimization, peak electrical tariff shaving |
| **Maintenance** | Interlocked status visualization on cards | Remaining Useful Life (RUL) vibration and acoustic modeling |
| **Energy Modeling** | Aggregate kW/MW real-time demand calculation | Dynamic power factor correction, harmonic distortion modeling |
| **Data Storage** | Ephemeral server memory + browser LocalStorage | Distributed time-series database with historical replay |
| **Access Control** | Optional shared API-key gate with constant-time check | Enterprise OAuth2/OIDC, team workspaces, RBAC |
