# 27. Equipment catalogue

This catalogue details the complete library of components available in SteelSim (`backend/app/models/component_library.py`), including both baseline units and extended facility equipment.

## Full component specifications

| Component Class | Display Name | Ports Configured | Default Parameters |
| :--- | :--- | :--- | :--- |
| `RAW_MATERIAL_STORAGE` | Raw Material Yard (Scrap & DRI) | `mat_out`, `pwr_in` | Inventory: 1000 t, Dispatch: 25 t/h, Power: 0.015 MW |
| `INDUCTION_FURNACE` | Medium Frequency Induction Furnace | `mat_in`, `mat_out`, `pwr_in`, `wat_in`, `wat_return` | Throughput: 25 t/h, Power: 12.5 MW, Water: 120 m³/h, Temp: 1620°C |
| `LADLE_REFINING_FURNACE` | Ladle Refining Furnace (LRF) | `mat_in`, `mat_out`, `pwr_in`, `wat_in` | Throughput: 25 t/h, Power: 3.2 MW, Water: 45 m³/h, Temp: 1580°C |
| `CONTINUOUS_CASTING_MACHINE` | Billet Continuous Caster (CCM) | `mat_in`, `mat_out`, `pwr_in`, `wat_in`, `wat_return` | Throughput: 25 t/h, Power: 0.45 MW, Water: 90 m³/h, Temp: 1150°C |
| `BILLET_YARD` | Billet Yard | `mat_in`, `mat_out` | Inventory: 500 t, Storage: 5000 t, Dispatch: 25 t/h |
| `CHARGING_TABLE` | Charging Table | `mat_in`, `mat_out` | Feed Capacity: 25 t/h |
| `REHEATING_FURNACE` | Walking Hearth Reheating Furnace | `mat_in`, `mat_out`, `elec_in` | Throughput: 25 t/h, Temp: 1200°C, Power: 0.18 MW |
| `ROLLING_MILL` | Continuous TMT Bar Rolling Mill | `mat_in`, `mat_out`, `pwr_in`, `wat_in` | Throughput: 25 t/h, Power: 2.8 MW, Water: 60 m³/h, Speed: 12 m/s |
| `ROUGHING_MILL` | Roughing Mill Stand | `mat_in`, `mat_out`, `elec_in`, `water_in` | Throughput: 25 t/h, Power: 2.4 MW, Speed: 2.5 m/s |
| `INTERMEDIATE_MILL` | Intermediate Mill Stand | `mat_in`, `mat_out`, `elec_in` | Throughput: 25 t/h, Power: 3.0 MW, Speed: 5.0 m/s |
| `FINISHING_MILL` | Finishing Mill Stand | `mat_in`, `mat_out`, `elec_in` | Throughput: 25 t/h, Power: 4.0 MW, Speed: 12.0 m/s |
| `TMT_COOLING` | In-Line TMT Cooling Box | `mat_in`, `mat_out`, `water_in` | Throughput: 25 t/h, Water: 180 m³/h, Pressure: 10 bar |
| `TMT_QUENCHING_BOX` | Thermex Rapid Quenching System | `mat_in`, `mat_out`, `pwr_in`, `wat_in`, `wat_return` | Throughput: 25 t/h, Power: 0.075 MW, Water: 150 m³/h, Temp: 580°C |
| `COOLING_BED` | Automated Rake Cooling Bed | `mat_in`, `mat_out`, `pwr_in` | Throughput: 25 t/h, Buffer: 50 t, Power: 0.095 MW, Temp: 150°C |
| `CUTTING_UNIT` | Flying Shear / Cold Shear | `mat_in`, `mat_out`, `elec_in` | Throughput: 25 t/h, Speed: 12 m/s |
| `BUNDLING_UNIT` | Automatic Rebar Bundling Station | `mat_in`, `mat_out` | Throughput: 25 t/h |
| `WEIGHING` | Finished Product Weighbridge | `mat_in`, `mat_out`, `signal_out` | Throughput: 25 t/h |
| `FINISHED_GOODS` | Finished Rebar Warehouse | `mat_in` | Inventory: 100 t, Storage: 5000 t, Dispatch: 25 t/h |
| `UTILITY_SUBSTATION` | High Voltage Plant Substation | `elec_out` | Available Power: 25.0 MW (33 kV / 11 kV) |
| `WATER_COOLING_SYSTEM` | Closed-Loop Cooling Station | `wat_out`, `wat_return`, `pwr_in` | Available Flow: 600 m³/h, Power: 0.12 MW |
| `WATER_PUMP` | Auxiliary Water Pump | `water_in`, `water_out`, `elec_in` | Flow: 100 m³/h, Power: 0.5 MW |
| `COMPRESSOR` | Industrial Air Compressor | `elec_in`, `air_out` | Flow: 500 Nm³/h |
| `BUFFER` | Intermediate Billet/Bar Buffer | `mat_in`, `mat_out` | Buffer Capacity: 20 t |
