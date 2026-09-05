# 25. Cleanup and retention

Because SteelSim executes simulations in memory, active simulation instances must be managed efficiently to avoid CPU and memory starvation.

## Bounded simulation retention

The backend `SimulationManager` enforces a bounded capacity on concurrent simulation instances:
1. **Active capacity limit:** The manager retains up to 10 simulation instances simultaneously.
2. **Automatic eviction:** When capacity is reached, the oldest inactive simulation (in state `PAUSED`, `COMPLETED`, or `READY`) is automatically evicted from memory.
3. **Explicit deletion:** Clients can destroy obsolete simulations directly using the REST endpoint:
   ```http
   DELETE /api/simulations/{sim_id} HTTP/1.1
   ```

## Plant-edit invalidation flow

When a user modifies a physical plant in the Builder, the active simulation is immediately invalidated:

<pre class="mermaid">
flowchart TD
    Edit["User Edits Physical Plant<br/>(Adds/removes node, modifies ports/parameters)"] --> Check{"Is Simulation Active?"}
    Check -->|No| Save["Save to LocalStorage"]
    Check -->|Yes| Invalidate["Client Invalidates Simulation<br/>(simulatedGraphRef = null)"]
    Invalidate --> Delete["Call DELETE /api/simulations/{id}"]
    Delete --> ResetUI["Simulation View Resets to 'No Plant' Baseline"]
    ResetUI --> Save
</pre>

Purely visual adjustments (such as dragging an equipment card to a new position) do not invalidate the simulation, allowing uninterrupted live monitoring while fine-tuning canvas layouts.
