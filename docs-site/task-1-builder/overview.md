# 6. Task 1 overview

Task 1 delivers an interactive visual engineering workspace in which plant engineers and operators can assemble, connect, validate, arrange, save, and inspect a steel manufacturing plant topology.

Traditional computer-aided design (CAD) software treats factory schematics as static geometries. In contrast, Task 1 models the steel plant as a directed, typed engineering graph. Every component on the canvas possesses explicit physical parameters (such as rated power in MW, water consumption in m³/h, and design throughput in t/h), and every connection carries strict industrial domain semantics.

## Core capabilities

- **React Flow engineering canvas:** Hardware-accelerated canvas with infinite panning, semantic zooming, multi-node selection, and snap-to-grid alignment.
- **Typed industrial ports:** Material, Electrical, Cooling Water, Signal, and Air connection points with strict directionality rules.
- **Structural and engineering validation:** Instant checking of port types, flow cycles, metallurgical sequences, and aggregate utility capacities.
- **Automation routines:** One-click tools for automatic process connection, utility distribution, and hierarchical collision-free layout.
- **Persistent canvas lifecycle:** The canvas remains mounted in the browser DOM across route switches, preserving custom layouts without re-rendering.
- **Real-time telemetry integration:** Equipment cards display live power draw, water circulation, operating temperature, and throughput during simulation runs.

## Workspace architecture

<pre class="mermaid">
flowchart TD
    subgraph Toolbar ["Canvas Toolbar"]
        Tools["Panels: [Library] [Inspector] [Issues] | Automation: [Auto Connect] [Auto Layout] [Auto Setup] | Actions: [Demo] [Save]"]
    end

    subgraph Workspace ["Builder Workspace Layout"]
        direction LR
        Palette["Component Palette (Left)<br/>• Melting & Refining<br/>• Casting & Reheat<br/>• Rolling & Quench<br/>• Substation & Pumps"]
        Canvas["React Flow Interactive Canvas (Center)<br/>• Visual Node Cards<br/>• Typed Connection Edges<br/>• Metallurgical Pass-Line Sequence"]
    end

    subgraph Bottom ["Issues & Console (Bottom)"]
        Issues["Topology Issues & Event Console<br/>• 0 Errors | 0 Warnings | Port Polarity & Aggregate Capacity Status"]
    end

    Toolbar --> Workspace --> Bottom
</pre>
