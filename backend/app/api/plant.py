from fastapi import APIRouter
from typing import List

from app.models.topology import PlantGraph, ConnectionEdge, EquipmentNode, ComponentClass, AutoSetupProposal
from fastapi import HTTPException
from app.engine.topology_validator import validate_topology, ValidationResult
from app.engine.auto_connect import propose_auto_connections, propose_auto_setup
from app.engine.auto_layout import apply_auto_layout
from app.models.component_library import COMPONENT_TEMPLATES, create_equipment_node, TMT_BASELINE_SEQUENCE

router = APIRouter(prefix="/api/plant")

@router.get("/templates")
async def get_templates():
    return COMPONENT_TEMPLATES

@router.post("/validate", response_model=ValidationResult)
async def validate_plant(graph: PlantGraph):
    return validate_topology(graph)

@router.post("/auto-connect", response_model=List[ConnectionEdge])
async def auto_connect(graph: PlantGraph):
    return propose_auto_connections(graph)

@router.post("/auto-layout", response_model=PlantGraph)
async def auto_layout(graph: PlantGraph):
    return apply_auto_layout(graph)

@router.get("/template/tmt", response_model=PlantGraph)
async def load_tmt_template():
    graph = PlantGraph()
    # Create nodes
    for c_class in TMT_BASELINE_SEQUENCE:
        graph.nodes.append(create_equipment_node(c_class))
        
    # Add required baseline utilities so it isn't broken by default
    graph.nodes.append(create_equipment_node(ComponentClass.UTILITY_SUBSTATION))
    graph.nodes.append(create_equipment_node(ComponentClass.WATER_COOLING_SYSTEM))
    
    # Use our new Auto Setup logic to perfectly connect it and lay it out
    proposal = propose_auto_setup(graph)
    if proposal.proposed_graph:
        return proposal.proposed_graph
    return graph

@router.get("/components/{c_class}", response_model=EquipmentNode)
async def get_component(c_class: str):
    try:
        enum_val = ComponentClass(c_class)
        return create_equipment_node(enum_val)
    except ValueError:
        raise HTTPException(status_code=404, detail="Component class not found")

@router.post("/auto-setup", response_model=AutoSetupProposal)
async def auto_setup(graph: PlantGraph):
    return propose_auto_setup(graph)
