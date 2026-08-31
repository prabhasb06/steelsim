import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

replacements = [
    ("type ViewMode = 'OVERVIEW' | 'BUILDER' | 'SIMULATION';", "type ViewMode = 'OVERVIEW' | 'BUILDER' | 'SIMULATION' | 'OPTIMIZATION';"),
    
    ("<NavItem icon={<Cpu />} label=\"AI Builder\" disabled />", "<NavItem icon={<Cpu />} label=\"Optimize Plant\" active={viewMode==='OPTIMIZATION'} onClick={() => setViewMode('OPTIMIZATION')} />"),
    
    ("const handleCreate = async () => {", """const handleCreate = async () => {
    if (!topologyValidation || !topologyValidation.is_valid) {
      alert("SIMULATION BLOCKED\\n\\nTopology errors detected. Fix these issues in the Validation Panel before simulation can begin.");
      return;
    }"""),

    ("viewMode === 'SIMULATION' ? 'Simulation Console' : 'Overview'", "viewMode === 'SIMULATION' ? 'Simulation Console' : viewMode === 'OPTIMIZATION' ? 'AI Optimization & Setup' : 'Overview'"),

    ("{/* SIMULATION VIEW */}", """{/* OPTIMIZATION VIEW */}
          {viewMode === 'OPTIMIZATION' && (
            <div className="absolute inset-0 overflow-auto p-6 flex flex-col space-y-6">
              <div className="bg-industrial-800 border border-industrial-700 rounded-md p-6 shadow-lg max-w-4xl">
                <h2 className="text-xl font-semibold mb-4 flex items-center"><Cpu className="w-6 h-6 mr-3 text-blue-500" /> AI Optimization Architecture</h2>
                <p className="text-sm text-gray-400 mb-8 leading-relaxed">
                  Define optimization objectives and structural constraints. AI proposals are deterministically validated before they can be applied.
                </p>

                <div className="space-y-6">
                  <div className="p-4 border border-industrial-700 bg-industrial-900/50 rounded">
                    <div className="text-sm font-bold text-gray-300 mb-2">Throughput Maximization</div>
                    <div className="text-xs text-amber-500 font-mono">STATUS: REQUIRES PRODUCTION ENGINE</div>
                    <p className="text-xs text-gray-500 mt-2">Evaluates material bottlenecks and recommends capacity adjustments.</p>
                  </div>
                  
                  <div className="p-4 border border-industrial-700 bg-industrial-900/50 rounded">
                    <div className="text-sm font-bold text-gray-300 mb-2">Energy per Tonne Minimization</div>
                    <div className="text-xs text-amber-500 font-mono">STATUS: REQUIRES ENERGY ENGINE</div>
                    <p className="text-xs text-gray-500 mt-2">Adjusts reheating curves and electrical loads to minimize power draw.</p>
                  </div>
                  
                  <div className="p-4 border border-industrial-700 bg-industrial-900/50 rounded">
                    <div className="text-sm font-bold text-gray-300 mb-2">Maintenance Scheduling Optimization</div>
                    <div className="text-xs text-amber-500 font-mono">STATUS: REQUIRES RELIABILITY ENGINE</div>
                    <p className="text-xs text-gray-500 mt-2">Calculates MTBF-based optimal downtime windows.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SIMULATION VIEW */}""")
]

replace_in_file("src/App.tsx", replacements)
