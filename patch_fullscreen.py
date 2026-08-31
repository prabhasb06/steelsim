import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        if old not in text:
            print(f"WARNING: '{old[:30]}' not found!")
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

bp_reps = [
    ("import { Play, RotateCcw, Network, LayoutTemplate, Undo2, Redo2, Save, FolderOpen, Wand2 } from 'lucide-react';",
     "import { Play, RotateCcw, Network, LayoutTemplate, Undo2, Redo2, Save, FolderOpen, Wand2, Maximize, Minimize } from 'lucide-react';"),
    
    ("const BlueprintCanvas = ({ setValidation }: { setValidation: (v: ValidationResult | null) => void }) => {",
     "const BlueprintCanvas = ({ setValidation }: { setValidation: (v: ValidationResult | null) => void }) => {\n  const containerRef = useRef<HTMLDivElement>(null);\n  const [isFullscreen, setIsFullscreen] = useState(false);\n\n  useEffect(() => {\n    const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);\n    document.addEventListener('fullscreenchange', onFullscreenChange);\n    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);\n  }, []);\n\n  const toggleFullscreen = () => {\n    if (!document.fullscreenElement) {\n        containerRef.current?.requestFullscreen().catch(err => console.error(err));\n    } else {\n        document.exitFullscreen().catch(err => console.error(err));\n    }\n  };"),
     
    ("  return (\n    <div className=\"flex-1 h-full flex flex-col\">\n      <div className=\"flex-1 flex flex-row min-h-0\">",
     "  return (\n    <div className=\"flex-1 h-full flex flex-col bg-[#121315]\" ref={containerRef}>\n      <div className=\"flex-1 flex flex-row min-h-0\">"),
     
    ("            <div className=\"flex gap-2 justify-end\">\n                <button onClick={handleLoadTemplate} className=\"flex items-center px-3 py-1.5 bg-blue-600 border border-blue-500 text-white text-xs rounded hover:bg-blue-500 transition-colors\">\n                    <Play className=\"w-3.5 h-3.5 mr-2\" /> Demo Plant\n                </button>\n                <button onClick={() => { setNodes([]); setEdges([]); setValidation(null); saveHistory([], []); }} className=\"flex items-center px-3 py-1.5 bg-red-900/50 border border-red-900 text-red-300 text-xs rounded hover:bg-red-800 transition-colors\">\n                    <RotateCcw className=\"w-3.5 h-3.5 mr-2\" /> Clear\n                </button>\n            </div>",
     "            <div className=\"flex gap-2 justify-end\">\n                <button onClick={handleLoadTemplate} className=\"flex items-center px-3 py-1.5 bg-blue-600 border border-blue-500 text-white text-xs rounded hover:bg-blue-500 transition-colors\">\n                    <Play className=\"w-3.5 h-3.5 mr-2\" /> Demo Plant\n                </button>\n                <button onClick={() => { setNodes([]); setEdges([]); setValidation(null); saveHistory([], []); }} className=\"flex items-center px-3 py-1.5 bg-red-900/50 border border-red-900 text-red-300 text-xs rounded hover:bg-red-800 transition-colors\">\n                    <RotateCcw className=\"w-3.5 h-3.5 mr-2\" /> Clear\n                </button>\n                <button onClick={toggleFullscreen} className=\"flex items-center px-2 py-1.5 bg-industrial-800 border border-industrial-700 text-gray-300 text-xs rounded hover:bg-industrial-700 transition-colors\" title=\"Toggle Fullscreen\">\n                    {isFullscreen ? <Minimize className=\"w-4 h-4\" /> : <Maximize className=\"w-4 h-4\" />}\n                </button>\n            </div>")
]

replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", bp_reps)
