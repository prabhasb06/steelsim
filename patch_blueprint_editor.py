import os
import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Editor operations to insert
editor_ops = """
  // ===================== EDITOR OPERATIONS ===================== //

  const handleDuplicate = () => {
      if (!selectedNode) return;
      const original = nodes.find(n => n.id === selectedNode);
      if (!original) return;
      
      const newId = `node_${Math.random().toString(36).substr(2, 8)}`;
      
      setNodes(nds => {
          const newNode = {
              ...original,
              id: newId,
              selected: true,
              position: { x: original.position.x + 40, y: original.position.y + 40 },
              data: {
                  ...original.data,
                  engineeringId: generateEngineeringId(original.data.component_class, nds)
              }
          };
          const updated = nds.map(n => ({ ...n, selected: false })).concat(newNode);
          setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
          return updated;
      });
  };

  const handleCopy = () => {
      if (!selectedNode) return;
      const original = nodes.find(n => n.id === selectedNode);
      if (!original) return;
      setClipboard({ nodes: [JSON.parse(JSON.stringify(original))], edges: [] });
  };

  const handleCut = () => {
      handleCopy();
      handleDeleteNode(selectedNode);
  };

  const handlePaste = () => {
      if (!clipboard.nodes.length) return;
      
      const original = clipboard.nodes[0];
      const newId = `node_${Math.random().toString(36).substr(2, 8)}`;
      
      setNodes(nds => {
          const newNode = {
              ...original,
              id: newId,
              selected: true,
              position: { x: original.position.x + 40, y: original.position.y + 40 },
              data: {
                  ...original.data,
                  engineeringId: generateEngineeringId(original.data.component_class, nds)
              }
          };
          const updated = nds.map(n => ({ ...n, selected: false })).concat(newNode);
          setTimeout(() => { saveHistory(updated, edges); validateGraph(updated, edges); }, 50);
          return updated;
      });
  };

  const handleDeleteNode = (nodeId: string | null) => {
      if (!nodeId) return;
      setNodes(nds => {
          const updatedNodes = nds.filter(n => n.id !== nodeId);
          setEdges(eds => {
              const updatedEdges = eds.filter(e => e.source !== nodeId && e.target !== nodeId);
              setTimeout(() => { saveHistory(updatedNodes, updatedEdges); validateGraph(updatedNodes, updatedEdges); }, 50);
              return updatedEdges;
          });
          return updatedNodes;
      });
      setSelectedNode(null);
  };

  const handleToggleLock = () => {
      if (!selectedNode) return;
      setNodes(nds => {
          const updated = nds.map(n => n.id === selectedNode ? { ...n, data: { ...n.data, locked: !n.data.locked } } : n);
          setTimeout(() => { saveHistory(updated, edges); }, 50);
          return updated;
      });
  };

  const handleDisconnect = () => {
      if (!selectedNode) return;
      setEdges(eds => {
          const updatedEdges = eds.filter(e => e.source !== selectedNode && e.target !== selectedNode);
          setTimeout(() => { saveHistory(nodes, updatedEdges); validateGraph(nodes, updatedEdges); }, 50);
          return updatedEdges;
      });
  };
  
  const handleShowUpstream = () => {
      if (!selectedNode) return;
      // Very basic upstream highlight logic: select all source nodes that lead here
      const upstream = new Set<string>();
      const traverse = (nodeId: string) => {
          edges.filter(e => e.target === nodeId).forEach(e => {
              if (!upstream.has(e.source)) {
                  upstream.add(e.source);
                  traverse(e.source);
              }
          });
      };
      traverse(selectedNode);
      if (upstream.size > 0) {
          setNodes(nds => nds.map(n => ({ ...n, selected: upstream.has(n.id) || n.id === selectedNode })));
      }
  };

  const handleShowDownstream = () => {
      if (!selectedNode) return;
      const downstream = new Set<string>();
      const traverse = (nodeId: string) => {
          edges.filter(e => e.source === nodeId).forEach(e => {
              if (!downstream.has(e.target)) {
                  downstream.add(e.target);
                  traverse(e.target);
              }
          });
      };
      traverse(selectedNode);
      if (downstream.size > 0) {
          setNodes(nds => nds.map(n => ({ ...n, selected: downstream.has(n.id) || n.id === selectedNode })));
      }
  };

  const onNodeContextMenu = (event: React.MouseEvent, node: any) => {
      event.preventDefault();
      setContextMenu({ x: event.clientX, y: event.clientY, nodeId: node.id });
      if (selectedNode !== node.id) {
          setNodes(nds => nds.map(n => ({ ...n, selected: n.id === node.id })));
          setSelectedNode(node.id);
      }
  };

  const onPaneContextMenu = (event: React.MouseEvent) => {
      event.preventDefault();
      setContextMenu({ x: event.clientX, y: event.clientY });
  };

  // Keyboard Shortcuts
  useEffect(() => {
      const handleKeyDown = (e: KeyboardEvent) => {
          const target = e.target as HTMLElement;
          if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable) {
              return;
          }
          
          if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'c') {
              handleCopy();
          } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'x') {
              handleCut();
          } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'v') {
              handlePaste();
          } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'd') {
              e.preventDefault();
              handleDuplicate();
          } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
              e.preventDefault();
              handleUndo();
          } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'z') {
              e.preventDefault();
              handleRedo();
          } else if (e.key === 'Delete' || e.key === 'Backspace') {
              if (selectedNode) handleDeleteNode(selectedNode);
          } else if (e.key.toLowerCase() === 'f') {
              if (selectedNode) {
                  const node = nodes.find(n => n.id === selectedNode);
                  if (node) zoomTo(1, { duration: 500 });
              }
          }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNode, nodes, edges, clipboard, historyIndex]);

  // ===================== END EDITOR OPERATIONS ===================== //
"""

text = text.replace("  const handleAutoConnect", editor_ops + "\n  const handleAutoConnect")

# Attach context menu events to ReactFlow
rf_events = """                    onNodesDelete={() => setTimeout(() => { saveHistory(nodes, edges); validateGraph(); setSelectedNode(null); }, 100)}
                    onNodeContextMenu={onNodeContextMenu}
                    onPaneContextMenu={onPaneContextMenu}
                    onPaneClick={() => { setContextMenu(null); setSelectedNode(null); }}
"""
text = re.sub(r'                    onNodesDelete=\{\(\) => setTimeout\(\(\) => \{ saveHistory\(nodes, edges\); validateGraph\(\); setSelectedNode\(null\); \}, 100\)\}', rf_events.strip(), text)

# Update layout map to lock positions
layout_str = """
          const layoutMap = new Map(layout.nodes.map((n: any) => [n.id, n.position]));
          const updatedNodes = currentNodes.map(n => ({
              ...n,
              position: n.data?.locked ? n.position : (layoutMap.get(n.id) || n.position)
          }));
"""
text = text.replace("""          const layoutMap = new Map(layout.nodes.map((n: any) => [n.id, n.position]));
          const updatedNodes = currentNodes.map(n => ({
              ...n,
              position: layoutMap.get(n.id) || n.position
          }));""", layout_str.strip())


# Render context menu
context_menu_render = """
                {contextMenu && (
                    <ContextMenu 
                        x={contextMenu.x} 
                        y={contextMenu.y} 
                        title={contextMenu.nodeId ? nodes.find(n => n.id === contextMenu.nodeId)?.data?.engineeringId || 'Component' : 'Canvas'}
                        subtitle={contextMenu.nodeId ? nodes.find(n => n.id === contextMenu.nodeId)?.data?.name : ''}
                        onClose={() => setContextMenu(null)}
                        actions={
                            contextMenu.nodeId ? [
                                { label: 'Inspect / Configure', onClick: () => { setInspectorOpen(true); } },
                                { label: 'Rename', onClick: () => {
                                    const newName = prompt('Enter new display name:');
                                    if (newName) {
                                        setNodes(nds => {
                                            const updated = nds.map(n => n.id === contextMenu.nodeId ? { ...n, data: { ...n.data, name: newName } } : n);
                                            setTimeout(() => { saveHistory(updated, edges); }, 50);
                                            return updated;
                                        });
                                    }
                                } },
                                { separator: true, onClick: () => {} },
                                { label: 'Duplicate', onClick: handleDuplicate },
                                { label: 'Copy', onClick: handleCopy },
                                { label: 'Cut', onClick: handleCut },
                                { separator: true, onClick: () => {} },
                                { label: 'Disconnect All', onClick: handleDisconnect },
                                { label: 'Show Upstream', onClick: handleShowUpstream },
                                { label: 'Show Downstream', onClick: handleShowDownstream },
                                { separator: true, onClick: () => {} },
                                { label: nodes.find(n => n.id === contextMenu.nodeId)?.data?.locked ? 'Unlock Position' : 'Lock Position', onClick: handleToggleLock },
                                { separator: true, onClick: () => {} },
                                { label: 'Delete', danger: true, onClick: () => handleDeleteNode(contextMenu.nodeId || null) }
                            ] : [
                                { label: 'Paste', disabled: clipboard.nodes.length === 0, onClick: handlePaste },
                                { separator: true, onClick: () => {} },
                                { label: 'Auto Connect', onClick: handleAutoConnect },
                                { label: 'Auto Layout', onClick: () => handleAutoLayout(nodes, edges) }
                            ]
                        }
                    />
                )}
"""
text = text.replace("{/* MAIN CONTENT OVERLAYS */}", "{/* MAIN CONTENT OVERLAYS */}\n" + context_menu_render)


with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
