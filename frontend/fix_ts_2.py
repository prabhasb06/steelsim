import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

replace_in_file("src/App.tsx", [
    ("import { SimulationState, SimulationSnapshot, SimulationEvent } from './types';", "import type { SimulationState, SimulationSnapshot, SimulationEvent } from './types';"),
    ("import { ValidationResult } from './types/topology';", "import type { ValidationResult } from './types/topology';"),
    ("Play, Pause, RotateCcw, Activity, Settings, LayoutDashboard, Factory, Cpu, Zap, Wrench, Shield, Truck", "Play, Pause, RotateCcw, Activity, LayoutDashboard, Factory, Cpu, Zap, Wrench, Shield, Truck")
])

replace_in_file("src/components/PlantBuilder/Blueprint.tsx", [
    ("Connection,\n  Edge,\n  Node,", ""),
    ("import { EquipmentNodeComponent } from './CustomNode';", "import type { Connection, Edge, Node } from '@xyflow/react';\nimport { EquipmentNodeComponent } from './CustomNode';"),
    ("import { PlantGraph, ValidationResult, ValidationIssue } from '../../types/topology';", "import type { PlantGraph, ValidationResult } from '../../types/topology';"),
    ("Play, RotateCcw, AlertTriangle, CheckCircle, Network, LayoutTemplate", "Play, RotateCcw, Network, LayoutTemplate"),
    ("const newEdges = addEdge(newEdge, edges);", "const newEdges = addEdge(newEdge as Edge, edges);")
])

replace_in_file("src/components/PlantBuilder/ComponentLibrary.tsx", [
    ("import type { ComponentClass } from '../../types/topology';\n", "")
])

replace_in_file("src/components/PlantBuilder/CustomNode.tsx", [
    ("import React from 'react';\n", "")
])

replace_in_file("src/components/PlantBuilder/ValidationPanel.tsx", [
    ("import React from 'react';\n", "")
])
