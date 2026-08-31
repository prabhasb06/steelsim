import os
import re

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

app_reps = [
    ("import { LayoutDashboard, Factory, Activity, Truck, Settings, AlertCircle, Wrench, Shield, Zap, Cpu, Play, Pause, RotateCcw } from 'lucide-react';",
     "import { LayoutDashboard, Factory, Activity, Truck, Wrench, Shield, Zap, Cpu, Play, Pause, RotateCcw } from 'lucide-react';")
]
replace_in_file("frontend/src/App.tsx", app_reps)

bp_reps = [
    ("  Controls, \n  Panel,\n", ""),
    ("  Connection, \n  Edge, \n", "  type Connection, \n  type Edge, \n"),
    ("  XYPosition\n", ""),
    ("import { EquipmentNode, ValidationResult } from '../../types/topology';",
     "import type { ValidationResult } from '../../types/topology';"),
    ("LayoutTemplate, Play, RotateCcw, Maximize, Minimize, Crosshair",
     "LayoutTemplate, RotateCcw, Crosshair"),
    ("const [isFullscreen, setIsFullscreen] = useState(false);",
     ""),
    ("  useEffect(() => {\n    const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);\n    document.addEventListener('fullscreenchange', onFullscreenChange);\n    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);\n  }, []);",
     ""),
    ("  const toggleFullscreen = () => {\n    if (!document.fullscreenElement) {\n        containerRef.current?.requestFullscreen().catch(err => console.error(err));\n    } else {\n        document.exitFullscreen().catch(err => console.error(err));\n    }\n  };\n",
     "")
]
replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", bp_reps)

cl_reps = [
    ("import { Layers, ChevronLeft, ChevronRight, Search } from 'lucide-react';",
     "import { Layers, ChevronLeft, Search } from 'lucide-react';")
]
replace_in_file("frontend/src/components/PlantBuilder/ComponentLibrary.tsx", cl_reps)

ins_reps = [
    ("<span className=\"text-[11px] text-gray-300 font-medium\">{p.name || p.id}</span>",
     "<span className=\"text-[11px] text-gray-300 font-medium\">{p.id}</span>")
]
replace_in_file("frontend/src/components/PlantBuilder/Inspector.tsx", ins_reps)

