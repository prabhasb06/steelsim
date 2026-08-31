import os

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

for i in range(len(lines)):
    if 'ode_;' in lines[i]:
        lines[i] = "          const newId = `node_${Math.random().toString(36).substr(2, 8)}`;"
    if 'id: edge_,' in lines[i]:
        lines[i] = "          id: `edge_${Math.random().toString(36).substr(2, 8)}`,"
    if 'const finalNewNodes = newNodes.map(nn => {' in lines[i]:
        lines[i] = "          newNodes.map(nn => {"

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
