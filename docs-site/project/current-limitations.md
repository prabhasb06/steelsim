# 49. Current limitations

SteelSim is an investor-facing digital-twin MVP. The boundaries below apply to the current codebase.

| Area | Current behavior | Later product work |
| :--- | :--- | :--- |
| Active sessions | The running engine and connected model keys live in one backend process. A restart ends active sessions. | Multi-user sessions and controlled recovery after service failures. |
| Operations history | Task 4 writes SQLite checkpoints, telemetry frames, incidents, and policy audit. An operator can restore a recorded run as a new paused session. | Managed persistent storage, backups, retention policy, and multi-user access. |
| Hosted storage | The current free Render configuration has no persistent disk. Recordings may disappear after a restart or deployment. | Provision persistent storage and verify backup and restore. |
| Plant projects | The Builder can save a plant in the current browser. | Shared projects with accounts and revision history. |
| Detection | Rolling throughput can trigger a registered recovery. Temperature, cooling-flow, and power deviations are grouped as operator-review evidence after three running ticks. | Validated procedures for more signal patterns, with plant-specific thresholds. |
| AI provider | Bring-your-own-key model reviews are advisory. The key is held in process memory. | Individual accounts, credential vault, budgets, and access controls. |
| Physics | Deterministic discrete simulation with simplified process and utility models. | Calibration and independent validation against plant measurements. |
| Real equipment | No PLC, SCADA, or physical actuation connection. | Read-only industrial data adapters first; physical control would require a separate safety engineering program. |

The demo proves how SteelSim creates and simulates a virtual plant and how ACAMIS handles selected simulated incidents. It does not prove performance or safety in a physical mill.
