import asyncio
import uuid
import random
from collections import deque
from datetime import datetime, timedelta, timezone

from app.models.schemas import (
    SimulationStatus, SimulationEvent, EventType, EventSeverity,
    SimulationConfiguration, SimulationState, SimulationSnapshot
)

class SteelSimEngine:
    MAX_EVENTS = 500
    MAX_TICKS_PER_SECOND = 240.0

    def __init__(self, config: SimulationConfiguration):
        self.id = f"sim_{uuid.uuid4().hex[:8]}"
        self.name = config.name
        self.created_at = datetime.now(timezone.utc)
        self.config = config
        self.seed = config.seed
        self.rng = random.Random(self.seed)
        
        self.initial_time = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        self.current_time = self.initial_time
        
        self.elapsed_seconds = 0
        self.tick = 0
        self.state_version = 0
        self.speed = "1x"
        self.status = SimulationStatus.READY
        self.events: list[SimulationEvent] = []
        self.acamis_scenario: str | None = None
        self.acamis_autonomy = "OBSERVE"
        self.acamis_mitigations: set[str] = set()
        self.acamis_audit: list[dict] = []
        self.acamis_last_resolution: dict | None = None
        self.acamis_model_config: dict | None = None
        self.acamis_last_model_advisory: dict | None = None
        
        self._task = None
        self._tick_step = 1  # 1 simulated second per tick
        self._subscribers: set[asyncio.Queue] = set()
        self._snapshots: deque[SimulationSnapshot] = deque(maxlen=120)
        
        self.node_telemetry: dict = {}
        self.plant_summary: dict = {
            "total_power_kw": 0.0,
            "total_power_mw": 0.0,
            "total_water_m3h": 0.0,
            "active_nodes": 0,
            "interlocked_nodes": 0,
            "total_nodes": len(self.config.plant.nodes) if self.config.plant else 0
        }
        self._calculate_telemetry()
        
        self._add_event(
            EventType.SIMULATION_CREATED,
            EventSeverity.INFO,
            "SimulationEngine",
            f"Simulation {self.id} created with seed {self.seed}"
        )

    def _calculate_telemetry(self):
        """Calculate deterministic per-node telemetry and plant-wide summary."""
        is_running = self.status == SimulationStatus.RUNNING
        phase = self.tick % 60
        load_factor = 0.92 + ((phase % 7) * 0.02) if is_running else 0.0
        if "reduce_heat_load" in self.acamis_mitigations:
            load_factor *= 0.78

        # Defaults cover only values that are intentionally not exposed as
        # configurable catalogue parameters. Configured engineering values
        # always take precedence.
        defaults = {
            "RAW_MATERIAL_STORAGE": {"power_kw": 15.0, "temp": 30.0},
            "INDUCTION_FURNACE": {"power_kw": 12500.0, "water": 120.0, "temp": 1620.0},
            "LADLE_REFINING_FURNACE": {"power_kw": 3200.0, "water": 45.0, "temp": 1580.0},
            "CONTINUOUS_CASTING_MACHINE": {"power_kw": 450.0, "water": 90.0, "temp": 1150.0},
            "ROLLING_MILL": {"power_kw": 2800.0, "water": 60.0, "temp": 1050.0},
            "TMT_QUENCHING_BOX": {"power_kw": 75.0, "water": 150.0, "temp": 580.0},
            "UTILITY_SUBSTATION": {"power_kw": 0.0, "temp": 45.0},
            "WATER_COOLING_SYSTEM": {"power_kw": 120.0, "temp": 32.0},
            "BILLET_YARD": {"power_kw": 35.0, "temp": 30.0},
            "CHARGING_TABLE": {"power_kw": 45.0, "temp": 35.0},
            "ROUGHING_MILL": {"water": 60.0, "temp": 1050.0},
            "INTERMEDIATE_MILL": {"water": 40.0, "temp": 930.0},
            "FINISHING_MILL": {"water": 35.0, "temp": 850.0},
            "TMT_COOLING": {"power_kw": 75.0, "temp": 580.0},
            "COOLING_BED": {"power_kw": 95.0, "temp": 150.0},
            "CUTTING_UNIT": {"power_kw": 120.0, "temp": 80.0},
            "BUNDLING_UNIT": {"power_kw": 55.0, "temp": 45.0},
            "WEIGHING": {"power_kw": 5.0, "temp": 30.0},
            "FINISHED_GOODS": {"power_kw": 10.0, "temp": 30.0},
            "TRANSFORMER": {"power_kw": 20.0, "temp": 45.0},
            "WATER_SYSTEM": {"power_kw": 25.0, "temp": 32.0},
            "COMPRESSOR": {"power_kw": 120.0, "temp": 50.0},
        }

        telemetry = {}
        nodes = self.config.plant.nodes if self.config.plant else []
        electrical_consumers = {
            edge.target_node for edge in self.config.plant.edges
            if edge.connection_type.value == "ELECTRICAL"
        } if self.config.plant else set()
        water_consumers = {
            edge.target_node for edge in self.config.plant.edges
            if edge.connection_type.value == "WATER"
        } if self.config.plant else set()
        material_sources: dict[str, list[str]] = {}
        material_targets: dict[str, list[str]] = {}
        if self.config.plant:
            for edge in self.config.plant.edges:
                if edge.connection_type.value == "MATERIAL":
                    material_sources.setdefault(edge.target_node, []).append(edge.source_node)
                    material_targets.setdefault(edge.source_node, []).append(edge.target_node)

        for n in nodes:
            c_class = n.component_class.value
            spec = defaults.get(c_class, {})
            params = n.parameters

            power_qty = params.get("power")
            if power_qty:
                rated_power_kw = power_qty.value * 1000.0 if power_qty.unit.upper() == "MW" else power_qty.value
            else:
                rated_power_kw = spec.get("power_kw", 0.0)

            water_qty = params.get("water_flow")
            rated_water = water_qty.value if water_qty else spec.get("water", 0.0)

            throughput_qty = next(
                (params[key] for key in ("throughput", "feed_capacity", "dispatch") if key in params),
                None,
            )
            rated_throughput = throughput_qty.value if throughput_qty else 0.0

            temperature_qty = params.get("temperature")
            rated_temperature = temperature_qty.value if temperature_qty else spec.get("temp", 25.0)

            needs_power = any(
                port.type.value == "ELECTRICAL" and port.direction.value == "IN"
                for port in n.ports
            )
            needs_water = any(
                port.type.value == "WATER" and port.direction.value == "IN"
                for port in n.ports
            )
            utilities_ready = (
                (not needs_power or n.id in electrical_consumers)
                and (not needs_water or n.id in water_consumers)
            )
            status_str = "IDLE"
            if is_running:
                status_str = "RUNNING" if utilities_ready else "INTERLOCKED"

            operating = status_str == "RUNNING"
            pwr = round(rated_power_kw * load_factor, 1) if operating else 0.0
            wat = round(rated_water * (0.95 + (phase % 4) * 0.02), 1) if operating else 0.0
            temp = round(rated_temperature + (phase % 5) - 2.0, 1) if operating else 25.0
            if self.acamis_scenario == "furnace_instability" and "FURNACE" in c_class and operating:
                temp += 85.0
                pwr = round(pwr * 1.15, 1)
            if self.acamis_scenario == "cooling_water_degradation" and rated_water > 0 and operating:
                temp += 42.0 if "activate_standby_cooling" not in self.acamis_mitigations else 8.0
            if self.acamis_scenario == "substation_capacity_constraint" and operating:
                pwr = round(pwr * 1.18, 1)

            telemetry[n.id] = {
                "id": n.id,
                "status": status_str,
                "power_kw": pwr,
                "power_mw": round(pwr / 1000.0, 2),
                "water_m3h": wat,
                "temperature_c": temp,
                "throughput_tph": 0.0,
                "rated_throughput_tph": rated_throughput,
            }

        # Material flow is evaluated in topological order so every downstream
        # rate is bounded by both its own capacity and actual upstream output.
        node_map = {node.id: node for node in nodes}
        in_degree = {node.id: len(material_sources.get(node.id, [])) for node in nodes}
        queue = [node.id for node in nodes if in_degree[node.id] == 0]
        flow_order: list[str] = []
        while queue:
            node_id = queue.pop(0)
            flow_order.append(node_id)
            for target_id in material_targets.get(node_id, []):
                in_degree[target_id] -= 1
                if in_degree[target_id] == 0:
                    queue.append(target_id)
        flow_order.extend(node.id for node in nodes if node.id not in flow_order)

        for node_id in flow_order:
            n = node_map[node_id]
            node_telemetry = telemetry[n.id]
            if node_telemetry["status"] != "RUNNING":
                continue
            has_material_input = any(
                port.type.value == "MATERIAL" and port.direction.value == "IN"
                for port in n.ports
            )
            rated_rate = node_telemetry["rated_throughput_tph"] * load_factor
            if self.acamis_scenario == "rolling_mill_slowdown" and "MILL" in n.component_class.value:
                rated_rate *= 0.45
            if self.acamis_scenario == "raw_material_disruption" and not has_material_input:
                rated_rate *= 0.35
            if "pace_upstream_material" in self.acamis_mitigations and not has_material_input:
                rated_rate *= 0.8
            if not has_material_input:
                node_telemetry["throughput_tph"] = round(rated_rate, 1)
                continue

            available_upstream = 0.0
            for source_id in material_sources.get(n.id, []):
                source_rate = telemetry.get(source_id, {}).get("throughput_tph", 0.0)
                sibling_ids = material_targets.get(source_id, [])
                sibling_demand = sum(
                    telemetry.get(target_id, {}).get("rated_throughput_tph", 0.0) * load_factor
                    for target_id in sibling_ids
                )
                if sibling_demand > 0 and rated_rate > 0:
                    available_upstream += source_rate * (rated_rate / sibling_demand)
                elif sibling_ids:
                    available_upstream += source_rate / len(sibling_ids)

            capacity = rated_rate if rated_rate > 0 else available_upstream
            actual_rate = min(capacity, available_upstream)
            if actual_rate > 0:
                node_telemetry["throughput_tph"] = round(actual_rate, 1)
            else:
                node_telemetry.update({
                    "status": "INTERLOCKED",
                    "power_kw": 0.0,
                    "power_mw": 0.0,
                    "water_m3h": 0.0,
                    "temperature_c": 25.0,
                })

        for node_telemetry in telemetry.values():
            node_telemetry.pop("rated_throughput_tph", None)

        operating_nodes = [item for item in telemetry.values() if item["status"] == "RUNNING"]
        total_power = sum(item["power_kw"] for item in operating_nodes)
        total_water = sum(item["water_m3h"] for item in operating_nodes)
        active_count = len(operating_nodes)
        interlocked_count = sum(1 for item in telemetry.values() if item["status"] == "INTERLOCKED")

        self.node_telemetry = telemetry
        self.plant_summary = {
            "total_power_kw": round(total_power, 1),
            "total_power_mw": round(total_power / 1000.0, 2),
            "total_water_m3h": round(total_water, 1),
            "active_nodes": active_count,
            "interlocked_nodes": interlocked_count,
            "total_nodes": len(nodes),
        }

    def _add_event(self, event_type: EventType, severity: EventSeverity, source: str, message: str):
        event = SimulationEvent(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            simulation_id=self.id,
            simulation_time=self.current_time.isoformat(),
            type=event_type,
            severity=severity,
            source=source,
            message=message,
        )
        self.events.append(event)
        if len(self.events) > self.MAX_EVENTS:
            del self.events[:-self.MAX_EVENTS]
        return event

    def _publish_snapshot(self) -> None:
        snapshot = self.get_snapshot()
        self._snapshots.append(snapshot)
        for queue in tuple(self._subscribers):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            queue.put_nowait(snapshot)

    def _state_changed(self) -> None:
        self.state_version += 1
        self._publish_snapshot()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=2)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    def get_snapshots(self) -> list[SimulationSnapshot]:
        return list(self._snapshots)

    def get_state(self) -> SimulationState:
        return SimulationState(
            id=self.id,
            name=self.name,
            created_at=self.created_at.isoformat(),
            seed=self.seed,
            initial_time=self.initial_time.isoformat(),
            current_time=self.current_time.isoformat(),
            elapsed_seconds=self.elapsed_seconds,
            tick=self.tick,
            state_version=self.state_version,
            speed=self.speed,
            status=self.status,
            configuration=self.config,
            events=self.events,
            node_telemetry=self.node_telemetry,
            plant_summary=self.plant_summary
        )

    def get_snapshot(self) -> SimulationSnapshot:
        return SimulationSnapshot(
            simulation_id=self.id,
            id=self.id,
            simulation_time=self.current_time.isoformat(),
            elapsed_seconds=self.elapsed_seconds,
            status=self.status,
            speed=self.speed,
            tick=self.tick,
            state_version=self.state_version,
            seed=self.seed,
            system_health="INCIDENT" if self.acamis_scenario else ("DEGRADED" if self.plant_summary["interlocked_nodes"] else "NORMAL"),
            node_telemetry=self.node_telemetry,
            plant_summary=self.plant_summary,
            events=self.events[-50:]  # Last 50 events for quick access
        )

    def start(self):
        if self.status not in (SimulationStatus.READY, SimulationStatus.PAUSED):
            raise ValueError(f"Cannot start from {self.status}")
        
        event_type = EventType.SIMULATION_STARTED if self.status == SimulationStatus.READY else EventType.SIMULATION_RESUMED
        self.status = SimulationStatus.RUNNING
        self._calculate_telemetry()
        self._add_event(event_type, EventSeverity.INFO, "SimulationControl", "Simulation started")
        self._state_changed()
        
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())

    def pause(self):
        if self.status != SimulationStatus.RUNNING:
            raise ValueError(f"Cannot pause from {self.status}")
        
        self.status = SimulationStatus.PAUSED
        self._calculate_telemetry()
        self._add_event(EventType.SIMULATION_PAUSED, EventSeverity.INFO, "SimulationControl", "Simulation paused")
        self._state_changed()
        
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None

    def reset(self):
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None
            
        self.status = SimulationStatus.READY
        self.current_time = self.initial_time
        self.elapsed_seconds = 0
        self.tick = 0
        self.speed = "1x"
        self.rng = random.Random(self.seed)
        self.acamis_scenario = None
        self.acamis_mitigations.clear()
        self.acamis_audit.clear()
        self.acamis_last_resolution = None
        self.acamis_last_model_advisory = None
        self._calculate_telemetry()
        
        self.events.clear()
        self._snapshots.clear()
        self._add_event(EventType.SIMULATION_RESET, EventSeverity.INFO, "SimulationControl", "Simulation reset to initial state")
        self._state_changed()

    def inject_acamis_scenario(self, scenario: str):
        self.acamis_scenario = scenario
        self.acamis_last_resolution = None
        self.acamis_mitigations.clear()
        self._calculate_telemetry()
        self._add_event(EventType.ACAMIS_SCENARIO_INJECTED, EventSeverity.WARNING, "ACAMIS Scenario Control", f"Injected deterministic scenario: {scenario}")
        self._state_changed()

    def clear_acamis_scenario(self):
        self.acamis_scenario = None
        self.acamis_mitigations.clear()
        self._calculate_telemetry()
        self._add_event(EventType.ACAMIS_SCENARIO_CLEARED, EventSeverity.INFO, "ACAMIS Scenario Control", "Cleared ACAMIS scenario and mitigations")
        self._state_changed()

    def apply_acamis_procedure(self, procedure: str):
        self.acamis_mitigations.add(procedure)
        self._calculate_telemetry()
        self._add_event(EventType.ACAMIS_PROCEDURE_APPLIED, EventSeverity.NOTICE, "ACAMIS Procedure Library", f"Applied approved simulated procedure: {procedure}")
        self._state_changed()

    def set_speed(self, speed: str):
        valid_speeds = ["1x", "5x", "10x", "60x", "MAX"]
        if speed not in valid_speeds:
            raise ValueError(f"Invalid speed: {speed}")
        
        self.speed = speed
        self._add_event(EventType.SIMULATION_SPEED_CHANGED, EventSeverity.INFO, "SimulationControl", f"Speed changed to {speed}")
        self._state_changed()

    async def _run_loop(self):
        speed_map = {
            "1x": 1.0,
            "5x": 5.0,
            "10x": 10.0,
            "60x": 60.0,
            "MAX": self.MAX_TICKS_PER_SECOND,
        }
        
        try:
            while self.status == SimulationStatus.RUNNING:
                # Calculate sleep time based on speed
                mult = speed_map.get(self.speed, 1.0)
                sleep_time = 1.0 / mult
                
                # Advance simulation by 1 step
                self.tick += 1
                self.elapsed_seconds += self._tick_step
                self.current_time += timedelta(seconds=self._tick_step)
                self._calculate_telemetry()
                self._state_changed()
                
                # Sleep to match real-time
                await asyncio.sleep(sleep_time)
                        
        except asyncio.CancelledError:
            pass
