# SteelSim Documentation

SteelSim is an industrial digital-twin MVP for MSME induction-furnace and TMT rebar manufacturing facilities. It pairs a visual plant-topology builder with a backend-authoritative deterministic simulation engine.

> **Core tenet:** “SteelSim creates the factory; ACAMIS understands the factory.”
>
> SteelSim provides the verifiable plant-builder and deterministic physical simulation foundation (Tasks 1 & 2). ACAMIS provides the operational intelligence, continuous telemetry anomaly detection, and policy-gated recovery layer (Tasks 3 & 3.1). SteelSim is an engineering digital twin and investor-facing MVP; it does not directly control physical machinery.

---

## Documentation Sections

<div class="openai-grid">

<a href="/getting-started/introduction" class="openai-card">
  <div class="openai-card-title">Getting Started</div>
  <div class="openai-card-desc">Problem statement, two-tiered architecture, verified MVP scope boundaries, and local installation.</div>
</a>

<a href="/getting-started/investor-demo" class="openai-card">
  <div class="openai-card-title">Investor Demonstration</div>
  <div class="openai-card-desc">Concise 5-minute timed demonstration script matching the verified browser E2E workflow.</div>
</a>

<a href="/task-1-builder/overview" class="openai-card">
  <div class="openai-card-title">Task 1: Plant Builder</div>
  <div class="openai-card-desc">React Flow canvas, typed industrial ports, auto-wiring, auto-layout, and topology validation.</div>
</a>

<a href="/task-2-simulation/overview" class="openai-card">
  <div class="openai-card-title">Task 2: Simulation Engine</div>
  <div class="openai-card-desc">Deterministic tick loop, monotonic state versioning, mass flow, utility capacities, and interlocks.</div>
</a>

<a href="/task-3-acamis/overview" class="openai-card">
  <div class="openai-card-title">Task 3: ACAMIS Intelligence</div>
  <div class="openai-card-desc">Operational intelligence, 6 specialist domains, rolling throughput anomaly detection, and policy gates.</div>
</a>

<a href="/task-2-simulation/control-center" class="openai-card">
  <div class="openai-card-title">Simulation Control Center</div>
  <div class="openai-card-desc">Dynamic Process Flow Diagram (PFD), KPI deck, equipment inspector, and live WebSocket telemetry.</div>
</a>

<a href="/reference/standard-tmt-topology" class="openai-card">
  <div class="openai-card-title">Standard TMT Baseline</div>
  <div class="openai-card-desc">Verified 10-node meltshop and rebar rolling mill topology (25 t/h) with zero validation issues.</div>
</a>

<a href="/reference/rest-api" class="openai-card">
  <div class="openai-card-title">API & WebSocket Reference</div>
  <div class="openai-card-desc">Complete REST endpoint catalog, unified lifecycle command dispatcher, and WebSocket streaming.</div>
</a>

<a href="/project/architecture" class="openai-card">
  <div class="openai-card-title">System Architecture</div>
  <div class="openai-card-desc">Decoupled React 19 and FastAPI architecture, DOM persistence, and state invalidation semantics.</div>
</a>

</div>

---

## Quick Start

Open two terminal sessions from the repository root:

```bash
# 1. Start backend service
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start frontend application
cd frontend
npm run dev
```

- **Frontend application:** `http://localhost:5173/`
- **Backend API & docs:** `http://127.0.0.1:8000/docs`
- **Backend health probe:** `http://127.0.0.1:8000/api/health`

---

## Verified Baseline Status

| Component | Target Metric | Verified Status |
| :--- | :--- | :--- |
| **Commit Hash** | `416cec95e3717c4081d689d9bd84329d30ffcba9` | **Verified** (`main` clean) |
| **Backend Tests** | 72 test cases | **72 / 72 Passed** (`pytest backend/tests`) |
| **Frontend Unit Tests** | 4 test cases | **4 / 4 Passed** (`node --test`) |
| **Frontend Linter** | 0 warnings, 0 errors | **Passed** (`oxlint`) |
| **TypeScript Compilation** | Strict type-check | **Passed** (`tsc --noEmit`) |
| **Task 3.1 Detector** | 3-tick persistence & recovery | **Verified** (100% test coverage) |
| **Browser E2E Workflow** | Headless smoke test | **Passed** (0 console errors) |
| **Standard Demo Topology** | 10 nodes, 22 connections | **Valid** (0 errors, 0 warnings) |

---

## System Architecture

<pre class="mermaid">
flowchart LR
    subgraph UI ["Client UI & Control (React 19)"]
        direction TB
        Builder["Plant Builder<br/>• React Flow Canvas<br/>• Typed Industrial Ports"]
        Control["Control Center Actions<br/>• Operator Commands<br/>• Sim Lifecycle Triggers"]
        ACAMISUI["ACAMIS Console<br/>• Advisory Interventions<br/>• Mitigation Approvals"]
    end

    subgraph API ["REST API Gateway"]
        direction TB
        CmdGate["REST Command Endpoints<br/>• POST /api/plant/validate<br/>• POST /api/simulations<br/>• POST /api/simulations/:id/command<br/>• REST /api/acamis/*"]
    end

    subgraph Backend ["Backend Runtime (Python / FastAPI)"]
        direction TB
        Validator["Topology Validator<br/>• Port & Utility Checks"]
        SimManager["Simulation Manager<br/>• Lifecycle State Machine"]
        Engine["Deterministic Engine<br/>• 1s Discrete Loop<br/>• Flow & Cascade Interlocks"]
        ACAMISCore["ACAMIS Core<br/>• Rolling Detector (Task 3.1)<br/>• 6 Specialist Evaluators"]
    end

    subgraph Stream ["Real-Time Streaming"]
        direction TB
        PollStream["WebSocket Stream & HTTP Poll<br/>• Sub-Second Real-Time Telemetry<br/>• Authoritative 1s Tick Broadcast"]
    end

    subgraph Monitoring ["Client Telemetry & Monitoring (React 19)"]
        direction TB
        Guard["Telemetry Guard<br/>• Monotonic Sequence Filter<br/>• Strict Schema Validation Gate"]
        LivePFD["Dynamic Process Flow Diagram<br/>• Live Node Status<br/>• Material & Utility Flows"]
        LiveKPI["KPI Summary Deck<br/>• Power, Water, Throughput<br/>• Incident Response Panel"]
    end

    Builder -->|Validate & Create| CmdGate
    Control -->|Control Commands| CmdGate
    ACAMISUI <-->|Mitigation Actions| CmdGate

    CmdGate --> Validator
    CmdGate --> SimManager
    CmdGate --> ACAMISCore

    SimManager --> Engine
    Engine --> ACAMISCore

    Engine -->|Authoritative Snapshots| PollStream
    PollStream -->|Validated Stream| Guard
    Guard --> LivePFD
    Guard --> LiveKPI
</pre>