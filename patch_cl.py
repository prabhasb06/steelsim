import os

text = open('frontend/src/components/PlantBuilder/ComponentLibrary.tsx', 'r', encoding='utf-8').read()
text = text.replace('interface ComponentLibraryProps {', 'interface ComponentLibraryProps {\n    onAddClick?: (c_class: string) => void;')
text = text.replace(
'''                            <div className="flex gap-1 ml-2 flex-shrink-0">
                                {matPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-blue-900/40 text-blue-400 font-semibold" title="Material Ports">M{matPorts}</span>}
                                {elecPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-yellow-900/40 text-yellow-400 font-semibold" title="Electrical Ports">E{elecPorts}</span>}
                                {waterPorts > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-cyan-900/40 text-cyan-400 font-semibold" title="Water Ports">W{waterPorts}</span>}
                            </div>''',
'''                            <div className="flex gap-1 ml-2 flex-shrink-0 items-center">
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
                            </div>'''
)
text = text.replace('export const ComponentLibrary = ({ isOpen, setIsOpen }: ComponentLibraryProps) => {', 'export const ComponentLibrary = ({ isOpen, setIsOpen, onAddClick }: ComponentLibraryProps) => {')

open('frontend/src/components/PlantBuilder/ComponentLibrary.tsx', 'w', encoding='utf-8').write(text)
