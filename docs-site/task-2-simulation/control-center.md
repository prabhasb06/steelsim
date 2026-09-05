# 22. Simulation Control Center

The Simulation Control Center is the primary operational workspace for Task 2, providing real-time monitoring and control of the running virtual factory.

## Interface breakdown

<pre class="mermaid">
flowchart TD
    subgraph Header ["1. Master Header & Controls"]
        Status["Status: RUNNING (Tick 142, 00:02:22) | Version: #142 | Power: 24.2 MW | Cooling: 980 m³/h"]
        Controls["Controls: [Run] [Pause] [Reset] | Speed Multipliers: [1x] [5x] [10x] [60x]"]
    end

    subgraph PFD ["2. Dynamic Process Flow Diagram (PFD)"]
        PassLine["Primary Process Pass-Line<br/>Raw Yard ➔ Furnace ➔ LRF ➔ CCM ➔ Reheat ➔ Mill ➔ Quench ➔ Cooling Bed"]
        Corridor["Infrastructure Utility Corridor<br/>High-Voltage Substation (Electrical Bus) | Cooling Station (Water Circuit)"]
    end

    subgraph BottomDeck ["3. Diagnostic Deck"]
        Inspector["Equipment Inspector Drawer<br/>• Real-time Power, Water, Temp, Throughput<br/>• Rated Limit Utilization & Interlock Status"]
        Journal["State Trace & Event Journal<br/>• Monotonic Event Stream<br/>• Telemetry & Interlock Trips Log"]
    end

    Header --> PFD --> BottomDeck
</pre>

## Dynamically generated Process Flow Diagram (PFD)

Unlike static SCADA graphics, the PFD in SteelSim is computed dynamically from the active plant graph:
- Process units are extracted, sorted topologically, and arranged along the horizontal pass-line.
- Utility supplies are partitioned into an infrastructure corridor below the process flow.
- Equipment cards update in real time with live throughput, thermal readings, and status indicators.
- Clicking any equipment card opens its real-time diagnostic parameters in the Equipment Inspector.
