# 21. Equipment interlocks

An industrial interlock is an automated safeguard that halts machinery when required operational preconditions are lost.

## Interlock trigger mechanisms

SteelSim implements two deterministic interlock conditions:

### 1. Utility deprivation interlock
- **Trigger:** Process machinery with required power (`pwr_in`) or cooling-water (`wat_in`) ports loses its connection to an active supply node.
- **Immediate effect:**
  - Node operational status trips to `INTERLOCKED`.
  - Machine throughput drops to $0.0	ext{ t/h}$.
  - Power consumption drops to standby ($0.0	ext{ kW}$).
  - Temperature halts at ambient or cooling equilibrium.
  - An `EQUIPMENT_FAULT` event is logged in the simulation event journal.

### 2. Upstream feed starvation interlock
- **Trigger:** Upstream process unit halts, dumps, or ceases material discharge.
- **Immediate effect:**
  - Downstream unit throughput drops to $0.0	ext{ t/h}$.
  - If prolonged, downstream machinery trips to `INTERLOCKED` or `IDLE` to prevent dry-running rolls or thermal shock.

## Cascade trip propagation

Because material flow is evaluated topologically, an interlock on an upstream unit (e.g., Induction Furnace water pump trip) cascades downstream:
```
Induction Furnace Trips ➔ Zero Output ➔ LRF Starves ➔ CCM Runs Dry ➔ Mill Idles
```
The Simulation Control Center displays interlocked equipment in bright red with warning badges, highlighting the root cause in the Equipment Inspector.
