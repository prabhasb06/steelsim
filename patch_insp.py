import re

with open('frontend/src/components/PlantBuilder/Inspector.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

new_empty_check = """if (!selectedNode && !selectedEdge) {
        content = (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 p-6 text-center">
                <Settings2 className="w-12 h-12 mb-4 opacity-20" />
                <div className="text-xs tracking-wider">NO SELECTION</div>
                <div className="text-[10px] mt-2 opacity-70">Select a component or connection to inspect.</div>
            </div>
        );
    } else if (selectedEdge && edges && nodes) {
        const edge = edges.find(e => e.id === selectedEdge);
        if (!edge) {
            content = <div className="p-4 text-gray-500 text-xs">Connection no longer exists.</div>;
        } else {
            const srcNode = nodes.find(n => n.id === edge.source);
            const tgtNode = nodes.find(n => n.id === edge.target);
            content = (
                <div className="p-4 flex flex-col gap-4">
                    <div>
                        <div className="text-[10px] font-semibold text-gray-400 tracking-wider mb-1">CONNECTION TYPE</div>
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
                    {onDeleteEdge && (
                        <button onClick={() => onDeleteEdge(edge.id)} className="mt-4 flex items-center justify-center px-3 py-2 bg-red-900/20 text-red-400 border border-red-900/50 hover:bg-red-900/40 rounded transition-colors text-xs font-bold tracking-wider">
                            DISCONNECT
                        </button>
                    )}
                </div>
            );
        }
    } else {"""

match = re.search(r'if \(!selectedNode\) \{([\s\S]*?)\} else \{', text)
if match:
    text = text.replace(match.group(0), new_empty_check)

with open('frontend/src/components/PlantBuilder/Inspector.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
