import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.acamis import multivariate, service
from app.history import HistoryStore
from app.manager.simulation_manager import SimulationManager
from app.models.schemas import SimulationConfiguration, SimulationStatus
from main import app


@pytest.fixture
def setup_run(tmp_path):
    store = HistoryStore(tmp_path / 'history.sqlite3')
    manager = SimulationManager(history=store)
    plant = TestClient(app).get('/api/plant/template/tmt').json()
    sim = manager.create_simulation(SimulationConfiguration(plant=plant))
    sim.status = SimulationStatus.RUNNING
    sim._calculate_telemetry()
    return store, manager, sim


def measure(sim, domains=('thermal', 'electrical')):
    sim.tick += 1
    sim._calculate_telemetry()
    node = next(n.id for n in sim.config.plant.nodes if n.component_class.value == 'INDUCTION_FURNACE')
    if 'thermal' in domains:
        sim.node_telemetry[node]['temperature_c'] += 80
    if 'electrical' in domains:
        sim.node_telemetry[node]['power_kw'] *= 1.3
    if 'cooling' in domains:
        sim.node_telemetry[node]['water_m3h'] *= 0.4
    multivariate.evaluate(sim)
    return node


def test_normal_transient_persistent_and_correlated(setup_run):
    _, _, sim = setup_run
    for _ in range(8):
        measure(sim, ())
    assert not sim.signal_monitor['findings']
    measure(sim)
    measure(sim, ())
    assert not sim.signal_monitor['findings']
    for _ in range(3):
        asset = measure(sim)
    finding = sim.signal_monitor['findings'][0]
    assert finding['equipment_id'] == asset
    assert finding['correlated']
    assert {s['domain'] for s in finding['signals']} == {'thermal', 'electrical'}
    assert all(s['persistence'] == 3 for s in finding['signals'])
    assessment = service.status(sim)
    assert assessment['plant_health'] == 'DEGRADED'
    assert assessment['snapshot']['system_health'] == 'DEGRADED'
    assert assessment['recovery_plan']['status'] == 'SIGNAL_REVIEW_REQUIRED'
    assert next(item for item in assessment['specialist_findings'] if item['domain'] == 'Safety')['affected_equipment'] == [asset]
    assert next(item for item in assessment['specialist_findings'] if item['domain'] == 'Energy')['severity'] == 'HIGH'
    assert sim.acamis_scenario is None
    assert sim.acamis_recovery_tick is None
    assert not sim.acamis_model_config
    for _ in range(4):
        measure(sim)
    assert len([a for a in sim.acamis_audit if a['event'] == 'SIGNAL_INCIDENT_CHANGED']) == 1


def test_signal_review_case_lifecycle_and_api(setup_run, monkeypatch):
    store, manager, sim = setup_run
    from app.api import acamis, history
    monkeypatch.setattr(acamis, 'manager', manager)
    monkeypatch.setattr(history, 'manager', manager)
    client = TestClient(app)
    measure(sim, ('cooling',))
    measure(sim, ('cooling',))
    assert sim.signal_monitor['cases'] == []
    asset = measure(sim, ('cooling',))
    cases = sim.signal_monitor['cases']
    assert len(cases) == 1
    case = cases[0]
    assert case['equipment_id'] == asset
    assert case['domain'] == 'cooling'
    assert case['status'] == 'OPEN'
    assert case['first_tick'] == 1
    assert case['persistence'] == 3
    measure(sim, ('cooling',))
    assert len(cases) == 1

    route = f'/api/simulations/{sim.id}/acamis/signals/{case["id"]}/acknowledge'
    response = client.post(route)
    assert response.status_code == 200
    assert response.json()['signal_monitoring']['cases'][0]['status'] == 'ACKNOWLEDGED'
    assert sim.acamis_scenario is None
    assert sim.acamis_recovery_tick is None
    assert len([entry for entry in sim.acamis_audit if entry['event'] == 'SIGNAL_REVIEW_ACKNOWLEDGED']) == 1
    assert client.post(route).status_code == 200
    assert len([entry for entry in sim.acamis_audit if entry['event'] == 'SIGNAL_REVIEW_ACKNOWLEDGED']) == 1
    assert client.post(f'/api/simulations/{sim.id}/acamis/signals/missing/acknowledge').status_code == 409

    measure(sim, ())
    assert case['status'] == 'RESOLVED'
    assert case['resolved_tick'] == sim.tick
    assert service.status(sim)['recovery_plan']['status'] == 'MONITORING'
    assert client.post(route).status_code == 409
    for _ in range(3):
        measure(sim, ('cooling',))
    assert len(cases) == 2
    assert cases[-1]['status'] == 'OPEN'
    sim.persist_history()
    report = client.get(f'/api/history/runs/{sim.history_run_id}/report').json()
    assert len(report['signal_review_cases']) == 2
    assert store.detail(sim.history_run_id)['checkpoint']['signal_monitor']['cases'] == cases


def test_restore_migrates_legacy_signal_monitor(setup_run):
    store, manager, sim = setup_run
    source = sim.history_run_id
    with store.connect() as db:
        row = db.execute('SELECT checkpoint FROM runs WHERE id=?', (source,)).fetchone()
        checkpoint = json.loads(row['checkpoint'])
        checkpoint['signal_monitor'].pop('cases')
        checkpoint['signal_monitor']['version'] = 'signals.v1'
        db.execute('UPDATE runs SET checkpoint=? WHERE id=?', (json.dumps(checkpoint), source))
    restored = store.restore(source, manager)
    assert restored.signal_monitor['version'] == 'signals.v2'
    assert restored.signal_monitor['cases'] == []


def test_case_retention_never_discards_an_active_deviation(setup_run):
    _, _, sim = setup_run
    for _ in range(3):
        measure(sim, ('cooling',))
    active = sim.signal_monitor['cases'][0]
    sim.signal_monitor['cases'] = [active] + [
        {**active, 'id': f'old-{index}', 'status': 'RESOLVED', 'resolved_tick': index}
        for index in range(105)
    ]
    measure(sim, ('cooling',))
    retained = sim.signal_monitor['cases']
    assert len(retained) == multivariate.MAX_CASES
    assert len([case for case in retained if case['status'] != 'RESOLVED']) == 1
    assert retained[-1]['id'] == active['id']


def test_pause_clear_reset_and_signal_change(setup_run):
    _, _, sim = setup_run
    for _ in range(3):
        measure(sim, ('cooling',))
    assert sim.signal_monitor['findings']
    frozen = json.dumps(sim.signal_monitor)
    sim.status = SimulationStatus.PAUSED
    measure(sim)
    assert json.dumps(sim.signal_monitor) == frozen
    service.clear_scenario(sim)
    assert sim.signal_monitor == multivariate.initial_state()
    sim.status = SimulationStatus.RUNNING
    for _ in range(3):
        measure(sim)
    measure(sim, ('thermal',))
    assert not sim.signal_monitor['findings'][0]['correlated']
    sim.reset()
    assert sim.signal_monitor == multivariate.initial_state()


def test_durable_history_replay_secrets_restore_and_reset(setup_run):
    store, manager, sim = setup_run
    source = sim.history_run_id
    sim.acamis_model_config = {'api_key': 'DO-NOT-ARCHIVE', 'provider': 'GEMINI', 'model': 'test'}
    # Credentials must remain memory-only even when provider calls fail.
    sim.acamis_audit.append({'id': 'remote', 'event': 'MODEL_REVIEW_FAILED', 'detail': 'DO-NOT-ARCHIVE'})
    for _ in range(3):
        measure(sim)
        sim._state_changed()
    before = store.detail(source)['frame_count']
    sim.persist_history()
    assert store.detail(source)['frame_count'] == before
    manager.delete_simulation(sim.id)
    reopened = HistoryStore(store.path)
    assert len(reopened.runs()) == 1
    record = reopened.detail(source)
    assert 'DO-NOT-ARCHIVE' not in json.dumps(record)
    first = reopened.frames(source, limit=2)
    second = reopened.frames(source, after=first[-1]['seq'])
    assert second and second[0]['seq'] > first[-1]['seq']
    assert any(f['signals'] for f in first + second)
    restored = reopened.restore(source, manager)
    assert restored.status == SimulationStatus.PAUSED
    assert restored._task is None
    assert restored.tick == 3
    assert restored.initial_time == sim.initial_time
    assert restored.history_run_id != source
    assert not restored.acamis_model_config
    assert restored.signal_monitor['findings']
    assert store.detail(restored.history_run_id)['audit'][0]['event'] == 'RUN_RESTORED'
    restored.reset()
    assert len(store.runs()) == 3
    assert store.detail(source)['frame_count'] == before


def test_storage_failure_does_not_stop_simulation(setup_run, monkeypatch):
    store, _, sim = setup_run
    def fail(_):
        raise sqlite3.OperationalError('disk unavailable')
    monkeypatch.setattr(store, 'record', fail)
    sim._state_changed()
    assert sim.history_error
    assert sim.status == SimulationStatus.RUNNING


def test_history_routes_and_paused_restore(setup_run, monkeypatch):
    store, manager, sim = setup_run
    from app.api import history
    monkeypatch.setattr(history, 'manager', manager)
    client = TestClient(app)
    assert client.get('/api/history/runs?limit=501').status_code == 422
    assert client.get('/api/history/runs/missing').status_code == 404
    run = client.get('/api/history/runs').json()[0]['id']
    detail = client.get(f'/api/history/runs/{run}').json()
    assert 'checkpoint' not in detail
    assert client.get(f'/api/history/runs/{run}/report').json()['contract_version'] == 'operations-report.v1'
    restored = client.post(f'/api/history/runs/{run}/restore')
    assert restored.status_code == 200
    assert restored.json()['status'] == 'PAUSED'
