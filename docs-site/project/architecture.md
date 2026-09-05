# 47. Architecture

SteelSim is architected as a decoupled, multi-tier industrial system designed for low latency, reproducible execution, automated incident mitigation, and reliable browser visualization.

## Detailed architecture diagram

<pre class="mermaid">
graph TB
    subgraph Browser ["Client Browser (React 19 / TypeScript / Vite)"]
        Canvas["React Flow Canvas<br/>• Preserved DOM State<br/>• Typed Industrial Ports<br/>• Transparent in Simulation"]
        Control["Control Center View<br/>• Dynamic PFD Renderer<br/>• KPI Deck & Inspector<br/>• State Trace & Events"]
        AcamisUI["ACAMIS Console<br/>• Incident Operations Center<br/>• Telemetry Anomaly Panel<br/>• BYOK Advisory Chat & Modal"]
        ClientGuard["Telemetry Guard<br/>• Schema Validation<br/>• Monotonic Version Filter<br/>• Simulation ID Matcher"]
    end

    subgraph Network ["Transport Protocols"]
        REST["REST API (HTTP/1.1)<br/>• Graph Validation & Layout<br/>• Simulation Lifecycle<br/>• ACAMIS Commands & BYOK"]
        WS["WebSocket Streaming<br/>• Sub-Second Telemetry<br/>• Subprotocol Auth Gate<br/>• ACAMIS Impact Payload"]
        Poll["HTTP Polling Fallback<br/>• Periodic /snapshot Queries"]
    end

    subgraph Backend ["Backend Runtime (Python 3.10+ / FastAPI / Uvicorn)"]
        AuthMiddleware["Security & CORS<br/>• Constant-Time Key Check<br/>• Origin Whitelisting"]
        TopologyEngine["Validation Engine<br/>• Structural Graph Checks<br/>• Aggregate Utility Checks"]
        SimManager["Simulation Manager<br/>• Bounded Memory Buffer<br/>• Oldest Inactive Eviction"]
        Engine["Deterministic Engine<br/>• Monotonic state_version<br/>• Tick Loop (1 Hz)<br/>• Mass & Energy Balance"]
        AcamisCore["ACAMIS Intelligence Engine<br/>• 8-Stage Evaluation Pipeline<br/>• 6 Specialist Evaluators<br/>• Telemetry Anomaly Detector<br/>• Autonomous Mitigation & Gates"]
        Gateway["Advisory Model Gateway<br/>• In-Memory Transient Keys<br/>• Sanitized Context Bundler"]
    end

    subgraph ExternalCloud ["External Advisory Layer"]
        GeminiAPI["Google AI Studio (Gemini)<br/>• generateContent REST API<br/>• Read-Only Advisory Reasoning"]
    end

    Canvas -->|POST /api/plant/*| REST
    Control -->|POST /api/simulations/*| REST
    AcamisUI -->|POST /api/simulations/:id/acamis/*| REST
    REST --> AuthMiddleware
    AuthMiddleware --> TopologyEngine
    AuthMiddleware --> SimManager
    SimManager --> Engine
    Engine -->|Snapshot Delivery| AcamisCore
    AcamisCore -->|Interventions & Throttling| Engine
    AcamisCore --> Gateway
    Gateway -->|BYOK HTTPS API| GeminiAPI
    Engine -->|Live Snapshots + Impact| WS
    Engine -->|Snapshot Query| Poll
    WS --> ClientGuard
    Poll --> ClientGuard
    ClientGuard --> Control
    ClientGuard --> AcamisUI
</pre>

## Architectural separation of concerns

- **Client (React 19):** Responsible for UI rendering, user interactions, graph manipulation, ACAMIS operations console, and telemetry presentation. Contains zero simulation physics logic.
- **Backend (FastAPI):** Single source of truth for topology validation, simulation state, tick loops, telemetry generation, specialist evaluations, and autonomous procedure execution.
- **Intelligence Layer (ACAMIS):** Consumes read-only snapshots at stage 1 of every tick, evaluates plant state across 6 engineering domains, detects throughput anomalies via statistical drift monitoring, and safely executes mitigation procedures subject to autonomy mode and human safety gates.
- **Authoritative boundary:** If client state drifts from the server, server state snapshots immediately overwrite client state. External LLM models operate strictly out-of-band as advisory consultants without direct actuation authority.

