# 34. ACAMIS REST API Reference

All ACAMIS operations are exposed via authenticated REST endpoints registered under `/api/simulations/{sim_id}/acamis`.

---

## Endpoint Summary

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/simulations/{sim_id}/acamis/status` | Ingest full ACAMIS status, monitoring, findings, and plan |
| `POST` | `/api/simulations/{sim_id}/acamis/scenarios/{scenario}` | Inject a controlled manual incident scenario |
| `POST` | `/api/simulations/{sim_id}/acamis/scenarios/reset` | Clear active scenario and restore simulation baseline |
| `POST` | `/api/simulations/{sim_id}/acamis/monitoring/demo` | Apply synthetic 50% rolling capacity restriction |
| `POST` | `/api/simulations/{sim_id}/acamis/autonomy` | Change autonomy level (`OBSERVE`, `ADVISORY`, `AUTONOMOUS_SIMULATION`) |
| `POST` | `/api/simulations/{sim_id}/acamis/procedures/{procedure}` | Execute or confirm an approved simulated procedure |
| `POST` | `/api/simulations/{sim_id}/acamis/model/connect` | Verify and connect an external LLM advisory key |
| `POST` | `/api/simulations/{sim_id}/acamis/model/disconnect` | Disconnect advisory model and purge credential from memory |
| `POST` | `/api/simulations/{sim_id}/acamis/model/chat` | Send an advisory prompt to the connected model |

---

## Detailed Endpoint Specifications

### 1. Ingest ACAMIS Status
```http
GET /api/simulations/{sim_id}/acamis/status
```

* **Purpose:** Returns the complete operational intelligence snapshot including plant health, incident details, specialist evaluations, recovery plan, model status, and audit trail.
* **Status Codes:**
  * `200 OK`: Successful response.
  * `404 Not Found`: Simulation ID does not exist.

#### Response Body Excerpt
```json
{
  "contract_version": "acamis.v1",
  "source": "SteelSim Digital Twin",
  "connection": "LIVE",
  "simulation_id": "sim_9a8b7c6d",
  "state_version": 142,
  "operating_mode": "AUTONOMOUS_SIMULATION",
  "plant_health": "INCIDENT",
  "incident": {
    "id": "telemetry_rolling_throughput_deviation",
    "title": "Rolling throughput deviation",
    "severity": "WARNING",
    "summary": "Measured rolling throughput remained more than 25% below its expected baseline for three running ticks.",
    "affected_equipment": ["mill_01"],
    "verified": true,
    "contained": false
  },
  "automatic_monitoring": {
    "contract_version": "rolling-monitor.v1",
    "state": "Detected",
    "active": true,
    "required_ticks": 3,
    "threshold_percent": 25,
    "evidence": [
      {
        "equipment_id": "mill_01",
        "actual_tph": 35.0,
        "expected_tph": 70.0,
        "deviation_percent": 50.0,
        "first_detected_tick": 18,
        "persistence_count": 3
      }
    ]
  },
  "recovery_plan": {
    "status": "RECOVERING",
    "recommended_procedures": ["pace_upstream_material", "inspect_rolling_mill"],
    "procedure_statuses": {
      "pace_upstream_material": "AVAILABLE",
      "inspect_rolling_mill": "AVAILABLE"
    }
  }
}
```

---

### 2. Inject Controlled Scenario
```http
POST /api/simulations/{sim_id}/acamis/scenarios/{scenario}
```

* **Valid Scenarios:** `cooling_water_degradation`, `furnace_instability`, `rolling_mill_slowdown`, `substation_capacity_constraint`, `raw_material_disruption`.
* **Errors:**
  * `409 Conflict`: Unknown scenario, or simulation is paused/stopped.

---

### 3. Change Operating Autonomy
```http
POST /api/simulations/{sim_id}/acamis/autonomy
```

#### Request Payload
```json
{
  "mode": "AUTONOMOUS_SIMULATION"
}
```
* **Valid Modes:** `OBSERVE`, `ADVISORY`, `AUTONOMOUS_SIMULATION`.

---

### 4. Execute Simulated Procedure
```http
POST /api/simulations/{sim_id}/acamis/procedures/{procedure}
```

#### Request Payload
```json
{
  "human_verified": true
}
```
* **Parameters:** `human_verified` (boolean, default `false`). Must be `true` when confirming a high-risk recovery action awaiting operator approval.
* **Errors:**
  * `409 Conflict`: Procedure not in active incident, operating in Observe mode, or missing human verification for high-risk actions.

---

### 5. Connect Advisory Model (BYOK)
```http
POST /api/simulations/{sim_id}/acamis/model/connect
```

#### Request Payload
```json
{
  "provider": "GEMINI",
  "model": "gemini-2.5-flash",
  "api_key": "AIzaSySanitizedExampleKey",
  "base_url": null
}
```
* **Security Behavior:** Keys are stored strictly in volatile memory and never returned in response payloads.\n