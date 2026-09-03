import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from app.engine.simulator import SteelSimEngine
from app.models.schemas import EventSeverity, EventType, SimulationConfiguration, SimulationStatus
from app.api.routes import manager

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
    tmt_cooling = snapshot["node_telemetry"][node_by_class["TMT_COOLING"]]
    transformer = snapshot["node_telemetry"][node_by_class["TRANSFORMER"]]

    assert furnace["power_kw"] > 2500
    assert furnace["temperature_c"] > 1100
    assert tmt_cooling["water_m3h"] > 170
    assert transformer["throughput_tph"] == 0
    assert snapshot["plant_summary"]["total_power_mw"] > 9

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
