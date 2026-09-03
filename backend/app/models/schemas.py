from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
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
    name: str = "SteelSim Default"
    seed: int = 42
    plant: PlantGraph = Field(default_factory=PlantGraph)

    @model_validator(mode="before")
    @classmethod
    def handle_plant_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "plant_graph" in data and "plant" not in data:
                data["plant"] = data["plant_graph"]
        return data

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
    id: str = ""
    simulation_time: str
    elapsed_seconds: int
    status: SimulationStatus
    speed: str
    tick: int
    seed: int
    system_health: str = "NORMAL"
    node_telemetry: Dict[str, Any] = Field(default_factory=dict)
    plant_summary: Dict[str, Any] = Field(default_factory=dict)
    events: list[SimulationEvent] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def set_id_fallback(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "id" not in data and "simulation_id" in data:
                data["id"] = data["simulation_id"]
            elif "simulation_id" not in data and "id" in data:
                data["simulation_id"] = data["id"]
        return data

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
    node_telemetry: Dict[str, Any] = Field(default_factory=dict)
    plant_summary: Dict[str, Any] = Field(default_factory=dict)

class ChangeSpeedRequest(BaseModel):
    speed: str
