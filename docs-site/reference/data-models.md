# 42. Data models

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

### 5. `SimulationSnapshot`
Broadcast by WebSocket and returned by REST endpoints:
```typescript
interface SimulationSnapshot {
  simulation_id: string;
  state_version: number;
  simulated_time_seconds: number;
  tick_index: number;
  node_telemetry: Record<string, NodeTelemetry>;
  edge_telemetry: Record<string, EdgeTelemetry>;
  plant_metrics: PlantMetrics;
  active_alarms: PlantAlarm[];
  expected_throughput_tph?: number | null;
  acamis_impact?: AcamisImpactSummary | null;
}
```

### 6. `AcamisStatusResponse`
The authoritative payload representing the ACAMIS operational center state:
```typescript
interface AcamisStatusResponse {
  current_evaluation: AcamisEvaluation | null;
  active_incidents: IncidentRecord[];
  incident_history: IncidentRecord[];
  available_procedures: AutonomousProcedure[];
  active_procedure: AutonomousProcedure | null;
  execution_history: ProcedureExecutionRecord[];
  operational_mode: 'OBSERVE' | 'ADVISORY' | 'AUTONOMOUS_SIMULATION';
  safety_gate_active: boolean;
  active_scenario: string | null;
  telemetry_detector: TelemetryAnomalyRecord;
}
```

### 7. `TelemetryAnomalyRecord` (Task 3.1)
Authoritative anomaly detection telemetry state:
```typescript
interface TelemetryAnomalyRecord {
  state: 'NORMAL' | 'WATCHING' | 'DETECTED' | 'RECOVERING' | 'RECOVERED';
  consecutive_under_ticks: number;
  actual_throughput_tph: number;
  expected_throughput_tph: number;
  evidence_payload: {
    ratio: number;
    threshold: number;
    underperforming_nodes: string[];
    affected_equipment: string[];
    observed_ticks: number;
    state_trace: Array<{
      tick: number;
      actual: number;
      expected: number;
    }>;
  };
  detected_at_tick: number | null;
  incident_id: string | null;
}
```

