from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class QuantityCategory(str, Enum):
    MASS = "MASS"
    MASS_FLOW = "MASS_FLOW"
    TEMPERATURE = "TEMPERATURE"
    POWER = "POWER"
    ENERGY = "ENERGY"
    SPECIFIC_ENERGY = "SPECIFIC_ENERGY"
    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    PRESSURE = "PRESSURE"
    VOLUMETRIC_FLOW = "VOLUMETRIC_FLOW"
    NORMALIZED_GAS_FLOW = "NORMALIZED_GAS_FLOW"
    LINEAR_SPEED = "LINEAR_SPEED"
    ROTATIONAL_SPEED = "ROTATIONAL_SPEED"
    LENGTH = "LENGTH"
    TIME = "TIME"
    CAPACITY = "CAPACITY"
    PERCENTAGE = "PERCENTAGE"
    VIBRATION = "VIBRATION"
    COST = "COST"
    SPECIFIC_COST = "SPECIFIC_COST"

class EngineeringQuantity(BaseModel):
    value: float
    unit: str
    category: QuantityCategory
    display_name: str

class PortType(str, Enum):
    MATERIAL = "MATERIAL"
    ELECTRICAL = "ELECTRICAL"
    WATER = "WATER"
    SIGNAL = "SIGNAL"
    AIR = "AIR"

class PortDirection(str, Enum):
    IN = "IN"
    OUT = "OUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"

class ComponentClass(str, Enum):
    BILLET_YARD = "BILLET_YARD"
    CHARGING_TABLE = "CHARGING_TABLE"
    REHEATING_FURNACE = "REHEATING_FURNACE"
    ROUGHING_MILL = "ROUGHING_MILL"
    INTERMEDIATE_MILL = "INTERMEDIATE_MILL"
    FINISHING_MILL = "FINISHING_MILL"
    TMT_COOLING = "TMT_COOLING"
    COOLING_BED = "COOLING_BED"
    CUTTING_UNIT = "CUTTING_UNIT"
    BUNDLING_UNIT = "BUNDLING_UNIT"
    FINISHED_GOODS = "FINISHED_GOODS"
    TRANSFORMER = "TRANSFORMER"
    WATER_PUMP = "WATER_PUMP"
    RAW_MATERIAL_STORAGE = "RAW_MATERIAL_STORAGE"
    TRANSFER_CONVEYOR = "TRANSFER_CONVEYOR"
    ROLLER_CONVEYOR = "ROLLER_CONVEYOR"
    BUFFER = "BUFFER"
    WEIGHING = "WEIGHING"
    ELECTRICAL_SUPPLY = "ELECTRICAL_SUPPLY"
    WATER_SYSTEM = "WATER_SYSTEM"
    COMPRESSOR = "COMPRESSOR"
    MAINTENANCE_STATION = "MAINTENANCE_STATION"
    QUALITY_INSPECTION = "QUALITY_INSPECTION"

class PortDef(BaseModel):
    id: str
    type: PortType
    direction: PortDirection

class EquipmentNode(BaseModel):
    id: str
    component_class: ComponentClass
    name: str
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    ports: List[PortDef] = Field(default_factory=list)
    parameters: Dict[str, EngineeringQuantity] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConnectionEdge(BaseModel):
    id: str
    source_node: str
    source_port: str
    target_node: str
    target_port: str
    connection_type: PortType

class PlantGraph(BaseModel):
    nodes: List[EquipmentNode] = Field(default_factory=list)
    edges: List[ConnectionEdge] = Field(default_factory=list)


class AutoSetupProposal(BaseModel):
    new_edges: List[ConnectionEdge] = Field(default_factory=list)
    new_nodes: List[EquipmentNode] = Field(default_factory=list)
    missing_utilities: List[str] = Field(default_factory=list)
    validation: Any = None
    proposed_graph: Optional[PlantGraph] = None
