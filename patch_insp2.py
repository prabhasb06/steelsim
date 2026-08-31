import re

with open('frontend/src/components/PlantBuilder/Inspector.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

new_empty_check = """    if (!selectedNode && !selectedEdge) {
        return (
            <div className="w-72 bg-industrial-800 border-l border-industrial-700 flex flex-col h-full transition-all duration-300 flex-shrink-0">
                <div className="h-10 border-b border-industrial-700 flex items-center justify-between px-3 bg-industrial-900/50">
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Inspector</div>
                    <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-industrial-700 rounded text-gray-400 hover:text-white" title="Collapse Inspector">
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
                <div className="flex flex-col items-center justify-center h-full text-gray-500 p-6 text-center">
                    <Settings2 className="w-12 h-12 mb-4 opacity-20" />
                    <div className="text-xs tracking-wider">NO SELECTION</div>
                    <div className="text-[10px] mt-2 opacity-70">Select a component or connection.</div>
                </div>
            </div>
        );
    }
    
    if (selectedEdge && edges && nodes) {
        const edge = edges.find(e => e.id === selectedEdge);
        if (!edge) {
            return (
                <div className="w-72 bg-industrial-800 border-l border-industrial-700 flex flex-col h-full">
                    <div className="p-4 text-gray-500 text-xs">Connection no longer exists.</div>
                </div>
            );
        }
        const srcNode = nodes.find(n => n.id === edge.source);
        const tgtNode = nodes.find(n => n.id === edge.target);
        
        return (
            <div className="w-72 bg-industrial-800 border-l border-industrial-700 flex flex-col h-full transition-all duration-300 flex-shrink-0">
                <div className="h-10 border-b border-industrial-700 flex items-center justify-between px-3 bg-industrial-900/50">
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Connection</div>
                    <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-industrial-700 rounded text-gray-400 hover:text-white">
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
                <div className="p-4 flex flex-col gap-4">
                    <div>
                        <div className="text-[10px] font-semibold text-gray-400 tracking-wider mb-1">TYPE</div>
                        <div className="text-xs font-mono font-bold bg-industrial-900 p-2 rounded border border-industrial-700">
                            {edge.data?.connection_type || 'Unknown'}
                        </div>
                    </div>
                    <div>
                        <div className="text-[10px] font-semibold text-gray-400 tracking-wider mb-1">SOURCE</div>
                        <div className="text-xs bg-industrial-900 p-2 rounded border border-industrial-700 text-gray-300">
                            <div className="font-bold mb-1">{srcNode ? srcNode.data.name : edge.source}</div>
                            <div className="opacity-70 font-mono text-[10px]">Port: {edge.sourceHandle}</div>
                        </div>
                    </div>
                    <div>
                        <div className="text-[10px] font-semibold text-gray-400 tracking-wider mb-1">TARGET</div>
                        <div className="text-xs bg-industrial-900 p-2 rounded border border-industrial-700 text-gray-300">
                            <div className="font-bold mb-1">{tgtNode ? tgtNode.data.name : edge.target}</div>
                            <div className="opacity-70 font-mono text-[10px]">Port: {edge.targetHandle}</div>
                        </div>
                    </div>
                    <div className="text-xs text-gray-500 italic mt-2 text-center">
                        Drag connection handle on canvas to reconnect.
                    </div>
                    {onDeleteEdge && (
                        <button onClick={() => onDeleteEdge(edge.id)} className="mt-4 flex items-center justify-center px-3 py-2 bg-red-900/20 text-red-400 border border-red-900/50 hover:bg-red-900/40 rounded transition-colors text-xs font-bold tracking-wider">
                            DISCONNECT
                        </button>
                    )}
                </div>
            </div>
        );
    }
"""

match = re.search(r'    if \(!selectedNode\) \{[\s\S]*?\}\n\n    const issues', text)
if match:
    text = text.replace(match.group(0), new_empty_check + '\n\n    if (!selectedNode) return null;\n\n    const issues')
    
with open('frontend/src/components/PlantBuilder/Inspector.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
