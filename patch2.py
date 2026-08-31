import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific start
pattern = r"return \(\s*<div className=\{\`flex-1 h-full flex flex-col bg\[#121315\] \$\{isFocusMode \? 'fixed inset-0 z-50' : ''\}\`\} ref=\{containerRef\}>"
replacement = r"return (\n    <ErrorBoundary>\n      <div className={`flex-1 h-full flex flex-col bg-[#121315] ${isFocusMode ? 'fixed inset-0 z-50' : ''}`} ref={containerRef}>"

text = re.sub(pattern, replacement, text)
text = text.replace('console.log("handleDeleteEdge");', '')

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
