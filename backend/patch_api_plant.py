import os
import re

with open('app/api/plant.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'from app.engine.auto_connect import propose_auto_connections', 
    'from app.engine.auto_connect import propose_auto_connections, propose_auto_setup'
)
text = text.replace(
    'from app.models.topology import PlantGraph, ValidationResult, ConnectionEdge',
    'from app.models.topology import PlantGraph, ValidationResult, ConnectionEdge, AutoSetupProposal'
)

new_route = """
@router.post("/auto-setup", response_model=AutoSetupProposal)
async def auto_setup(graph: PlantGraph):
    return propose_auto_setup(graph)
"""

if "/auto-setup" not in text:
    text += new_route

with open('app/api/plant.py', 'w', encoding='utf-8') as f:
    f.write(text)
