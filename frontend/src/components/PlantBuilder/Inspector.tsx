import type { EquipmentNode, ValidationResult, EngineeringQuantity } from '../../types/topology';
import type { NodeTelemetry } from '../../types';
import { Settings2, Zap, ShieldAlert, ChevronRight, Target } from 'lucide-react';

interface InspectorProps {
    selectedNode: (EquipmentNode & { liveTelemetry?: NodeTelemetry }) | null;
    selectedEdge?: string | null;
    edges?: any[];
    nodes?: any[];
    onDeleteEdge?: (id: string) => void;
    validation: ValidationResult | null;
    isOpen: boolean;
    setIsOpen: (open: boolean) => void;
}

export const Inspector = ({ selectedNode, selectedEdge, edges, nodes, onDeleteEdge, validation, isOpen, setIsOpen }: InspectorProps) => {

    if (!isOpen) {
        return (
            <div className="w-12 bg-industrial-800 border-l border-industrial-700 flex flex-col h-full items-center py-3 transition-all duration-300 flex-shrink-0">
                <button onClick={() => setIsOpen(true)} className="p-2 bg-industrial-900 border border-industrial-700 hover:border-blue-500 rounded text-gray-400 hover:text-white mb-2 shadow-sm" title="Open Inspector">
                    <Settings2 className="w-5 h-5" />
                </button>
            </div>
        );
    }

    if (!selectedNode && !selectedEdge) {
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


    if (!selectedNode) return null;

    const issues = validation?.issues.filter(i => i.node_id === selectedNode.id) || [];
    
    return (
        <div className="w-80 bg-industrial-800 border-l border-industrial-700 flex flex-col h-full transition-all duration-300 flex-shrink-0">
            {/* HEADER */}
            <div className="h-10 border-b border-industrial-700 flex items-center justify-between px-3 bg-industrial-900/50">
                <div className="flex items-center text-xs font-semibold uppercase tracking-widest text-gray-300">
                    <Target className="w-3.5 h-3.5 mr-2 opacity-70" />
                    {selectedNode.id}
                </div>
                <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-industrial-700 rounded text-gray-400 hover:text-white" title="Collapse Inspector">
                    <ChevronRight className="w-4 h-4" />
                </button>
            </div>
            
            <div className="px-4 py-3 border-b border-industrial-700 bg-industrial-800">
                <div className="text-sm font-semibold text-gray-100">{selectedNode.name}</div>
                <div className="text-[10px] font-semibold tracking-widest uppercase text-gray-500 mt-0.5">
                    {selectedNode.component_class.replace(/_/g, ' ')}
                </div>
            </div>

            {/* CONTENT */}
            <div className="flex-1 overflow-y-auto">
                {(() => {
                    const liveTelemetry = selectedNode.liveTelemetry;
                    if (!liveTelemetry) return null;
                    return (
                        <div className="p-3 border-b border-industrial-700 bg-industrial-900/60">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-semibold uppercase tracking-widest text-emerald-400 flex items-center gap-1.5">
                                    <span className={`w-2 h-2 rounded-full ${liveTelemetry.status === 'RUNNING' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
                                    Live Telemetry
                                </span>
                                <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60">
                                    {liveTelemetry.status}
                                </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                                <div className="bg-industrial-800 p-2 rounded border border-industrial-700">
                                    <div className="text-[10px] text-gray-400 uppercase">Power Draw</div>
                                    <div className="text-amber-400 font-bold mt-0.5">
                                        {liveTelemetry.power_mw > 0 ? `${liveTelemetry.power_mw} MW` : `${liveTelemetry.power_kw} kW`}
                                    </div>
                                </div>
                                <div className="bg-industrial-800 p-2 rounded border border-industrial-700">
                                    <div className="text-[10px] text-gray-400 uppercase">Temperature</div>
                                    <div className="text-rose-400 font-bold mt-0.5">
                                        {liveTelemetry.temperature_c} °C
                                    </div>
                                </div>
                                <div className="bg-industrial-800 p-2 rounded border border-industrial-700">
                                    <div className="text-[10px] text-gray-400 uppercase">Throughput</div>
                                    <div className="text-blue-400 font-bold mt-0.5">
                                        {liveTelemetry.throughput_tph} t/h
                                    </div>
                                </div>
                                <div className="bg-industrial-800 p-2 rounded border border-industrial-700">
                                    <div className="text-[10px] text-gray-400 uppercase">Water Flow</div>
                                    <div className="text-cyan-400 font-bold mt-0.5">
                                        {liveTelemetry.water_m3h} m³/h
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })()}
                
                {/* STATUS & VALIDATION */}
                {issues.length > 0 && (
                    <div className="p-3 border-b border-industrial-700">
                        <div className="flex items-center text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">
                            <ShieldAlert className="w-3.5 h-3.5 mr-1.5" /> Validation
                        </div>
                        <div className="space-y-1.5">
                            {issues.map((iss, i) => (
                                <div key={i} className={`px-2 py-1.5 rounded border text-xs ${iss.level === 'ERROR' ? 'bg-red-900/20 border-red-900/50 text-red-300' : 'bg-amber-900/20 border-amber-900/50 text-amber-300'}`}>
                                    <div className="font-semibold text-[10px] tracking-wider mb-0.5">{iss.issue_code}</div>
                                    <div className="leading-tight text-[11px]">{iss.message}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* ENGINEERING PARAMETERS */}
                <div className="p-3 border-b border-industrial-700">
                    <div className="flex items-center text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-3">
                        <Settings2 className="w-3.5 h-3.5 mr-1.5" /> Configured Assumptions
                    </div>
                    {Object.keys(selectedNode.parameters || {}).length === 0 ? (
                        <div className="text-[11px] text-gray-500 italic">No engineering parameters configured.</div>
                    ) : (
                        <div className="space-y-2">
                            {Object.entries(selectedNode.parameters).map(([key, qty]: [string, EngineeringQuantity]) => (
                                <div key={key} className="flex justify-between items-center group">
                                    <label className="text-xs text-gray-300 truncate pr-2 group-hover:text-white transition-colors">{qty.display_name}</label>
                                    <div className="flex items-center flex-shrink-0">
                                        <div className="bg-industrial-900 border border-industrial-700 rounded-l px-2 py-1 text-[11px] font-mono text-gray-200 w-16 text-right">
                                            {qty.value}
                                        </div>
                                        <div className="bg-industrial-700 border border-industrial-700 border-l-0 rounded-r px-1.5 py-1 text-[10px] font-semibold text-gray-400 w-10 text-center uppercase">
                                            {qty.unit}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* PORTS */}
                <div className="p-3 border-b border-industrial-700">
                    <div className="flex items-center text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-3">
                        <Zap className="w-3.5 h-3.5 mr-1.5" /> Connectivity
                    </div>
                    <div className="space-y-1">
                        {selectedNode.ports.map(p => (
                            <div key={p.id} className="flex items-center justify-between bg-industrial-900/30 border border-industrial-700/50 rounded px-2 py-1.5">
                                <span className="text-[11px] text-gray-300 font-medium">{p.id}</span>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-[9px] text-gray-500 uppercase tracking-widest">{p.direction}</span>
                                    <span className={`text-[9px] font-semibold uppercase tracking-wider px-1 rounded ${
                                        p.type === 'MATERIAL' ? 'bg-blue-900/40 text-blue-400' :
                                        p.type === 'ELECTRICAL' ? 'bg-yellow-900/40 text-yellow-400' :
                                        p.type === 'WATER' ? 'bg-cyan-900/40 text-cyan-400' : 'bg-purple-900/40 text-purple-400'
                                    }`}>
                                        {p.type}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
};
