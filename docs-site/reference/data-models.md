# 30. Data models

All core entities in SteelSim are strictly modeled using Pydantic in the backend and matching TypeScript interfaces in the frontend.

## Core entity definitions

### 1. `PlantGraph`
The top-level container representing a complete factory layout:
```typescript
interface PlantGraph {
  nodes: EquipmentNode[];
  edges: ConnectionEdge[];
}
```

### 2. `EquipmentNode`
Represents a physical machine or utility asset:
```typescript
interface EquipmentNode {
  id: string;                      // Unique ID (e.g., node_8f9a2b1c)
  component_class: ComponentClass; // Industrial asset class enum
  name: string;                    // Human-readable asset name
  position: { x: number; y: number }; // Canvas 2D coordinates
  ports: PortDef[];                // List of industrial port interfaces
  parameters: Record<string, EngineeringQuantity>; // Rated specifications
  metadata: Record<string, any>;   // Sequence order and grouping
}
```

### 3. `ConnectionEdge`
Represents a physical piping, cabling, or signal connection:
```typescript
interface ConnectionEdge {
  id: string;
  source_node: string;
  source_port: string;
  target_node: string;
  target_port: string;
  connection_type: PortType; // MATERIAL | ELECTRICAL | WATER | SIGNAL | AIR
}
```

### 4. `EngineeringQuantity`
Enforces typed values with physical engineering units:
```typescript
interface EngineeringQuantity {
  value: number;
  unit: string;               // MW, kW, t/h, m³/h, °C, bar, m/s
  category: QuantityCategory; // POWER, MASS_FLOW, TEMPERATURE, etc.
  display_name: string;
}
```
