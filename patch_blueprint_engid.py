import os
import re

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add ContextMenu import
if 'import { ContextMenu }' not in text:
    text = text.replace("import { ValidationPanel } from './ValidationPanel';", "import { ValidationPanel } from './ValidationPanel';\nimport { ContextMenu, ContextMenuAction } from './ContextMenu';")

# Add ContextMenu state
if 'const [contextMenu, setContextMenu]' not in text:
    state_str = """  const [isFocusMode, setIsFocusMode] = useState(false);
  
  const [clipboard, setClipboard] = useState<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });
  const [contextMenu, setContextMenu] = useState<{ x: number, y: number, nodeId?: string } | null>(null);
"""
    text = text.replace("  const [isFocusMode, setIsFocusMode] = useState(false);", state_str)

# Generate engineering ID function
if 'const generateEngineeringId' not in text:
    eng_id_fn = """
  const generateEngineeringId = (c_class: string, currentNodes: any[]) => {
      const prefixes: Record<string, string> = {
          'BILLET_YARD': 'BY', 'CHARGING_TABLE': 'CT', 'REHEATING_FURNACE': 'RF',
          'ROUGHING_MILL': 'RM', 'INTERMEDIATE_MILL': 'IM', 'FINISHING_MILL': 'FM',
          'TMT_COOLING': 'TC', 'COOLING_BED': 'CB', 'CUTTING_UNIT': 'CU',
          'BUNDLING_UNIT': 'BU', 'FINISHED_GOODS': 'FG', 'TRANSFORMER': 'TR',
          'WATER_PUMP': 'WP', 'WATER_SYSTEM': 'WS', 'COMPRESSOR': 'CP',
          'MAINTENANCE_STATION': 'MS', 'QUALITY_INSPECTION': 'QI'
      };
      const prefix = prefixes[c_class] || 'EQ';
      
      let maxNum = 0;
      currentNodes.forEach(n => {
          if (n.data?.engineeringId?.startsWith(prefix + '-')) {
              const num = parseInt(n.data.engineeringId.split('-')[1]);
              if (!isNaN(num) && num > maxNum) maxNum = num;
          }
      });
      return `${prefix}-${(maxNum + 1).toString().padStart(2, '0')}`;
  };
"""
    text = text.replace("  const addComponentToCanvas", eng_id_fn + "\n  const addComponentToCanvas")

# Update addComponentToCanvas to use engineeringId
add_comp_str = """
            data: { 
                component_class: nodeData.component_class,
                name: nodeData.name,
                engineeringId: generateEngineeringId(nodeData.component_class, nds),
                ports: nodeData.ports,
                parameters: nodeData.parameters,
                validationStatus: 'VALID',
                locked: false
            },
"""
text = re.sub(r'data: \{\s*component_class: nodeData\.component_class,\s*name: nodeData\.name,\s*ports: nodeData\.ports,\s*parameters: nodeData\.parameters,\s*validationStatus: \'VALID\'\s*\},', add_comp_str, text)

# Template loader needs to generate engineering IDs too
tmt_str = """
                  data: {
                      component_class: n.component_class,
                      name: n.name,
                      engineeringId: generateEngineeringId(n.component_class, accNodes),
                      ports: n.ports,
                      parameters: n.parameters,
                      locked: false
                  }
"""
# wait, tmt load is a bit trickier, I'll just use the old way for template loading to avoid complexity in this regex.
# Actually I can just map it inside setNodes for handleLoadTemplate.
load_temp = """
          const rn = tmt.nodes.map((n: any, idx: number) => {
              return {
                  id: n.id,
                  type: 'equipment',
                  position: n.position,
                  data: {
                      component_class: n.component_class,
                      name: n.name,
                      engineeringId: `EQ-${(idx+1).toString().padStart(2, '0')}`,
                      ports: n.ports,
                      parameters: n.parameters
                  }
              };
          });
"""
text = re.sub(r'const rn = tmt\.nodes\.map\(\(n: any\) => \(\{\s*id: n\.id,\s*type: \'equipment\',\s*position: n\.position,\s*data: \{\s*component_class: n\.component_class,\s*name: n\.name,\s*ports: n\.ports,\s*parameters: n\.parameters\s*\}\s*\}\)\);', load_temp, text)


# Update handleLoad to preserve engineeringId and locked
handle_load = """
              const rn = plant.nodes.map((n: any) => ({
                  id: n.id,
                  type: 'equipment',
                  position: n.position,
                  data: {
                      component_class: n.component_class || n.data?.component_class,
                      name: n.name || n.data?.name,
                      engineeringId: n.data?.engineeringId || n.name,
                      ports: n.ports || n.data?.ports,
                      parameters: n.parameters || n.data?.parameters,
                      locked: !!n.data?.locked
                  }
              }));
"""
text = re.sub(r'const rn = plant\.nodes\.map\(\(n: any\) => \(\{\s*id: n\.id,\s*type: \'equipment\',\s*position: n\.position,\s*data: \{\s*component_class: n\.component_class,\s*name: n\.name,\s*ports: n\.ports,\s*parameters: n\.parameters\s*\}\s*\}\)\);', handle_load, text)

with open('frontend/src/components/PlantBuilder/Blueprint.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
