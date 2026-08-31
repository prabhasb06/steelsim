import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

def replacer(match):
    s = match.group(0)
    # Replace literal newlines with \n
    return s.replace('\n', '\\n')

# Find string literals starting with double quotes or single quotes
text = re.sub(r'\"[^\"]*\"', replacer, text)
text = re.sub(r'\'[^\']*\'', replacer, text)

# Fix the ErrorBoundary JSX
text = text.replace('    <ErrorBoundary>', '    <ErrorBoundary>') # no op
text = text.replace('      </ErrorBoundary>', '      </ErrorBoundary>') 

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
