# 29. Scenario Control (Controlled Incidents)

**Scenario Control** provides a repeatable catalog of deterministic incident scenarios. These scenarios are deliberately injected by an operator to test mitigation policies, train personnel, demonstrate digital-twin capabilities to investors, and run regression tests.

> [!IMPORTANT]
> **Controlled Demonstrations vs. Telemetry Detection:**
> Scenarios listed on this page are **not** automatically discovered anomalies. They are synthetic disturbances triggered on demand via the user interface or API. When active, they bear the origin badge `Manual scenario`.

---

## Implemented Scenario Catalogue

### 1. Cooling-Water Degradation (`cooling_water_degradation`)
* **Industrial Meaning:** Cooling water pump pressure drops or a circulation line develops severe scale, restricting thermal dissipation.
* **Affected Assets:** Induction Furnace, Ladle Refining Furnace, Continuous Caster, Rolling Mill (all assets with water intake ports).
* **Telemetry Impact:** Operating node temperatures rise by **+42.0°C** above baseline.
* **Severity:** `HIGH`
* **Procedures:**
  * Containment: `reduce_heat_load` (drops plant load factor to 78%).
  * Final Resolution: `activate_standby_cooling` (brings temperature delta down to +8.0°C and restores normal water envelopes).
* **Autonomous Mode Behavior:** Automatic containment (`reduce_heat_load`) executes immediately. Final recovery halts for **mandatory human verification** because restarting auxiliary cooling pumps carries physical risk.

---

### 2. Furnace Instability (`furnace_instability`)
* **Industrial Meaning:** Induction furnace electrical lining wear or charge composition variations cause temperature excursions and erratic current draw.
* **Affected Assets:** `INDUCTION_FURNACE`, `LADLE_REFINING_FURNACE`.
* **Telemetry Impact:** Furnace temperature spikes by **+85.0°C**; electrical draw surges by **+15.0%**.
* **Severity:** `HIGH`
* **Procedures:**
  * Containment: `reduce_heat_load`.
  * Final Resolution: `stabilize_furnace`.
* **Autonomous Mode Behavior:** Automatic containment applied. Final recovery requires **mandatory human verification** to inspect refractory integrity.

---

### 3. Rolling-Mill Slowdown (`rolling_mill_slowdown`)
* **Industrial Meaning:** Mechanical drive slip, bearing friction, or roll pass wear constrains the finishing mill's delivery speed.
* **Affected Assets:** `ROLLING_MILL`, `ROUGHING_MILL`, `INTERMEDIATE_MILL`, `FINISHING_MILL`, and connected downstream units.
* **Telemetry Impact:** Mill rated throughput drops to **45%** of normal capacity. Downstream cooling beds and bundling units throttle proportionally.
* **Severity:** `WARNING`
* **Procedures:**
  * Optional Mitigation: `pace_upstream_material` (reduces billet feed to 80%).
  * Final Resolution: `inspect_rolling_mill`.
* **Autonomous Mode Behavior:** Because this is classified as a low-risk mechanical bottleneck, Autonomous Simulation automatically schedules recovery after **12 running simulation ticks**.

---

### 4. Electrical Capacity Constraint (`substation_capacity_constraint`)
* **Industrial Meaning:** Total plant kVA draw approaches the contractual maximum demand limit of the grid substation transformer.
* **Affected Assets:** All active electrical consumers across melting and rolling.
* **Telemetry Impact:** Measured power draw surges by **+18.0%** across operating assets.
* **Severity:** `HIGH`
* **Procedures:**
  * Containment: `reduce_heat_load`.
  * Final Resolution: `stage_energy_consumers`.
* **Autonomous Mode Behavior:** Automatic containment applied. Final recovery requires **mandatory human verification** before restoring full electrical load.

---

### 5. Raw-Material Supply Disruption (`raw_material_disruption`)
* **Industrial Meaning:** Scrap yard crane breakdown or scrap density shortages choke incoming material feed into the furnace charging tables.
* **Affected Assets:** `RAW_MATERIAL_STORAGE`, scrap charging conveyors.
* **Telemetry Impact:** Initial material feed drops to **35%** of capacity, starving the melt shop.
* **Severity:** `WARNING`
* **Procedures:**
  * Optional Mitigation: `pace_upstream_material`.
  * Final Resolution: `review_material_plan`.
* **Autonomous Mode Behavior:** Low-risk operational rebalancing; autonomous simulation automatically recovers after **12 running ticks**.

---

## Reset Behavior

Any active scenario can be immediately cleared:
* Via UI: Click **Clear scenario** in the Scenario Control toolbar.
* Via API: `POST /api/simulations/{id}/acamis/scenarios/reset`.
* Via Master Reset: Calling `POST /api/simulations/{id}/command` with `{"command": "reset"}` resets the entire simulation and ACAMIS state simultaneously.\n