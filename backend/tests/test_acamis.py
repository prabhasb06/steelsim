import pytest
from fastapi.testclient import TestClient

from app.api.routes import manager
from main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    manager._simulations.clear()
    yield
    for sim in list(manager._simulations.values()):
        if sim._task and not sim._task.done():
            sim._task.cancel()
    manager._simulations.clear()


def create_running_tmt_simulation() -> str:
    plant = client.get("/api/plant/template/tmt").json()
    sim_id = client.post("/api/simulations", json={"plant": plant}).json()["id"]
    response = client.post(f"/api/simulations/{sim_id}/command", json={"command": "start"})
    assert response.status_code == 200
    return sim_id


def test_acamis_status_uses_versioned_steelsim_snapshot():
    sim_id = create_running_tmt_simulation()
    response = client.get(f"/api/simulations/{sim_id}/acamis/status")
    assert response.status_code == 200
    data = response.json()
    assert data["contract_version"] == "acamis.v1"
    assert data["source"] == "SteelSim Digital Twin"
    assert data["connection"] == "LIVE"
    assert data["plant_health"] == "NORMAL"
    assert len(data["specialist_findings"]) == 6
    assert data["snapshot"]["state_version"] == data["state_version"]


def test_cooling_incident_changes_telemetry_and_requires_verification():
    sim_id = create_running_tmt_simulation()
    baseline = client.get(f"/api/simulations/{sim_id}/snapshot").json()
    response = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/cooling_water_degradation")
    assert response.status_code == 200
    data = response.json()
    assert data["incident"]["verified"] is True
    assert data["plant_health"] == "INCIDENT"
    assert data["recovery_plan"]["status"] == "HUMAN_VERIFICATION_REQUIRED"
    assert len(data["incident"]["affected_equipment"]) > 0
    changed = data["snapshot"]
    water_nodes = [node_id for node_id, telemetry in baseline["node_telemetry"].items() if telemetry["water_m3h"] > 0]
    assert any(changed["node_telemetry"][node_id]["temperature_c"] > baseline["node_telemetry"][node_id]["temperature_c"] for node_id in water_nodes)


def test_observe_mode_blocks_procedure_then_advisory_allows_it():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/cooling_water_degradation")
    blocked = client.post(f"/api/simulations/{sim_id}/acamis/procedures/activate_standby_cooling")
    assert blocked.status_code == 409
    changed_mode = client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "ADVISORY"})
    assert changed_mode.status_code == 200
    applied = client.post(f"/api/simulations/{sim_id}/acamis/procedures/activate_standby_cooling")
    assert applied.status_code == 200
    assert applied.json()["audit"][0]["event"] == "PROCEDURE_EXECUTED"


def test_static_reset_route_clears_incident_and_mitigations():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/furnace_instability")
    response = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["incident"] is None
    assert data["plant_health"] == "NORMAL"
    assert data["audit"][0]["event"] == "SCENARIO_CLEARED"


def test_unknown_scenario_and_procedure_are_rejected():
    sim_id = create_running_tmt_simulation()
    assert client.post(f"/api/simulations/{sim_id}/acamis/scenarios/not-real").status_code == 409
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "ADVISORY"})
    assert client.post(f"/api/simulations/{sim_id}/acamis/procedures/not-real").status_code == 409


def test_autonomous_mode_executes_safe_procedure_but_escalates_high_risk():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "AUTONOMOUS_SIMULATION"})
    safe = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/rolling_mill_slowdown")
    assert safe.status_code == 200
    assert safe.json()["audit"][0]["event"] == "AUTONOMOUS_PROCEDURE_EXECUTED"

    critical = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/furnace_instability")
    assert critical.status_code == 200
    assert critical.json()["recovery_plan"]["status"] == "HUMAN_VERIFICATION_REQUIRED"
    assert critical.json()["audit"][0]["event"] == "HUMAN_VERIFICATION_REQUESTED"
    blocked = client.post(f"/api/simulations/{sim_id}/acamis/procedures/reduce_heat_load")
    assert blocked.status_code == 409
    assert "Human verification" in blocked.json()["detail"]


def test_model_gateway_verifies_connection_without_exposing_key(monkeypatch):
    sim_id = create_running_tmt_simulation()
    requests = []
    def fake_provider_request(url, **kwargs):
        requests.append((url, kwargs))
        if kwargs.get("method") == "POST":
            return {"choices": [{"message": {"content": "Advisory review complete."}}]}
        return {"data": []}
    monkeypatch.setattr("app.acamis.model_gateway._request_json", fake_provider_request)
    response = client.post(f"/api/simulations/{sim_id}/acamis/model/connect", json={
        "provider": "OPENAI_COMPATIBLE",
        "model": "test-model",
        "api_key": "secret-value",
        "base_url": "http://127.0.0.1:11434/v1",
    })
    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert "api_key" not in response.json()
    status = client.get(f"/api/simulations/{sim_id}/acamis/status").json()
    assert status["model_gateway"]["model"] == "test-model"
    assert "api_key" not in status["model_gateway"]

    reviewed = client.post(f"/api/simulations/{sim_id}/acamis/model/chat", json={"message": "Assess the incident"})
    assert reviewed.status_code == 200
    assert reviewed.json() == {"reply": "Advisory review complete.", "provider": "OPENAI_COMPATIBLE", "model": "test-model", "advisory_only": True}
    assert "CONTEXT:" in requests[-1][1]["payload"]["messages"][1]["content"]
    assert "secret-value" not in requests[-1][1]["payload"]["messages"][1]["content"]

    disconnected = client.post(f"/api/simulations/{sim_id}/acamis/model/disconnect")
    assert disconnected.status_code == 200
    assert disconnected.json()["model_gateway"]["configured"] is False
