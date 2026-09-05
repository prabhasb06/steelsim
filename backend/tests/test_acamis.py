import pytest
from fastapi.testclient import TestClient

from app.api.routes import manager
from app.acamis.model_gateway import _provider_error_message
from main import app


client = TestClient(app)


def test_model_gateway_translates_invalid_api_key_without_echoing_provider_json():
    detail = '{"error":{"code":400,"message":"API key not valid. Please pass a valid API key.","details":[{"reason":"API_KEY_INVALID"}]}}'
    message = _provider_error_message(400, detail)
    assert message.startswith("INVALID API KEY:")
    assert "Google AI Studio" in message
    assert "{\"error\"" not in message


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
    assert applied.json()["plant_health"] == "NORMAL"
    assert applied.json()["recovery_plan"]["status"] == "RECOVERED"
    assert applied.json()["audit"][0]["event"] == "INCIDENT_RECOVERED"


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


@pytest.mark.parametrize("scenario", ["cooling_water_degradation", "furnace_instability", "rolling_mill_slowdown", "substation_capacity_constraint", "raw_material_disruption"])
def test_scenario_impact_matches_actual_telemetry_and_clears(scenario):
    sim_id = create_running_tmt_simulation()
    data = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/{scenario}").json()
    impact = data["snapshot"]["acamis_impact"]
    assert impact["equipment"]
    assert set(data["incident"]["affected_equipment"]) == set(impact["equipment"])
    for node_id, metrics in impact["equipment"].items():
        for metric, values in metrics.items():
            assert values["actual"] != values["baseline"]
            assert values["actual"] == data["snapshot"]["node_telemetry"][node_id][metric]
    cleared = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/reset").json()
    assert cleared["snapshot"]["acamis_impact"] is None


def test_pause_freezes_recovery_and_rejects_new_injection():
    from app.acamis.service import advance_recovery
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "AUTONOMOUS_SIMULATION"})
    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/rolling_mill_slowdown")
    sim = manager.get_simulation(sim_id)
    impact = sim.acamis_impact["equipment"]
    sim.pause()
    sim.tick = sim.acamis_recovery_tick
    advance_recovery(sim)
    assert sim.acamis_scenario == "rolling_mill_slowdown"
    assert sim.acamis_impact["equipment"] == impact
    assert client.post(f"/api/simulations/{sim_id}/acamis/scenarios/raw_material_disruption").status_code == 409
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "OBSERVE"})
    assert sim.acamis_recovery_tick is None
    sim.reset()
    assert sim.get_snapshot().acamis_impact is None


def test_unrelated_procedure_cannot_repair_active_incident():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "ADVISORY"})
    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/rolling_mill_slowdown")
    assert client.post(f"/api/simulations/{sim_id}/acamis/procedures/stabilize_furnace").status_code == 409


def test_autonomous_mode_executes_safe_procedure_but_escalates_high_risk():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "AUTONOMOUS_SIMULATION"})
    safe = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/rolling_mill_slowdown")
    assert safe.status_code == 200
    assert safe.json()["incident"] is not None
    assert safe.json()["recovery_plan"]["status"] == "RECOVERING"
    from app.acamis.service import advance_recovery, status
    sim = manager.get_simulation(sim_id)
    sim.tick = sim.acamis_recovery_tick - 1
    advance_recovery(sim)
    assert sim.acamis_scenario == "rolling_mill_slowdown"
    sim.tick += 1
    advance_recovery(sim)
    assert status(sim)["incident"] is None
    assert status(sim)["recovery_plan"]["status"] == "RECOVERED"
    assert sim.get_snapshot().acamis_impact["state"] == "RECOVERED"

    critical = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/furnace_instability")
    assert critical.status_code == 200
    assert critical.json()["plant_health"] == "STABILIZED"
    assert critical.json()["incident"]["contained"] is True
    assert critical.json()["recovery_plan"]["status"] == "HUMAN_VERIFICATION_REQUIRED"
    assert critical.json()["audit"][0]["event"] == "HUMAN_VERIFICATION_REQUESTED"
    blocked = client.post(f"/api/simulations/{sim_id}/acamis/procedures/reduce_heat_load")
    assert blocked.status_code == 409
    assert "Human verification" in blocked.json()["detail"]
    approved = client.post(
        f"/api/simulations/{sim_id}/acamis/procedures/stabilize_furnace",
        json={"human_verified": True},
    )
    assert approved.status_code == 200
    assert approved.json()["plant_health"] == "NORMAL"
    assert approved.json()["recovery_plan"]["status"] == "RECOVERED"
    assert any(item["event"] == "HUMAN_VERIFICATION_CONFIRMED" for item in approved.json()["audit"])


def test_switching_to_autonomous_re_evaluates_existing_incident():
    sim_id = create_running_tmt_simulation()
    injected = client.post(f"/api/simulations/{sim_id}/acamis/scenarios/furnace_instability")
    assert injected.json()["plant_health"] == "INCIDENT"

    autonomous = client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "AUTONOMOUS_SIMULATION"})
    assert autonomous.status_code == 200
    data = autonomous.json()
    assert data["plant_health"] == "STABILIZED"
    assert data["incident"]["contained"] is True
    assert [item["event"] for item in data["audit"][:2]] == ["HUMAN_VERIFICATION_REQUESTED", "AUTONOMOUS_CONTAINMENT_EXECUTED"]


def test_advisory_human_approval_completes_high_risk_repair():
    sim_id = create_running_tmt_simulation()
    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/furnace_instability")
    client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "ADVISORY"})
    repaired = client.post(f"/api/simulations/{sim_id}/acamis/procedures/stabilize_furnace")
    assert repaired.status_code == 200
    assert repaired.json()["incident"] is None
    assert repaired.json()["plant_health"] == "NORMAL"
    assert repaired.json()["recovery_plan"]["status"] == "RECOVERED"


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

    client.post(f"/api/simulations/{sim_id}/acamis/scenarios/rolling_mill_slowdown")
    automatic = client.post(f"/api/simulations/{sim_id}/acamis/autonomy", json={"mode": "AUTONOMOUS_SIMULATION"})
    assert automatic.status_code == 200
    assert automatic.json()["model_advisory"]["reply"] == "Advisory review complete."
    assert automatic.json()["model_advisory"]["trigger"] == "AUTONOMY_ENABLED"
    assert automatic.json()["audit"][0]["event"] == "MODEL_AUTONOMOUS_REVIEW_RECEIVED"

    reviewed = client.post(f"/api/simulations/{sim_id}/acamis/model/chat", json={"message": "Assess the incident"})
    assert reviewed.status_code == 200
    assert reviewed.json() == {"reply": "Advisory review complete.", "provider": "OPENAI_COMPATIBLE", "model": "test-model", "advisory_only": True}
    assert "CONTEXT:" in requests[-1][1]["payload"]["messages"][1]["content"]
    assert "secret-value" not in requests[-1][1]["payload"]["messages"][1]["content"]

    disconnected = client.post(f"/api/simulations/{sim_id}/acamis/model/disconnect")
    assert disconnected.status_code == 200
    assert disconnected.json()["model_gateway"]["configured"] is False


def test_gemini_connection_replaces_retired_model_and_uses_generate_content(monkeypatch):
    sim_id = create_running_tmt_simulation()
    requests = []

    def fake_provider_request(url, **kwargs):
        requests.append((url, kwargs))
        if kwargs.get("method") == "POST":
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "Residual risk is low."}]}}
                ],
            }
        return {
            "models": [
                {"name": "models/gemini-3.6-flash", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/text-embedding-005", "supportedGenerationMethods": ["embedContent"]},
            ]
        }

    monkeypatch.setattr("app.acamis.model_gateway._request_json", fake_provider_request)
    connected = client.post(f"/api/simulations/{sim_id}/acamis/model/connect", json={
        "provider": "GEMINI",
        "model": "models/gemini-2.5-flash",
        "api_key": "transient-secret",
    })
    assert connected.status_code == 200
    gateway = connected.json()
    assert gateway["model"] == "gemini-3.6-flash"
    assert gateway["transport"] == "GENERATE_CONTENT"
    assert gateway["available_models"] == ["gemini-3.6-flash"]
    assert "selected gemini-3.6-flash" in gateway["message"]
    assert "api_key" not in gateway

    reviewed = client.post(f"/api/simulations/{sim_id}/acamis/model/chat", json={"message": "Review recovery"})
    assert reviewed.status_code == 200
    assert reviewed.json()["reply"] == "Residual risk is low."
    assert requests[-1][0].endswith("/models/gemini-3.6-flash:generateContent")
    payload = requests[-1][1]["payload"]
    assert payload["generationConfig"]["temperature"] == 0.2
    assert "systemInstruction" in payload
    assert "CONTEXT:" in payload["contents"][0]["parts"][0]["text"]
    assert "transient-secret" not in payload["contents"][0]["parts"][0]["text"]
