# 6. Task 1 overview

Task 1 delivers an interactive visual engineering workspace in which plant engineers and operators can assemble, connect, validate, arrange, save, and inspect a steel manufacturing plant topology.

Traditional computer-aided design (CAD) software treats factory schematics as static geometries. In contrast, Task 1 models the steel plant as a directed, typed engineering graph. Every component on the canvas possesses explicit physical parameters (such as rated power in MW, water consumption in m³/h, and design throughput in t/h), and every connection carries strict industrial domain semantics.

## Core capabilities

- **React Flow engineering canvas:** Hardware-accelerated canvas with infinite panning, semantic zooming, multi-node selection, and snap-to-grid alignment.
- **Typed industrial ports:** Material, Electrical, Cooling Water, Signal, and Air connection points with strict directionality rules.
- **Structural and engineering validation:** Instant checking of port types, flow cycles, metallurgical sequences, and aggregate utility capacities.
- **Automation routines:** One-click tools for automatic process connection, utility distribution, and hierarchical collision-free layout.
- **Persistent canvas lifecycle:** The canvas remains mounted in the browser DOM across route switches, preserving custom layouts without re-rendering.
- **Real-time telemetry integration:** Equipment cards display live power draw, water circulation, operating temperature, and throughput during simulation runs.

## Workspace architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CANVAS TOOLBAR                                                              │
│ [Library] [Inspector] [Issues] | [Auto Connect] [Auto Layout] [Auto Setup]  │
│                                | [Undo] [Redo] [Zoom] [Fit] [Demo] [Save]   │
├────────────────────────────────┬────────────────────────────────────────────┤
│ COMPONENT PALETTE (Left)       │ REACT FLOW INTERACTIVE CANVAS              │
│ • Raw Material Storage         │                                            │
│ • Induction Furnace            │   [Raw Yard] ────> [Induction Furnace]     │
│ • Ladle Refining Furnace       │        │                   │               │
│ • Continuous Casting Machine   │        ▼                   ▼               │
│ • Reheating Furnace            │    (Material)         (Liquid Steel)       │
│ • Rolling Mill Stands          │                                            │
│ • Quenching Box                ├────────────────────────────────────────────┤
│ • Cooling Bed                  │ TOPOLOGY ISSUES & EVENT CONSOLE (Bottom)   │
│ • Substation / Cooling Station │ 0 Errors | 0 Warnings | All ports wired.   │
└────────────────────────────────┴────────────────────────────────────────────┘
```
