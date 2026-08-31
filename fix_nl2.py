import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

def replacer(match):
    s = match.group(0)
    return s.replace('\n', '\\n')

text = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', replacer, text, flags=re.DOTALL)
text = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", replacer, text, flags=re.DOTALL)

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
