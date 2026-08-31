import os

with open('app/engine/auto_connect.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

old_logic = """                    src = water_providers[0]
                    src_port = next(p for p in src.ports if p.type == PortType.WATER and p.direction == PortDirection.OUT)
                    tgt_port = next(p for p in node.ports if p.type == PortType.WATER and p.direction == PortDirection.IN)"""

new_logic = """                    # Pick a provider that is not the node itself
                    src = next((p for p in water_providers if p.id != node.id), None)
                    if src:
                        src_port = next(p for p in src.ports if p.type == PortType.WATER and p.direction == PortDirection.OUT)
                        tgt_port = next(p for p in node.ports if p.type == PortType.WATER and p.direction == PortDirection.IN)
                    else:
                        proposal.missing_utilities.append(f"{node.name} requires Cooling Water")
                        continue"""

text = text.replace(old_logic, new_logic)

old_logic_e = """                    src = elec_providers[0]
                    src_port = next(p for p in src.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.OUT)
                    tgt_port = next(p for p in node.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.IN)"""

new_logic_e = """                    src = next((p for p in elec_providers if p.id != node.id), None)
                    if src:
                        src_port = next(p for p in src.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.OUT)
                        tgt_port = next(p for p in node.ports if p.type == PortType.ELECTRICAL and p.direction == PortDirection.IN)
                    else:
                        proposal.missing_utilities.append(f"{node.name} requires Electrical Supply")
                        continue"""

text = text.replace(old_logic_e, new_logic_e)

with open('app/engine/auto_connect.py', 'w', encoding='utf-8') as f:
    f.write(text)
