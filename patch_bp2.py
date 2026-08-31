import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        if old not in text:
            print(f"WARNING: '{old[:30]}' not found!")
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

bp_reps = [
    ("import { Inspector } from './Inspector';",
     "import { Inspector } from './Inspector';\nimport { ValidationPanel } from './ValidationPanel';"),
    
    ("    <div className=\"flex-1 h-full flex flex-row\">\n      <div className=\"flex-1 h-full relative\" ref={reactFlowWrapper}>",
     "    <div className=\"flex-1 h-full flex flex-col\">\n      <div className=\"flex-1 flex flex-row min-h-0\">\n        <div className=\"flex-1 h-full relative\" ref={reactFlowWrapper}>"),
     
    ("      </ReactFlow>\n    </div>\n    <Inspector selectedNode={selectedNode} validation={currentValidation} />\n    </div>",
     "      </ReactFlow>\n        </div>\n        <Inspector selectedNode={selectedNode} validation={currentValidation} />\n      </div>\n      <ValidationPanel \n        validation={currentValidation} \n        onSelectNode={(id) => {\n            setNodes(nds => nds.map(n => ({ ...n, selected: n.id === id })));\n            const node = nodes.find(n => n.id === id);\n            if (node) {\n                setSelectedNode(node);\n                fitView({ nodes: [node], duration: 800, padding: 0.5 });\n            }\n        }} \n      />\n    </div>")
]

replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", bp_reps)
