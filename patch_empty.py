import os

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

empty_placeholder = """
                    {nodes.length === 0 && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                            <div className="text-center text-gray-400 p-8 rounded bg-industrial-900/50 border border-industrial-800/50 backdrop-blur-sm">
                                <h3 className="text-lg font-bold text-gray-300 mb-2">Start building your plant</h3>
                                <p className="text-sm mb-4">Drag equipment from Library or click + to add equipment</p>
                                <div className="flex justify-center gap-4 pointer-events-auto">
                                    <button onClick={() => setLibraryOpen(true)} className="px-4 py-2 bg-industrial-800 border border-industrial-700 rounded hover:bg-industrial-700 transition-colors text-sm">Open Library</button>
                                    <button onClick={handleLoadTemplate} className="px-4 py-2 bg-blue-900/40 border border-blue-900 rounded hover:bg-blue-800/50 transition-colors text-blue-400 text-sm">Load TMT Template</button>
                                </div>
                            </div>
                        </div>
                    )}
"""

if 'Start building your plant' not in text:
    text = text.replace('</ReactFlow>', empty_placeholder + '\n                    </ReactFlow>')

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
