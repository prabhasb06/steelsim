export type PortType = "MATERIAL" | "ELECTRICAL" | "WATER" | "SIGNAL" | "AIR";
export type PortDirection = "IN" | "OUT" | "BIDIRECTIONAL";

export type ComponentClass = 
    | "BILLET_YARD"
    | "CHARGING_TABLE"
    | "REHEATING_FURNACE"
    | "ROUGHING_MILL"
    | "INTERMEDIATE_MILL"
    | "FINISHING_MILL"
    | "TMT_COOLING"
    | "COOLING_BED"
    | "CUTTING_UNIT"
    | "BUNDLING_UNIT"
    | "FINISHED_GOODS"
    | "TRANSFORMER"
    | "WATER_PUMP"
    | "RAW_MATERIAL_STORAGE"
    | "TRANSFER_CONVEYOR"
    | "ROLLER_CONVEYOR"
    | "BUFFER"
    | "WEIGHING"
    | "ELECTRICAL_SUPPLY"
    | "WATER_SYSTEM"
    | "COMPRESSOR"
    | "MAINTENANCE_STATION"
    | "QUALITY_INSPECTION";

export type QuantityCategory = "MASS" | "MASS_FLOW" | "TEMPERATURE" | "POWER" | "ENERGY" | "SPECIFIC_ENERGY" | "VOLTAGE" | "CURRENT" | "PRESSURE" | "VOLUMETRIC_FLOW" | "NORMALIZED_GAS_FLOW" | "LINEAR_SPEED" | "ROTATIONAL_SPEED" | "LENGTH" | "TIME" | "CAPACITY" | "PERCENTAGE" | "VIBRATION" | "COST" | "SPECIFIC_COST";

export interface EngineeringQuantity {
    value: number;
    unit: string;
    category: QuantityCategory;
    display_name: string;
}

export interface PortDef {
    id: string;
    type: PortType;
    direction: PortDirection;
}

export interface EquipmentNode {
    id: string;
    component_class: ComponentClass;
    name: string;
    position: { x: number; y: number };
    ports: PortDef[];
    parameters: Record<string, EngineeringQuantity>;
    metadata: Record<string, any>;
}

export interface ConnectionEdge {
    id: string;
    source_node: string;
    source_port: string;
    target_node: string;
    target_port: string;
    connection_type: PortType;
}

export interface PlantGraph {
    nodes: EquipmentNode[];
    edges: ConnectionEdge[];
}

export interface ValidationIssue {
    level: "ERROR" | "WARNING" | "INFO";
    issue_code: string;
    node_id?: string;
    edge_id?: string;
    message: string;
    engineering_reason: string;
    suggested_resolution: string;
    blocks_simulation: boolean;
}

export interface ValidationResult {
    is_valid: boolean;
    issues: ValidationIssue[];
}
