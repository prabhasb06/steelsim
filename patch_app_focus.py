import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        if old not in text:
            print(f"WARNING: String not found in {filepath}:\n{old[:50]}...")
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

app_reps = [
    ("  const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');",
     "  const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');\n  const [isFocusMode, setIsFocusMode] = useState(false);\n  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);"),

    ("      <div className=\"w-16 md:w-64 bg-industrial-800 border-r border-industrial-700 flex flex-col z-10 transition-all\">",
     "      {!isFocusMode && (\n      <div className={`bg-industrial-800 border-r border-industrial-700 flex flex-col z-10 transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-16 md:w-64'}`}>"),
     
    ("        <div className=\"h-14 flex items-center px-4 border-b border-industrial-700 bg-industrial-900\">\n          <Factory className=\"w-6 h-6 text-blue-500 mr-3\" />\n          <span className=\"font-bold text-lg tracking-tight hidden md:inline\">SteelSim</span>",
     "        <div className=\"h-14 flex items-center justify-between px-4 border-b border-industrial-700 bg-industrial-900\">\n          <div className=\"flex items-center cursor-pointer\" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>\n            <Factory className=\"w-6 h-6 text-blue-500 mr-3\" />\n            <span className={`font-bold text-lg tracking-tight ${sidebarCollapsed ? 'hidden' : 'hidden md:inline'}`}>SteelSim</span>\n          </div>"),
     
    ("          <NavItem icon={<Truck />} label=\"Logistics\" disabled />\n        </div>\n      </div>",
     "          <NavItem icon={<Truck />} label=\"Logistics\" disabled />\n        </div>\n      </div>\n      )}"),
     
    ("          {/* BUILDER VIEW */}\n          {viewMode === 'BUILDER' && (\n            <div className=\"absolute inset-0 flex\">\n              <ComponentLibrary />\n              <div className=\"flex-1 flex flex-col relative\">\n                <Blueprint setValidation={setTopologyValidation} />",
     "          {/* BUILDER VIEW */}\n          {viewMode === 'BUILDER' && (\n            <div className=\"absolute inset-0 flex flex-col\">\n                <Blueprint setValidation={setTopologyValidation} isFocusMode={isFocusMode} setIsFocusMode={setIsFocusMode} />"),
     
    ("              </div>\n            </div>\n          )}",
     "            </div>\n          )}")
]

replace_in_file("frontend/src/App.tsx", app_reps)
