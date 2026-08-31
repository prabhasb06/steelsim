import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

replace_in_file("src/components/PlantBuilder/Blueprint.tsx", [
    ("const [nodes, setNodes, onNodesChange] = useNodesState([]);", "const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);"),
    ("const [edges, setEdges, onEdgesChange] = useEdgesState([]);", "const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);")
])

replace_in_file("src/components/PlantBuilder/ComponentLibrary.tsx", [
    ("import { ComponentClass } from '../../types/topology';", "import type { ComponentClass } from '../../types/topology';")
])

replace_in_file("src/components/PlantBuilder/CustomNode.tsx", [
    ("import { Handle, Position, NodeProps } from '@xyflow/react';", "import { Handle, Position } from '@xyflow/react';\nimport type { NodeProps } from '@xyflow/react';"),
    ("import { PortDef, PortType } from '../../types/topology';", "import type { PortDef, PortType } from '../../types/topology';")
])

replace_in_file("src/components/PlantBuilder/ValidationPanel.tsx", [
    ("import { ValidationResult } from '../../types/topology';", "import type { ValidationResult } from '../../types/topology';")
])
