# 49. Current limitations

To maintain engineering honesty, the architectural constraints of the current release (Tasks 1, 2, and 3.1) are explicitly documented.

## Current limitations and planned upgrades

| Domain | Current MVP Limitation | Planned Upgrade |
| :--- | :--- | :--- |
| **Backend State** | In-memory only; active simulations and ACAMIS state clear on server restart | Persistent simulation and incident state backed by PostgreSQL / Redis |
| **Plant Persistence** | Saved in browser LocalStorage under `steelsim_plant_graph` | Cloud database with multi-user project workspaces |
| **Authentication** | Optional shared API-key gate via constant-time digest | Enterprise OAuth2/OIDC with role-based access control (RBAC) |
| **Physics Model** | Discrete mass-balance and aggregate utility approximations | Non-linear thermodynamic heat loss and metallurgical models |
| **Hardware Interfacing** | No connection to physical factory machinery | Read-only industrial IoT connectors (OPC-UA, MQTT, Modbus) |
| **Anomaly Detection** | Task 3.1 explainable rolling throughput detector | Full multivariate thermal, hydraulic, and electrical detectors |
| **Advisory Model** | External LLM suggestions are advisory; transient in-memory keys | Verified multi-agent reasoning with cryptographic audit signatures |
| **Collaboration** | Single-user local browser session | Real-time multi-user collaborative canvas synchronization |

## Positioning statement

::: tip Investor & Engineering Positioning
**“SteelSim is complete and reliable for its defined investor-facing MVP workflow. It is not presented as production-certified industrial control software.”**
:::
