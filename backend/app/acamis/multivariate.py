"""Versioned, explainable simulated telemetry rules; no model or scenario lookup."""
from math import isfinite

RULES = (
    ("thermal", "temperature_c", 40.0, "absolute"),
    ("cooling", "water_m3h", 0.75, "low"),
    ("electrical", "power_kw", 1.12, "high"),
)


def evaluate(sim):
    if sim.status.value != "RUNNING":
        return
    state = sim.signal_monitor
    if sim.tick <= state["last_tick"]:
        return
    if state["last_tick"] >= 0 and sim.tick != state["last_tick"] + 1:
        state["samples"] = {}
    state["last_tick"] = sim.tick
    findings = []
    for node in sim.config.plant.nodes:
        actual = sim.node_telemetry.get(node.id, {})
        baseline = sim.expected_telemetry.get(node.id, {})
        signals = []
        for domain, metric, limit, direction in RULES:
            value, expected = actual.get(metric), baseline.get(metric)
            valid = (actual.get("status") == "RUNNING" and isinstance(value, (int, float))
                     and isinstance(expected, (int, float)) and isfinite(value) and isfinite(expected) and expected > 0)
            abnormal = valid and (abs(value - expected) > limit if direction == "absolute"
                                  else value < expected * limit if direction == "low" else value > expected * limit)
            key = f"{node.id}:{domain}"
            sample = state["samples"].setdefault(key, {"count": 0, "first_tick": None})
            if not abnormal:
                sample.update(count=0, first_tick=None)
                continue
            if not sample["count"]:
                sample["first_tick"] = sim.tick
            sample["count"] += 1
            if sample["count"] >= 3:
                signals.append({"domain": domain, "metric": metric, "actual": value, "expected": expected,
                                "first_tick": sample["first_tick"], "persistence": sample["count"]})
        if signals:
            findings.append({"equipment_id": node.id, "name": node.name, "signals": signals,
                             "correlated": len(signals) > 1, "severity": "HIGH",
                             "response": "Operator review required. No automatic repair is registered for this signal finding."})
    old = {(f["equipment_id"], s["domain"]) for f in state["findings"] for s in f["signals"]}
    new = {(f["equipment_id"], s["domain"]) for f in findings for s in f["signals"]}
    state["findings"] = findings
    if new != old:
        from app.acamis.service import _audit
        _audit(sim, "SIGNAL_INCIDENT_CHANGED", f"Telemetry findings: {len(findings)} assets; opened {len(new - old)} signals, cleared {len(old - new)}.", "HIGH" if new else "INFO")


def initial_state():
    return {"version": "signals.v1", "last_tick": -1, "samples": {}, "findings": []}
