# 22. Simulation Control Center

The Simulation Control Center is the primary operational workspace for Task 2, providing real-time monitoring and control of the running virtual factory.

## Interface breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MASTER HEADER                                           ● Backend Connected │
│ Status: RUNNING | Version: #142 | Sim Time: 00:02:22 | Tick: 142            │
│ Plant Power: 24.2 MW | Cooling: 980.0 m³/h | Active Units: 8/10             │
│ Controls: [ ▶ Run ] [ ⏸ Pause ] [ ↺ Reset ] | Speed: [1x] [5x] [10x] [60x] │
├─────────────────────────────────────────────────────────────────────────────┤
│ DYNAMIC PROCESS FLOW DIAGRAM (PFD)                                          │
│                                                                             │
│ [Raw Yard] ➔ [Furnace] ➔ [LRF] ➔ [CCM] ➔ [Reheat] ➔ [Mill] ➔ [Quench] ➔ [Bed]│
│                                                                             │
│ INFRASTRUCTURE CORRIDOR                                                     │
│ [High-Voltage Substation 33kV/11kV]  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (Electrical Bus) │
│ [Closed-Loop Cooling Station]        ═════════════════════ (Water Circuit)  │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ EQUIPMENT INSPECTOR                  │ STATE TRACE & EVENT JOURNAL          │
│ Asset: Induction Furnace             │ 10:14:02 [INFO] Simulation RUNNING   │
│ Status: RUNNING                      │ 10:14:05 [WARN] CCM thermal nominal  │
│ Power: 12,500 kW (12.5 MW)           │ 10:14:10 [TELEMETRY] Version #142    │
│ Water: 120.0 m³/h                    │                                      │
│ Temperature: 1,620 °C                │                                      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

## Dynamically generated Process Flow Diagram (PFD)

Unlike static SCADA graphics, the PFD in SteelSim is computed dynamically from the active plant graph:
- Process units are extracted, sorted topologically, and arranged along the horizontal pass-line.
- Utility supplies are partitioned into an infrastructure corridor below the process flow.
- Equipment cards update in real time with live throughput, thermal readings, and status indicators.
- Clicking any equipment card opens its real-time diagnostic parameters in the Equipment Inspector.
