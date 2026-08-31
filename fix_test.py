import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

test_reps = [
    ("    res = validate_topology(graph)\n    assert res.is_valid\n    assert any(\"No downstream material connection\" in i.message for i in res.issues)",
     "    res = validate_topology(graph)\n    assert not res.is_valid\n    assert any(\"has no downstream material connection\" in i.message for i in res.issues)\n    \n    # Test valid fully connected path\n    fg = create_equipment_node(ComponentClass.FINISHED_GOODS)\n    graph.nodes.append(fg)\n    edges = propose_auto_connections(graph)\n    graph.edges.extend(edges)\n    res2 = validate_topology(graph)\n    assert res2.is_valid"),
]

replace_in_file("backend/tests/test_topology.py", test_reps)
