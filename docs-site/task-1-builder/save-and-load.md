# 14. Save and load

SteelSim provides browser-local persistence for plant designs, allowing operators to save, reload, and transfer custom configurations across sessions without requiring a server database.

## Storage mechanism

- **Primary store:** HTML5 LocalStorage under the key `steelsim_plant_graph`.
- **Payload serialization:** The entire graph structure is serialized as a JSON object containing:
  - Node identifiers, component classes, coordinates, port allocations, and configured parameters.
  - Edge identifiers, source/target nodes, source/target ports, and connection types.

## Demo template loading

The canvas toolbar includes a **Demo** button that loads the verified 10-node TMT manufacturing baseline. The loading sequence:
1. Calls `GET /api/plant/template/tmt` to fetch the authoritative baseline graph.
2. Deserializes nodes and edges into the React Flow state.
3. Automatically triggers Auto Setup to ensure optimal layout coordinates.
4. Serializes the loaded template into LocalStorage as the new baseline design.

## Canvas clear and simulation cleanup

Clicking **Clear Canvas** removes all nodes and edges from the screen. Because clearing the plant fundamentally changes its physical structure:
1. The client immediately marks any running simulation as obsolete.
2. An asynchronous `DELETE /api/simulations/{id}` request is dispatched to free backend memory.
3. The Simulation Control Center resets to a clean "no-plant" baseline state.
