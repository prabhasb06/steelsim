import React, { useEffect, useState } from 'react';
import { Layers, ChevronLeft, Search } from 'lucide-react';
import { apiRequest } from '../../api';

interface ComponentLibraryProps {
    onAddClick?: (c_class: string) => void;
    isOpen: boolean;
    setIsOpen: (open: boolean) => void;
}

export const ComponentLibrary = ({ isOpen, setIsOpen, onAddClick }: ComponentLibraryProps) => {
    const [templates, setTemplates] = useState<Record<string, any>>({});
    const [search, setSearch] = useState('');
    const [loadError, setLoadError] = useState<string | null>(null);

    useEffect(() => {
        apiRequest<Record<string, any>>('/api/plant/templates')
            .then(data => setTemplates(data))
            .catch(error => setLoadError(error instanceof Error ? error.message : 'Unable to load components.'));
    }, []);

    const onDragStart = (event: React.DragEvent, c_class: string) => {
        event.dataTransfer.setData('application/reactflow', c_class);
        event.dataTransfer.effectAllowed = 'move';
    };

    const filtered = Object.entries(templates).filter(([k, v]) => 
        k.toLowerCase().includes(search.toLowerCase()) || 
        v.name.toLowerCase().includes(search.toLowerCase())
    );

    if (!isOpen) {
        return (
            <div className="w-12 bg-industrial-800 border-r border-industrial-700 flex flex-col h-full items-center py-3 transition-all duration-300 flex-shrink-0">
                <button onClick={() => setIsOpen(true)} className="p-2 bg-industrial-900 border border-industrial-700 hover:border-blue-500 rounded text-gray-400 hover:text-white mb-2 shadow-sm" title="Open Component Library">
                    <Layers className="w-5 h-5" />
                </button>
            </div>
        );
    }

    return (
        <div className="w-64 bg-industrial-800 border-r border-industrial-700 flex flex-col h-full transition-all duration-300 flex-shrink-0 relative">
            <div className="h-10 border-b border-industrial-700 flex items-center justify-between px-3 bg-industrial-900/50">
                <div className="flex items-center">
                    <Layers className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-xs font-semibold text-gray-300 uppercase tracking-widest">Library</span>
                </div>
                <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-industrial-700 rounded text-gray-400 hover:text-white" title="Collapse Library">
                    <ChevronLeft className="w-4 h-4" />
                </button>
            </div>
            
            <div className="p-3 border-b border-industrial-700">
                <div className="relative">
                    <Search className="w-3.5 h-3.5 absolute left-2 top-2 text-gray-500" />
                    <input 
                        type="text" 
                        placeholder="Search components..." 
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-industrial-900 border border-industrial-700 rounded pl-7 pr-2 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
                {loadError && <div role="alert" className="rounded border border-red-800 bg-red-950/50 p-2 text-xs text-red-200">{loadError}</div>}
                {filtered.map(([c_class, tpl]) => {
                    const matPorts = tpl.ports.filter((p:any) => p.type === 'MATERIAL').length;
                    const elecPorts = tpl.ports.filter((p:any) => p.type === 'ELECTRICAL').length;
                    const waterPorts = tpl.ports.filter((p:any) => p.type === 'WATER').length;
                    
                    return (
                        <div 
                            key={c_class}
                            className="bg-industrial-900/50 border border-industrial-700 p-2 rounded cursor-grab hover:border-blue-500 hover:bg-industrial-700 transition-colors flex items-center"
                            onDragStart={(e) => onDragStart(e, c_class)}
                            draggable
                        >
                            <div className="flex-1 min-w-0">
                                <div className="text-[11px] font-semibold text-gray-200 truncate">{tpl.name}</div>
                                <div className="text-[9px] text-gray-500 uppercase tracking-widest truncate">{c_class.replace(/_/g, ' ')}</div>
                            </div>
                            <div className="flex gap-1 ml-2 flex-shrink-0 items-center">
                                {matPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-blue-900/40 text-blue-400 font-semibold" title="Material Ports">M{matPorts}</span>}
                                {elecPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-yellow-900/40 text-yellow-400 font-semibold" title="Electrical Ports">E{elecPorts}</span>}
                                {waterPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-cyan-900/40 text-cyan-400 font-semibold" title="Water Ports">W{waterPorts}</span>}
                                <button 
                                    onClick={(e) => { e.stopPropagation(); if (onAddClick) onAddClick(c_class); }}
                                    className="ml-1 px-1.5 py-0.5 bg-industrial-700 hover:bg-blue-600 rounded text-[10px] font-bold text-white transition-colors"
                                    title="Add to Canvas"
                                >
                                    +
                                </button>
                            </div>
                        </div>
                    );
                })}
                {filtered.length === 0 && (
                    <div className="text-center text-xs text-gray-500 mt-4">No components found.</div>
                )}
            </div>
        </div>
    );
};
