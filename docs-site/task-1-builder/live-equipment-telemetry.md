# 15. Live equipment telemetry

During an active simulation run, the Plant Builder canvas doubles as a live operational monitoring surface. Equipment nodes visually display their real-time telemetry directly on the canvas cards.

## On-card telemetry indicators

```
┌────────────────────────────────────────┐
│ Medium Frequency Induction Furnace    │
│ [RUNNING ●]                   1,620 °C │
├────────────────────────────────────────┤
│ Power Draw:   12,500 kW (12.50 MW)     │
│ Cooling Flow: 120.0 m³/h               │
│ Throughput:   25.0 t/h                 │
└────────────────────────────────────────┘
```

- **Operational status badge:**
  - `RUNNING:` Emerald badge with a pulsating green indicator dot.
  - `IDLE:` Blue badge indicating zero throughput and nominal standby power.
  - `INTERLOCKED:` Red badge with warning icon indicating utility loss or upstream starvation.
- **Dynamic metric readouts:**
  - Real-time power draw displayed in both kW and MW.
  - Circulating cooling-water flow in m³/h.
  - Operating temperature in °C with thermal color gradients.
  - Active mass throughput in t/h.

## Inspector deep-dive

Selecting any node on the canvas opens the right-side **Inspector** panel. When a simulation is active, the Inspector renders a dedicated **Live Telemetry** drawer showing:
- Raw sensor telemetry fields.
- Percentage utilization against rated design limits.
- Upstream material feed source and downstream discharge target.
- Interlock trip reason (if tripped due to utility or supply failure).
