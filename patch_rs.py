import os

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'BILLET_YARD': 'BY'", "'RAW_MATERIAL_STORAGE': 'RS', 'BILLET_YARD': 'BY'")

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
