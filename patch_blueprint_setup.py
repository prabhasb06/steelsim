import os

text = open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8').read()

# 1. Add authoritative createComponent wrapper
create_fn = """
  const addComponentToCanvas = async (c_class: string, position: { x: number, y: number }) => {
      const res = await fetch(`/api/plant/components/${c_class}`);
      if (res.ok) {
          const nodeData = await res.json();
          const newNode = {
            id: nodeData.id,
            type: 'equipment',
            position,
            data: { 
                component_class: nodeData.component_class,
                name: nodeData.name,
                ports: nodeData.ports,
                parameters: nodeData.parameters,
                validationStatus: 'VALID'
            },
          };
          setNodes((nds) => {
              const updated = nds.concat(newNode);
              setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
              return updated;
          });
      }
  };

  const onAddClick = (c_class: string) => {
      // get center of viewport
      const viewport = getViewport();
      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const x = reactFlowBounds ? (reactFlowBounds.width / 2 - viewport.x) / viewport.zoom : 400;
      const y = reactFlowBounds ? (reactFlowBounds.height / 2 - viewport.y) / viewport.zoom : 300;
      
      // slight jitter so multiple clicks don't perfectly overlap
      const jitterX = Math.random() * 40 - 20;
      const jitterY = Math.random() * 40 - 20;
      
      addComponentToCanvas(c_class, { x: x + jitterX, y: y + jitterY });
  };
"""

text = text.replace(
    "  const onDragOver = useCallback((event: React.DragEvent) => {", 
    create_fn + "\n  const onDragOver = useCallback((event: React.DragEvent) => {"
)

# 2. Update onDrop to use it
old_on_drop = """
  const onDrop = useCallback(
    async (event: React.DragEvent) => {
      event.preventDefault();
      const componentClass = event.dataTransfer.getData('application/reactflow');
      if (!componentClass) return;

      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      
      const res = await fetch(`/api/plant/components/${componentClass}`);
      if (res.ok) {
          const nodeData = await res.json();
          const newNode = {
            id: nodeData.id,
            type: 'equipment',
            position,
            data: { 
                component_class: nodeData.component_class,
                name: nodeData.name,
                ports: nodeData.ports,
                parameters: nodeData.parameters,
                validationStatus: 'VALID'
            },
          };
          setNodes((nds) => {
              const updated = nds.concat(newNode);
              setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
              return updated;
          });
      }
    },
    [screenToFlowPosition, edges, validateGraph, saveHistory],
  );
"""

new_on_drop = """
  const onDrop = useCallback(
    async (event: React.DragEvent) => {
      event.preventDefault();
      const componentClass = event.dataTransfer.getData('application/reactflow');
      if (!componentClass) return;

      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      await addComponentToCanvas(componentClass, position);
    },
    [screenToFlowPosition, edges, validateGraph, saveHistory],
  );
"""
text = text.replace(old_on_drop.strip(), new_on_drop.strip())


# 3. Update handleAutoSetup to use /api/plant/auto-connect
old_handle_auto_setup = """
  const handleAutoSetup = async () => {
      const res = await fetch('/api/plant/auto-setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(getGraph())
      });
      if (res.ok) {
          const setup = await res.json();
          const newEdges = [...edges];
          let added = 0;
          setup.edges.forEach((e: any) => {
              newEdges.push({
                  id: e.id,
                  source: e.source_node,
                  sourceHandle: e.source_port,
                  target: e.target_node,
                  targetHandle: e.target_port,
                  data: { connection_type: e.connection_type },
                  style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '5,5' },
                  markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' }
              });
              added++;
          });
          
          if (window.confirm(`AUTO SETUP\\n\\nDetected: ${nodes.length} components\\nChanges: +${added} connections, full repositioning.\\n\\nApply Setup?`)) {
              setEdges(newEdges);
              await handleAutoLayout(nodes);
              validateGraph(nodes, newEdges);
          }
      }
  };
"""

new_handle_auto_setup = """
  const handleAutoSetup = async () => {
      if (nodes.length === 0) {
          alert("AUTO SETUP\\n\\nNo equipment has been added to the plant.\\nAdd equipment manually or load a template first.");
          return;
      }
      const res = await fetch('/api/plant/auto-connect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(getGraph())
      });
      if (res.ok) {
          const suggested = await res.json();
          const newEdges = [...edges];
          let added = 0;
          suggested.forEach((e: any) => {
              if (!edges.some(existing => existing.source === e.source_node && existing.target === e.target_node)) {
                  newEdges.push({
                      id: e.id,
                      source: e.source_node,
                      sourceHandle: e.source_port,
                      target: e.target_node,
                      targetHandle: e.target_port,
                      data: { connection_type: e.connection_type },
                      style: { stroke: '#10b981', strokeWidth: 2, strokeDasharray: '5,5' },
                      markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' }
                  });
                  added++;
              }
          });
          
          if (added === 0) {
             alert("AUTO SETUP\\n\\nNo new valid connections could be proposed for the current components.\\nCheck for missing sequential process stages.");
             return;
          }
          
          if (window.confirm(`AUTO SETUP PREVIEW\\n\\nDetected Components: ${nodes.length}\\nProposed Connections: ${added}\\nProposed Layout Changes: Full Repositioning\\n\\nApply Setup?`)) {
              setEdges(newEdges);
              await handleAutoLayout(nodes, newEdges);
          }
      } else {
          alert("AUTO SETUP FAILED\\n\\nUnable to resolve process sequence.");
      }
  };
"""
text = text.replace(old_handle_auto_setup.strip(), new_handle_auto_setup.strip())

# 4. Modify handleAutoLayout signature so handleAutoSetup can pass the NEW edges before state updates natively.
old_handle_auto_layout = """
  const handleAutoLayout = async (currentNodes = nodes) => {
"""
new_handle_auto_layout = """
  const handleAutoLayout = async (currentNodes = nodes, currentEdges = edges) => {
"""
text = text.replace(old_handle_auto_layout.strip(), new_handle_auto_layout.strip())

text = text.replace(
    "nodes: currentNodes.map((n: any)",
    "nodes: currentNodes.map((n: any)"
)

old_body_auto_layout = """
          edges: edges.map((e: any) => ({
"""
new_body_auto_layout = """
          edges: currentEdges.map((e: any) => ({
"""
text = text.replace(old_body_auto_layout.strip(), new_body_auto_layout.strip())

old_save = """
          saveHistory(updatedNodes, edges);
"""
new_save = """
          saveHistory(updatedNodes, currentEdges);
          validateGraph(updatedNodes, currentEdges);
"""
text = text.replace(old_save.strip(), new_save.strip())

# 5. Pass onAddClick to ComponentLibrary
text = text.replace(
    '<ComponentLibrary isOpen={libraryOpen} setIsOpen={setLibraryOpen} />',
    '<ComponentLibrary isOpen={libraryOpen} setIsOpen={setLibraryOpen} onAddClick={onAddClick} />'
)

open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8').write(text)
