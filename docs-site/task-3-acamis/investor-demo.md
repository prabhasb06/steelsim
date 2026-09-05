# 36. ACAMIS Investor Demonstration Script

This structured, repeatable 5-minute demonstration script showcases the complete capabilities of ACAMIS Intelligence to partners, investors, and industrial operators.

---

## Demonstration Flow Overview

<pre class="mermaid">
flowchart LR
    Step1["1. Baseline Simulation<br/>• Load 10-Node TMT<br/>• Run at 1x Clock<br/>• Verify Normal Health"]
    Step2["2. Low-Risk Scenario<br/>• Rolling Mill Slowdown<br/>• Autonomous Recovery<br/>• 12-Tick Clock Advance"]
    Step3["3. Severe Incident<br/>• Furnace Instability<br/>• Automatic Containment<br/>• Human Risk Modal Gate"]
    Step4["4. Automatic Detection<br/>• Telemetry Drift Demo<br/>• 3-Tick Persistence Rule<br/>• Evidence Trace Capture"]
    Step5["5. Optional AI Model<br/>• BYOK Gemini Review<br/>• Context Anonymization<br/>• Read-Only Advisory Chat"]

    Step1 --> Step2 --> Step3 --> Step4 --> Step5
</pre>

---

## Step-by-Step Demonstration Script

### 1. Launch & Baseline Verification (1 Minute)
1. Open the SteelSim web app at `http://127.0.0.1:5173/` (or `http://localhost:5173/`).
2. In the Plant Builder canvas, click **TMT 10-Node Demo** to populate the pre-validated mini-mill topology.
3. In the top control bar, click **Run** (speed: 1x).
4. Click the **ACAMIS** tab in the top navigation.
5. **Key Talking Point:** Show that ACAMIS connects immediately to the live digital twin:
   * Plant Health: `NORMAL`
   * Automatic Monitoring: `Active · Normal`
   * Specialist Intelligence: 6 domains evaluating shared telemetry in real time.

---

### 2. Low-Risk Autonomous Recovery (Manual scenario) (1 Minute)
1. In the **Scenario Control** toolbar, click **Rolling mill**.
2. **Observe:**
   * Plant Health transitions to `INCIDENT` (Yellow/Warning).
   * Origin badge clearly shows **Manual scenario**.
   * **Incident Impact** deck displays mill throughput cut from 70 t/h to 31.5 t/h.
   * Click **Locate in plant** to demonstrate cross-navigation: view jumps to Plant Builder and centers on the affected finishing mill.
3. Switch back to ACAMIS and change the Operating Mode dropdown to **AUTONOMOUS SIMULATION**.
4. **Observe:**
   * Recovery Plan status updates to `RECOVERING`.
   * The countdown timer announces: *"Autonomous simulated recovery in 12 simulation ticks."*
   * As the simulation clock reaches tick $T + 12$, the incident closes, plant health returns to `NORMAL`, and the audit timeline records `INCIDENT_RECOVERED`.

---

### 3. Severe Incident & Human-in-the-Loop Safety Gate (1.5 Minutes)
1. While still in **AUTONOMOUS SIMULATION** mode, click **Furnace stability** in Scenario Control.
2. **Observe:**
   * Plant Health immediately escalates to `INCIDENT` (Red/High).
   * Safe containment (`reduce_heat_load`) is automatically dispatched to protect equipment.
   * Plant Health shifts to `STABILIZED`.
   * **Alert Modal Pops Up:** ACAMIS halts final recovery with `HUMAN_VERIFICATION_REQUIRED`.
3. **Key Talking Point:** Point out the safety guarantee:
   > *"Even in fully autonomous simulation mode, ACAMIS policy strictly prevents the AI from restarting high-temperature furnace arcs without explicit human sign-off."*
4. Click **Apply human intervention** in the modal.
5. Plant health returns to `NORMAL`, and the audit log records the authorized operator sign-off.

---

### 4. Automatic Anomaly Detection (Task 3.1) (1 Minute)
1. Reset scenarios by clicking **Reset scenario**.
2. In the **Automatic Monitoring** card, click **Inject throughput anomaly (demo)**.
3. **Observe:**
   * The persistence counter increments live: `Watching (1/3)` $\rightarrow$ `Watching (2/3)` $\rightarrow$ `Detected (3/3)`.
   * Origin badge displays **Telemetry detector** (not a manual scenario!).
   * Expand the incident details to show the captured **Evidence Payload**: live throughput trace, threshold deficit ($45\% < 75\%$), and affected rolling mill node IDs.
4. With autonomy enabled, the 12-tick countdown initiates and clears the detector anomaly automatically.

---

### 5. Optional BYOK AI Model Review (30 Seconds)
1. In the **Advisory Model Gateway** card, enter a valid Gemini API key.
2. Click **Connect model**.
3. Select `gemini-2.5-flash` and type:
   > *"Review current plant metrics and advise on cooling water margins."*
4. Receive clean, structured industrial reasoning based on the live simulation snapshot.
5. Emphasize that the API key is transient and held strictly in volatile process memory.\n