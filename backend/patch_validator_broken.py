import os

with open('app/engine/topology_validator.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = """    for node in graph.nodes:
        if node.component_class != ComponentClass.FINISHED_GOODS:
            out_edges = material_adj[node.id]
            if not out_edges:
                issues.append(ValidationIssue(level="ERROR", issue_code="PROCESS_PATH_BROKEN", node_id=node.id,"""

new_logic = """    for node in graph.nodes:
        if node.component_class != ComponentClass.FINISHED_GOODS:
            # Only complain if the node ACTUALLY has a material_out port
            has_mat_out = any(p.type == PortType.MATERIAL and p.direction == "OUT" for p in node.ports)
            out_edges = material_adj[node.id]
            if has_mat_out and not out_edges:
                issues.append(ValidationIssue(level="ERROR", issue_code="PROCESS_PATH_BROKEN", node_id=node.id,"""

text = text.replace(old_logic, new_logic)

with open('app/engine/topology_validator.py', 'w', encoding='utf-8') as f:
    f.write(text)
