# 36. Task 1 and Task 2 integration

The primary architectural achievement of SteelSim is the seamless integration of **Task 1 (Visual Plant Builder)** and **Task 2 (Deterministic Simulation Engine & Control Center)** within a unified single-page application.

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
    
    Observe --> EditChoice{Does User Edit Topology?}
    EditChoice -->|Visual Repositioning Only| KeepSim[Keep Simulation Running]
    KeepSim --> Observe
    
    EditChoice -->|Physical Graph Edit| Invalidate["Invalidate Simulation<br/>DELETE /api/simulations/{id}"]
    Invalidate --> SimView
</pre>

## DOM persistence architecture

In `frontend/src/App.tsx`, the Plant Builder component (`<Blueprint />`) is kept mounted in the DOM regardless of the active view. When an operator switches to the Simulation Control Center:
- The builder container is assigned `opacity: 0` and `pointer-events: none`.
- All React Flow node positions, edge connections, and inspector states are preserved.
- When the operator switches back to the Plant Builder, the canvas is immediately visible without re-rendering or reloading from storage.

## Physics-relevant vs. layout-only modifications
The system computes a deterministic hash (`plantSimulationSignature`) of all physical parameters and connections:
- **Layout modifications (Moving cards):** Do not change the signature. The active simulation continues running without interruption.
- **Physics modifications (Adding/deleting nodes, editing parameters, rewiring edges):** Alter the signature. The client immediately calls `DELETE /api/simulations/{id}`, clearing obsolete telemetry and preventing invalid simulation states.
