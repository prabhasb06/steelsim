# 19. Material-flow model

The material-flow engine calculates the mass-balance progression of steel through the facility on every tick.

## Topological flow propagation

1. **Topological sorting:** The engine computes an in-degree dependency graph of all material edges. Nodes with zero in-degree (e.g., Raw Material Yard) are evaluated first, followed by downstream units in topological sequence.
2. **Upstream bounded throughput:** For any process node $i$, real-time throughput $T_i$ is bounded by:
   $$T_i = minleft(T_{	ext{rated}, i} 	imes L_f,; T_{	ext{available, upstream}}ight)$$
   where $L_f$ is the operational load factor ($0.92 le L_f le 1.04$ during active melting).
3. **Starvation propagation:** If the Raw Material Yard runs dry or the Induction Furnace halts tapping, upstream available material drops to $0.0	ext{ t/h}$. Downstream units (LRF, CCM, Mill) immediately starve and transition into an idle or interlocked state.

## Material flow diagram

<pre class="mermaid">
graph LR
    Yard["1. Raw Material Yard<br/>25 t/h Scrap & DRI"] -->|Liquid Steel| Furnace["2. Induction Furnace<br/>25 t/h Melt (1620°C)"]
    Furnace -->|Molten Steel| LRF["3. Ladle Furnace<br/>25 t/h Refined (1580°C)"]
    LRF -->|Tundish Feed| CCM["4. Billet Caster<br/>25 t/h Billets (1150°C)"]
    CCM -->|Hot Billets| Reheat["5. Reheat Furnace<br/>25 t/h Discharge (1200°C)"]
    Reheat -->|Bar Feed| Mill["6. Rolling Mill<br/>25 t/h Ribbed Bar (1050°C)"]
    Mill -->|Hot Rebar| Quench["7. Thermex Quenching<br/>25 t/h Water Quench (580°C)"]
    Quench -->|Finished Bar| Bed["8. Rake Cooling Bed<br/>25 t/h Air Cool (150°C)"]
</pre>

## Bottleneck modeling

If a downstream machine has a lower rated throughput than upstream output (e.g., Reheating Furnace rated at 20 t/h fed by a 25 t/h Caster), the engine clamps downstream flow to 20 t/h and emits a `CAPACITY_BOTTLENECK` notice.

::: tip Modeling Scope
The material flow model is a deterministic mass-balance approximation designed for plant-scale bottleneck and interlock evaluation. It does not model fluid dynamics, chemical equilibria, or microscopic phase transformations.
:::
