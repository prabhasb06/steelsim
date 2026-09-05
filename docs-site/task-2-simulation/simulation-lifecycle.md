# 17. Simulation lifecycle

The simulation engine implements a formal finite-state machine (FSM). State transitions are governed by strict lifecycle invariants, and illegal transitions are rejected by the server.

## Lifecycle state diagram

<pre class="mermaid">
stateDiagram-v2
    [*] --> READY : POST /api/simulations
    
    READY --> RUNNING : start / run
    RUNNING --> PAUSED : pause
    PAUSED --> RUNNING : resume / run
    RUNNING --> READY : reset
    PAUSED --> READY : reset
    
    RUNNING --> COMPLETED : Max Duration Reached
    RUNNING --> ERROR : Unrecoverable Fault
    PAUSED --> ERROR : Fault Trigger
    
    READY --> [*] : DELETE /api/simulations/:id
    PAUSED --> [*] : DELETE /api/simulations/:id
    COMPLETED --> [*] : DELETE /api/simulations/:id
    ERROR --> [*] : DELETE /api/simulations/:id
</pre>

## State definitions and transitions

| State | Entry Trigger | Execution Behavior | Available Next Commands |
| :--- | :--- | :--- | :--- |
| **`READY`** | Simulation created or reset | Clock at tick 0; baseline telemetry computed; tick loop inactive. | `start`, `run`, `delete` |
| **`RUNNING`** | `start`, `run`, or `resume` command | Tick loop actively progressing; telemetry updating and broadcasting. | `pause`, `reset`, `set_speed` |
| **`PAUSED`** | `pause` command | Clock frozen; telemetry static; subscribers receive pause notification. | `resume`, `run`, `reset` |
| **`COMPLETED`**| Target batch/duration reached | Execution finished; final snapshots preserved in memory buffer. | `reset`, `delete` |
| **`ERROR`** | Unhandled runtime exception | Execution halted; error details recorded in event journal. | `reset`, `delete` |

## Server-side validation gate

The `start`, `run`, and `resume` commands invoke `require_runnable_topology(sim)` on the backend. If the plant graph contains blocking errors (such as missing utility lines or reversed ports), the backend rejects the lifecycle command with HTTP 409 Conflict.
