# 12. Auto Layout

When equipment nodes are added to the canvas manually, they often overlap or appear disorganized. Auto Layout automatically positions nodes into a clean, readable plant layout.

## Hierarchical layout algorithm

Auto Layout uses a two-lane architectural layout strategy:

<pre class="mermaid">
flowchart LR
    subgraph ProcessLane ["Process Pass-Line (Y = 120 px)"]
        direction LR
        Raw["Raw Yard"] --> Furn["Induction Furnace"] --> LRF["Ladle Furnace"] --> CCM["Continuous Caster"] --> Reheat["Reheat Furnace"] --> Mill["Rolling Mill"] --> Quench["Quench Box"] --> Bed["Cooling Bed"]
    end

    subgraph UtilityLane ["Infrastructure Corridor (Y = 480 px & 640 px)"]
        direction LR
        Sub["High-Voltage Substation (33kV/11kV)"]
        Pump["Closed-Loop Cooling Station (600 m³/h)"]
    end

    Sub -.->|"Electrical Power Bus"| ProcessLane
    Pump ==>|"Circulating Water Lines"| ProcessLane
</pre>

### 1. Process pass-line (Primary Lane)
- Process nodes are positioned along a primary horizontal line at coordinate $Y = 120\text{ px}$.
- Nodes are sequenced from left to right according to metallurgical flow order.
- Node spacing maintains a fixed horizontal pitch ($X_{\text{offset}} \approx 320\text{ px}$) to provide ample space for port handles and connection labels.

### 2. Infrastructure corridor (Utility Lanes)
- High-voltage power infrastructure (Substations and Transformers) is placed in a lower utility corridor at $Y = 480\text{ px}$.
- Cooling towers, pumping stations, and compressors are positioned at $Y = 640\text{ px}$.
- This separation prevents utility power and water lines from crossing or obscuring primary material paths.

## Layout preservation vs. simulation invalidation
Modifying node positions via Auto Layout or manual dragging updates only the visual coordinates (`position: { x, y }`). Because coordinates do not alter physical parameters or port connectivity, layout changes **do not** invalidate or restart an active simulation.\n