# 36. ACAMIS investor demonstration

The [full product demo](/getting-started/investor-demo) covers Plant Builder, Simulation, ACAMIS, and Operations History. This shorter route focuses on ACAMIS's response to simulated incidents.

## Normal plant

Load **Demo** in Plant Builder and start the plant from **Simulation** with **Run Simulation**. Open **ACAMIS Intelligence**. Plant health should show normal operation, and the automatic rolling monitor becomes active while the simulation runs.

## Defined low-risk recovery

In **Scenario Control**, select **Rolling mill**. Show the **Manual scenario** origin and the affected equipment. Set the operating mode to **Autonomous Simulation**. ACAMIS schedules an approved simulated procedure; after 12 running ticks, the incident closes and the audit records recovery. Pause freezes the simulated countdown.

## Severe incident requiring a person

Select **Furnace stability**. ACAMIS applies simulated containment and shows the human-intervention prompt. The final high-risk procedure waits for explicit human verification. You can demonstrate the approval control or leave the plant stabilized while explaining the gate.

## Automatic throughput detection

Clear the scenario. Click **Demonstrate telemetry drift** in **Automatic Monitoring**. The button reduces simulated rolling capacity; the backend detector evaluates the resulting readings for three running ticks. An incident then appears with **Telemetry detector** as its origin. The detector follows a defined throughput rule; it does not diagnose unknown physical failures.

## Recorded evidence and optional model review

Open **Operations History** to replay frames, inspect audit evidence, and download the JSON report. Restore creates a separate paused session. If you have a permitted provider key and quota, **Test & connect** in the model gateway makes a real generation request, after which **Request model review** sends the current simulated plant context. The provider's text is advisory and does not execute a procedure.

Use the [Task 4 reference](/task-4-history/overview) for storage limits and the [model gateway reference](/task-3-acamis/model-gateway) for key and data-sharing details.
