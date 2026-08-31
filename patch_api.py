import os
text = open('backend/app/api/plant.py', 'r', encoding='utf-8').read()
text = text.replace('from app.models.topology import PlantGraph, ConnectionEdge', 'from app.models.topology import PlantGraph, ConnectionEdge, EquipmentNode, ComponentClass\nfrom fastapi import HTTPException')
route = """
@router.get("/components/{c_class}", response_model=EquipmentNode)
async def get_component(c_class: str):
    try:
        enum_val = ComponentClass(c_class)
        return create_equipment_node(enum_val)
    except ValueError:
        raise HTTPException(status_code=404, detail="Component class not found")
"""
text += route
open('backend/app/api/plant.py', 'w', encoding='utf-8').write(text)
