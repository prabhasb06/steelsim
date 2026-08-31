import os

def replace_in_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements:
        text = text.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

top_replacements = [
    ("    WATER_PUMP = \"WATER_PUMP\"", """    WATER_PUMP = "WATER_PUMP"
    RAW_MATERIAL_STORAGE = "RAW_MATERIAL_STORAGE"
    TRANSFER_CONVEYOR = "TRANSFER_CONVEYOR"
    ROLLER_CONVEYOR = "ROLLER_CONVEYOR"
    BUFFER = "BUFFER"
    WEIGHING = "WEIGHING"
    ELECTRICAL_SUPPLY = "ELECTRICAL_SUPPLY"
    WATER_SYSTEM = "WATER_SYSTEM"
    COMPRESSOR = "COMPRESSOR"
    MAINTENANCE_STATION = "MAINTENANCE_STATION"
    QUALITY_INSPECTION = "QUALITY_INSPECTION\"""")
]

replace_in_file("backend/app/models/topology.py", top_replacements)

lib_replacements = [
    ("TMT_SEQUENCE = [", """TMT_SEQUENCE = [
    ComponentClass.RAW_MATERIAL_STORAGE,"""),
    ("    ComponentClass.BUNDLING_UNIT,\n    ComponentClass.FINISHED_GOODS", "    ComponentClass.BUNDLING_UNIT,\n    ComponentClass.WEIGHING,\n    ComponentClass.FINISHED_GOODS"),
    ("    ComponentClass.WATER_PUMP: {", """    ComponentClass.RAW_MATERIAL_STORAGE: {
        "name": "Raw Material Storage",
        "ports": [create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)]
    },
    ComponentClass.TRANSFER_CONVEYOR: {
        "name": "Transfer Conveyor",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ]
    },
    ComponentClass.ROLLER_CONVEYOR: {
        "name": "Roller Conveyor",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ]
    },
    ComponentClass.BUFFER: {
        "name": "Buffer",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT)
        ]
    },
    ComponentClass.WEIGHING: {
        "name": "Weighing Station",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("signal_out", PortType.SIGNAL, PortDirection.OUT)
        ]
    },
    ComponentClass.ELECTRICAL_SUPPLY: {
        "name": "Electrical Grid",
        "ports": [
            create_port("elec_out", PortType.ELECTRICAL, PortDirection.OUT)
        ]
    },
    ComponentClass.WATER_SYSTEM: {
        "name": "Water System",
        "ports": [
            create_port("water_out", PortType.WATER, PortDirection.OUT)
        ]
    },
    ComponentClass.COMPRESSOR: {
        "name": "Compressor",
        "ports": [
            create_port("elec_in", PortType.ELECTRICAL, PortDirection.IN),
            create_port("air_out", PortType.SIGNAL, PortDirection.OUT)  # Use SIGNAL for air temporarily until AIR type added
        ]
    },
    ComponentClass.MAINTENANCE_STATION: {
        "name": "Maintenance Station",
        "ports": []
    },
    ComponentClass.QUALITY_INSPECTION: {
        "name": "Quality Inspection",
        "ports": [
            create_port("mat_in", PortType.MATERIAL, PortDirection.IN),
            create_port("mat_out", PortType.MATERIAL, PortDirection.OUT),
            create_port("signal_out", PortType.SIGNAL, PortDirection.OUT)
        ]
    },
    ComponentClass.WATER_PUMP: {""")
]

replace_in_file("backend/app/models/component_library.py", lib_replacements)


ts_replacements = [
    ("    | \"WATER_PUMP\";", """    | "WATER_PUMP"
    | "RAW_MATERIAL_STORAGE"
    | "TRANSFER_CONVEYOR"
    | "ROLLER_CONVEYOR"
    | "BUFFER"
    | "WEIGHING"
    | "ELECTRICAL_SUPPLY"
    | "WATER_SYSTEM"
    | "COMPRESSOR"
    | "MAINTENANCE_STATION"
    | "QUALITY_INSPECTION";""")
]

replace_in_file("frontend/src/types/topology.ts", ts_replacements)

print("Patched models successfully.")
