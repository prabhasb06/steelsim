# 5. Investor demo

This structured, five-minute presentation script matches the verified end-to-end (E2E) workflow tested continuously in the SteelSim test suite.

## Presentation timeline

| Timecode | Phase | Primary Action | Key Talking Points |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:45** | Introduction | Show Overview view | MSME steel challenges; high energy/cooling risks; accessible digital twin. |
| **00:45 – 01:45** | Plant Builder | Load Demo & Auto Setup | React Flow canvas; typed industrial ports; automated wiring and layout. |
| **01:45 – 02:45** | Engineering Validation | Open Topology Issues | Zero-defect rule engine; aggregate utility capacity enforcement. |
| **02:45 – 04:00** | Simulation Control | Click Run, 5× speed, Pause | Backend authority; dynamic PFD; sub-second WebSockets; monotonic state. |
| **04:00 – 05:00** | Architectural Vision | Return to Builder & clear | "Creates the factory; ACAMIS understands it"; clean MVP boundaries. |

---

## Word-for-word spoken track

### 00:00 – 00:45 | Problem statement
> “Welcome. Today we are demonstrating SteelSim, an industrial digital-twin minimum viable product built specifically for MSME induction-furnace and TMT rebar plants.
>
> Secondary steel mills operate on thin margins and face severe electrical and cooling risks. Traditional digital twins cost tens of thousands of dollars and demand complex desktop CAD. SteelSim runs directly in the browser, pairing visual topological design with a backend-authoritative deterministic simulation engine.”

### 00:45 – 01:45 | Visual Plant Builder (Task 1)
*[Action: Open Plant Builder ➔ Click **Demo** ➔ Click **Auto Setup**]*
> “In the Plant Builder, we load our standard 10-node TMT baseline: raw material yard, induction furnace, ladle refining, continuous casting, reheating, rolling mill, Thermex quenching, cooling bed, plus the substation and cooling water station.
>
> These connections are not cosmetic lines—they are typed industrial ports: material flow, high-voltage electrical distribution, and cooling-water circuits. With one click on 'Auto Setup', SteelSim verifies process sequence, wires utility consumers to their respective supplies, and applies collision-free layout coordinates.”

### 01:45 – 02:45 | Zero-defect validation
*[Action: Open Topology Issues panel ➔ Highlight zero errors]*
> “Before the simulation can run, our server-side validation engine inspects the plant graph. It enforces port polarity, prevents loops, verifies metallurgical order, and checks aggregate utility capacities.
>
> If the combined electrical draw of the furnace and rolling mill exceeded the substation rating, the system would block startup. Here, our baseline validates with zero issues.”

### 02:45 – 04:00 | Simulation Control Center (Task 2)
*[Action: Navigate to Simulation ➔ Click **Run** ➔ Toggle speed to **5×**]*
> “Now we transition to the Simulation Control Center. When I click 'Run', FastAPI instantiates our deterministic engine. Telemetry streams in real time over WebSockets.
>
> Look at the Process Flow Diagram: it is generated dynamically from the active graph. We see 24.2 MW total load, 980 m³/h cooling water, and 25 tonnes per hour throughput. I can select the Induction Furnace to inspect its 1,600°C melt temperature and 15 MW draw. If I pause, execution freezes deterministically. When I reset, we return cleanly to tick 0.”

### 04:00 – 05:00 | Operational intelligence & closing
*[Action: Navigate to ACAMIS Operations Console ➔ Trigger Cooling Water Scenario ➔ Show autonomous mitigation]*
> “With Task 3 and Task 3.1 completed, SteelSim doesn't just run the factory—ACAMIS actively protects and optimizes it.
>
> When a cooling pump fails or throughput drifts, ACAMIS's 8-stage evaluation pipeline detects the anomaly within three ticks, generates root-cause diagnostics, and either alerts the operator or autonomously throttles upstream melt rate to avert catastrophic equipment damage.
>
> All 72 backend tests pass, frontend static analysis is zero-defect, and external Gemini advisory reasoning is securely isolated in transient memory. SteelSim and ACAMIS together provide a complete, investor-ready industrial operating twin. Thank you.”

> [!TIP]
> **Complete ACAMIS Demo Script:**
> For the full timed script demonstrating autonomous mitigation, safety gates, automatic anomaly drift detection, and advisory LLM chat, see [36. ACAMIS Investor Demonstration Script](/task-3-acamis/investor-demo).

