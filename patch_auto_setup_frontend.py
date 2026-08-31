import os

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# We will replace handleAutoSetup function block
match = re.search(r'const handleAutoSetup = async \(\) => \{.*?\n  \};', text, re.DOTALL)

new_fn = """const handleAutoSetup = async () => {
      if (nodes.length === 0) {
          alert("AUTO SETUP\\n\\nNo equipment has been added to the plant.\\nAdd equipment manually or load a template first.");
          return;
      }
      
      const res = await fetch('/api/plant/auto-setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(getGraph())
      });
      
      if (res.ok) {
          const proposal = await res.json();
          const newEdges = [...edges];
          let added = 0;
          
          proposal.new_edges.forEach((e: any) => {
              if (!edges.some(existing => existing.source === e.source_node && existing.target === e.target_node)) {
                  newEdges.push({
                      id: e.id,
                      source: e.source_node,
                      sourceHandle: e.source_port,
                      target: e.target_node,
                      targetHandle: e.target_port,
                      type: 'smoothstep',
                      data: { connection_type: e.connection_type },
                      style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '5,5' },
                      markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' }
                  });
                  added++;
              }
          });
          
          if (added === 0 && proposal.missing_utilities.length === 0) {
             alert("AUTO SETUP\\n\\nPlant already satisfies recommended baseline topology.\\nNo new connections needed.");
             return;
          }
          
          let previewMsg = `AUTO SETUP PREVIEW\\n\\nDetected Components: ${nodes.length}\\nProposed Connections: ${added}\\n`;
          if (proposal.missing_utilities.length > 0) {
              previewMsg += `\\nMISSING REQUIRED UTILITIES:\\n- ${proposal.missing_utilities.join('\\n- ')}\\n`;
          }
          if (proposal.validation && !proposal.validation.is_valid) {
              previewMsg += `\\nWARNING: Proposed setup is NOT SIMULATION READY.\\nErrors remain.\\n`;
          }
          previewMsg += `\\nApply Setup?`;
          
          if (window.confirm(previewMsg)) {
              setEdges(newEdges);
              await handleAutoLayout(nodes, newEdges);
          }
      }
  };"""

if match:
    text = text[:match.start()] + new_fn + text[match.end():]
    with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
else:
    print("MATCH NOT FOUND")
