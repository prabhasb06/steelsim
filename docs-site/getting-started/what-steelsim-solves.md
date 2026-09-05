# 2. What SteelSim solves

MSME steel manufacturing facilities represent a critical portion of infrastructure steel production, converting steel scrap and Direct-Reduced Iron (DRI) into high-strength TMT rebar. Despite their economic significance, MSME facilities face distinct operational and technological barriers.

## Operational challenges in MSME steel plants

### 1. High utility vulnerability
Medium-frequency induction furnaces rely on high-power electrical transformers (often 10–25 MW per furnace) and continuous cooling water circuits. An unpredicted drop in cooling-water flow can overheat the induction coil within seconds, while an aggregate electrical overload trips substation breakers, causing liquid steel to freeze in the ladle or continuous caster.

### 2. Cascading process interlocks
Secondary steelmaking is tightly coupled:
```
Raw Material Yard
  ➔ Induction Furnace
  ➔ Ladle Refining Furnace (LRF)
  ➔ Continuous Casting Machine (CCM)
  ➔ Reheating Furnace
  ➔ Rolling Mill
  ➔ Thermex Quenching
  ➔ Cooling Bed
```
Because molten steel loses temperature rapidly during transport, any unplanned halt downstream forces upstream furnaces to hold or dump heats, resulting in high refractory wear and wasted energy.

### 3. Inaccessibility of legacy digital twins
Traditional digital-twin and plant simulation platforms (such as enterprise finite-element packages or proprietary discrete-event simulators) suffer from:
- Prohibitive licensing costs (tens of thousands of dollars annually).
- Excessive setup complexity requiring weeks of specialized consulting.
- Desktop-only software architectures incompatible with modern web collaboration.
- Lack of built-in templates tailored to induction-furnace and mini-mill flows.

## How SteelSim addresses the problem

| Challenge | Legacy Approach | SteelSim Solution |
| :--- | :--- | :--- |
| **Plant Design** | Static 2D AutoCAD or Visio schematics without domain validation | Interactive web canvas with typed industrial ports and automatic wiring |
| **Utility Sizing** | Manual spreadsheet calculations prone to omission errors | Automated aggregate capacity checks comparing consumer draw against substation and pump ratings |
| **Operational Feasibility** | Trial-and-error commissioning on physical machinery | Deterministic virtual factory simulation testing mass flows, bottlenecks, and utility deprivation |
| **Deployment Speed** | Months of setup and model calibration | Instant browser-based launch with a pre-validated 10-node TMT demo baseline |
| **Cost & Footprint** | Heavy workstation hardware and costly seat licenses | Zero-install web client running on standard modern browsers |

## Separation from physical control
SteelSim simulates plant behavior numerically for planning, training, design validation, and investment evaluation. It does not replace certified industrial Programmable Logic Controllers (PLCs), Distributed Control Systems (DCS), or safety-instrumented systems (SIS).
