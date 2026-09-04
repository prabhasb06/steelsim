from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SUPPORTED_PROVIDERS = {"OPENAI_COMPATIBLE", "GEMINI"}


def public_status(sim: Any) -> dict[str, Any]:
    config = getattr(sim, "acamis_model_config", None)
    if not config:
        return {
            "configured": False,
            "connected": False,
            "provider": None,
            "model": None,
            "base_url": None,
            "last_tested_at": None,
            "message": "Deterministic ACAMIS policy engine is active; no external reasoning model is connected.",
        }
    return {key: value for key, value in config.items() if key != "api_key"}


def _request_json(url: str, *, api_key: str, method: str = "GET", payload: dict[str, Any] | None = None, provider: str) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if provider == "GEMINI":
        headers["x-goog-api-key"] = api_key
    else:
        headers["Authorization"] = f"Bearer {api_key}"
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise ValueError(f"Provider rejected the request ({exc.code}): {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to reach a valid model endpoint: {exc}") from exc


async def connect(sim: Any, provider: str, model: str, api_key: str, base_url: str | None) -> dict[str, Any]:
    provider = provider.upper().strip()
    model = model.strip()
    api_key = api_key.strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError("Provider must be OPENAI_COMPATIBLE or GEMINI")
    if not model or not api_key:
        raise ValueError("Model name and API key are required")
    resolved_base = (base_url or "").strip().rstrip("/")
    if provider == "GEMINI":
        resolved_base = resolved_base or "https://generativelanguage.googleapis.com/v1beta"
    elif not resolved_base:
        raise ValueError("An HTTPS base URL is required for an OpenAI-compatible provider")
    if not resolved_base.startswith("https://") and not resolved_base.startswith("http://127.0.0.1") and not resolved_base.startswith("http://localhost"):
        raise ValueError("Use HTTPS for remote providers; HTTP is allowed only for a local model server")

    test_url = f"{resolved_base}/models"
    await asyncio.to_thread(_request_json, test_url, api_key=api_key, provider=provider)
    sim.acamis_model_config = {
        "configured": True,
        "connected": True,
        "provider": provider,
        "model": model,
        "base_url": resolved_base,
        "api_key": api_key,
        "last_tested_at": datetime.now(timezone.utc).isoformat(),
        "message": "Connection verified. Model output is advisory and remains behind ACAMIS policy gates.",
    }
    return public_status(sim)


def disconnect(sim: Any) -> dict[str, Any]:
    sim.acamis_model_config = None
    return public_status(sim)


async def ask(sim: Any, operator_message: str, acamis_context: dict[str, Any]) -> dict[str, Any]:
    config = getattr(sim, "acamis_model_config", None)
    if not config or not config.get("connected"):
        raise ValueError("Connect and verify a model before using ACAMIS model review")
    message = operator_message.strip()
    if not message:
        raise ValueError("Operator message is required")
    system = (
        "You are the advisory reasoning model inside ACAMIS for the SteelSim digital twin. "
        "Use only the supplied snapshot, incidents, specialist findings, and approved procedures. "
        "Never claim a physical action occurred, never bypass safety gates, and clearly identify actions requiring human verification."
    )
    context_text = json.dumps(acamis_context, separators=(",", ":"), default=str)
    if config["provider"] == "GEMINI":
        endpoint = f"{config['base_url']}/models/{quote(config['model'], safe='')}:generateContent"
        payload = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": f"CONTEXT:\n{context_text}\n\nOPERATOR:\n{message}"}]}]}
        result = await asyncio.to_thread(_request_json, endpoint, api_key=config["api_key"], provider=config["provider"], method="POST", payload=payload)
        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Gemini returned no readable response") from exc
    else:
        endpoint = f"{config['base_url']}/chat/completions"
        payload = {"model": config["model"], "temperature": 0.1, "messages": [{"role": "system", "content": system}, {"role": "user", "content": f"CONTEXT:\n{context_text}\n\nOPERATOR:\n{message}"}]}
        result = await asyncio.to_thread(_request_json, endpoint, api_key=config["api_key"], provider=config["provider"], method="POST", payload=payload)
        try:
            reply = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("The model endpoint returned no readable response") from exc
    return {"reply": str(reply), "provider": config["provider"], "model": config["model"], "advisory_only": True}
