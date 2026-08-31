import os

file_path = "src/App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix unused AlertTriangle
text = text.replace("Truck, AlertTriangle", "Truck")

# Fix type imports
text = text.replace("import { SimulationState, SimulationSnapshot, SimulationEvent, SimulationStatus } from './types';", "import type { SimulationState, SimulationSnapshot, SimulationEvent } from './types';")

# Fix ref type
text = text.replace("const eventsEndRef = useRef<HTMLDivElement>(null);", "const eventsEndRef = useRef<HTMLTableRowElement>(null);")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
