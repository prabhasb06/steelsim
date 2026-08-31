from app.models.topology import ComponentClass, EquipmentNode, PortDef, PortType, PortDirection, EngineeringQuantity, QuantityCategory
import uuid

TMT_SEQUENCE = [
    ComponentClass.RAW_MATERIAL_STORAGE,
    ComponentClass.BILLET_YARD,
    ComponentClass.CHARGING_TABLE,
    ComponentClass.REHEATING_FURNACE,
    ComponentClass.ROUGHING_MILL,
    ComponentClass.INTERMEDIATE_MILL,
    ComponentClass.FINISHING_MILL,
    ComponentClass.TMT_COOLING,
    ComponentClass.COOLING_BED,
    ComponentClass.CUTTING_UNIT,
    ComponentClass.BUNDLING_UNIT,
    ComponentClass.WEIGHING,
    ComponentClass.FINISHED_GOODS
]

def create_port(pid: str, ptype: PortType, direction: PortDirection) -> PortDef:
    return PortDef(id=pid, type=ptype, direction=direction)

def q_throughput(val=30.0): return EngineeringQuantity(value=val, unit="t/h", category=QuantityCategory.MASS_FLOW, display_name="Rated Throughput")
def q_power(val=2.0): return EngineeringQuantity(value=val, unit="MW", category=QuantityCategory.POWER, display_name="Motor Power")
def q_temp(val=1100.0): return EngineeringQuantity(value=val, unit="°C", category=QuantityCategory.TEMPERATURE, display_name="Target Temperature")
def q_util(val=80.0): return EngineeringQuantity(value=val, unit="%", category=QuantityCategory.PERCENTAGE, display_name="Utilization")
def q_water(val=150.0): return EngineeringQuantity(value=val, unit="m³/h", category=QuantityCategory.VOLUMETRIC_FLOW, display_name="Cooling Water Flow")
def q_pressure(val=10.0): return EngineeringQuantity(value=val, unit="bar", category=QuantityCategory.PRESSURE, display_name="Pressure")
def q_speed(val=5.0): return EngineeringQuantity(value=val, unit="m/s", category=QuantityCategory.LINEAR_SPEED, display_name="Line Speed")
def q_mass(val=500.0): return EngineeringQuantity(value=val, unit="t", category=QuantityCategory.MASS, display_name="Inventory")

COMPONENT_TEMPLATES = {
    ComponentClass.RAW_MATERIAL_STORAGE: {
        "name": "Raw Material Storage",
        "ports": [create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)],
        "params": {"inventory": q_mass(1000), "dispatch": q_throughput(25)}
    },
    ComponentClass.BILLET_YARD: {
        "name": "Billet Yard",
        "ports": [create_port("mat_in", PortType.MATERIAL, PortDirection.IN), create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)],
        "params": {"inventory": q_mass(500), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(25)}
    },
    ComponentClass.CHARGING_TABLE: {
        "name": "Charging Table",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"feed_capacity": q_throughput(25)}
    },
    ComponentClass.REHEATING_FURNACE: {
        "name": "Reheating Furnace",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "temperature": q_temp(1150), "power": q_power(2.8)}
    },
    ComponentClass.ROUGHING_MILL: {
        "name": "Roughing Mill",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN),
            create_port("water_in", PortType.WATER, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "power": q_power(2.4), "speed": q_speed(2.5)}
    },
    ComponentClass.INTERMEDIATE_MILL: {
        "name": "Intermediate Mill",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "power": q_power(3.0), "speed": q_speed(5.0)}
    },
    ComponentClass.FINISHING_MILL: {
        "name": "Finishing Mill",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "power": q_power(4.0), "speed": q_speed(12.0)}
    },
    ComponentClass.TMT_COOLING: {
        "name": "TMT Cooling",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("water_in", PortType.WATER, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "water_flow": q_water(180), "water_pressure": q_pressure(10.0)}
    },
    ComponentClass.COOLING_BED: {
        "name": "Cooling Bed",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"throughput": q_throughput(25), "buffer_capacity": q_mass(50)}
    },
    ComponentClass.CUTTING_UNIT: {
        "name": "Cutting Unit",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN)
        ],
        "params": {"throughput": q_throughput(25), "speed": q_speed(12.0)}
    },
    ComponentClass.BUNDLING_UNIT: {
        "name": "Bundling Unit",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"throughput": q_throughput(25)}
    },
    ComponentClass.WEIGHING: {
        "name": "Weighing Station",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("signal_out", PortType.SIGNAL, PortDirection.OUT)
        ],
        "params": {"throughput": q_throughput(25)}
    },
    ComponentClass.FINISHED_GOODS: {
        "name": "Finished Goods",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN)
        ],
        "params": {"inventory": q_mass(100), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(25)}
    },
    ComponentClass.ELECTRICAL_SUPPLY: {
        "name": "Electrical Grid",
        "ports": [
            create_port("elec_out", PortType.ELECTRICAL, PortDirection.OUT)
        ],
        "params": {"available_power": EngineeringQuantity(value=20.0, unit="MW", category=QuantityCategory.POWER, display_name="Available Power")}
    },
    ComponentClass.TRANSFORMER: {
        "name": "Transformer",
        "ports": [
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN),
            create_port("elec_out", PortType.ELECTRICAL, PortDirection.OUT)
        ],
        "params": {"rating": EngineeringQuantity(value=10.0, unit="MVA", category=QuantityCategory.POWER, display_name="Rating")}
    },
    ComponentClass.WATER_SYSTEM: {
        "name": "Water System",
        "ports": [
            create_port("water_out", PortType.WATER, PortDirection.OUT)
        ],
        "params": {"available_flow": EngineeringQuantity(value=200.0, unit="m³/h", category=QuantityCategory.VOLUMETRIC_FLOW, display_name="Available Flow")}
    },
    ComponentClass.WATER_PUMP: {
        "name": "Water Pump",
        "ports": [
            create_port("water_in", PortType.WATER, PortDirection.IN),
            create_port("water_out", PortType.WATER, PortDirection.OUT),
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN)
        ],
        "params": {"flow": EngineeringQuantity(value=100.0, unit="m³/h", category=QuantityCategory.VOLUMETRIC_FLOW, display_name="Flow"), "power": q_power(0.5)}
    },
    ComponentClass.COMPRESSOR: {
        "name": "Compressor",
        "ports": [
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN),
            create_port("air_out", PortType.AIR, PortDirection.OUT)
        ],
        "params": {"flow": EngineeringQuantity(value=500.0, unit="Nm³/h", category=QuantityCategory.NORMALIZED_GAS_FLOW, display_name="Air Flow")}
    },
    ComponentClass.MAINTENANCE_STATION: {
        "name": "Maintenance Station",
        "ports": [],
        "params": {}
    },
    ComponentClass.QUALITY_INSPECTION: {
        "name": "Quality Inspection",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("signal_out", PortType.SIGNAL, PortDirection.OUT)
        ],
        "params": {}
    },
    ComponentClass.TRANSFER_CONVEYOR: {
        "name": "Transfer Conveyor",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"throughput": q_throughput(25), "speed": q_speed(1.0)}
    },
    ComponentClass.ROLLER_CONVEYOR: {
        "name": "Roller Conveyor",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"throughput": q_throughput(25), "speed": q_speed(1.0)}
    },
    ComponentClass.BUFFER: {
        "name": "Buffer",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ],
        "params": {"buffer_capacity": q_mass(20)}
    }
}

def create_equipment_node(c_class: ComponentClass, x: float = 0.0, y: float = 0.0) -> EquipmentNode:
    tpl = COMPONENT_TEMPLATES[c_class]
    return EquipmentNode(
        id=f"node_{uuid.uuid4().hex[:8]}",
        component_class=c_class,
        name=tpl["name"],
        position={"x": x, "y": y},
        ports=tpl["ports"],
        parameters=tpl["params"]
    )
