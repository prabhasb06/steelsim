# 51. Glossary

Key terminology used across the SteelSim digital twin, ACAMIS intelligence layer, and MSME steel manufacturing:

- **ACAMIS:** Autonomous Cyber-Physical Agentic Manufacturing Intelligence System; the integrated simulation-only monitoring and policy layer. Its current detectors and specialist evaluations are deterministic rules, not general AI diagnosis.
- **Advisory Mode:** ACAMIS operating mode where mitigation procedures are recommended to operators but require explicit approval before execution.
- **Autonomous Simulation Mode:** ACAMIS operating mode that schedules registered low-risk simulated recovery after 12 running ticks and applies registered containment for severe scenarios. Final high-risk recovery awaits human verification.
- **Billet:** A semi-finished square length of steel produced by a continuous casting machine, used as feedstock for rolling mills.
- **BYOK (Bring Your Own Key):** Security architecture where external API credentials (e.g., Google AI Studio) are held transiently in server memory per simulation session and never persisted to disk or `.env` files.
- **Continuous Casting Machine (CCM):** Industrial machinery that solidifies molten steel into continuous billet strands.
- **Direct-Reduced Iron (DRI):** Also known as sponge iron; iron ore reduced in solid state, charged alongside scrap into induction furnaces.
- **Evidence Payload:** Recorded measurements for a detected deviation, including the affected asset, actual and expected values, first abnormal tick, and persistence count. It is not an immutable forensic record.
- **Induction Furnace:** High-efficiency melting furnace utilizing alternating electromagnetic fields to heat and liquefy steel scrap.
- **Interlock:** An automatic hardware or software safeguard that restricts or trips machinery when safe operational conditions are violated.
- **Ladle Refining Furnace (LRF):** Secondary metallurgical unit used to homogenize temperature, adjust chemistry, and desulfurize steel.
- **Monotonic Version:** A strictly increasing integer sequence number assigned to each simulation state snapshot to prevent out-of-order rendering.
- **Observe Mode:** ACAMIS operating mode providing passive telemetry monitoring and diagnostic evaluations without generating mitigation procedures.
- **Process Flow Diagram (PFD):** An engineering schematic illustrating the primary sequence of process equipment and material flows.
- **React Flow:** Modern web framework powering the visual drag-and-drop plant canvas.
- **Safety Gate:** Policy check that requires an explicit human-verification flag for the final high-risk simulated procedure in Autonomous Simulation mode; the UI presents an intervention prompt.
- **Signal Review Case:** A tracked temperature, cooling-flow, or power deviation requiring operator review. Acknowledgement records review but does not change telemetry or execute repair.
- **Specialist Evaluator:** One of six deterministic assessment categories: Safety, Maintenance, Quality, Production, Energy, or Logistics.
- **Telemetry Anomaly Detector:** The Task 3.1 deterministic rule evaluating rolling throughput against its expected baseline ($A_T < 0.75 \times E_T$) over three running ticks.
- **Thermex Quenching:** An in-line water-quench hardening process that creates a self-tempered martensitic outer rim on rebar while preserving a ductile core.
- **Tick:** A single discrete time step in the simulation engine representing one simulated second.
- **TMT Rebar:** Thermo-Mechanically Treated steel reinforcing bars widely used in civil construction for high yield strength and ductility.
