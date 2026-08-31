import os

with open('app/engine/auto_connect.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_logic = """
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
                    src = water_providers[0]
                    src_port = next(p for p in src.ports if p.type == PortType.WATER and p.direction == PortDirection.OUT)
                    tgt_port = next(p for p in node.ports if p.type == PortType.WATER and p.direction == PortDirection.IN)
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
                    src = elec_providers[0]
                    src_port = next(p for p in src.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.OUT)
                    tgt_port = next(p for p in node.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.IN)
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
"""

if "def propose_auto_setup" not in text:
    text += new_logic
    with open('app/engine/auto_connect.py', 'w', encoding='utf-8') as f:
        f.write(text)
