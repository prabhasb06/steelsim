# 48. Task 1, Task 2, and Task 3 integration

The core architectural achievement of SteelSim is the seamless integration of **Task 1 (Visual Plant Builder)**, **Task 2 (Deterministic Simulation Engine & Control Center)**, and **Task 3 / 3.1 (ACAMIS Operational Intelligence)** within a unified, reactive single-page application.

## Integrated workflow diagram

<pre class="mermaid">
flowchart TD
    Start([User Starts in Plant Builder]) --> Design[Place & Connect Industrial Nodes]
    Design --> Auto[Run Auto Setup / Manual Wiring]
    Auto --> Validate{Validate Topology}
    
    Validate -->|Errors Found| Fix[Display Issues in Bottom Drawer]
    Fix --> Design
    
    Validate -->|Zero Errors| SimView[Switch to Simulation View]
    SimView --> CreateSim[Backend Creates Simulation ID<br/>Status: READY]
    CreateSim --> Run[Click Run Simulation]
    Run --> SimLoop[Deterministic Engine Advances Ticks]
    SimLoop --> Stream[Stream WebSocket Telemetry]
    Stream --> Observe[Observe PFD, KPIs & Inspector]
    
    Observe --> ACAMIS[Open ACAMIS Intelligence]
    ACAMIS --> Monitor[Task 3.1 Automatic Telemetry Monitoring]
    Monitor --> Incident[Detect Anomaly or Manual Scenario]
    Incident --> Navigate[Click Locate in Plant or Inspect Simulation]
    Navigate --> Action[Autonomous Recovery or Human Intervention]
    Action --> SimLoop

    Observe --> EditChoice{Does User Edit Topology?}
    EditChoice -->|Visual Repositioning Only| KeepSim[Keep Simulation Running]
    KeepSim --> Observe
    
    EditChoice -->|Physical Graph Edit| Invalidate["Invalidate Simulation<br/>DELETE /api/simulations/:id"]
    Invalidate --> SimView
</pre>

## DOM persistence architecture

In `frontend/src/App.tsx`, the Plant Builder component (`<Blueprint />`) is kept mounted in the DOM regardless of the active view. When an operator switches to the Simulation Control Center or ACAMIS:
- The builder container is assigned `opacity: 0` and `pointer-events: none`.
- All React Flow node positions, edge connections, inspector states, and active anomaly badges are preserved.
- When an operator clicks **Locate in plant** from the ACAMIS Incident Impact deck, the app switches view to `BUILDER`, focuses the target asset using `fitView`, and selects the node.

## Physics-relevant vs. layout-only modifications
The system computes a deterministic hash (`plantSimulationSignature`) of all physical parameters and connections:
- **Layout modifications (Moving cards):** Do not change the signature. The active simulation continues running without interruption.
- **Physics modifications (Adding/deleting nodes, editing parameters, rewiring edges):** Alter the signature. The client immediately calls `DELETE /api/simulations/:id`, clearing obsolete telemetry, invalidating active ACAMIS incident states, and resetting the session cleanly.
