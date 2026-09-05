# 8. Equipment library

The equipment library defines all industrial assets available for placement on the canvas. Assets are divided into process equipment, shaping units, and utility infrastructure.

## Component categories

<pre class="mermaid">
flowchart TD
    Library["Industrial Component Library"]
    Primary["Primary Metallurgy<br/>• Raw Material Yard<br/>• Induction Furnace<br/>• Ladle Refining Furnace<br/>• Continuous Caster"]
    Shaping["Shaping & Finishing<br/>• Reheating Furnace<br/>• Rolling Mill Stands<br/>• Thermex Quenching<br/>• Rake Cooling Bed"]
    Utility["Utility Infrastructure<br/>• Plant Substation<br/>• Cooling Pumping Station<br/>• Compressors & Pumps"]

    Library --> Primary
    Library --> Shaping
    Library --> Utility
</pre>


### Primary metallurgy
1. **Raw Material Yard (`RAW_MATERIAL_STORAGE`):** Storage yard for scrap steel and Direct-Reduced Iron (DRI). Dispatches solid charge at nominal 25 t/h.
2. **Medium-Frequency Induction Furnace (`INDUCTION_FURNACE`):** Core electrical melting asset (12.5–15 MW, 1,600–1,620°C). Requires high-pressure cooling water.
3. **Ladle Refining Furnace (`LADLE_REFINING_FURNACE`):** Secondary metallurgical station for desulfurization, alloying, and temperature control (3.2–3.5 MW, 1,580–1,620°C).
4. **Billet Continuous Casting Machine (`CONTINUOUS_CASTING_MACHINE`):** Twin-strand caster solidifying liquid steel into semi-finished square billets (0.45–1.2 MW, 1,050–1,150°C).

### Shaping and finishing
5. **Walking Hearth Reheating Furnace (`REHEATING_FURNACE`):** Equalizes billet temperature prior to rolling (1,150–1,200°C).
6. **Continuous TMT Bar Rolling Mill (`ROLLING_MILL`):** Multi-stand continuous rolling mill reducing billets into ribbed rebar (2.8–4.5 MW, 1,050°C, 12 m/s delivery).
7. **Thermex Rapid Quenching System (`TMT_QUENCHING_BOX`):** In-line high-pressure water quench box creating a self-tempered martensitic outer rim (150–350 m³/h, 580°C).
8. **Automated Rake Cooling Bed (`COOLING_BED`):** Mechanical rake bed for final uniform atmospheric cooling (150°C discharge).

### Utility infrastructure
9. **High-Voltage Plant Substation (`UTILITY_SUBSTATION`):** 33 kV / 11 kV transformer substation supplying electrical power (25–35 MW rated capacity).
10. **Closed-Loop Cooling-Water Pumping Station (`WATER_COOLING_SYSTEM`):** Industrial pump house and cooling tower providing process cooling (600–1,200 m³/h).
