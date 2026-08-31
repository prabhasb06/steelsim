import os
import re

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

bp_reps = [
    ("fitView({ padding: 0.2 })", "fitView({ padding: 0.2, minZoom: 0.8, maxZoom: 1.2, duration: 800 })"),
    ("fitView({ padding: 0.2, duration: 800 })", "fitView({ padding: 0.2, minZoom: 0.8, maxZoom: 1.2, duration: 800 })"),
    ("fitView({ padding: 0.2, duration: 400 })", "fitView({ padding: 0.2, minZoom: 0.8, maxZoom: 1.2, duration: 400 })")
]

replace_in_file("frontend/src/components/PlantBuilder/Blueprint.tsx", bp_reps)
