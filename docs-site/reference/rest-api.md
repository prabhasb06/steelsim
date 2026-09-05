# 28. REST API

The SteelSim backend exposes a comprehensive RESTful API for plant topology management, validation, and simulation lifecycle control.

## Endpoint reference

| Method | Path | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Public health check / liveness probe | `{"status": "ok", "service": "steelsim-backend"}` |
| `GET` | `/api/plant/templates` | Returns component templates catalog | `Dict[str, ComponentTemplate]` |
| `GET` | `/api/plant/template/tmt` | Returns standard 10-node TMT plant graph | `PlantGraph` |
| `GET` | `/api/plant/components/{c_class}`| Returns default node for component class | `EquipmentNode` |
| `POST` | `/api/plant/validate` | Validates plant graph against rule matrix | `ValidationResult` |
| `POST` | `/api/plant/auto-connect` | Proposes automatic connection edges | `List[ConnectionEdge]` |
| `POST` | `/api/plant/auto-layout` | Applies two-lane hierarchical layout | `PlantGraph` |
| `POST` | `/api/plant/auto-setup` | Executes complete auto-wire and layout | `AutoSetupProposal` |
| `GET` | `/api/simulations` | Lists active simulations in memory | `List[SimulationState]` |
| `POST` | `/api/simulations` | Creates a new simulation instance | `SimulationState` (State: `READY`) |
| `GET` | `/api/simulations/{id}` | Retrieves simulation metadata and state | `SimulationState` |
| `DELETE`| `/api/simulations/{id}` | Destroys simulation and frees memory | `{"deleted": true, "simulation_id": "..."}` |
| `POST` | `/api/simulations/{id}/command` | Unified lifecycle command dispatcher | `SimulationSnapshot` |
| `POST` | `/api/simulations/{id}/start` | Convenience endpoint to start simulation | `SimulationState` |
| `POST` | `/api/simulations/{id}/pause` | Convenience endpoint to pause simulation | `SimulationState` |
| `POST` | `/api/simulations/{id}/resume`| Convenience endpoint to resume simulation| `SimulationState` |
| `POST` | `/api/simulations/{id}/reset` | Resets simulation clock and telemetry | `SimulationState` |
| `POST` | `/api/simulations/{id}/speed` | Updates clock speed multiplier | `SimulationState` |
| `GET` | `/api/simulations/{id}/snapshot`| Fetches latest authoritative snapshot | `SimulationSnapshot` |
| `GET` | `/api/simulations/{id}/snapshots`| Fetches bounded snapshot history (120 max)| `List[SimulationSnapshot]` |
| `GET` | `/api/simulations/{id}/events` | Fetches bounded event log (500 max) | `List[SimulationEvent]` |

## Unified command dispatcher (`POST /api/simulations/{id}/command`)

The unified command endpoint simplifies client integration by handling all lifecycle operations through a single payload:

```json
{
  "command": "start" | "pause" | "resume" | "reset" | "set_speed",
  "payload": {
    "speed": "5x"
  }
}
```
