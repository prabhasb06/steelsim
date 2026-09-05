# 10. Topology validation

The SteelSim validation engine (`topology_validator.py`) inspects the plant graph against an industrial rule matrix. Validation runs continuously on the client and is strictly enforced by the backend before simulation startup.

## Validation rule matrix

| Rule Code | Severity | Trigger Condition | Safety / Engineering Purpose |
| :--- | :--- | :--- | :--- |
| **`PORT_MISMATCH`** | ERROR | Edge connects two ports of differing types | Prevents incompatible connections (e.g., water line to electrical terminal). |
| **`PORT_DIRECTION_INVALID`** | ERROR | Connection runs from input port or to output port | Enforces physical flow directionality. |
| **`DUPLICATE_CONNECTION`** | ERROR | Two identical edges share the same port pair | Prevents double-accounting of flow or electrical capacity. |
| **`CIRCULAR_FLOW`** | ERROR | Loop detected in material connections | Enforces that steelmaking is strictly acyclic from scrap to rebar. |
| **`PROCESS_SEQUENCE_INVALID`**| ERROR | Downstream process placed before upstream process | Enforces metallurgical sequence (e.g., Casting must precede Rolling). |
| **`PROCESS_PATH_BROKEN`** | ERROR | Intermediate unit has material output with no target | Prevents broken flow paths that leave product uncollected. |
| **`UTILITY_REQUIRED`** | ERROR | Unit requiring power or cooling has no supply | Prevents running unpowered or uncooled machinery. |
| **`UTILITY_SOURCE_INVALID`** | ERROR | Utility edge originates from node without capacity | Enforces that power or water connections originate from rated sources. |
| **`UTILITY_CAPACITY_INSUFFICIENT`**| ERROR | Total connected consumer load exceeds supply | Blocks simulation startup if substation MW or water m³/h is undersized. |
| **`INVALID_CONFIGURATION`** | ERROR | Parameter has negative value or out-of-bounds ratio| Prevents mathematically invalid engineering parameters. |
| **`CAPACITY_BOTTLENECK`** | WARNING | Upstream output exceeds downstream capacity by >5% | Non-blocking warning notifying operator of potential throughput choking. |

## Server-side safety gate

Client validation is mirrored on the server. If an invalid or unpowered plant graph is submitted via the API (`POST /api/simulations/{id}/start`), the backend rejects the command with an HTTP 400/409 error:

```json
{
  "detail": "Simulation blocked by 2 topology issues"
}
```
