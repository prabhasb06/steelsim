# 37. Current limitations

To maintain engineering honesty, the architectural constraints of the current MVP release are explicitly documented.

## Current limitations and planned upgrades

| Domain | Current MVP Limitation | Planned Upgrade |
| :--- | :--- | :--- |
| **Backend State** | In-memory only; active simulations clear on server restart | Persistent simulation state backed by PostgreSQL / Redis |
| **Plant Persistence** | Saved in browser LocalStorage under `steelsim_plant_graph` | Cloud database with multi-user project workspaces |
| **Authentication** | Optional shared API-key gate via constant-time digest | Enterprise OAuth2/OIDC with role-based access control (RBAC) |
| **Physics Model** | Discrete mass-balance and aggregate utility approximations | Non-linear thermodynamic heat loss and metallurgical models |
| **Hardware Interfacing** | No connection to physical factory machinery | Read-only industrial IoT connectors (OPC-UA, MQTT, Modbus) |
| **Optimization** | Informational roadmap placeholder | ACAMIS multi-agent AI for peak shaving and heat scheduling |
| **Collaboration** | Single-user local browser session | Real-time multi-user collaborative canvas synchronization |

## Positioning statement

::: tip Investor & Engineering Positioning
**“SteelSim is complete and reliable for its defined investor-facing MVP workflow. It is not presented as production-certified industrial control software.”**
:::
