from typing import List, Dict
import uuid
from app.models.topology import PlantGraph, EquipmentNode, ConnectionEdge, PortType, PortDirection, ComponentClass
from app.models.component_library import TMT_SEQUENCE

def propose_auto_connections(graph: PlantGraph) -> List[ConnectionEdge]:
    """
    Inspect all nodes in the graph. Create proposed material connections
    based on the logical TMT sequence.
    """
    proposed_edges: List[ConnectionEdge] = []
    
    # Sort nodes by their expected process order
    ordered_nodes = []
    for c_class in TMT_SEQUENCE:
        nodes_of_class = [n for n in graph.nodes if n.component_class == c_class]
        ordered_nodes.extend(nodes_of_class)
        
    # Attempt to connect sequentially
    for i in range(len(ordered_nodes) - 1):
        source = ordered_nodes[i]
        target = ordered_nodes[i+1]
        
        src_port = next((p for p in source.ports if p.type == PortType.MATERIAL and p.direction == PortDirection.OUT), None)
        tgt_port = next((p for p in target.ports if p.type == PortType.MATERIAL and p.direction == PortDirection.IN), None)
        
        if src_port and tgt_port:
            # Check if this edge already exists in the graph
            exists = any(
                e.source_node == source.id and e.target_node == target.id 
                and e.source_port == src_port.id and e.target_port == tgt_port.id
                for e in graph.edges
            )
            
            if not exists:
                edge = ConnectionEdge(
                    id=f"edge_{uuid.uuid4().hex[:8]}",
                    source_node=source.id,
                    source_port=src_port.id,
                    target_node=target.id,
                    target_port=tgt_port.id,
                    connection_type=PortType.MATERIAL
                )
                proposed_edges.append(edge)
                
    return proposed_edges

from app.models.topology import AutoSetupProposal
from app.engine.topology_validator import validate_topology
from app.engine.auto_layout import apply_auto_layout
import copy

def propose_auto_setup(graph: PlantGraph) -> AutoSetupProposal:
    proposal = AutoSetupProposal()
    
    # 1. Propose material connections (existing logic)
    mat_edges = propose_auto_connections(graph)
    
    # 2. Propose utility connections
    util_edges = []
    # Identify utility providers
    water_providers = [n for n in graph.nodes if any(p.type == PortType.WATER and p.direction == PortDirection.OUT for p in n.ports)]
    elec_providers = [n for n in graph.nodes if any(p.type == PortType.ELECTRICAL and p.direction == PortDirection.OUT for p in n.ports)]
    
    for node in graph.nodes:
        # Check if node needs water
        if any(p.type == PortType.WATER and p.direction == PortDirection.IN for p in node.ports):
            # Is it already connected?
            if not any(e.target_node == node.id and e.connection_type == PortType.WATER for e in graph.edges):
                if water_providers:
                    # Pick a provider that is not the node itself
                    src = next((p for p in water_providers if p.id != node.id), None)
                    if src:
                        src_port = next(p for p in src.ports if p.type == PortType.WATER and p.direction == PortDirection.OUT)
                        tgt_port = next(p for p in node.ports if p.type == PortType.WATER and p.direction == PortDirection.IN)
                    else:
                        proposal.missing_utilities.append(f"{node.name} requires Cooling Water")
                        continue
                    util_edges.append(ConnectionEdge(
                        id=f"edge_{uuid.uuid4().hex[:8]}", source_node=src.id, source_port=src_port.id,
                        target_node=node.id, target_port=tgt_port.id, connection_type=PortType.WATER
                    ))
                else:
                    proposal.missing_utilities.append(f"{node.name} requires Cooling Water (Water System recommended)")
                    
        # Check if node needs electrical
        if any(p.type == PortType.ELECTRICAL and p.direction == PortDirection.IN for p in node.ports):
            if not any(e.target_node == node.id and e.connection_type == PortType.ELECTRICAL for e in graph.edges):
                if elec_providers:
                    src = next((p for p in elec_providers if p.id != node.id), None)
                    if src:
                        src_port = next(p for p in src.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.OUT)
                        tgt_port = next(p for p in node.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.IN)
                    else:
                        proposal.missing_utilities.append(f"{node.name} requires Electrical Supply")
                        continue
                    util_edges.append(ConnectionEdge(
                        id=f"edge_{uuid.uuid4().hex[:8]}", source_node=src.id, source_port=src_port.id,
                        target_node=node.id, target_port=tgt_port.id, connection_type=PortType.ELECTRICAL
                    ))
                else:
                    proposal.missing_utilities.append(f"{node.name} requires Electrical Supply (Transformer recommended)")

    proposal.new_edges = mat_edges + util_edges
    
    # Generate proposed graph
    cloned_graph = copy.deepcopy(graph)
    cloned_graph.edges.extend(proposal.new_edges)
    
    # Auto Layout
    laid_out = apply_auto_layout(cloned_graph)
    proposal.proposed_graph = laid_out
    
    # Validate
    proposal.validation = validate_topology(laid_out)
    
    return proposal
