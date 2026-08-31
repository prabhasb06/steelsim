import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

new_alert = """      if (pTypeSource !== pTypeTarget) {
          alert(`CONNECTION REJECTED\\n\\nCannot connect ${pTypeSource} out to ${pTypeTarget} in.`);
          return;
      }"""

text = re.sub(r'      if \(pTypeSource !== pTypeTarget\) \{[\s\S]*?\}', new_alert, text)

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
