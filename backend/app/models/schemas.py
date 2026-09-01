from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.topology import PlantGraph

class SimulationStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class EventSeverity(str, Enum):
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class EventType(str, Enum):
    SIMULATION_CREATED = "SIMULATION_CREATED"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_PAUSED = "SIMULATION_PAUSED"
    SIMULATION_RESUMED = "SIMULATION_RESUMED"
    SIMULATION_RESET = "SIMULATION_RESET"
    SIMULATION_SPEED_CHANGED = "SIMULATION_SPEED_CHANGED"
    SIMULATION_COMPLETED = "SIMULATION_COMPLETED"
    SIMULATION_ERROR = "SIMULATION_ERROR"

class SimulationConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = "SteelSim Default"
    seed: int = 42
    plant: PlantGraph = Field(default_factory=PlantGraph)

class SimulationEvent(BaseModel):
    id: str
    simulation_id: str
    simulation_time: str
    type: EventType
    severity: EventSeverity
    source: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SimulationSnapshot(BaseModel):
    simulation_id: str
    simulation_time: str
    elapsed_seconds: int
    status: SimulationStatus
    speed: str
    tick: int
    seed: int
    system_health: str = "NORMAL"

class SimulationState(BaseModel):
    id: str
    name: str
    created_at: str
    seed: int
    initial_time: str
    current_time: str
    elapsed_seconds: int
    tick: int
    speed: str
    status: SimulationStatus
    configuration: SimulationConfiguration
    events: list[SimulationEvent] = Field(default_factory=list)

class ChangeSpeedRequest(BaseModel):
    speed: str
