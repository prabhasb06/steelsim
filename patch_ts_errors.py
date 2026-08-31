import os
import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix unused import
text = text.replace("import { ContextMenu, ContextMenuAction } from './ContextMenu';", "import { ContextMenu } from './ContextMenu';")

# 2. Add clipboard and contextMenu state
if 'const [clipboard' not in text:
    state_str = """
  const [clipboard, setClipboard] = useState<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });
  const [contextMenu, setContextMenu] = useState<{ x: number, y: number, nodeId?: string } | null>(null);
  """
    text = text.replace("const [historyIndex, setHistoryIndex] = useState(0);", "const [historyIndex, setHistoryIndex] = useState(0);\n" + state_str)

# 3. Add zoomTo
text = text.replace("const { screenToFlowPosition, fitView, zoomIn, zoomOut, getViewport } = useReactFlow();", "const { screenToFlowPosition, fitView, zoomIn, zoomOut, zoomTo, getViewport } = useReactFlow();")
text = text.replace("const { screenToFlowPosition, fitView, getViewport } = useReactFlow();", "const { screenToFlowPosition, fitView, zoomTo, getViewport } = useReactFlow();")

# 4. Fix 'nds' usage in addComponentToCanvas
text = text.replace("generateEngineeringId(nodeData.component_class, nds)", "generateEngineeringId(nodeData.component_class, nodes)")

# 5. Fix handleDuplicate / handlePaste engineering ID which also uses 'nds' incorrectly in state setter
text = text.replace("engineeringId: generateEngineeringId(original.data.component_class, nds)", "engineeringId: generateEngineeringId(original.data.component_class, nodes)")

# 6. Fix onPaneContextMenu typing
text = text.replace("const onPaneContextMenu = (event: React.MouseEvent) => {", "const onPaneContextMenu = (event: React.MouseEvent | MouseEvent) => {")

# 7. Unused handles: handleToggleLock, handleDisconnect, handleShowUpstream, handleShowDownstream are used in ContextMenu! 
# But wait, I added ContextMenu to the bottom, why did TS say they're unused?
# Ah! My previous patch might have missed adding ContextMenu to the render tree!
# Let me check if <ContextMenu /> is in the code.
if '<ContextMenu' not in text:
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
                                            setTimeout(() => { saveHistory(updated, edges); validateGraph(); }, 50);
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
    text = text.replace("{/* COMPONENT LIBRARY SIDEBAR */}", context_menu_render + "\n                {/* COMPONENT LIBRARY SIDEBAR */}")

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
