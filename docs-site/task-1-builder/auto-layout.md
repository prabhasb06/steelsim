# 12. Auto Layout

When equipment nodes are added to the canvas manually, they often overlap or appear disorganized. Auto Layout automatically positions nodes into a clean, readable plant layout.

## Hierarchical layout algorithm

Auto Layout uses a two-lane architectural layout strategy:

```
Y=120  [Raw Yard] ──> [Furnace] ──> [LRF] ──> [CCM] ──> [Reheat] ──> [Mill] ──> [Quench] ──> [Bed]
          ▲               ▲          ▲         ▲         ▲          ▲          ▲           ▲
Y=480  [Substation (33kV/11kV)] ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (Power)
Y=640  [Cooling Pumping Station] ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (Water)
```

### 1. Process pass-line (Primary Lane)
- Process nodes are positioned along a primary horizontal line at coordinate $Y = 120	ext{ px}$.
- Nodes are sequenced from left to right according to metallurgical flow order.
- Node spacing maintains a fixed horizontal pitch ($X_{	ext{offset}} approx 320	ext{ px}$) to provide ample space for port handles and connection labels.

### 2. Infrastructure corridor (Utility Lanes)
- High-voltage power infrastructure (Substations and Transformers) is placed in a lower utility corridor at $Y = 480	ext{ px}$.
- Cooling towers, pumping stations, and compressors are positioned at $Y = 640	ext{ px}$.
- This separation prevents utility power and water lines from crossing or obscuring primary material paths.

## Layout preservation vs. simulation invalidation
Modifying node positions via Auto Layout or manual dragging updates only the visual coordinates (`position: { x, y }`). Because coordinates do not alter physical parameters or port connectivity, layout changes **do not** invalidate or restart an active simulation.
