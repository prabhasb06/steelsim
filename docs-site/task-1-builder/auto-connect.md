# 11. Auto Connect

Manual wiring of a ten-node steel plant requires creating more than twenty individual connections across material, electrical, and cooling circuits. Auto Connect automates this process using industrial rule heuristics.

## Dual connection algorithms

Auto Connect is divided into two specialized routines:

### 1. Auto Connect Process
- Evaluates placed equipment nodes and identifies process assets along the primary flow line.
- Sorts nodes using the industrial `TMT_SEQUENCE` catalog:
  ```
  Raw Yard ➔ Induction Furnace ➔ LRF ➔ CCM ➔ Reheating Furnace ➔ Rolling Mill ➔ Quenching Box ➔ Cooling Bed
  ```
- Automatically connects the primary `mat_out` port of each stage to the `mat_in` port of the subsequent stage.
- Ignores disconnected utility stations, ensuring clean process line formation.

### 2. Auto Connect Utilities
- Identifies utility sources: High-Voltage Plant Substation (`elec_out`) and Cooling Pumping Station (`wat_out`).
- Scans all placed equipment nodes for unfulfilled utility input ports (`pwr_in`, `wat_in`).
- Routes dedicated electrical edges from the Substation to each electrical consumer.
- Routes dedicated cooling-water lines from the Pumping Station to each water consumer.
- Checks aggregate capacities before proposing connections to avoid over-subscribing utility supplies.

## API contract

Auto-connect proposals are computed via the REST endpoint:
```http
POST /api/plant/auto-connect HTTP/1.1
Content-Type: application/json

{
  "nodes": [ ... ],
  "edges": [ ... ]
}
```
