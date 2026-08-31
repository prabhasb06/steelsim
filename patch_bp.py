import os

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('return (\n      <div className="flex-1 relative bg-industrial-900"', 'return (\n    <ErrorBoundary>\n      <div className="flex-1 relative bg-industrial-900"')

# The component ends with:
#       </div>
#   );
# }

text = text.replace('      </div>\n  );\n}', '      </div>\n    </ErrorBoundary>\n  );\n}')

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
