import os

with open('app/models/component_library.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix Billet yard ports
text = text.replace(
    '        "ports": [create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)],\n        "params": {"inventory": q_mass(500), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(40)}',
    '        "ports": [create_port("mat_in", PortType.MATERIAL, PortDirection.IN), create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)],\n        "params": {"inventory": q_mass(500), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(25)}'
)

# Normalize all throughputs to 25 to avoid fake bottlenecks
for num in ['50', '40', '35', '30', '24', '18']:
    text = text.replace(f'q_throughput({num})', 'q_throughput(25)')

with open('app/models/component_library.py', 'w', encoding='utf-8') as f:
    f.write(text)
