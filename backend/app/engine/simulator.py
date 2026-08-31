import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone

from app.models.schemas import (
    SimulationStatus, SimulationEvent, EventType, EventSeverity,
    SimulationConfiguration, SimulationState, SimulationSnapshot
)

class SteelSimEngine:
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
        self.speed = "1x"
        self.status = SimulationStatus.READY
        self.events: list[SimulationEvent] = []
        
        self._task = None
        self._tick_step = 1  # 1 simulated second per tick
        
        self._add_event(
            EventType.SIMULATION_CREATED,
            EventSeverity.INFO,
            "SimulationEngine",
            f"Simulation {self.id} created with seed {self.seed}"
        )

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
        return event

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
            speed=self.speed,
            status=self.status,
            configuration=self.config,
            events=self.events
        )

    def get_snapshot(self) -> SimulationSnapshot:
        return SimulationSnapshot(
            simulation_id=self.id,
            simulation_time=self.current_time.isoformat(),
            elapsed_seconds=self.elapsed_seconds,
            status=self.status,
            speed=self.speed,
            tick=self.tick,
            seed=self.seed,
            system_health="NORMAL"
        )

    def start(self):
        if self.status not in (SimulationStatus.READY, SimulationStatus.PAUSED):
            raise ValueError(f"Cannot start from {self.status}")
        
        event_type = EventType.SIMULATION_STARTED if self.status == SimulationStatus.READY else EventType.SIMULATION_RESUMED
        self.status = SimulationStatus.RUNNING
        self._add_event(event_type, EventSeverity.INFO, "SimulationControl", "Simulation started")
        
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())

    def pause(self):
        if self.status != SimulationStatus.RUNNING:
            raise ValueError(f"Cannot pause from {self.status}")
        
        self.status = SimulationStatus.PAUSED
        self._add_event(EventType.SIMULATION_PAUSED, EventSeverity.INFO, "SimulationControl", "Simulation paused")
        
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
        
        self.events.clear()
        self._add_event(EventType.SIMULATION_RESET, EventSeverity.INFO, "SimulationControl", "Simulation reset to initial state")

    def set_speed(self, speed: str):
        valid_speeds = ["1x", "5x", "10x", "60x", "MAX"]
        if speed not in valid_speeds:
            raise ValueError(f"Invalid speed: {speed}")
        
        self.speed = speed
        self._add_event(EventType.SIMULATION_SPEED_CHANGED, EventSeverity.INFO, "SimulationControl", f"Speed changed to {speed}")

    async def _run_loop(self):
        speed_map = {
            "1x": 1.0,
            "5x": 5.0,
            "10x": 10.0,
            "60x": 60.0
        }
        
        try:
            while self.status == SimulationStatus.RUNNING:
                # Calculate sleep time based on speed
                if self.speed == "MAX":
                    sleep_time = 0.0
                else:
                    mult = speed_map.get(self.speed, 1.0)
                    sleep_time = 1.0 / mult
                
                # Advance simulation by 1 step
                self.tick += 1
                self.elapsed_seconds += self._tick_step
                self.current_time += timedelta(seconds=self._tick_step)
                
                # Sleep to match real-time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    # In MAX mode, yield event loop every 100 ticks to not block API completely
                    if self.tick % 100 == 0:
                        await asyncio.sleep(0)
                        
        except asyncio.CancelledError:
            pass
