# 38. Roadmap

Development of the SteelSim ecosystem is organized into three sequential horizons:

## Horizon 1 — SteelSim MVP (Completed)
- Visual plant builder with typed industrial ports (Material, Power, Water, Signal, Air).
- Multi-tier engineering validation rules and aggregate utility capacity enforcement.
- Deterministic simulation engine with monotonic state versioning and WebSocket streaming.
- Dynamic Process Flow Diagram (PFD) and real-time Simulation Control Center.
- 10-node verified 25 t/h TMT manufacturing baseline.

## Horizon 2 — Enterprise Platform Extensions (Next)
- Cloud-hosted workspace with PostgreSQL persistence for plant schematics and user accounts.
- Export and import of industrial formats (P&ID DXF/SVG, AutomationML, and CSV batch recipes).
- Multi-furnace parallel meltshop topologies and multi-strand continuous caster configurations.
- Time-series telemetry archiving with comparative simulation run charting and CSV export.

## Horizon 3 — ACAMIS Cognitive Layer Integration (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                       ACAMIS LAYER                          │
│     Autonomous Cognitive Asset & Manufacturing Intelligence  │
├──────────────────────────────┬──────────────────────────────┤
│ 1. Energy Intelligence       │ Real-time tariff tracking &  │
│                              │ peak-demand furnace shaving  │
├──────────────────────────────┼──────────────────────────────┤
│ 2. Predictive Maintenance    │ Bearing vibration analytics  │
│                              │ and remaining useful life    │
├──────────────────────────────┼──────────────────────────────┤
│ 3. Autonomous Scheduling     │ Dynamic ladle sequencing and │
│                              │ caster synchronization       │
├──────────────────────────────┼──────────────────────────────┤
│ 4. Safety & HAZOP Advisor    │ Automated hazard assessment  │
│                              │ and compliance auditing      │
└──────────────────────────────┴──────────────────────────────┘
```

ACAMIS will consume approved telemetry contracts from SteelSim without compromising the deterministic foundation of the simulation engine.
