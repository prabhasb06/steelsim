import pytest
import asyncio
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from main import app
from app.engine.simulator import SteelSimEngine
from app.models.schemas import EventSeverity, EventType, SimulationConfiguration, SimulationStatus
from app.api.routes import manager
from app.manager.simulation_manager import SimulationManager

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    # Cleanup before and after each test
    manager._simulations.clear()
    yield
    for sim in list(manager._simulations.values()):
        if sim._task and not sim._task.done():
            sim._task.cancel()
    manager._simulations.clear()

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200

def test_create_simulation():
    res = client.post("/api/simulations", json={"seed": 42})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "READY"
    assert data["seed"] == 42
    assert "sim_" in data["id"]

def test_create_accepts_legacy_plant_graph_payload():
    res = client.post("/api/simulations", json={"plant_graph": {"nodes": [], "edges": []}})
    assert res.status_code == 200
    assert res.json()["configuration"]["plant"]["nodes"] == []

def test_optional_api_key_protects_http_and_websocket(monkeypatch):
    monkeypatch.setenv("STEELSIM_API_KEY", "investor-demo-secret")
    secured_client = TestClient(app)

    assert secured_client.get("/api/health").status_code == 200
    assert secured_client.get("/api/simulations").status_code == 401
    created = secured_client.post(
        "/api/simulations",
        json={"seed": 42},
        headers={"X-SteelSim-API-Key": "investor-demo-secret"},
    )
    assert created.status_code == 200

    sim_id = created.json()["id"]
    with pytest.raises(WebSocketDisconnect) as rejected:
        with secured_client.websocket_connect(f"/api/simulations/{sim_id}/stream"):
            pass
    assert rejected.value.code == 4401

    with secured_client.websocket_connect(
        f"/api/simulations/{sim_id}/stream",
        subprotocols=["steelsim", "steelsim-key.aW52ZXN0b3ItZGVtby1zZWNyZXQ"],
    ) as websocket:
        assert websocket.receive_json()["simulation_id"] == sim_id

def test_ready_to_running():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    res = client.post(f"/api/simulations/{sim_id}/start")
    assert res.status_code == 200
    assert res.json()["status"] == "RUNNING"

def test_running_to_paused():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    client.post(f"/api/simulations/{sim_id}/start")
    
    res = client.post(f"/api/simulations/{sim_id}/pause")
    assert res.status_code == 200
    assert res.json()["status"] == "PAUSED"

def test_paused_to_running():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    client.post(f"/api/simulations/{sim_id}/start")
    client.post(f"/api/simulations/{sim_id}/pause")
    
    res = client.post(f"/api/simulations/{sim_id}/resume")
    assert res.status_code == 200
    assert res.json()["status"] == "RUNNING"

def test_resume_endpoint_cannot_bypass_topology_gate():
    furnace = client.get("/api/plant/components/INDUCTION_FURNACE").json()
    sim_id = client.post(
        "/api/simulations",
        json={"plant": {"nodes": [furnace], "edges": []}},
    ).json()["id"]

    response = client.post(f"/api/simulations/{sim_id}/resume")

    assert response.status_code == 400
    assert "Cannot resume" in response.json()["detail"]

def test_reset():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    client.post(f"/api/simulations/{sim_id}/start")
    
    res = client.post(f"/api/simulations/{sim_id}/reset")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "READY"
    assert data["tick"] == 0
    assert data["elapsed_seconds"] == 0

def test_speed_change():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    res = client.post(f"/api/simulations/{sim_id}/speed", json={"speed": "60x"})
    assert res.status_code == 200
    assert res.json()["speed"] == "60x"

def test_invalid_transition():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    # Cannot pause from READY
    res = client.post(f"/api/simulations/{sim_id}/pause")
    assert res.status_code == 400

def test_unified_command_rejects_invalid_transition():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]

    res = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "pause", "payload": {}},
    )

    assert res.status_code == 409
    assert "Cannot pause" in res.json()["detail"]

def test_unified_resume_requires_paused_state():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]

    response = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "resume", "payload": {}},
    )

    assert response.status_code == 409
    assert "Cannot resume" in response.json()["detail"]

def test_unified_command_rejects_invalid_speed():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]

    res = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "set_speed", "payload": {"speed": "warp"}},
    )

    assert res.status_code == 409
    assert "Invalid speed" in res.json()["detail"]

@pytest.mark.asyncio
async def test_simulation_clock_advancement():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    # Set to MAX to advance immediately
    client.post(f"/api/simulations/{sim_id}/speed", json={"speed": "MAX"})
    client.post(f"/api/simulations/{sim_id}/start")
    
    await asyncio.sleep(0.1) # Yield to event loop
    client.post(f"/api/simulations/{sim_id}/pause")
    
    res = client.get(f"/api/simulations/{sim_id}/snapshot")
    assert res.json()["tick"] > 0
    assert res.json()["elapsed_seconds"] > 0
    assert res.json()["tick"] < 100

@pytest.mark.asyncio
async def test_pause_prevents_advancement():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    client.post(f"/api/simulations/{sim_id}/speed", json={"speed": "MAX"})
    client.post(f"/api/simulations/{sim_id}/start")
    await asyncio.sleep(0.05)
    client.post(f"/api/simulations/{sim_id}/pause")
    
    snap1 = client.get(f"/api/simulations/{sim_id}/snapshot").json()
    await asyncio.sleep(0.05)
    snap2 = client.get(f"/api/simulations/{sim_id}/snapshot").json()
    
    assert snap1["tick"] == snap2["tick"]

def test_reset_restores_initial():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    initial_time = res.json()["initial_time"]
    
    client.post(f"/api/simulations/{sim_id}/speed", json={"speed": "MAX"})
    client.post(f"/api/simulations/{sim_id}/start")
    client.post(f"/api/simulations/{sim_id}/reset")
    
    state = client.get(f"/api/simulations/{sim_id}/state").json()
    assert state["current_time"] == initial_time
    assert state["tick"] == 0

@pytest.mark.asyncio
async def test_seeded_reproducibility():
    plant = client.get("/api/plant/template/tmt").json()
    config = SimulationConfiguration(seed=99, plant=plant)
    sim_a = SteelSimEngine(config)
    sim_b = SteelSimEngine(config)
    for sim in (sim_a, sim_b):
        sim.status = SimulationStatus.RUNNING
        sim.tick = 17
        sim._calculate_telemetry()

    assert sim_a.node_telemetry == sim_b.node_telemetry
    assert sim_a.plant_summary == sim_b.plant_summary

def test_tmt_telemetry_uses_catalogue_engineering_values():
    plant = client.get("/api/plant/template/tmt").json()
    sim_id = client.post("/api/simulations", json={"plant": plant}).json()["id"]
    snapshot = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "start", "payload": {}},
    ).json()
    node_by_class = {node["component_class"]: node["id"] for node in plant["nodes"]}

    furnace = snapshot["node_telemetry"][node_by_class["REHEATING_FURNACE"]]
    induction_furnace = snapshot["node_telemetry"][node_by_class["INDUCTION_FURNACE"]]
    tmt_cooling = snapshot["node_telemetry"][node_by_class["TMT_QUENCHING_BOX"]]
    substation = snapshot["node_telemetry"][node_by_class["UTILITY_SUBSTATION"]]

    assert induction_furnace["power_kw"] > 11000
    assert furnace["temperature_c"] > 1100
    assert tmt_cooling["water_m3h"] > 140
    assert substation["throughput_tph"] == 0
    assert snapshot["plant_summary"]["total_power_mw"] > 17

def test_event_history_is_bounded():
    sim = SteelSimEngine(SimulationConfiguration())
    for index in range(sim.MAX_EVENTS + 25):
        sim._add_event(
            EventType.SIMULATION_SPEED_CHANGED,
            EventSeverity.INFO,
            "test",
            f"event {index}",
        )

    assert len(sim.events) == sim.MAX_EVENTS
    assert sim.events[0].message == "event 25"

def test_multiple_simulation_isolation():
    res1 = client.post("/api/simulations", json={"seed": 1})
    res2 = client.post("/api/simulations", json={"seed": 2})
    
    id1 = res1.json()["id"]
    id2 = res2.json()["id"]
    
    client.post(f"/api/simulations/{id1}/start")
    
    assert client.get(f"/api/simulations/{id1}").json()["status"] == "RUNNING"
    assert client.get(f"/api/simulations/{id2}").json()["status"] == "READY"

def test_delete_simulation_releases_manager_entry():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]

    deleted = client.delete(f"/api/simulations/{sim_id}")

    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True
    assert client.get(f"/api/simulations/{sim_id}").status_code == 404

def test_manager_evicts_oldest_inactive_simulation_at_capacity():
    small_manager = SimulationManager(max_simulations=2)
    first = small_manager.create_simulation(SimulationConfiguration(seed=1))
    second = small_manager.create_simulation(SimulationConfiguration(seed=2))
    third = small_manager.create_simulation(SimulationConfiguration(seed=3))

    assert small_manager.get_simulation(first.id) is None
    assert small_manager.get_simulation(second.id) is not None
    assert small_manager.get_simulation(third.id) is not None

def test_event_generation():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    client.post(f"/api/simulations/{sim_id}/start")
    client.post(f"/api/simulations/{sim_id}/pause")
    
    events = client.get(f"/api/simulations/{sim_id}/events").json()
    types = [e["type"] for e in events]
    assert "SIMULATION_CREATED" in types
    assert "SIMULATION_STARTED" in types
    assert "SIMULATION_PAUSED" in types

def test_api_errors():
    res = client.get("/api/simulations/invalid_id")
    assert res.status_code == 404
    
    res = client.post("/api/simulations/invalid_id/start")
    assert res.status_code == 404

def test_snapshot_correctness():
    res = client.post("/api/simulations", json={"seed": 42})
    sim_id = res.json()["id"]
    
    snap = client.get(f"/api/simulations/{sim_id}/snapshot").json()
    assert snap["simulation_id"] == sim_id
    assert snap["status"] == "READY"
    assert "system_health" in snap

def test_investor_baseline_contains_melt_shop_and_utilities():
    plant = client.get("/api/plant/template/tmt").json()
    classes = {node["component_class"] for node in plant["nodes"]}

    assert len(plant["nodes"]) == 10
    assert {
        "INDUCTION_FURNACE",
        "LADLE_REFINING_FURNACE",
        "CONTINUOUS_CASTING_MACHINE",
        "ROLLING_MILL",
        "TMT_QUENCHING_BOX",
        "UTILITY_SUBSTATION",
        "WATER_COOLING_SYSTEM",
    }.issubset(classes)
    validation = client.post("/api/plant/validate", json=plant).json()
    assert validation["is_valid"]
    assert validation["issues"] == []

def test_material_flow_is_bounded_by_upstream_output():
    plant = client.get("/api/plant/template/tmt").json()
    for node in plant["nodes"]:
        if node["component_class"] == "RAW_MATERIAL_STORAGE":
            node["parameters"]["dispatch"]["value"] = 20

    sim_id = client.post("/api/simulations", json={"plant": plant}).json()["id"]
    snapshot = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "start", "payload": {}},
    ).json()
    material_rates = [
        snapshot["node_telemetry"][node["id"]]["throughput_tph"]
        for node in plant["nodes"]
        if node["component_class"] not in {"UTILITY_SUBSTATION", "WATER_COOLING_SYSTEM"}
    ]

    assert material_rates[0] > 0
    assert all(rate <= material_rates[0] for rate in material_rates[1:])

def test_backend_blocks_invalid_non_empty_topology():
    furnace = client.get("/api/plant/components/INDUCTION_FURNACE").json()
    sim_id = client.post(
        "/api/simulations",
        json={"plant": {"nodes": [furnace], "edges": []}},
    ).json()["id"]

    response = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "start", "payload": {}},
    )

    assert response.status_code == 409
    assert "topology" in response.json()["detail"].lower()

def test_snapshot_history_records_authoritative_changes():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]
    client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "set_speed", "payload": {"speed": "5x"}},
    )

    history = client.get(f"/api/simulations/{sim_id}/snapshots").json()

    assert len(history) == 1
    assert history[0]["speed"] == "5x"
    assert history[0]["state_version"] == 1

def test_state_version_remains_monotonic_across_reset():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]
    changed = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "set_speed", "payload": {"speed": "5x"}},
    ).json()
    reset = client.post(
        f"/api/simulations/{sim_id}/command",
        json={"command": "reset", "payload": {}},
    ).json()

    assert reset["state_version"] > changed["state_version"]

def test_websocket_stream_sends_initial_and_changed_snapshot():
    sim_id = client.post("/api/simulations", json={"seed": 42}).json()["id"]

    with client.websocket_connect(f"/api/simulations/{sim_id}/stream") as websocket:
        initial = websocket.receive_json()
        client.post(
            f"/api/simulations/{sim_id}/command",
            json={"command": "set_speed", "payload": {"speed": "5x"}},
        )
        changed = websocket.receive_json()

    assert initial["state_version"] == 0
    assert changed["state_version"] == 1
    assert changed["speed"] == "5x"
