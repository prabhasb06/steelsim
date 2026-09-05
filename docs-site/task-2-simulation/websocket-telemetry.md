# 23. WebSocket telemetry

Real-time telemetry in SteelSim is transmitted using a dual-transport architecture: low-latency WebSocket streaming as the primary protocol, with automatic HTTP snapshot polling as a resilient fallback.

## Transport sequence and fallback

<pre class="mermaid">
sequenceDiagram
    autonumber
    actor UI as Simulation Control Center
    participant WS as WebSocket Endpoint (/stream)
    participant REST as HTTP Snapshot Endpoint (/snapshot)
    participant Sim as Simulation Engine

    UI->>WS: Connect WebSocket (subprotocol: steelsim)
    alt WebSocket Connected
        WS-->>UI: Accept Connection
        loop Every Tick (1s)
            Sim->>WS: Emit Snapshot JSON
            WS-->>UI: Real-Time Telemetry Payload
            UI->>UI: Validate Monotonic Version & Render
        end
    else WebSocket Disconnected / Network Error
        UI->>UI: Set Status: RECONNECTING
        loop Fallback Polling (Every 5s)
            UI->>REST: GET /api/simulations/{id}/snapshot
            REST->>Sim: Fetch Authoritative Snapshot
            Sim-->>REST: Snapshot JSON
            REST-->>UI: Render Telemetry
        end
        UI->>WS: Retry WebSocket Connection
    end
</pre>

## Telemetry payload schema

Every snapshot packet emitted by the server contains:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **`simulation_id`** | string | Unique simulation identifier (`sim_XXXXXXXX`). |
| **`state_version`** | integer | Monotonically increasing version sequence number. |
| **`tick`** | integer | Elapsed simulation ticks (seconds). |
| **`simulation_time`**| ISO 8601 string | Simulated factory clock timestamp. |
| **`status`** | string | Lifecycle state: `READY`, `RUNNING`, `PAUSED`, `COMPLETED`, `ERROR`. |
| **`speed`** | string | Active speed multiplier (`1x`, `5x`, `10x`, `60x`, `MAX`). |
| **`system_health`** | string | Global operational health: `NORMAL` or `DEGRADED`. |
| **`plant_summary`** | object | Plant totals: `total_power_mw`, `total_water_m3h`, `active_nodes`, `interlocked_nodes`.|
| **`node_telemetry`** | dictionary | Map of node IDs to live machine telemetry (`status`, `power_kw`, `water_m3h`, `temp`, `throughput`). |
| **`events`** | array | Last 50 simulation events for the scrolling log. |
