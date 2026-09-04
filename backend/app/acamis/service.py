from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.acamis import model_gateway

SCENARIOS: dict[str, dict[str, Any]] = {
    "cooling_water_degradation": {"title": "Cooling-water degradation", "severity": "HIGH", "summary": "Cooling capacity has fallen below the process demand envelope.", "procedures": ["activate_standby_cooling", "reduce_heat_load"], "containment": "reduce_heat_load", "resolution": "activate_standby_cooling"},
    "furnace_instability": {"title": "Furnace instability", "severity": "HIGH", "summary": "Furnace process temperature is deviating from its operating window.", "procedures": ["reduce_heat_load", "stabilize_furnace"], "containment": "reduce_heat_load", "resolution": "stabilize_furnace"},
    "rolling_mill_slowdown": {"title": "Rolling-mill slowdown", "severity": "WARNING", "summary": "Rolling capacity is constrained and downstream throughput is at risk.", "procedures": ["pace_upstream_material", "inspect_rolling_mill"], "resolution": "inspect_rolling_mill"},
    "substation_capacity_constraint": {"title": "Electrical capacity constraint", "severity": "HIGH", "summary": "Electrical demand is approaching the configured utility operating envelope.", "procedures": ["reduce_heat_load", "stage_energy_consumers"], "containment": "reduce_heat_load", "resolution": "stage_energy_consumers"},
    "raw_material_disruption": {"title": "Raw-material supply disruption", "severity": "WARNING", "summary": "Incoming material availability is constraining the production chain.", "procedures": ["pace_upstream_material", "review_material_plan"], "resolution": "review_material_plan"},
}
DOMAINS = ("Safety", "Maintenance", "Quality", "Production", "Energy", "Logistics")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _audit(sim: Any, event: str, detail: str, severity: str = "INFO") -> None:
    if not hasattr(sim, "acamis_audit"):
        sim.acamis_audit = []
    sim.acamis_audit.append({"id": f"acamis-{len(sim.acamis_audit) + 1}", "at": _now(), "event": event, "detail": detail, "severity": severity, "state_version": sim.state_version})
    del sim.acamis_audit[:-200]

def _affected_equipment(sim: Any) -> list[str]:
    scenario = getattr(sim, "acamis_scenario", None)
    matching = {
        "cooling_water_degradation": ("WATER", "COOLING", "TMT", "ROLLING", "FURNACE"),
        "furnace_instability": ("FURNACE", "INDUCTION", "LADLE"),
        "rolling_mill_slowdown": ("ROLLING", "MILL", "TMT", "COOLING"),
        "substation_capacity_constraint": ("SUBSTATION", "TRANSFORMER", "FURNACE", "MILL"),
        "raw_material_disruption": ("RAW", "YARD", "STORAGE", "CHARGING"),
    }.get(scenario, ())
    return [node.id for node in sim.config.plant.nodes if any(token in node.component_class.value or token in node.name.upper() for token in matching)][:6]

def _finding(domain: str, scenario: str | None, severity: str, affected: list[str]) -> dict[str, Any]:
    if not scenario:
        return {"domain": domain, "severity": "INFO", "confidence": 0.98, "summary": "No active anomaly detected in the simulated operating envelope.", "evidence": ["Live SteelSim snapshot is within the configured baseline."], "affected_equipment": [], "recommended_procedures": [], "escalation_required": False}
    title = SCENARIOS[scenario]["title"]
    language = {
        "Safety": ("Protect operating limits while the incident is contained.", scenario in {"cooling_water_degradation", "furnace_instability"}),
        "Maintenance": ("Prioritize inspection of the affected simulated assets.", False),
        "Quality": ("Monitor process conditions for product-quality exposure.", scenario == "furnace_instability"),
        "Production": ("Rebalance the process plan to limit throughput loss.", False),
        "Energy": ("Evaluate utility demand before returning to full load.", scenario in {"cooling_water_degradation", "substation_capacity_constraint"}),
        "Logistics": ("Align material movement with the revised production pace.", False),
    }
    summary, escalate = language[domain]
    return {"domain": domain, "severity": severity if domain in {"Safety", "Quality", "Energy"} else "WARNING", "confidence": 0.92, "summary": f"{title}: {summary}", "evidence": [f"Active deterministic scenario: {title}.", f"Affected assets: {len(affected)}."], "affected_equipment": affected, "recommended_procedures": SCENARIOS[scenario]["procedures"], "escalation_required": escalate}

def status(sim: Any) -> dict[str, Any]:
    scenario = getattr(sim, "acamis_scenario", None)
    definition = SCENARIOS.get(scenario) if scenario else None
    affected = _affected_equipment(sim)
    severity = definition["severity"] if definition else "INFO"
    findings = [_finding(domain, scenario, severity, affected) for domain in DOMAINS]
    escalation = any(item["escalation_required"] for item in findings)
    contained = bool(definition and definition.get("containment") in getattr(sim, "acamis_mitigations", set()))
    procedure_statuses: dict[str, str] = {}
    if definition:
        for procedure in definition["procedures"]:
            if procedure in getattr(sim, "acamis_mitigations", set()):
                procedure_statuses[procedure] = "APPLIED"
            elif escalation and procedure == definition.get("resolution"):
                procedure_statuses[procedure] = "AWAITING_HUMAN_APPROVAL"
            else:
                procedure_statuses[procedure] = "AVAILABLE"
    return {
        "contract_version": "acamis.v1", "source": "SteelSim Digital Twin", "connection": "LIVE" if sim.status.value == "RUNNING" else "STANDBY", "simulation_id": sim.id, "state_version": sim.state_version,
        "operating_mode": getattr(sim, "acamis_autonomy", "OBSERVE"), "plant_health": "STABILIZED" if contained else ("INCIDENT" if scenario else ("DEGRADED" if sim.plant_summary["interlocked_nodes"] else "NORMAL")),
        "incident": None if not definition else {"id": scenario, "title": definition["title"], "severity": severity, "summary": definition["summary"], "affected_equipment": affected, "verified": True, "contained": contained},
        "specialist_findings": findings,
        "recovery_plan": {"status": "HUMAN_VERIFICATION_REQUIRED" if escalation else ("READY" if scenario else "RECOVERED" if getattr(sim, "acamis_last_resolution", None) else "MONITORING"), "priority_order": ["Safety", "Equipment limits", "Quality", "Maintenance", "Production", "Energy", "Logistics"], "recommended_procedures": definition["procedures"] if definition else [], "procedure_statuses": procedure_statuses, "rationale": "Safe containment is automatic. Final high-risk repairs require an operator; low-risk incidents recover automatically."},
        "model_gateway": model_gateway.public_status(sim),
        "model_advisory": getattr(sim, "acamis_last_model_advisory", None),
        "context_manifest": {"ruleset": "acamis-simulation-policy.v1", "snapshot_contract": "acamis.v1", "domains": list(DOMAINS), "approved_procedures_only": True},
        "audit": list(reversed(getattr(sim, "acamis_audit", [])))[0:50], "snapshot": sim.get_snapshot().model_dump(mode="json"),
    }

def _resolve_incident(sim: Any, scenario: str, procedure: str, autonomous: bool) -> None:
    sim.apply_acamis_procedure(procedure)
    _audit(sim, "AUTONOMOUS_PROCEDURE_EXECUTED" if autonomous else "PROCEDURE_EXECUTED", f"Applied simulated recovery procedure: {procedure}.")
    sim.acamis_last_resolution = {"scenario": scenario, "procedure": procedure, "at": _now()}
    sim.clear_acamis_scenario()
    _audit(sim, "INCIDENT_RECOVERED", f"Verified recovery from {SCENARIOS[scenario]['title']}; plant returned to its operating envelope.")

def _run_autonomous_response(sim: Any) -> None:
    scenario = getattr(sim, "acamis_scenario", None)
    if not scenario or getattr(sim, "acamis_autonomy", "OBSERVE") != "AUTONOMOUS_SIMULATION":
        return
    definition = SCENARIOS[scenario]
    assessment = status(sim)
    if assessment["recovery_plan"]["status"] == "READY":
        _resolve_incident(sim, scenario, definition["resolution"], autonomous=True)
        return
    containment = definition.get("containment")
    if containment and containment not in sim.acamis_mitigations:
        sim.apply_acamis_procedure(containment)
        _audit(sim, "AUTONOMOUS_CONTAINMENT_EXECUTED", f"ACAMIS safely contained the incident with: {containment}.", "WARNING")
    _audit(sim, "HUMAN_VERIFICATION_REQUESTED", "The plant is stabilized. Human verification is required for the final high-risk repair.", "HIGH")

def inject_scenario(sim: Any, scenario: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError("Unknown ACAMIS scenario")
    sim.inject_acamis_scenario(scenario)
    _audit(sim, "SCENARIO_INJECTED", SCENARIOS[scenario]["title"], SCENARIOS[scenario]["severity"])
    _run_autonomous_response(sim)
    return status(sim)

def clear_scenario(sim: Any) -> dict[str, Any]:
    sim.clear_acamis_scenario()
    sim.acamis_last_resolution = None
    _audit(sim, "SCENARIO_CLEARED", "Scenario cleared and simulation baseline restored.")
    return status(sim)

def set_autonomy(sim: Any, mode: str) -> dict[str, Any]:
    if mode not in {"OBSERVE", "ADVISORY", "AUTONOMOUS_SIMULATION"}:
        raise ValueError("Invalid ACAMIS operating mode")
    sim.acamis_autonomy = mode
    _audit(sim, "AUTONOMY_MODE_CHANGED", f"ACAMIS operating mode set to {mode}.")
    _run_autonomous_response(sim)
    return status(sim)

def execute_procedure(sim: Any, procedure: str, *, human_verified: bool = False) -> dict[str, Any]:
    valid = {name for item in SCENARIOS.values() for name in item["procedures"]}
    if procedure not in valid:
        raise ValueError("Procedure is not registered in the ACAMIS library")
    if getattr(sim, "acamis_autonomy", "OBSERVE") == "OBSERVE":
        raise ValueError("Set ACAMIS to Advisory or Autonomous Simulation before applying a procedure")
    assessment = status(sim)
    if (
        getattr(sim, "acamis_autonomy", "OBSERVE") == "AUTONOMOUS_SIMULATION"
        and assessment["recovery_plan"]["status"] == "HUMAN_VERIFICATION_REQUIRED"
    ):
        scenario = getattr(sim, "acamis_scenario", None)
        if not human_verified:
            raise ValueError("Human verification is required before applying the final recovery procedure")
        if not scenario or procedure != SCENARIOS[scenario]["resolution"]:
            raise ValueError("Human verification can approve only the incident's final recovery procedure")
        _audit(sim, "HUMAN_VERIFICATION_CONFIRMED", f"Operator approved the final simulated recovery procedure: {procedure}.", "HIGH")
    scenario = getattr(sim, "acamis_scenario", None)
    if scenario and procedure == SCENARIOS[scenario]["resolution"]:
        _resolve_incident(sim, scenario, procedure, autonomous=False)
    else:
        sim.apply_acamis_procedure(procedure)
        _audit(sim, "PROCEDURE_EXECUTED", f"Applied simulated procedure: {procedure}.")
    return status(sim)
