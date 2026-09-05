# 32. Advisory Model Gateway (BYOK)

ACAMIS includes an optional **Advisory Model Gateway** enabling plant operators to connect modern large language models (such as Google Gemini) to assist with incident root-cause analysis and operational strategy.

---

## Architectural Separation & Safety Perimeter

To guarantee industrial safety and air-gapped compliance, the Model Gateway operates strictly as a read-only advisory layer:

<pre class="mermaid">
flowchart TD
    Cloud["External AI Provider<br/>(Google AI Studio / Gemini API)"]
    Gateway["ACAMIS Advisory Gateway<br/>• Transient In-Memory Key<br/>• Sanitized Context Bundler<br/>• Response Schema Parser"]
    Policy["Deterministic Policy & Safety Gate<br/>• Enforces Role Permissions<br/>• Rejects Hallucinated Actions<br/>• Blocks High-Risk Autonomy"]
    Engine["SteelSim Simulation Core<br/>(Deterministic Digital Twin)"]

    Cloud -->|"Advisory Recommendations (Read-Only)"| Gateway
    Gateway -->|"Validated Structured Advice"| Policy
    Policy -->|"Operator-Approved Procedures Only"| Engine
</pre>

### Fundamental Security Guarantees
1. **Bring-Your-Own-Key (BYOK):** SteelSim does **not** ship with hardcoded API keys and does not read keys from `.env` files. The operator supplies their own Google AI Studio key at runtime.
2. **Transient In-Memory Storage:** The API key is stored exclusively in process memory associated with the active simulation ID. It is **never** written to disk, SQLite/PostgreSQL databases, or server log files.
3. **Immediate Revocation:** Clicking **Disconnect model** or deleting the simulation instance immediately purges the credential from memory.
4. **Read-Only Context:** The model is provided with a sanitized, anonymous snapshot of current telemetry (temperatures, flow rates, throughputs, and active alarm codes). It has **zero direct actuation authority**.
5. **No Autonomous LLM Actuation:** Operational procedures cannot be triggered directly by LLM text output. Every procedure must match a registered, deterministic procedure definition and satisfy all active safety gates.

---

## Supported Models & Fallback Hierarchy

The gateway connects to the standard Google Gemini REST endpoint:

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

The gateway maintains a tested fallback catalog:
1. `gemini-2.5-flash` (Default: Fast, low latency, structured JSON reasoning)
2. `gemini-1.5-pro` (Deep metallurgical analysis and complex scenario evaluation)
3. `gemini-1.5-flash` (Reliable baseline fallback)

---

## REST API Integration

### Connect Model Key
```bash
curl -X POST http://127.0.0.1:8000/api/simulations/{id}/acamis/model/connect \
  -H "Content-Type: application/json" \
  -d '{"api_key": "AIzaSy...", "model_name": "gemini-2.5-flash"}'
```

### Advisory Chat Query
```bash
curl -X POST http://127.0.0.1:8000/api/simulations/{id}/acamis/model/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze thermal load on the induction furnace and evaluate water flow margins."}'
```

### Disconnect & Purge
```bash
curl -X POST http://127.0.0.1:8000/api/simulations/{id}/acamis/model/disconnect
```\n