from typing import List, Dict
from app.models.topology import PlantGraph, EquipmentNode, ComponentClass

def apply_auto_layout(graph: PlantGraph) -> PlantGraph:
    """
    Applies an intelligent, multi-lane topological layout.
    Prevents excessively wide single-line graphs by wrapping rows.
    Separates Utilities (top), Primary Process (middle), Support (bottom).
    """
    UTILITY_CLASSES = {
        ComponentClass.WATER_SYSTEM, ComponentClass.WATER_PUMP,
        ComponentClass.TRANSFORMER, ComponentClass.ELECTRICAL_SUPPLY,
        ComponentClass.COMPRESSOR
    }
    SUPPORT_CLASSES = {
        ComponentClass.MAINTENANCE_STATION, ComponentClass.QUALITY_INSPECTION,
        ComponentClass.WEIGHING
    }

    in_degree = {n.id: 0 for n in graph.nodes}
    adj = {n.id: [] for n in graph.nodes}
    
    # Only consider MATERIAL and primary sequence edges for topological rank
    for edge in graph.edges:
        if edge.connection_type == "MATERIAL":
            adj[edge.source_node].append(edge.target_node)
            in_degree[edge.target_node] += 1
            
    ranks: Dict[str, int] = {}
    queue = [n.id for n in graph.nodes if in_degree[n.id] == 0]
    
    for q in queue:
        ranks[q] = 0
        
    while queue:
        curr = queue.pop(0)
        curr_rank = ranks[curr]
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if neighbor not in ranks or ranks[neighbor] < curr_rank + 1:
                ranks[neighbor] = curr_rank + 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    for n in graph.nodes:
        if n.id not in ranks:
            ranks[n.id] = 0

    # Layout Parameters
    X_SPACING = 300
    LANE_Y_SPACING = 300  # Distance between utility/primary/support lanes
    MAX_ITEMS_PER_ROW = 6
    START_X = 100
    START_Y = 250  # Center primary lane
    
    # Process primary nodes to calculate wrap offsets
    primary_nodes = [n for n in graph.nodes if n.component_class not in UTILITY_CLASSES and n.component_class not in SUPPORT_CLASSES]
    primary_nodes.sort(key=lambda x: ranks[x.id])
    
    for i, node in enumerate(primary_nodes):
        row = i // MAX_ITEMS_PER_ROW
        col = i % MAX_ITEMS_PER_ROW
        
        # User strictly requested uniform left-to-right rows, NO serpentine.
            
        x = START_X + (col * X_SPACING)
        y = START_Y + (row * LANE_Y_SPACING * 0.8)  # Wrap down primary lane
        node.position = {"x": x, "y": y}

    # Group utilities and support
    util_nodes = [n for n in graph.nodes if n.component_class in UTILITY_CLASSES]
    supp_nodes = [n for n in graph.nodes if n.component_class in SUPPORT_CLASSES]

    for i, node in enumerate(util_nodes):
        node.position = {"x": START_X + (i * X_SPACING), "y": START_Y - LANE_Y_SPACING}

    # Support goes below all primary rows
    max_primary_row = len(primary_nodes) // MAX_ITEMS_PER_ROW
    support_y = START_Y + ((max_primary_row + 1) * LANE_Y_SPACING * 0.8) + 100
    
    for i, node in enumerate(supp_nodes):
        node.position = {"x": START_X + (i * X_SPACING), "y": support_y}

    return graph
