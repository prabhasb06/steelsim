# 35. Architecture

SteelSim is architected as a decoupled, client-server system designed for low latency, reproducible execution, and reliable browser visualization.

## Detailed architecture diagram

<pre class="mermaid">
graph TB
    subgraph Browser ["Client Browser (React 19 / TypeScript / Vite)"]
        Canvas["React Flow Canvas<br/>• Preserved DOM State<br/>• Typed Industrial Ports<br/>• Transparent in Simulation"]
        Control["Control Center View<br/>• Dynamic PFD Renderer<br/>• KPI Deck & Inspector<br/>• State Trace & Events"]
        ClientGuard["Telemetry Guard<br/>• Schema Validation<br/>• Monotonic Version Filter<br/>• Simulation ID Matcher"]
    end

    subgraph Network ["Transport Protocols"]
        REST["REST API (HTTP/1.1)<br/>• Graph Validation<br/>• Auto-Setup Heuristics<br/>• Lifecycle Commands"]
        WS["WebSocket Streaming<br/>• Sub-Second Telemetry<br/>• Subprotocol Auth Gate"]
        Poll["HTTP Polling Fallback<br/>• Periodic /snapshot Queries"]
    end

    subgraph Backend ["Backend Runtime (Python 3.10+ / FastAPI / Uvicorn)"]
        AuthMiddleware["Security & CORS<br/>• Constant-Time Key Check<br/>• Origin Whitelisting"]
        TopologyEngine["Validation Engine<br/>• Structural Graph Checks<br/>• Aggregate Utility Checks"]
        SimManager["Simulation Manager<br/>• Bounded Memory Buffer<br/>• Oldest Inactive Eviction"]
        Engine["Deterministic Engine<br/>• Monotonic state_version<br/>• Tick Loop (1s)<br/>• Flow & Interlocks"]
    end

    Canvas -->|POST /api/plant/*| REST
    Control -->|POST /api/simulations/*| REST
    REST --> AuthMiddleware
    AuthMiddleware --> TopologyEngine
    AuthMiddleware --> SimManager
    SimManager --> Engine
    Engine -->|Live Snapshots| WS
    Engine -->|Snapshot Query| Poll
    WS --> ClientGuard
    Poll --> ClientGuard
    ClientGuard --> Control
</pre>

## Architectural separation of concerns
- **Client (React 19):** Responsible for UI rendering, user interactions, graph manipulation, and telemetry presentation. Contains zero simulation physics logic.
- **Backend (FastAPI):** Single source of truth for topology validation, simulation state, tick loops, and telemetry generation.
- **Authoritative boundary:** If client state drifts from the server, server state snapshots immediately overwrite client state.
