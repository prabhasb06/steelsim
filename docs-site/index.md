# SteelSim Documentation

SteelSim is an industrial digital-twin MVP for MSME induction-furnace and TMT rebar manufacturing facilities. It pairs a visual plant-topology builder with a backend-authoritative deterministic simulation engine and a recorded operations history.

> **Core tenet:** “SteelSim creates the factory; ACAMIS understands the factory.”
>
> SteelSim provides the plant builder and deterministic simulation foundation (Tasks 1 & 2). ACAMIS provides defined anomaly detectors, a policy-gated recovery workflow, and operational history (Tasks 3, 3.1 & 4). This MVP does not control physical machinery.

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

<a href="/task-4-history/overview" class="openai-card">
  <div class="openai-card-title">Task 4: Operations History</div>
  <div class="openai-card-desc">Recorded runs, telemetry replay, signal evidence, incident reports, and paused restoration.</div>
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

## Current implementation status

| Component | Current status | Verification |
| :--- | :--- | :--- |
| **Plant Builder and Simulation** | Demo plant, typed connections, live control center | Local browser smoke test passed. |
| **ACAMIS** | Manual scenarios, rolling-throughput detection, policy-gated recovery | Backend and browser tests passed. |
| **Operations History** | SQLite run journal, frame replay, report, paused restore | Backend and browser tests passed. |
| **Advisory Model Gateway** | Gemini and OpenAI-compatible keys, real generation check | Verified with a local test provider; a user's actual provider key needs its own live test. |
| **Test suite at the last code verification** | 85 backend tests and 4 frontend unit tests | Passed; type check, lint, production build, and browser smoke test also passed. |
| **Public deployment** | Site-specific status | Verify the live application URL and storage configuration before a presentation. |

---

## System Architecture

<pre class="mermaid">
flowchart TB
    subgraph Browser ["Client (React 19 / TypeScript)"]
        direction LR
        Guard["Telemetry Guard<br/>• Monotonic Version Check<br/>• Schema Validation"]
        Builder["Plant Builder<br/>• React Flow Canvas<br/>• Typed Industrial Ports"]
        ACAMISUI["ACAMIS Console<br/>• Monitoring & Plan<br/>• Impact Deck & Chat"]
        Control["Control Center<br/>• Dynamic PFD<br/>• Live KPI Summary"]
    end

    subgraph Server ["Backend (Python / FastAPI)"]
        direction LR
        Validator["Topology Validator<br/>• Port & Utility Checks"]
        SimManager["Simulation Manager<br/>• Lifecycle State Machine"]
        Engine["Deterministic Engine<br/>• Tick Loop (1s)<br/>• Flow & Interlocks"]
        ACAMISCore["ACAMIS Core<br/>• Rolling Detector (Task 3.1)<br/>• 6 Specialist Evaluators"]
    end

    Builder -->|POST /api/plant/validate| Validator
    Builder -->|POST /api/simulations| SimManager
    Control -->|POST command| SimManager
    ACAMISUI -->|REST API| ACAMISCore

    SimManager --> Engine
    Engine --> ACAMISCore

    Engine -->|WebSocket Stream<br/>& HTTP Poll| Guard
    Guard --> Control
    Guard --> ACAMISUI
</pre>
