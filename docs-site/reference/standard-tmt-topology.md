# 26. Standard TMT topology

The standard SteelSim demo includes a verified, pre-configured 10-node industrial baseline representing a nominal 25 tonne-per-hour (t/h) MSME induction-furnace and continuous TMT rebar manufacturing line.

## Ten baseline equipment nodes

| # | Asset Name | Component Class | Role in Baseline | Rated Specifications |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Raw Material Yard** | `RAW_MATERIAL_STORAGE` | Primary scrap & DRI storage | 25 t/h dispatch, 1,000 t inventory, 15 kW |
| **2** | **Induction Furnace** | `INDUCTION_FURNACE` | Primary electrical melting | 25 t/h melt, 12.5 MW, 120 m³/h water, 1,620°C |
| **3** | **Ladle Refining Furnace** | `LADLE_REFINING_FURNACE` | Secondary steel metallurgy | 25 t/h refine, 3.2 MW, 45 m³/h water, 1,580°C |
| **4** | **Continuous Caster (CCM)**| `CONTINUOUS_CASTING_MACHINE`| Twin-strand billet casting | 25 t/h billets, 0.45 MW, 90 m³/h water, 1,150°C |
| **5** | **Reheating Furnace** | `REHEATING_FURNACE` | Walking hearth billet reheat | 25 t/h discharge, 0.18 MW, 1,200°C |
| **6** | **Rolling Mill** | `ROLLING_MILL` | Multi-stand rebar reduction | 25 t/h rolling, 2.8 MW, 60 m³/h water, 12 m/s |
| **7** | **Thermex Quenching** | `TMT_QUENCHING_BOX` | Water quench surface hardening| 25 t/h quench, 0.075 MW, 150 m³/h water, 580°C |
| **8** | **Rake Cooling Bed** | `COOLING_BED` | Atmospheric rake air cooling | 25 t/h finish, 0.095 MW, 150°C discharge |
| **9** | **Plant Substation** | `UTILITY_SUBSTATION` | Primary electrical source | 33 kV / 11 kV, 25.0 MW available power |
| **10**| **Cooling Pump Station** | `WATER_COOLING_SYSTEM` | Central cooling water source | 600.0 m³/h available flow, 120 kW pump power |

## Baseline connectivity summary

The 10-node topology includes 22 individual connection edges:
- **7 Material edges:** Linear pass-line connecting units 1 through 8.
- **8 Electrical edges:** Power distribution from the Substation (9) to units 1, 2, 3, 4, 5, 6, 7, 8, and 10.
- **7 Cooling-water edges:** Water lines from the Pumping Station (10) to thermal consumers (units 2, 3, 4, 6, and 7).

## Baseline operational profile

- **Net plant power demand:** $approx 19.3	ext{ MW}$ (within the 25.0 MW substation capacity).
- **Net plant cooling-water circulation:** $approx 465.0	ext{ m}^3	ext{/h}$ (within the 600.0 m³/h pumping station capacity).
- **Net throughput:** $25.0	ext{ t/h}$ continuous finished rebar.
- **Topology validation:** 0 Errors, 0 Warnings out of the box.
