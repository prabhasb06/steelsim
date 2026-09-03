from typing import List, Dict, Set, Optional
from pydantic import BaseModel
from app.models.topology import PlantGraph, EquipmentNode, ConnectionEdge, PortType, ComponentClass
from app.models.component_library import TMT_SEQUENCE

class ValidationIssue(BaseModel):
    level: str  # "ERROR" | "WARNING" | "INFO"
    issue_code: str
    node_id: Optional[str] = None
    edge_id: Optional[str] = None
    message: str
    engineering_reason: str = ""
    suggested_resolution: str = ""
    blocks_simulation: bool = False

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue]

def validate_topology(graph: PlantGraph) -> ValidationResult:
    issues: List[ValidationIssue] = []
    node_map = {n.id: n for n in graph.nodes}
    
    # Check empty
    if not graph.nodes:
        issues.append(ValidationIssue(
            level="WARNING",
            issue_code="EMPTY_PLANT",
            message="Empty plant layout",
            engineering_reason="No equipment configured.",
            blocks_simulation=False
        ))
        
    # 1. Port Types & Duplicate/Self Connections
    material_adj: Dict[str, List[str]] = {n.id: [] for n in graph.nodes}
    water_consumers = set()
    electrical_consumers = set()
    connection_keys = set()
    
    for edge in graph.edges:
        source = node_map.get(edge.source_node)
        target = node_map.get(edge.target_node)
        
        if not source or not target:
            issues.append(ValidationIssue(level="ERROR", issue_code="MISSING_NODE", edge_id=edge.id, message="Edge connects missing node", blocks_simulation=True))
            continue
            
        if source.id == target.id:
            issues.append(ValidationIssue(level="ERROR", issue_code="CIRCULAR_FLOW", node_id=source.id, edge_id=edge.id, message="Self-connection detected", engineering_reason="Component connected to itself.", blocks_simulation=True))
            continue

        src_port = next((p for p in source.ports if p.id == edge.source_port), None)
        tgt_port = next((p for p in target.ports if p.id == edge.target_port), None)
        
        if not src_port or not tgt_port:
            issues.append(ValidationIssue(level="ERROR", issue_code="INVALID_PORT", edge_id=edge.id, message="Edge connects invalid ports", blocks_simulation=True))
            continue
            
        if src_port.type != tgt_port.type:
            issues.append(ValidationIssue(
                level="ERROR", issue_code="PORT_MISMATCH", edge_id=edge.id, 
                message=f"Port mismatch: {src_port.type} to {tgt_port.type}", 
                engineering_reason="Cannot pipe incompatible industrial domains.",
                suggested_resolution="Connect to a compatible port.",
                blocks_simulation=True))

        if src_port.type != edge.connection_type or tgt_port.type != edge.connection_type:
            issues.append(ValidationIssue(
                level="ERROR", issue_code="CONNECTION_TYPE_MISMATCH", edge_id=edge.id,
                message="Connection type does not match its endpoint ports.",
                engineering_reason="The declared industrial domain must match both connected ports.",
                blocks_simulation=True))

        if src_port.direction not in ("OUT", "BIDIRECTIONAL") or tgt_port.direction not in ("IN", "BIDIRECTIONAL"):
            issues.append(ValidationIssue(
                level="ERROR", issue_code="PORT_DIRECTION_INVALID", edge_id=edge.id,
                message="Connection must run from an output port to an input port.",
                engineering_reason="Reversed industrial flow would produce an invalid topology.",
                blocks_simulation=True))

        connection_key = (edge.source_node, edge.source_port, edge.target_node, edge.target_port, edge.connection_type)
        if connection_key in connection_keys:
            issues.append(ValidationIssue(
                level="ERROR", issue_code="DUPLICATE_CONNECTION", edge_id=edge.id,
                message="Duplicate connection detected.",
                blocks_simulation=True))
        connection_keys.add(connection_key)
            
        if edge.connection_type == PortType.MATERIAL:
            material_adj[edge.source_node].append(edge.target_node)
        elif edge.connection_type == PortType.WATER:
            water_consumers.add(edge.target_node)
        elif edge.connection_type == PortType.ELECTRICAL:
            electrical_consumers.add(edge.target_node)

    # 2. Sequence check & Circular Flow for MATERIAL
    visited = set()
    rec_stack = set()
    def is_cyclic(v):
        visited.add(v)
        rec_stack.add(v)
        for neighbor in material_adj.get(v, []):
            if neighbor not in visited:
                if is_cyclic(neighbor): return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(v)
        return False

    for node in graph.nodes:
        if node.id not in visited:
            if is_cyclic(node.id):
                issues.append(ValidationIssue(level="ERROR", issue_code="CIRCULAR_FLOW", node_id=node.id, message="Circular material flow detected.", engineering_reason="Process flows must be acyclic.", blocks_simulation=True))

    terminal_classes = {ComponentClass.FINISHED_GOODS, ComponentClass.COOLING_BED}
    for node in graph.nodes:
        if node.component_class not in terminal_classes:
            # Only complain if the node ACTUALLY has a material_out port
            has_mat_out = any(p.type == PortType.MATERIAL and p.direction == "OUT" for p in node.ports)
            out_edges = material_adj[node.id]
            if has_mat_out and not out_edges:
                issues.append(ValidationIssue(level="ERROR", issue_code="PROCESS_PATH_BROKEN", node_id=node.id, 
                    message=f"{node.name} has no downstream material connection.", 
                    engineering_reason="Material path ends prematurely.",
                    suggested_resolution="Connect a downstream process stage.",
                    blocks_simulation=True))
        elif node.component_class == ComponentClass.FINISHED_GOODS:
            if material_adj[node.id]:
                issues.append(ValidationIssue(level="ERROR", issue_code="INVALID_ROUTING", node_id=node.id, message="Finished Goods should not have downstream connections.", blocks_simulation=True))

    for node in graph.nodes:
        if node.component_class not in TMT_SEQUENCE: continue
        curr_idx = TMT_SEQUENCE.index(node.component_class)
        for target_id in material_adj[node.id]:
            target = node_map[target_id]
            if target.component_class not in TMT_SEQUENCE: continue
            tgt_idx = TMT_SEQUENCE.index(target.component_class)
            if tgt_idx <= curr_idx:
                issues.append(ValidationIssue(level="ERROR", issue_code="PROCESS_SEQUENCE_INVALID", node_id=node.id, 
                    message=f"Invalid sequence: {node.name} -> {target.name}", 
                    engineering_reason="Process goes backward industrially.", blocks_simulation=True))

    # 3. Utility & Parameter Validation (Capacity mismatch)
    for node in graph.nodes:
        # Check utility
        req_water = any(p.type == PortType.WATER and p.direction == "IN" for p in node.ports)
        if req_water and node.id not in water_consumers:
            issues.append(ValidationIssue(level="ERROR", issue_code="UTILITY_REQUIRED", node_id=node.id, 
                message=f"Missing cooling-water supply for {node.name}.", 
                engineering_reason="Component depends on water to function safely.", 
                blocks_simulation=True))

        req_electrical = any(p.type == PortType.ELECTRICAL and p.direction == "IN" for p in node.ports)
        if req_electrical and node.id not in electrical_consumers:
            issues.append(ValidationIssue(level="ERROR", issue_code="UTILITY_REQUIRED", node_id=node.id,
                message=f"Missing electrical supply for {node.name}.",
                engineering_reason="Component requires a connected electrical source to operate.",
                blocks_simulation=True))
                
        # Negative capacity check
        for param_key, qty in node.parameters.items():
            if qty.value < 0:
                issues.append(ValidationIssue(level="ERROR", issue_code="INVALID_CONFIGURATION", node_id=node.id, 
                    message=f"{qty.display_name} cannot be negative.", blocks_simulation=True))
            if qty.category == "PERCENTAGE" and (qty.value < 0 or qty.value > 100):
                issues.append(ValidationIssue(level="ERROR", issue_code="INVALID_CONFIGURATION", node_id=node.id, 
                    message=f"{qty.display_name} must be 0-100%.", blocks_simulation=True))

    # Capacity mismatch check
    for edge in graph.edges:
        if edge.connection_type == PortType.MATERIAL:
            src = node_map.get(edge.source_node)
            tgt = node_map.get(edge.target_node)
            if src and tgt:
                src_tp = src.parameters.get("throughput") or src.parameters.get("dispatch") or src.parameters.get("feed_capacity")
                tgt_tp = tgt.parameters.get("throughput") or tgt.parameters.get("feed_capacity")
                if src_tp and tgt_tp and src_tp.value > tgt_tp.value:
                    diff = src_tp.value - tgt_tp.value
                    # 5% tolerance threshold
                    if diff > (src_tp.value * 0.05):
                        issues.append(ValidationIssue(level="WARNING", issue_code="CAPACITY_BOTTLENECK", node_id=tgt.id, edge_id=edge.id,
                            message=f"Capacity mismatch: Upstream is {src_tp.value} {src_tp.unit}, Downstream is {tgt_tp.value} {tgt_tp.unit}.",
                            engineering_reason=f"Potential configured restriction of {round(diff, 2)} {tgt_tp.unit} (>{round(diff/src_tp.value*100, 1)}% deficit).",
                            blocks_simulation=False))
                        
    # Validate connected utility networks against aggregate demand. Checking
    # consumers one-by-one misses a common failure where every branch is below
    # source capacity but their combined load is not.
    electrical_demands = {
        node.id: node.parameters["power"].value
        for node in graph.nodes
        if node.id in electrical_consumers and "power" in node.parameters
    }
    electrical_source_ids = {
        edge.source_node
        for edge in graph.edges
        if edge.connection_type == PortType.ELECTRICAL and edge.target_node in electrical_demands
    }
    electrical_capacity = 0.0
    for source_id in electrical_source_ids:
        source = node_map[source_id]
        capacity = source.parameters.get("available_power") or source.parameters.get("rating")
        if capacity:
            electrical_capacity += capacity.value / 1000.0 if capacity.unit.lower() == "kw" else capacity.value
        else:
            issues.append(ValidationIssue(
                level="ERROR", issue_code="UTILITY_SOURCE_INVALID", node_id=source.id,
                message=f"{source.name} supplies electrical loads but has no declared capacity.",
                engineering_reason="A utility connection must originate from a rated source.",
                blocks_simulation=True))

    total_electrical_demand = sum(electrical_demands.values())
    if electrical_demands and electrical_capacity < total_electrical_demand:
        issues.append(ValidationIssue(
            level="ERROR", issue_code="UTILITY_CAPACITY_INSUFFICIENT",
            message=f"Connected electrical demand is {total_electrical_demand:.3f} MW but rated supply is {electrical_capacity:.3f} MW.",
            engineering_reason="Aggregate connected load exceeds available substation or transformer capacity.",
            suggested_resolution="Increase electrical supply capacity or reduce connected equipment load.",
            blocks_simulation=True))

    water_demands = {
        node.id: node.parameters["water_flow"].value
        for node in graph.nodes
        if node.id in water_consumers and "water_flow" in node.parameters
    }
    water_source_ids = {
        edge.source_node
        for edge in graph.edges
        if edge.connection_type == PortType.WATER and edge.target_node in water_demands
    }
    water_capacity = 0.0
    for source_id in water_source_ids:
        source = node_map[source_id]
        capacity = source.parameters.get("available_flow") or source.parameters.get("flow")
        if capacity:
            water_capacity += capacity.value
        else:
            issues.append(ValidationIssue(
                level="ERROR", issue_code="UTILITY_SOURCE_INVALID", node_id=source.id,
                message=f"{source.name} supplies cooling-water loads but has no declared capacity.",
                engineering_reason="A utility connection must originate from a rated source.",
                blocks_simulation=True))

    total_water_demand = sum(water_demands.values())
    if water_demands and water_capacity < total_water_demand:
        issues.append(ValidationIssue(
            level="ERROR", issue_code="UTILITY_CAPACITY_INSUFFICIENT",
            message=f"Connected cooling-water demand is {total_water_demand:.1f} m³/h but rated supply is {water_capacity:.1f} m³/h.",
            engineering_reason="Aggregate connected flow exceeds available cooling-system capacity.",
            suggested_resolution="Increase cooling-water capacity or reduce connected flow demand.",
            blocks_simulation=True))

    is_valid = not any(i.blocks_simulation for i in issues)
    return ValidationResult(is_valid=is_valid, issues=issues)
