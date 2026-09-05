# 9. Ports and connections

Industrial connectivity in SteelSim is governed by typed ports. Ports define physical flow interfaces with strict engineering validation.

## Port domains and specifications

| Port Type | CSS / Visual Color | Flow Direction | Typical Media / Application |
| :--- | :--- | :--- | :--- |
| **Material** | Industrial Amber | Source (`OUT`) ➔ Target (`IN`) | Solid scrap, liquid steel, continuous billets, hot-rolled rebar |
| **Electrical** | Electric Yellow | Source (`OUT`) ➔ Target (`IN`) | High-voltage (33 kV), medium-voltage (11 kV), and motor power |
| **Cooling Water**| Cool Cyan | Inflow (`IN`) & Return (`BIDIRECTIONAL`) | Chilled process supply and return circuits |
| **Signal** | Control Violet | Source (`OUT`) ➔ Target (`IN`) | Interlock triggers, scale weight feedback, emergency stops |
| **Air** | Pneumatic Slate | Source (`OUT`) ➔ Target (`IN`) | Compressed air for pneumatic actuators and valve control |

## Port directionality rules

Every port definition (`PortDef`) declares an industrial direction:
- **`IN` (Target):** Receives mass, energy, or cooling media. Can only accept incoming connection edges.
- **`OUT` (Source):** Emits product, power, or fluids. Can only originate outgoing connection edges.
- **`BIDIRECTIONAL`:** Reserved for closed-loop return manifolds (e.g., cooling-water return pipes). Can function as either source or target.

## Connection edge validation

When an operator connects two ports on the canvas, the system evaluates:
1. **Type equivalence:** `source_port.type === target_port.type` (e.g., cannot wire water to an electrical bus).
2. **Directional polarity:** `source_port.direction !== "IN"` and `target_port.direction !== "OUT"`.
3. **No self-connections:** `edge.source_node !== edge.target_node`.
4. **No duplicates:** Only one edge is permitted between an identical source-target port pair.
