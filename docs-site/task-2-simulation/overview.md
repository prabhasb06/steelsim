# 16. Task 2 overview

Task 2 provides the backend-authoritative virtual factory engine and the live Simulation Control Center.

While Task 1 models the structural connectivity of the plant, Task 2 simulates its dynamic operations. The simulation engine calculates the deterministic movement of steel through the facility, evaluates concurrent utility draws against connected substations and cooling towers, and handles interlocks when conditions deviate from safe operational envelopes.

## Core principles

1. **Backend authority:** The frontend is strictly a visualization layer. All physics approximations, clock ticks, state versions, and telemetry packets are generated exclusively by the Python/FastAPI backend.
2. **Deterministic execution:** Given the same initial topology, parameters, and random seed, the virtual factory produces identical telemetry traces across independent runs.
3. **Monotonic versioning:** Every tick and command increments a monotonic state version (`state_version`). The frontend validates this version to prevent stale or out-of-order renders.
4. **Resilient telemetry streaming:** Telemetry is broadcast continuously over WebSockets, with automatic client-side degradation to HTTP snapshot polling if network interruptions occur.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SIMULATION CONTROL CENTER (React 19 Frontend)                               │
│ • State: RUNNING (v142)  • Sim Time: 00:02:22  • Power: 24.2 MW             │
│ • Controls: [Run] [Pause] [Reset] [Speed: 1x, 5x, 10x, 60x]                 │
│ • Dynamic Process Flow Diagram & Utility Lane                               │
│ • Live Equipment Cards, Inspector Drawer & State Trace Log                  │
└──────────────────────────────────────▲──────────────────────────────────────┘
                                       │
                         WebSocket Stream / HTTP Polling
                                       │
┌──────────────────────────────────────┴──────────────────────────────────────┐
│ DETERMINISTIC SIMULATION ENGINE (Python / FastAPI Backend)                  │
│ • Discrete Tick Loop (1s Simulated Time / Tick)                             │
│ • Topological Material Propagation (Bottleneck-Aware Flow)                  │
│ • Utility Demand Summation & Over-Capacity Gating                           │
│ • Cascade Equipment Interlocking & Ring-Buffered Event Journal              │
└─────────────────────────────────────────────────────────────────────────────┘
```
