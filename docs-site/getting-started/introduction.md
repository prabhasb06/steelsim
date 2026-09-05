# 1. Introduction

SteelSim is an industrial digital-twin minimum viable product (MVP) engineered for secondary steel producers—specifically micro, small, and medium enterprises (MSMEs) operating induction melting furnaces and continuous thermo-mechanically treated (TMT) rebar rolling mills.

The system addresses the gap between static computer-aided design (CAD) schematics and dynamic operational reality. In standard industrial workflows, plant layout diagrams and Process Flow Diagrams (PFDs) do not validate whether connected electrical substations or closed-loop cooling towers have sufficient aggregate capacity to support peak operational loads. SteelSim bridges this gap by unifying visual topological plant design with a backend-authoritative deterministic simulation engine.

## Core architectural statement

::: tip Architectural Division of Responsibility
**“SteelSim creates the factory; ACAMIS understands the factory.”**
:::

SteelSim models, edits, validates, and serializes the physical factory graph, and executes the deterministic physical simulation. ACAMIS is an independent, separate cognitive layer designed for future multi-agent optimization, energy demand forecasting, and predictive maintenance. SteelSim does not control real-world factory hardware and must not be described as certified industrial control software.

## Two completed milestones

1. **Task 1 — Visual Plant Builder:** A browser-based engineering workspace using React Flow that allows operators to drag, connect, configure, and validate complete steel plant topologies using typed industrial ports.
2. **Task 2 — Deterministic Simulation Engine & Control Center:** A Python and FastAPI execution runtime that computes discrete, tick-driven physical approximations (mass throughput, electrical loads, cooling water demand, and cascade interlocks) and streams authoritative telemetry to a live Simulation Control Center.

## System overview diagram

<pre class="mermaid">
graph TB
    subgraph Client ["Client Browser (React 19 / TypeScript)"]
        Builder["Plant Builder (Task 1)<br/>• React Flow Canvas<br/>• Typed Industrial Ports<br/>• LocalStorage Persistence"]
        ControlCenter["Simulation Control Center (Task 2)<br/>• Dynamic Process Flow Diagram<br/>• Equipment Inspector<br/>• State Trace & Event Log"]
        Guard["Client Telemetry Guard<br/>• Monotonic Version Check<br/>• Schema Validation"]
    end

    subgraph Backend ["Backend Runtime (Python / FastAPI)"]
        Validator["Topology Validator<br/>• Graph Syntax & Sequencing<br/>• Aggregate Utility Checks"]
        SimManager["Simulation Manager<br/>• Lifecycle State Machine<br/>• Bounded Memory & Eviction"]
        Engine["Deterministic Engine<br/>• Discrete Ticks (1s)<br/>• Flow & Interlock Propagation"]
    end

    Builder -->|POST /api/plant/validate| Validator
    Builder -->|POST /api/simulations| SimManager
    ControlCenter -->|POST /api/simulations/:id/command| SimManager
    SimManager --> Engine
    Engine -->|WebSocket Stream & HTTP Polling| Guard
    Guard --> ControlCenter
</pre>

## Verification and baseline status

The repository is synchronized at verified commit `e1dad6ef603ee8975a8500ab33debb40d1697d46` with:
- **43 of 43** backend Pytest tests passing
- **4 of 4** frontend Node unit tests passing
- **0** linter errors or warnings across 17 files via Oxlint
- Clean TypeScript strict compilation and Vite production build
- Headless Puppeteer browser E2E test passing with zero console errors
