import pytest
from app.models.topology import PlantGraph, EquipmentNode, ConnectionEdge, PortType, ComponentClass
from app.models.component_library import create_equipment_node
from app.engine.topology_validator import validate_topology
from app.engine.auto_connect import propose_auto_connections
from app.engine.auto_layout import apply_auto_layout

def test_empty_topology():
    graph = PlantGraph()
    res = validate_topology(graph)
    # empty should have a warning, but is_valid=True (no ERROR)
    assert res.is_valid
    assert len(res.issues) == 1
    assert res.issues[0].level == "WARNING"

def test_valid_topology():
    graph = PlantGraph()
    yard = create_equipment_node(ComponentClass.BILLET_YARD)
    furnace = create_equipment_node(ComponentClass.REHEATING_FURNACE)
    graph.nodes.extend([yard, furnace])
    
    # Missing connections, should have WARNING for dead-end
    res = validate_topology(graph)
    assert not res.is_valid
    assert any("has no downstream material connection" in i.message for i in res.issues)
    
    # Test valid fully connected path
    fg = create_equipment_node(ComponentClass.FINISHED_GOODS)
    graph.nodes.append(fg)
    edges = propose_auto_connections(graph)
    graph.edges.extend(edges)
    res2 = validate_topology(graph)
    assert res2.is_valid
    
def test_auto_connect():
    graph = PlantGraph()
    yard = create_equipment_node(ComponentClass.BILLET_YARD)
    furnace = create_equipment_node(ComponentClass.REHEATING_FURNACE)
    # Skip charging table to see if it jumps
    graph.nodes.extend([yard, furnace])
    
    edges = propose_auto_connections(graph)
    assert len(edges) == 1
    assert edges[0].source_node == yard.id
    assert edges[0].target_node == furnace.id
    
def test_auto_layout():
    graph = PlantGraph()
    yard = create_equipment_node(ComponentClass.BILLET_YARD)
    furnace = create_equipment_node(ComponentClass.REHEATING_FURNACE)
    graph.nodes.extend([yard, furnace])
    
    edges = propose_auto_connections(graph)
    graph.edges.extend(edges)
    
    apply_auto_layout(graph)
    assert yard.position["x"] < furnace.position["x"]

def test_negative_capacity():
    graph = PlantGraph()
    yard = create_equipment_node(ComponentClass.BILLET_YARD)
    yard.parameters['dispatch'].value = -10
    graph.nodes.append(yard)
    res = validate_topology(graph)
    assert not res.is_valid
    assert any('cannot be negative' in i.message for i in res.issues)

def test_circular_flow():
    graph = PlantGraph()
    yard = create_equipment_node(ComponentClass.BILLET_YARD)
    graph.nodes.append(yard)
    edge = ConnectionEdge(id='e1', source_node=yard.id, source_port=yard.ports[0].id, target_node=yard.id, target_port=yard.ports[0].id, connection_type=PortType.MATERIAL)
    graph.edges.append(edge)
    res = validate_topology(graph)
    assert not res.is_valid
    assert any('Self-connection detected' in i.message for i in res.issues)

def test_capacity_mismatch():
    graph = PlantGraph()
    rm = create_equipment_node(ComponentClass.ROUGHING_MILL)
    im = create_equipment_node(ComponentClass.INTERMEDIATE_MILL)
    rm.parameters['throughput'].value = 30
    im.parameters['throughput'].value = 20
    graph.nodes.extend([rm, im])
    graph.edges.extend(propose_auto_connections(graph))
    res = validate_topology(graph)
    assert any(i.issue_code == 'CAPACITY_BOTTLENECK' and i.level == 'WARNING' for i in res.issues)
    
def test_missing_utility():
    graph = PlantGraph()
    tc = create_equipment_node(ComponentClass.TMT_COOLING)
    fg = create_equipment_node(ComponentClass.FINISHED_GOODS)
    graph.nodes.extend([tc, fg])
    graph.edges.extend(propose_auto_connections(graph))
    res = validate_topology(graph)
    assert not res.is_valid
    assert any(i.issue_code == 'UTILITY_REQUIRED' and i.level == 'ERROR' for i in res.issues)
