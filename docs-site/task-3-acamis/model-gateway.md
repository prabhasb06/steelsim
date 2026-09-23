# 32. Advisory Model Gateway

ACAMIS can send its current simulated plant snapshot, incident evidence, specialist findings, and approved recovery plan to an external text model for an advisory review. The model can explain the situation; it cannot call SteelSim procedures or override the deterministic safety gates.

## Connect a model

1. Start a SteelSim simulation and open **ACAMIS Intelligence**.
2. In **Advisory Model Gateway**, choose **Google Gemini** or **OpenAI-compatible**.
3. Paste your own API key. For an OpenAI-compatible service, also enter its model ID and API base URL, usually ending in `/v1`.
4. Click **Test & connect**. SteelSim makes a small generation request. A successful model-list request alone does not mark the connection as verified. Your provider may count or charge for this test.
5. Click **Request model review** to receive advice about the current plant state. The review sends the latest simulated telemetry and incident information.

For Gemini, the gateway queries the key's current model catalog and can select a compatible text model automatically. It calls the standard `models/{model}:generateContent` endpoint. A key without access to a compatible model, generation permission, or available quota will not verify. The interface reports connection and review errors; a failed review marks the connection for retesting.

## Data and control boundaries

- The supplied key is held in backend memory for the active simulation. ACAMIS history does not archive the key, prompts, or model replies. Disconnect, simulation deletion, and backend restart clear the connection.
- A connected external provider receives simulation data over the network. The context includes equipment IDs, telemetry, incident evidence, and policy information. **This is not an air-gapped or anonymized mode.** Use only with data you are allowed to send to that provider.
- Model output is advisory text. Existing approved procedures, simulation modes, and human verification rules determine actions independently of that text.
- The public MVP has no individual accounts or per-user model-key isolation. Do not put a personal model key into a shared public demonstration session.

## API example

Replace `{id}` with a live simulation ID. Keep the key out of committed scripts and URLs.

```bash
curl -X POST "http://127.0.0.1:8000/api/simulations/{id}/acamis/model/connect" \
  -H "Content-Type: application/json" \
  -d '{"provider":"GEMINI","model":"auto","api_key":"YOUR_KEY"}'

curl -X POST "http://127.0.0.1:8000/api/simulations/{id}/acamis/model/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Review the current simulated incident and its remaining risk."}'

curl -X POST "http://127.0.0.1:8000/api/simulations/{id}/acamis/model/disconnect"
```

The key above is a placeholder. The request and response contract is defined in [`backend/app/api/acamis.py`](https://github.com/prabhasb06/steelsim/blob/main/backend/app/api/acamis.py).
