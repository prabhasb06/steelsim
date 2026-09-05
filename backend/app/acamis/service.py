from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.acamis import model_gateway
from app.acamis import detector

SCENARIOS: dict[str, dict[str, Any]] = {
    "cooling_water_degradation": {"title": "Cooling-water degradation", "severity": "HIGH", "summary": "Cooling capacity has fallen below the process demand envelope.", "procedures": ["activate_standby_cooling", "reduce_heat_load"], "containment": "reduce_heat_load", "resolution": "activate_standby_cooling"},
    "furnace_instability": {"title": "Furnace instability", "severity": "HIGH", "summary": "Furnace process temperature is deviating from its operating window.", "procedures": ["reduce_heat_load", "stabilize_furnace"], "containment": "reduce_heat_load", "resolution": "stabilize_furnace"},
    "rolling_mill_slowdown": {"title": "Rolling-mill slowdown", "severity": "WARNING", "summary": "Rolling capacity is constrained and downstream throughput is at risk.", "procedures": ["pace_upstream_material", "inspect_rolling_mill"], "resolution": "inspect_rolling_mill"},
    "substation_capacity_constraint": {"title": "Electrical capacity constraint", "severity": "HIGH", "summary": "Electrical demand is approaching the configured utility operating envelope.", "procedures": ["reduce_heat_load", "stage_energy_consumers"], "containment": "reduce_heat_load", "resolution": "stage_energy_consumers"},
    "raw_material_disruption": {"title": "Raw-material supply disruption", "severity": "WARNING", "summary": "Incoming material availability is constraining the production chain.", "procedures": ["pace_upstream_material", "review_material_plan"], "resolution": "review_material_plan"},
}
DOMAINS = ("Safety", "Maintenance", "Quality", "Production", "Energy", "Logistics")
MANUAL_SCENARIOS = frozenset(SCENARIOS)
SCENARIOS[detector.INCIDENT] = {**SCENARIOS["rolling_mill_slowdown"], "title": "Rolling throughput deviation", "summary": "Measured rolling throughput remained more than 25% below its expected baseline for three running ticks."}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _audit(sim: Any, event: str, detail: str, severity: str = "INFO") -> None:
    if not hasattr(sim, "acamis_audit"):
        sim.acamis_audit = []
    sim.acamis_audit.append({"id": f"acamis-{uuid4().hex}", "at": _now(), "event": event, "detail": detail, "severity": severity, "state_version": sim.state_version})
    del sim.acamis_audit[:-200]

def _affected_equipment(sim: Any) -> list[str]:
    return list(dict.fromkeys([*list((sim.acamis_impact or {}).get("equipment", {})),
                              *([item["equipment_id"] for item in sim.rolling_monitor["evidence"]] if sim.acamis_scenario == detector.INCIDENT else [])]))

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
    if scenario == detector.INCIDENT:
        for finding in findings:
            finding["evidence"] = [f"Measured {item['actual_tph']} t/h versus expected {item['expected_tph']} t/h; {item['deviation_percent']}% deviation persisted {item['persistence_count']} ticks." for item in sim.rolling_monitor["evidence"]]
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
        "automatic_monitoring": detector.public_status(sim),
        "incident_origin": "Telemetry detector" if scenario == detector.INCIDENT else "Manual scenario" if scenario else None,
        "incident_evidence": sim.rolling_monitor["evidence"] if scenario == detector.INCIDENT else [],
        "recovery_plan": {"status": "HUMAN_VERIFICATION_REQUIRED" if escalation else ("RECOVERING" if sim.acamis_recovery_tick is not None else "READY" if scenario else "RECOVERED" if getattr(sim, "acamis_last_resolution", None) else "MONITORING"), "priority_order": ["Safety", "Equipment limits", "Quality", "Maintenance", "Production", "Energy", "Logistics"], "recommended_procedures": definition["procedures"] if definition else [], "procedure_statuses": procedure_statuses, "rationale": "In autonomous mode, safe containment is automatic. Final high-risk repairs require an operator; low-risk simulated recovery advances with the simulation clock."},
        "model_gateway": model_gateway.public_status(sim),
        "model_advisory": getattr(sim, "acamis_last_model_advisory", None),
        "context_manifest": {"ruleset": "acamis-simulation-policy.v1", "snapshot_contract": "acamis.v1", "domains": list(DOMAINS), "approved_procedures_only": True},
        "audit": list(reversed(getattr(sim, "acamis_audit", [])))[0:50], "snapshot": sim.get_snapshot().model_dump(mode="json"),
    }

def _resolve_incident(sim: Any, scenario: str, procedure: str, autonomous: bool) -> None:
    if scenario == detector.INCIDENT and sim.status.value != "RUNNING":
        raise ValueError("Resume the simulation before applying recovery so live throughput can be verified")
    recorded_impact = sim.acamis_impact
    if scenario == detector.INCIDENT:
        sim.rolling_disturbance.clear()
    sim.apply_acamis_procedure(procedure)
    if scenario == detector.INCIDENT:
        from math import isfinite
        def recovered_reading(item):
            actual = sim.node_telemetry.get(item["equipment_id"], {}).get("throughput_tph")
            expected = sim.expected_telemetry.get(item["equipment_id"], {}).get("throughput_tph")
            return (actual is not None and expected is not None and isfinite(actual)
                    and isfinite(expected) and expected > 0 and actual >= expected * detector.LIMIT)
        unresolved = not sim.rolling_monitor["evidence"] or not all(recovered_reading(item) for item in sim.rolling_monitor["evidence"])
        if unresolved:
            sim.acamis_recovery_tick = None
            sim.rolling_monitor["state"] = "Detected"
            sim._calculate_telemetry()
            sim._state_changed()
            _audit(sim, "RECOVERY_VERIFICATION_FAILED", "Throughput remains below the monitored range after simulated inspection; incident remains open.", "WARNING")
            return
    _audit(sim, "AUTONOMOUS_PROCEDURE_EXECUTED" if autonomous else "PROCEDURE_EXECUTED", f"Applied simulated recovery procedure: {procedure}.")
    impact = {**(recorded_impact or {}), "state": "RECOVERED"}
    sim.acamis_last_resolution = {"scenario": scenario, "procedure": procedure, "at": _now(), "impact": impact}
    sim.clear_acamis_scenario()
    if scenario == detector.INCIDENT:
        sim.rolling_monitor["state"] = "Recovered"
        sim.rolling_monitor["samples"] = {}
    _audit(sim, "INCIDENT_RECOVERED", f"Verified recovery from {SCENARIOS[scenario]['title']}; plant returned to its operating envelope.")

def _run_autonomous_response(sim: Any) -> None:
    scenario = getattr(sim, "acamis_scenario", None)
    if not scenario or getattr(sim, "acamis_autonomy", "OBSERVE") != "AUTONOMOUS_SIMULATION":
        return
    definition = SCENARIOS[scenario]
    assessment = status(sim)
    if assessment["recovery_plan"]["status"] in {"READY", "RECOVERING"}:
        if sim.acamis_recovery_tick is None:
            sim.acamis_recovery_tick = sim.tick + 12
            sim._calculate_telemetry()
            sim._state_changed()
            _audit(sim, "AUTONOMOUS_RECOVERY_SCHEDULED", "Simulated inspection and recovery scheduled after 12 running simulation ticks; pause freezes this procedure.")
        return
    containment = definition.get("containment")
    if containment and containment not in sim.acamis_mitigations:
        sim.apply_acamis_procedure(containment)
        _audit(sim, "AUTONOMOUS_CONTAINMENT_EXECUTED", f"ACAMIS safely contained the incident with: {containment}.", "WARNING")
    _audit(sim, "HUMAN_VERIFICATION_REQUESTED", "The plant is stabilized. Human verification is required for the final high-risk repair.", "HIGH")

def advance_recovery(sim: Any) -> None:
    """Advance approved low-risk simulated work only with the simulation clock."""
    if (sim.status.value == "RUNNING" and sim.acamis_autonomy == "AUTONOMOUS_SIMULATION"
            and sim.acamis_scenario and sim.acamis_recovery_tick is not None
            and sim.tick >= sim.acamis_recovery_tick):
        scenario = sim.acamis_scenario
        _resolve_incident(sim, scenario, SCENARIOS[scenario]["resolution"], autonomous=True)

def inject_scenario(sim: Any, scenario: str) -> dict[str, Any]:
    if scenario not in MANUAL_SCENARIOS:
        raise ValueError("Unknown ACAMIS scenario")
    if sim.status.value != "RUNNING":
        raise ValueError("Run or resume the simulation before injecting a scenario so its telemetry effects are visible.")
    sim.inject_acamis_scenario(scenario)
    _audit(sim, "SCENARIO_INJECTED", SCENARIOS[scenario]["title"], SCENARIOS[scenario]["severity"])
    _run_autonomous_response(sim)
    return status(sim)

def clear_scenario(sim: Any) -> dict[str, Any]:
    detector.reset(sim)
    sim.rolling_disturbance.clear()
    sim.acamis_last_resolution = None
    sim.clear_acamis_scenario()
    _audit(sim, "SCENARIO_CLEARED", "Scenario cleared and simulation baseline restored.")
    return status(sim)

def set_autonomy(sim: Any, mode: str) -> dict[str, Any]:
    if mode not in {"OBSERVE", "ADVISORY", "AUTONOMOUS_SIMULATION"}:
        raise ValueError("Invalid ACAMIS operating mode")
    sim.acamis_autonomy = mode
    if mode != "AUTONOMOUS_SIMULATION":
        sim.acamis_recovery_tick = None
        sim._calculate_telemetry()
        sim._state_changed()
    _audit(sim, "AUTONOMY_MODE_CHANGED", f"ACAMIS operating mode set to {mode}.")
    _run_autonomous_response(sim)
    return status(sim)

def start_telemetry_demo(sim: Any) -> dict[str, Any]:
    if sim.status.value != "RUNNING" or sim.acamis_scenario or sim.rolling_disturbance:
        raise ValueError("Run the simulation and clear the current incident or disturbance first.")
    mills = [node.id for node in sim.config.plant.nodes if node.component_class.value in detector.MILLS]
    if not mills:
        raise ValueError("This plant has no rolling-mill equipment.")
    detector.reset(sim)
    sim.acamis_last_resolution = None
    sim.rolling_disturbance[mills[0]] = 0.5
    sim._calculate_telemetry()
    _audit(sim, "TELEMETRY_DEMO_STARTED", "Applied 50% rolling capacity disturbance; the monitor must independently detect its measured effect.")
    sim._state_changed()
    return status(sim)

def execute_procedure(sim: Any, procedure: str, *, human_verified: bool = False) -> dict[str, Any]:
    valid = {name for item in SCENARIOS.values() for name in item["procedures"]}
    if procedure not in valid:
        raise ValueError("Procedure is not registered in the ACAMIS library")
    if not sim.acamis_scenario or procedure not in SCENARIOS[sim.acamis_scenario]["procedures"]:
        raise ValueError("Procedure does not belong to the active incident")
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
