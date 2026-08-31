import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        if old not in text:
            print(f"WARNING: String not found in {filepath}:\n{old[:50]}...")
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

blueprint_reps = [
    ("import { Play, RotateCcw, Network, LayoutTemplate, Undo2, Redo2, Save, FolderOpen, Wand2 } from 'lucide-react';",
     "import { Play, RotateCcw, Network, LayoutTemplate, Undo2, Redo2, Save, FolderOpen, Wand2 } from 'lucide-react';\nimport { Inspector } from './Inspector';"),
    
    ("const BlueprintCanvas = ({ setValidation }: { setValidation: (v: ValidationResult | null) => void }) => {",
     "const BlueprintCanvas = ({ setValidation }: { setValidation: (v: ValidationResult | null) => void }) => {\n  const [selectedNode, setSelectedNode] = useState<any>(null);\n  const [currentValidation, setCurrentValidation] = useState<ValidationResult | null>(null);"),

    ("const res = await fetch('/api/plant/validate', {",
     "const res = await fetch('/api/plant/validate', {"),

    ("          const v: ValidationResult = await res.json();\n          setValidation(v);",
     "          const v: ValidationResult = await res.json();\n          setCurrentValidation(v);\n          setValidation(v);\n          \n          // Update nodes with validation status\n          setNodes((nds) => nds.map((n) => {\n              const issues = v.issues.filter(i => i.node_id === n.id);\n              const hasError = issues.some(i => i.level === 'ERROR');\n              const hasWarning = issues.some(i => i.level === 'WARNING');\n              return { ...n, data: { ...n.data, validationStatus: hasError ? 'ERROR' : hasWarning ? 'WARNING' : 'VALID' } };\n          }));"),

    ("        onNodesDelete={() => setTimeout(() => { saveHistory(nodes, edges); validateGraph(); }, 100)}",
     "        onNodesDelete={() => setTimeout(() => { saveHistory(nodes, edges); validateGraph(); setSelectedNode(null); }, 100)}\n        onSelectionChange={({ nodes }) => setSelectedNode(nodes.length > 0 ? getGraph(nodes, []).nodes[0] : null)}"),
     
    ("  return (\n    <div className=\"flex-1 h-full relative\" ref={reactFlowWrapper}>",
     "  return (\n    <div className=\"flex-1 h-full flex flex-row\">\n      <div className=\"flex-1 h-full relative\" ref={reactFlowWrapper}>"),
     
    ("      </ReactFlow>\n    </div>\n  );",
     "      </ReactFlow>\n    </div>\n    <Inspector selectedNode={selectedNode} validation={currentValidation} />\n    </div>\n  );")
]

replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", blueprint_reps)
