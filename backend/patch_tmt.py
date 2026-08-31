import os

with open('app/api/plant.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

match = re.search(r'@router\.get\("/template/tmt".*?return apply_auto_layout\(graph\)', text, re.DOTALL)
if match:
    old_fn = match.group(0)
    new_fn = """@router.get("/template/tmt", response_model=PlantGraph)
async def load_tmt_template():
    graph = PlantGraph()
    # Create nodes
    for c_class in TMT_SEQUENCE:
        graph.nodes.append(create_equipment_node(c_class))
        
    # Add required baseline utilities so it isn't broken by default
    graph.nodes.append(create_equipment_node(ComponentClass.WATER_SYSTEM))
    graph.nodes.append(create_equipment_node(ComponentClass.TRANSFORMER))
    
    # Use our new Auto Setup logic to perfectly connect it and lay it out
    proposal = propose_auto_setup(graph)
    if proposal.proposed_graph:
        return proposal.proposed_graph
    return graph"""
    text = text.replace(old_fn, new_fn)
    with open('app/api/plant.py', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("MATCH NOT FOUND")
