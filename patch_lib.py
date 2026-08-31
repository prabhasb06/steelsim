import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        if old not in text:
            print(f"WARNING: String not found in {filepath}:\n{old[:50]}...")
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

lib_reps = [
    ('"params": {"inventory": q_mass(500), "dispatch": q_throughput(40)}',
     '"params": {"inventory": q_mass(500), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(40)}'),
    
    ('"params": {"throughput": q_throughput(30), "temperature": q_temp(1100), "thermal_input": q_power(5.0)}',
     '"params": {"throughput": q_throughput(30), "temperature": q_temp(1150), "power": q_power(2.8)}'),
     
    ('"params": {"inventory": q_mass(100), "capacity": q_mass(5000)}',
     '"params": {"inventory": q_mass(100), "storage_capacity": EngineeringQuantity(value=5000, unit="t", category=QuantityCategory.MASS, display_name="Storage Capacity"), "dispatch": q_throughput(40)}'),
]

replace_in_file("backend/app/models/component_library.py", lib_reps)
