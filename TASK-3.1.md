# Task 3.1: automatic rolling throughput monitoring

The backend checks rolling throughput once per running simulation tick. A shortfall greater than 25% against the same-tick deterministic plant baseline must persist for three ticks on the same mill. The baseline includes configured upstream flow and normal load variation. This is an explainable simulation detector, not a general machine-learning fault classifier.

## Demo

1. Load the TMT template and Run at 1x.
2. Open ACAMIS Intelligence. Automatic Monitoring should show Active / Normal.
3. Choose Observe and click Demonstrate telemetry drift. This changes the simulated mill's capacity by 50%; it does not create an incident.
4. After three running ticks, the monitor creates a Telemetry detector incident with throughput, baseline, percentage deviation, first tick, and persistence evidence.
5. Locate the mill in Plant Builder or inspect its simulation readings. Downstream throughput impact is also displayed.
6. Select Autonomous Simulation. The existing 12-tick simulated inspection completes recovery; the detector retains historical evidence and equipment impact.
7. Clear monitoring demo resets the disturbance, incident, and monitor. Simulation Reset also clears them. Pause freezes counting and recovery.

Observe only detects. Advisory permits operator-applied procedures. Autonomous Simulation schedules the approved low-risk response. Existing high-risk approval behavior remains in place. Manual scenarios take priority over automatic detection and are labelled separately.

## Scope and limits

No model API key is required. The model gateway remains optional and advisory. This release monitors only rolling throughput against a simulator baseline; it does not establish a physical root cause, detect arbitrary unknown faults, or connect to SCADA. The repeatable disturbance is synthetic. State and evidence remain in memory and do not survive backend restart. Only one operational incident is active at a time. Real telemetry adapters, additional detectors, durable history, and broader diagnosis remain future work.
