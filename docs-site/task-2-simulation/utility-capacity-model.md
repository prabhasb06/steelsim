# 20. Utility-capacity model

Secondary steel manufacturing is exceptionally utility-intensive. SteelSim models electrical and cooling-water distribution as aggregate capacity networks.

## Electrical network model

Process machinery specifies required electrical power connections. The backend computes the sum of active electrical draws and compares it against connected substation capacity:

$$P_{	ext{total}} = sum_{i in 	ext{Consumers}} P_{	ext{rated}, i} 	imes L_f$$

$$	ext{Capacity Check: } P_{	ext{total}} le P_{	ext{substation, rated}}$$

If total connected power exceeds rated substation supply (e.g., $32.5	ext{ MW}$ connected to a $25.0	ext{ MW}$ substation), the validation engine rejects simulation startup with `UTILITY_CAPACITY_INSUFFICIENT`.

## Cooling-water network model

Thermal units (Induction Furnaces, CCM molds, and Thermex Quenching boxes) require continuous water circulation:

$$Q_{	ext{water, total}} = sum_{i in 	ext{Consumers}} Q_{	ext{rated}, i}$$

$$	ext{Capacity Check: } Q_{	ext{water, total}} le Q_{	ext{pump_station, rated}}$$

## Utility relationship diagram

<pre class="mermaid">
graph TB
    subgraph Electrical ["Electrical Distribution (33 kV / 11 kV)"]
        Substation["High-Voltage Substation<br/>Rated: 35.0 MW"]
        Substation -.->|12.5 MW| FurnaceElec["Induction Furnace"]
        Substation -.->|3.2 MW| LRFElec["Ladle Furnace"]
        Substation -.->|0.45 MW| CCMElec["Billet Caster"]
        Substation -.->|2.8 MW| MillElec["Rolling Mill"]
    end

    subgraph Cooling ["Closed-Loop Cooling Circuit"]
        PumpStation["Cooling Pumping Station<br/>Rated: 1200 m³/h"]
        PumpStation ==>|120 m³/h| FurnaceWat["Induction Furnace"]
        PumpStation ==>|45 m³/h| LRFWat["Ladle Furnace"]
        PumpStation ==>|90 m³/h| CCMWat["Billet Caster"]
        PumpStation ==>|150 m³/h| QuenchWat["Thermex Quenching"]
    end
</pre>
