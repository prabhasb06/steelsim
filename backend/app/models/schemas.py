from enum import Enum
from typing import Any, Dict
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
            data = data.copy()
            if "plant_graph" in data and "plant" not in data:
                data["plant"] = data["plant_graph"]
            data.pop("plant_graph", None)
        return data

class NodeTelemetry(BaseModel):
    id: str
    status: str
    power_kw: float = 0.0
    power_mw: float = 0.0
    water_m3h: float = 0.0
    temperature_c: float = 25.0
    throughput_tph: float = 0.0

class PlantSummary(BaseModel):
    total_power_kw: float = 0.0
    total_power_mw: float = 0.0
    total_water_m3h: float = 0.0
    active_nodes: int = 0
    interlocked_nodes: int = 0
    total_nodes: int = 0

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
    state_version: int = 0
    seed: int
    system_health: str = "NORMAL"
    node_telemetry: Dict[str, NodeTelemetry] = Field(default_factory=dict)
    plant_summary: PlantSummary = Field(default_factory=PlantSummary)
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
    state_version: int = 0
    speed: str
    status: SimulationStatus
    configuration: SimulationConfiguration
    events: list[SimulationEvent] = Field(default_factory=list)
    node_telemetry: Dict[str, NodeTelemetry] = Field(default_factory=dict)
    plant_summary: PlantSummary = Field(default_factory=PlantSummary)

class ChangeSpeedRequest(BaseModel):
    speed: str
