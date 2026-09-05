# SteelSim Documentation

SteelSim is an industrial digital-twin MVP for MSME induction-furnace and TMT rebar manufacturing facilities. It pairs a visual plant-topology builder with a backend-authoritative deterministic simulation engine.

> **Core tenet:** “SteelSim creates the factory; ACAMIS understands the factory.”
>
> SteelSim provides the verifiable plant-builder and deterministic physical simulation foundation. ACAMIS represents a separate future decision-support layer. SteelSim is an engineering demonstration and investor-facing MVP; it does not directly control physical machinery.

---

## Documentation Sections

<div class="openai-grid">

<a href="/getting-started/introduction" class="openai-card">
  <div class="openai-card-title">Getting Started</div>
  <div class="openai-card-desc">Problem statement, two-tiered architecture, verified MVP scope boundaries, and local installation.</div>
</a>

<a href="/getting-started/investor-demo" class="openai-card">
  <div class="openai-card-title">Investor Demonstration</div>
  <div class="openai-card-desc">Concise 5-minute timed demonstration script matching the 18-step verified browser E2E workflow.</div>
</a>

<a href="/task-1-builder/overview" class="openai-card">
  <div class="openai-card-title">Task 1: Plant Builder</div>
  <div class="openai-card-desc">React Flow canvas, typed industrial ports, auto-wiring, auto-layout, and topology validation.</div>
</a>

<a href="/task-2-simulation/overview" class="openai-card">
  <div class="openai-card-title">Task 2: Simulation Engine</div>
  <div class="openai-card-desc">Deterministic tick loop, monotonic state versioning, mass flow, utility capacities, and interlocks.</div>
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

- **Frontend application:** `http://127.0.0.1:5173/`
- **Backend API & docs:** `http://127.0.0.1:8000/docs`
- **Backend health probe:** `http://127.0.0.1:8000/api/health`

---

## Verified Baseline Status

| Component | Target Metric | Verified Status |
| :--- | :--- | :--- |
| **Commit Hash** | `e1dad6ef603ee8975a8500ab33debb40d1697d46` | **Verified** (`main` clean) |
| **Backend Tests** | 43 test cases | **43 / 43 Passed** (`pytest`) |
| **Frontend Unit Tests** | 4 test cases | **4 / 4 Passed** (`node --test`) |
| **Frontend Linter** | 0 warnings, 0 errors | **Passed** (`oxlint`) |
| **TypeScript Compilation** | Strict type-check | **Passed** (`tsc -b`) |
| **Production Build** | Vite bundle | **Passed** (`vite build`) |
| **Browser E2E Workflow** | 18-step headless smoke test | **Passed** (0 console errors) |
| **Standard Demo Topology** | 10 nodes, 22 connections | **Valid** (0 errors, 0 warnings) |

---

## System Architecture

```mermaid
graph TB
    subgraph Browser ["Client (React 19 / TypeScript)"]
        Builder["Plant Builder<br/>React Flow Canvas<br/>Typed Industrial Ports"]
        Control["Control Center<br/>Dynamic PFD<br/>Live KPI Summary"]
        Guard["Telemetry Guard<br/>Monotonic Version Check"]
    end

    subgraph Server ["Backend (Python / FastAPI)"]
        Validator["Topology Validator<br/>Port & Utility Checks"]
        SimManager["Simulation Manager<br/>Lifecycle State Machine"]
        Engine["Deterministic Engine<br/>Tick Loop (1s)<br/>Flow & Interlocks"]
    end

    Builder -->|POST /api/plant/validate| Validator
    Builder -->|POST /api/simulations| SimManager
    Control -->|POST /api/simulations/{id}/command| SimManager
    SimManager --> Engine
    Engine -->|WebSocket Stream & HTTP Poll| Guard
    Guard --> Control
```