import os
import re

def replace_app():
    with open("frontend/src/App.tsx", "r", encoding="utf-8") as f:
        text = f.read()

    # Add focus mode state
    text = text.replace(
        "const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');",
        "const [viewMode, setViewMode] = useState<ViewMode>('BUILDER');\n  const [isFocusMode, setIsFocusMode] = useState(false);\n  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);"
    )

    # Hide sidebar in focus mode and support collapse
    text = text.replace(
        '<div className="w-16 md:w-64 bg-industrial-800 border-r border-industrial-700 flex flex-col z-10 transition-all">',
        '{!isFocusMode && (\n      <div className={`bg-industrial-800 border-r border-industrial-700 flex flex-col z-10 transition-all duration-300 ${sidebarCollapsed ? \'w-16\' : \'w-16 md:w-64\'}`}>'
    )

    text = text.replace(
        '<Factory className="w-6 h-6 text-blue-500 mr-3" />\n          <span className="font-bold text-lg tracking-tight hidden md:inline">SteelSim</span>',
        '<div className="flex items-center cursor-pointer overflow-hidden" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>\n            <Factory className="w-6 h-6 text-blue-500 mr-3 flex-shrink-0" />\n            <span className={`font-bold text-lg tracking-tight ${sidebarCollapsed ? \'hidden\' : \'hidden md:inline whitespace-nowrap\'}`}>SteelSim</span>\n          </div>'
    )
    
    text = text.replace(
        '<NavItem icon={<Truck />} label="Logistics" disabled />\n        </div>\n      </div>',
        '<NavItem icon={<Truck />} label="Logistics" disabled />\n        </div>\n      </div>\n      )}'
    )

    # Hide top bar in focus mode
    text = text.replace(
        '<div className="h-14 border-b border-industrial-700 bg-industrial-800 flex items-center justify-between px-6 z-0">',
        '{!isFocusMode && (\n        <div className="h-14 border-b border-industrial-700 bg-industrial-800 flex items-center justify-between px-6 z-0">'
    )
    
    text = text.replace(
        '</span>\n            </div>\n          </div>\n        </div>',
        '</span>\n            </div>\n          </div>\n        </div>\n        )}'
    )

    # Move ComponentLibrary into Blueprint and pass focusMode props
    text = text.replace(
        '''          {/* BUILDER VIEW */}
          {viewMode === 'BUILDER' && (
            <div className="absolute inset-0 flex">
              <ComponentLibrary />
              <div className="flex-1 flex flex-col relative">
                <Blueprint setValidation={setTopologyValidation} />
              </div>
            </div>
          )}''',
        '''          {/* BUILDER VIEW */}
          {viewMode === 'BUILDER' && (
            <div className="absolute inset-0 flex flex-col">
                <Blueprint 
                  setValidation={setTopologyValidation} 
                  isFocusMode={isFocusMode} 
                  setIsFocusMode={setIsFocusMode} 
                />
            </div>
          )}'''
    )
    
    # Remove unused ComponentLibrary import
    text = text.replace("import { ComponentLibrary } from './components/PlantBuilder/ComponentLibrary';\n", "")

    with open("frontend/src/App.tsx", "w", encoding="utf-8") as f:
        f.write(text)

replace_app()
