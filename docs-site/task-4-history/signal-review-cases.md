# Telemetry review cases

ACAMIS turns persistent simulated temperature, cooling-flow, and electrical-demand deviations into operator-review cases. These cases are **not** the same as the primary ACAMIS incident. A rolling-throughput incident has a registered simulated recovery procedure; the additional signal cases have no approved automatic repair.

## When a case opens

The backend compares each running asset with the deterministic baseline calculated by SteelSim. A signal must breach its rule for three consecutive running simulation ticks:

| Signal | Opens when |
| :--- | :--- |
| Thermal | Temperature differs from expected by more than 40 °C. |
| Cooling | Water flow is below 75% of expected. |
| Electrical | Power demand is above 112% of expected. |

The case records the asset, signal domain, metric, actual and expected readings, first abnormal tick, persistence count, and opening tick. Repeated abnormal readings update the **same open case** rather than creating duplicates. Multiple signals on one asset can be displayed together, but this correlation does not prove a root cause.

The monitor advances only while the simulation runs. Pause freezes its counters and cases; **Clear scenario** and simulation **Reset** clear the monitoring state. Cases are bounded in the live monitor so long runs do not grow the in-memory list without limit. Active cases take priority over older resolved cases.

## Operator workflow

1. Open **ACAMIS Intelligence → Multivariate telemetry monitoring**. Review the measured values and use **Locate in plant** or **Inspect in simulation** to view the affected asset.
2. Select **Acknowledge for review** on an open case. ACAMIS records an audit entry and changes the case to `ACKNOWLEDGED`. Repeating the request does not add another acknowledgement.
3. Investigate the simulated reading. Acknowledgement does **not** change telemetry, approve a high-risk action, or execute a repair.
4. When the reading returns inside the configured rule, ACAMIS changes the case to `RESOLVED` and records its resolution tick. Recent resolved cases remain visible in the ACAMIS panel.

With signal cases but no primary incident, the plant and simulation snapshot report `DEGRADED`, and the central plan reports `SIGNAL_REVIEW_REQUIRED`. Relevant specialist cards show the measured evidence. The plan intentionally has **no procedure button** for these cases because none is registered. A manual scenario or the rolling-throughput incident can still have its own separate recovery plan.

## Audit and history

The acknowledgement is recorded as `SIGNAL_REVIEW_ACKNOWLEDGED`. Task 4 saves the case ledger in the run checkpoint and includes it in the downloaded JSON report as `signal_review_cases`. Historical frame replay shows signal findings; it does not expose the full case ledger for every past frame. Older `signals.v1` checkpoints can be restored, with an empty case ledger initialized in the new paused session.

The current hosted Render configuration has no persistent disk, so recorded cases and audit may not survive a host replacement. This is simulation evidence for an MVP, not a physical-plant diagnosis or a certified alarm system.

## API

The [ACAMIS API reference](/task-3-acamis/api-reference) documents the status response and `POST /api/simulations/{sim_id}/acamis/signals/{case_id}/acknowledge`. No external AI key is needed for detection or acknowledgement.
