"""Deterministic telemetry monitoring; no scenario or model input is used to detect."""
from math import isfinite

INCIDENT = "telemetry_rolling_throughput_deviation"
MILLS = {"ROLLING_MILL", "ROUGHING_MILL", "INTERMEDIATE_MILL", "FINISHING_MILL"}
WINDOW = 3
LIMIT = 0.75


def reset(sim):
    sim.rolling_monitor = {"contract_version": "rolling-monitor.v1", "state": "Normal",
                           "last_tick": -1, "samples": {}, "evidence": []}


def public_status(sim):
    monitor = sim.rolling_monitor
    rows = []
    for node in sim.config.plant.nodes:
        if node.component_class.value not in MILLS:
            continue
        current = sim.node_telemetry.get(node.id, {})
        expected = sim.expected_telemetry.get(node.id, {}).get("throughput_tph", 0)
        rows.append({"equipment_id": node.id, "name": node.name,
                     "actual_tph": current.get("throughput_tph", 0), "expected_tph": expected,
                     "lower_bound_tph": round(expected * LIMIT, 2),
                     "persistence": monitor["samples"].get(node.id, {}).get("count", 0)})
    state = monitor["state"]
    if sim.acamis_scenario == INCIDENT:
        state = "Recovering" if sim.acamis_recovery_tick is not None else "Detected"
    return {"contract_version": monitor["contract_version"], "state": state,
            "active": sim.status.value == "RUNNING" and bool(rows) and sim.acamis_scenario in (None, INCIDENT),
            "required_ticks": WINDOW, "threshold_percent": 25, "equipment": rows,
            "evidence": monitor["evidence"], "demo_active": bool(sim.rolling_disturbance),
            "suspended_by_manual_incident": sim.acamis_scenario not in (None, INCIDENT)}


def evaluate(sim):
    if sim.status.value != "RUNNING" or sim.tick <= sim.rolling_monitor["last_tick"]:
        return
    monitor = sim.rolling_monitor
    if monitor["last_tick"] >= 0 and sim.tick != monitor["last_tick"] + 1 and sim.acamis_scenario != INCIDENT:
        monitor["samples"] = {}
    monitor["last_tick"] = sim.tick
    if sim.acamis_scenario not in (None, INCIDENT):
        monitor["samples"] = {}
        monitor["state"] = "Normal"
        return
    if sim.acamis_scenario == INCIDENT:
        monitor["state"] = "Recovering" if sim.acamis_recovery_tick is not None else "Detected"
        return
    snapshot = sim.get_snapshot()
    watching = False
    evidence = []
    for node in sim.config.plant.nodes:
        if node.component_class.value not in MILLS:
            continue
        telemetry = snapshot.node_telemetry.get(node.id)
        expected = snapshot.expected_throughput_tph.get(node.id, 0)
        actual = telemetry.throughput_tph if telemetry else None
        valid = actual is not None and isfinite(actual) and isfinite(expected) and expected > 0
        sample = monitor["samples"].setdefault(node.id, {"count": 0, "first_tick": None})
        if not valid or actual >= expected * LIMIT:
            sample.update(count=0, first_tick=None)
            continue
        watching = True
        if not sample["count"]:
            sample["first_tick"] = sim.tick
        sample["count"] += 1
        if sample["count"] >= WINDOW:
            evidence.append({"equipment_id": node.id, "actual_tph": actual, "expected_tph": expected,
                             "deviation_percent": round((expected - actual) / expected * 100, 2),
                             "first_detected_tick": sample["first_tick"], "persistence_count": sample["count"]})
    if evidence:
        from app.acamis import service
        monitor["evidence"] = evidence
        monitor["state"] = "Detected"
        sim.acamis_scenario = INCIDENT
        sim.acamis_last_resolution = None
        sim.acamis_last_model_advisory = None
        sim._calculate_telemetry()
        if sim.acamis_impact is not None:
            for item in evidence:
                sim.acamis_impact["equipment"].setdefault(item["equipment_id"], {})["throughput_tph"] = {"baseline": item["expected_tph"], "actual": item["actual_tph"]}
        service._audit(sim, "TELEMETRY_ANOMALY_DETECTED", f"Rolling throughput exceeded the 25% deviation threshold for {WINDOW} running ticks.", "WARNING")
        service._run_autonomous_response(sim)
        monitor["state"] = "Recovering" if sim.acamis_recovery_tick is not None else "Detected"
    elif watching:
        monitor["state"] = "Watching"
    elif monitor["state"] != "Recovered":
        monitor["state"] = "Normal"
