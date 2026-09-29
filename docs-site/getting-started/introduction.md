# 1. Introduction

SteelSim is an industrial digital-twin minimum viable product (MVP) engineered for secondary steel producers—specifically micro, small, and medium enterprises (MSMEs) operating induction melting furnaces and continuous thermo-mechanically treated (TMT) rebar rolling mills.

The system addresses the gap between static computer-aided design (CAD) schematics and dynamic operational reality. In standard industrial workflows, plant layout diagrams and Process Flow Diagrams (PFDs) do not validate whether connected electrical substations or closed-loop cooling towers have sufficient aggregate capacity to support peak operational loads. SteelSim bridges this gap by unifying visual topological plant design with a backend-authoritative deterministic simulation engine.

## Core architectural statement

::: tip Architectural Division of Responsibility
**“SteelSim creates the factory; ACAMIS understands the factory.”**
:::

SteelSim models, edits, validates, and serializes the virtual factory graph, then runs a deterministic simulation. The integrated ACAMIS module reads that simulation's backend state, evaluates defined incidents and signal deviations, and applies only registered simulated procedures under its operating-mode rules. Future optimization, forecasting, and predictive maintenance are not implemented. SteelSim does not control real-world factory hardware and is not certified industrial control software.

## Implemented modules

1. **Task 1 — Visual Plant Builder:** A browser-based engineering workspace using React Flow that allows operators to drag, connect, configure, and validate complete steel plant topologies using typed industrial ports.
2. **Task 2 — Deterministic Simulation Engine & Control Center:** A Python and FastAPI execution runtime that computes discrete, tick-driven physical approximations (mass throughput, electrical loads, cooling water demand, and cascade interlocks) and streams authoritative telemetry to a live Simulation Control Center.
3. **Task 3/3.1 — ACAMIS Intelligence:** Deterministic scenario response, a rolling-throughput detector, six domain assessments, policy-gated simulated procedures, and optional advisory model reviews.
4. **Task 4 — Operations History:** Local SQLite run recordings and replay, plus operator-review cases for persistent temperature, cooling, and power deviations.

## System overview diagram

<pre class="mermaid">
flowchart TB
    subgraph Client ["Client Browser (React 19 / TypeScript)"]
        direction LR
        Guard["Client Telemetry Guard<br/>• Monotonic Version Check<br/>• Strict Schema Validation"]
        Builder["Plant Builder (Task 1)<br/>• React Flow Canvas<br/>• Typed Industrial Ports<br/>• LocalStorage Persistence"]
        ControlCenter["Simulation Control Center (Task 2)<br/>• Dynamic Process Flow Diagram<br/>• Equipment Inspector<br/>• State Trace & Event Log"]
    end

    subgraph Backend ["Backend Runtime (Python / FastAPI)"]
        direction LR
        Validator["Topology Validator<br/>• Graph Syntax & Sequencing<br/>• Aggregate Utility Checks"]
        SimManager["Simulation Manager<br/>• Lifecycle State Machine<br/>• Bounded Memory & Eviction"]
        Engine["Deterministic Engine<br/>• Discrete Ticks (1s)<br/>• Flow & Interlock Propagation"]
    end

    Builder -->|POST /api/plant/validate| Validator
    Builder -->|POST /api/simulations| SimManager
    ControlCenter -->|POST command| SimManager
    SimManager --> Engine
    Engine -->|WebSocket Stream<br/>& HTTP Polling| Guard
    Guard --> ControlCenter
</pre>

## Verification and baseline status

The repository is synchronized at verified commit `e1dad6ef603ee8975a8500ab33debb40d1697d46` with:
- **43 of 43** backend Pytest tests passing
- **4 of 4** frontend Node unit tests passing
- **0** linter errors or warnings across 17 files via Oxlint
- Clean TypeScript strict compilation and Vite production build
- Headless Puppeteer browser E2E test passing with zero console errors
