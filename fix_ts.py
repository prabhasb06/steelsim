import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

app_reps = [
    ("import { ValidationPanel } from './components/PlantBuilder/ValidationPanel';\n", "")
]
replace_in_file("frontend/src/App.tsx", app_reps)

bp_reps = [
    ("              ports: node.data.ports as any,\n              capacity: node.data.capacity as number,\n              metadata: {}",
     "              ports: node.data.ports as any,\n              parameters: node.data.parameters as any,\n              metadata: {}"),
    ("                  ports: n.ports,\n                  capacity: n.capacity",
     "                  ports: n.ports,\n                  parameters: n.parameters")
]
replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", bp_reps)

ins_reps = [
    ("import { EquipmentNode, ValidationResult, EngineeringQuantity } from '../../types/topology';",
     "import type { EquipmentNode, ValidationResult, EngineeringQuantity } from '../../types/topology';"),
    ("import { Settings, Info, Zap, Settings2, ShieldAlert } from 'lucide-react';",
     "import { Info, Zap, Settings2, ShieldAlert } from 'lucide-react';"),
    ("    const errors = issues.filter(i => i.level === 'ERROR');\n    const warnings = issues.filter(i => i.level === 'WARNING');\n", "")
]
replace_in_file("frontend/src/components/PlantBuilder/Inspector.tsx", ins_reps)

vp_reps = [
    ("import { useReactFlow } from '@xyflow/react';\n", "")
]
replace_in_file("frontend/src/components/PlantBuilder/ValidationPanel.tsx", vp_reps)
