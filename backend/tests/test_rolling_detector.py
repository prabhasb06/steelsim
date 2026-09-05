from app.acamis import detector, service
from app.engine.simulator import SteelSimEngine
from app.models.schemas import SimulationConfiguration, SimulationStatus
from fastapi.testclient import TestClient
from main import app
import pytest


def plant_engine():
    plant = TestClient(app).get('/api/plant/template/tmt').json()
    sim = SteelSimEngine(SimulationConfiguration(plant=plant))
    sim.status = SimulationStatus.RUNNING
    sim._calculate_telemetry()
    return sim


def tick(sim, count=1):
    for _ in range(count):
        sim.tick += 1
        sim._calculate_telemetry()
        detector.evaluate(sim)
        service.advance_recovery(sim)


def test_normal_and_transient_fluctuations_do_not_trigger():
    sim = plant_engine()
    tick(sim, 70)
    assert sim.acamis_scenario is None
    service.start_telemetry_demo(sim)
    tick(sim)
    assert sim.rolling_monitor['state'] == 'Watching'
    sim.rolling_disturbance.clear()
    tick(sim, 5)
    assert sim.acamis_scenario is None


def test_persistent_raw_measurements_detect_without_scenario_or_demo_flag():
    sim = plant_engine()
    mill = next(n.id for n in sim.config.plant.nodes if n.component_class.value == 'ROLLING_MILL')
    for _ in range(3):
        sim.tick += 1
        sim._calculate_telemetry()
        sim.node_telemetry[mill]['throughput_tph'] *= 0.5
        detector.evaluate(sim)
    assert sim.acamis_scenario == detector.INCIDENT
    evidence = sim.rolling_monitor['evidence'][0]
    assert evidence['equipment_id'] == mill
    assert evidence['deviation_percent'] == 50
    assert evidence['first_detected_tick'] == 1
    assert evidence['persistence_count'] == 3
    tick(sim, 8)
    assert len([a for a in sim.acamis_audit if a['event'] == 'TELEMETRY_ANOMALY_DETECTED']) == 1
    assert not sim.acamis_model_config


def test_autonomous_recovery_pause_reset_and_history():
    sim = plant_engine()
    service.set_autonomy(sim, 'AUTONOMOUS_SIMULATION')
    service.start_telemetry_demo(sim)
    assert sim.acamis_scenario is None
    tick(sim, 3)
    assert sim.acamis_scenario == detector.INCIDENT
    assert sim.rolling_monitor['state'] == 'Recovering'
    assert sim.acamis_impact['equipment']
    deadline = sim.acamis_recovery_tick
    sim.status = SimulationStatus.PAUSED
    detector.evaluate(sim)
    service.advance_recovery(sim)
    assert sim.acamis_recovery_tick == deadline
    sim.status = SimulationStatus.RUNNING
    tick(sim, 12)
    assert sim.acamis_scenario is None
    assert sim.rolling_monitor['state'] == 'Recovered'
    assert sim.get_snapshot().acamis_impact['origin'] == 'Telemetry detector'
    assert sim.get_snapshot().acamis_impact['equipment']
    tick(sim, 10)
    assert len([a for a in sim.acamis_audit if a['event'] == 'AUTONOMOUS_RECOVERY_SCHEDULED']) == 1
    sim.reset()
    assert sim.rolling_monitor['state'] == 'Normal'
    assert sim.rolling_monitor['evidence'] == []
    assert not sim.rolling_disturbance


def test_observe_and_advisory_and_manual_priority():
    sim = plant_engine()
    service.start_telemetry_demo(sim)
    tick(sim, 6)
    assert sim.rolling_monitor['state'] == 'Detected'
    assert sim.acamis_recovery_tick is None
    service.set_autonomy(sim, 'ADVISORY')
    service.execute_procedure(sim, 'inspect_rolling_mill')
    assert sim.acamis_scenario is None
    service.inject_scenario(sim, 'furnace_instability')
    tick(sim, 5)
    assert sim.acamis_scenario == 'furnace_instability'
    assert service.status(sim)['recovery_plan']['status'] == 'HUMAN_VERIFICATION_REQUIRED'
    service.clear_scenario(sim)
    assert sim.rolling_monitor['evidence'] == []


def test_ready_and_missing_mills_do_not_detect():
    sim = SteelSimEngine(SimulationConfiguration())
    detector.evaluate(sim)
    assert sim.acamis_scenario is None
    sim.status = SimulationStatus.RUNNING
    tick(sim, 5)
    assert not detector.public_status(sim)['active']


def test_repeated_snapshot_and_pause_do_not_count_as_new_evidence():
    sim = plant_engine()
    service.start_telemetry_demo(sim)
    tick(sim)
    before = detector.public_status(sim)['equipment'][0]['persistence']
    for _ in range(10):
        detector.evaluate(sim)
    assert detector.public_status(sim)['equipment'][0]['persistence'] == before
    sim.status = SimulationStatus.PAUSED
    sim.tick += 1
    detector.evaluate(sim)
    assert detector.public_status(sim)['equipment'][0]['persistence'] == before
    service.clear_scenario(sim)
    assert sim.rolling_monitor['samples'] == {}


def test_configured_upstream_bottleneck_is_part_of_expected_baseline():
    sim = plant_engine()
    source = next(n for n in sim.config.plant.nodes if n.component_class.value == 'RAW_MATERIAL_STORAGE')
    for name in ('throughput', 'feed_capacity', 'dispatch'):
        if name in source.parameters:
            source.parameters[name].value = 5
    tick(sim, 10)
    assert sim.acamis_scenario is None
    row = detector.public_status(sim)['equipment'][0]
    assert row['actual_tph'] == row['expected_tph']
    assert row['expected_tph'] < 10


def test_skipped_samples_restart_persistence():
    sim = plant_engine()
    service.start_telemetry_demo(sim)
    tick(sim, 2)
    sim.tick += 10
    tick(sim)
    assert sim.acamis_scenario is None
    assert detector.public_status(sim)['equipment'][0]['persistence'] == 1
    tick(sim, 2)
    assert sim.acamis_scenario == detector.INCIDENT


def test_paused_repair_cannot_report_zero_throughput_as_recovery():
    sim = plant_engine()
    service.start_telemetry_demo(sim)
    tick(sim, 3)
    service.set_autonomy(sim, 'ADVISORY')
    sim.pause()
    with pytest.raises(ValueError, match='Resume'):
        service.execute_procedure(sim, 'inspect_rolling_mill')
    assert sim.acamis_scenario == detector.INCIDENT
    assert sim.rolling_disturbance
    assert sim.acamis_last_resolution is None


def test_mode_change_updates_monitor_state_without_waiting_for_tick():
    sim = plant_engine()
    service.start_telemetry_demo(sim)
    tick(sim, 3)
    assert service.set_autonomy(sim, 'AUTONOMOUS_SIMULATION')['automatic_monitoring']['state'] == 'Recovering'
    assert service.set_autonomy(sim, 'OBSERVE')['automatic_monitoring']['state'] == 'Detected'
