import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace actual literal newlines inside strings with \\n
def replacer(match):
    s = match.group(0)
    # Don't replace newlines in template literals, they are valid in JS!
    if s.startswith('`'): return s
    return s.replace('\n', '\\n')

text = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', replacer, text, flags=re.DOTALL)
text = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", replacer, text, flags=re.DOTALL)

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
