from __future__ import annotations

import asyncio
import ipaddress
import json
import os
import socket
from datetime import datetime, timezone
from typing import Any
from types import SimpleNamespace
from urllib.parse import urlsplit, urlencode
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


SUPPORTED_PROVIDERS = {"OPENAI_COMPATIBLE", "GEMINI"}
DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"
MAX_MODEL_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_OPERATOR_MESSAGE_LENGTH = 8000


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _validate_destination(url: str) -> None:
    """Reject server-side requests to private services, including DNS aliases."""
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid model endpoint URL") from exc
    if not hostname or parsed.username or parsed.password or parsed.scheme not in {"https", "http"}:
        raise ValueError("Invalid model endpoint URL")

    allow_local = os.getenv("STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS", "").lower() in {"1", "true", "yes"}
    if parsed.scheme != "https" and not (allow_local and parsed.scheme == "http" and hostname in {"localhost", "127.0.0.1", "::1"}):
        raise ValueError("Model endpoints must use HTTPS; local HTTP requires explicit developer opt-in")
    try:
        addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(hostname, port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
    except (OSError, ValueError) as exc:
        raise ValueError("Unable to resolve the model endpoint hostname") from exc
    if not addresses or any(not address.is_global for address in addresses):
        if not (allow_local and hostname in {"localhost", "127.0.0.1", "::1"} and all(address.is_loopback for address in addresses)):
            raise ValueError("Model endpoints cannot address private or local network services")


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


def _gemini_model_names(catalog: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for entry in catalog.get("models", []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).removeprefix("models/").strip()
        methods = entry.get("supportedGenerationMethods", [])
        if name.startswith('gemini-') and 'generateContent' in methods and not any(marker in name for marker in ('image', 'tts', 'live', 'omni')):
            names.append(name)
    return names


def _select_gemini_model(requested: str, available: list[str]) -> tuple[str, bool]:
    requested = requested.removeprefix("models/")
    if requested in available:
        return requested, False

    stable_flash = [
        name for name in available
        if name.startswith("gemini-")
        and "flash" in name
        and not any(marker in name for marker in ("image", "live", "preview", "exp", "tts"))
    ]
    for preferred in (DEFAULT_GEMINI_MODEL, "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"):
        if preferred in stable_flash:
            return preferred, True
    if stable_flash:
        return sorted(stable_flash, reverse=True)[0], True

    generative = [name for name in available if name.startswith("gemini-")]
    if generative:
        return sorted(generative, reverse=True)[0], True
    raise ValueError("The API key has no compatible Gemini text-generation model available")


def _provider_error_message(status_code: int, detail: str) -> str:
    try:
        payload = json.loads(detail)
        error = payload.get("error", {}) if isinstance(payload, dict) else {}
        message = str(error.get("message", ""))
        reasons = {
            str(item.get("reason", ""))
            for item in error.get("details", [])
            if isinstance(item, dict)
        }
    except (json.JSONDecodeError, AttributeError, TypeError):
        message = detail
        reasons = set()

    lowered = message.lower()
    if "API_KEY_INVALID" in reasons or "api key not valid" in lowered:
        return (
            "INVALID API KEY: Google did not accept this credential. Copy an active Gemini API key "
            "from Google AI Studio and paste the complete value; ACAMIS does not save it."
        )
    if status_code == 401:
        return "INVALID API KEY: the provider rejected this credential. Check the key and selected provider."
    if status_code == 403:
        return "API KEY PERMISSION DENIED: verify this key's provider permissions and restrictions."
    if status_code == 429:
        return "MODEL RATE LIMIT REACHED: wait for the provider quota window to reset, then retry."
    if status_code == 404 and "model" in lowered:
        return "MODEL UNAVAILABLE: reconnect so ACAMIS can select a model from the provider's current catalog."
    return f"Provider rejected the request ({status_code}): {message[:240] or detail[:240]}"


def _request_json(url: str, *, api_key: str, method: str = "GET", payload: dict[str, Any] | None = None, provider: str) -> dict[str, Any]:
    _validate_destination(url)
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
        with build_opener(_NoRedirectHandler()).open(request, timeout=45) as response:
            data = response.read(MAX_MODEL_RESPONSE_BYTES + 1)
            if len(data) > MAX_MODEL_RESPONSE_BYTES:
                raise ValueError("The model endpoint returned an oversized response")
            result = json.loads(data.decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError('The model endpoint returned an invalid JSON response')
            return result
    except HTTPError as exc:
        if 300 <= exc.code < 400:
            raise ValueError("Model endpoint redirects are not allowed; use the provider's final HTTPS API URL") from exc
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise ValueError(_provider_error_message(exc.code, detail.replace(api_key, '[REDACTED]'))) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError("Unable to reach the model endpoint or read its response. Check the URL, network, and provider availability.") from exc


async def connect(sim: Any, provider: str, model: str, api_key: str, base_url: str | None) -> dict[str, Any]:
    provider = provider.upper().strip()
    model = model.strip()
    api_key = api_key.strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError("Provider must be OPENAI_COMPATIBLE or GEMINI")
    if not model or not api_key:
        raise ValueError("Model name and API key are required")
    if len(model) > 256 or len(api_key) > 4096 or (base_url and len(base_url) > 2048):
        raise ValueError("Model connection details exceed the supported size")
    resolved_base = (base_url or "").strip().rstrip("/")
    if provider == "GEMINI":
        resolved_base = resolved_base or "https://generativelanguage.googleapis.com/v1beta"
    elif not resolved_base:
        raise ValueError("An HTTPS base URL is required for an OpenAI-compatible provider")
    try:
        parsed = urlsplit(resolved_base)
    except ValueError as exc:
        raise ValueError("Invalid model endpoint URL") from exc
    if parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.hostname:
        raise ValueError('Use a base URL without credentials, query parameters, or fragments')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost', '::1'} and os.getenv('STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS', '').lower() in {'1', 'true', 'yes'}):
        raise ValueError("Use HTTPS for remote providers; local HTTP requires explicit developer opt-in")

    available_models: list[str] = []
    model_changed = False
    if provider == "GEMINI":
        token = None
        for _ in range(20):
            query = urlencode({'pageSize': 100, **({'pageToken': token} if token else {})})
            catalog = await asyncio.to_thread(_request_json, f'{resolved_base}/models?{query}', api_key=api_key, provider=provider)
            available_models.extend(_gemini_model_names(catalog))
            token = catalog.get('nextPageToken')
            if not token:
                break
        available_models = list(dict.fromkeys(available_models))
        model, model_changed = _select_gemini_model(model, available_models)

    message = "Generation verified: the model returned a test response. Model output remains advisory."
    if model_changed:
        message = f"Requested model is unavailable; ACAMIS selected {model} from the verified provider catalog. Policy gates remain in control."
    candidate = {
        "configured": True,
        "connected": True,
        "provider": provider,
        "model": model,
        "base_url": resolved_base,
        "transport": "GENERATE_CONTENT" if provider == "GEMINI" else "CHAT_COMPLETIONS",
        "available_models": available_models[:25],
        "api_key": api_key,
        "last_tested_at": datetime.now(timezone.utc).isoformat(),
        "message": message,
    }
    # A catalog response alone does not verify generation permissions, quota or model ID.
    # Do not replace a working connection until the candidate actually responds.
    await _ask(SimpleNamespace(acamis_model_config=candidate), 'Reply briefly with ACAMIS connection confirmed.', {})
    sim.acamis_model_config = candidate
    sim.acamis_last_model_advisory = None
    return public_status(sim)


def disconnect(sim: Any) -> dict[str, Any]:
    sim.acamis_model_config = None
    sim.acamis_last_model_advisory = None
    return public_status(sim)


async def ask(sim: Any, operator_message: str, acamis_context: dict[str, Any]) -> dict[str, Any]:
    config = getattr(sim, 'acamis_model_config', None)
    message = operator_message.strip()
    if not message:
        raise ValueError("Operator message is required")
    if len(message) > MAX_OPERATOR_MESSAGE_LENGTH:
        raise ValueError("Operator message is too long")
    try:
        result = await _ask(sim, message, acamis_context)
    except ValueError as exc:
        if config and getattr(sim, 'acamis_model_config', None) is config:
            config['connected'] = False
            config['message'] = f'Model review failed; reconnect to verify: {exc}'
        raise
    if getattr(sim, 'acamis_model_config', None) is not config:
        raise ValueError('The model connection changed during this review. Request a new review.')
    return result


async def _ask(sim: Any, operator_message: str, acamis_context: dict[str, Any]) -> dict[str, Any]:
    config = getattr(sim, "acamis_model_config", None)
    if not config or not config.get("connected"):
        raise ValueError("Connect and verify a model before using ACAMIS model review")
    message = operator_message.strip()
    if not message:
        raise ValueError("Operator message is required")
    if len(message) > MAX_OPERATOR_MESSAGE_LENGTH:
        raise ValueError("Operator message is too long")
    system = (
        "You are the advisory reasoning model inside ACAMIS for the SteelSim digital twin. "
        "Use only the supplied snapshot, incidents, specialist findings, and approved procedures. "
        "Never claim a physical action occurred, never bypass safety gates, and clearly identify actions requiring human verification."
    )
    context_text = json.dumps(acamis_context, separators=(",", ":"), default=str)
    if config["provider"] == "GEMINI":
        endpoint = f"{config['base_url']}/models/{config['model']}:generateContent"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"CONTEXT:\n{context_text}\n\nOPERATOR:\n{message}"}],
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system}],
            },
            "generationConfig": {
                "temperature": 0.2,
            },
        }
        result = await asyncio.to_thread(
            _request_json,
            endpoint,
            api_key=config["api_key"],
            provider=config["provider"],
            method="POST",
            payload=payload,
        )
        candidates = result.get("candidates", [])
        if not isinstance(candidates, list) or not candidates or not isinstance(candidates[0], dict) or not isinstance(candidates[0].get('content'), dict):
            raise ValueError("Gemini returned no readable response candidate")
        parts = candidates[0]["content"].get("parts", [])
        if not isinstance(parts, list):
            raise ValueError('Gemini returned no readable text parts')
        reply = "".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get('text'), str) and not part.get('thought')
        )
        if not reply.strip():
            raise ValueError("Gemini returned an empty response")
    else:
        endpoint = f"{config['base_url']}/chat/completions"
        payload = {"model": config["model"], "temperature": 0.1, "messages": [{"role": "system", "content": system}, {"role": "user", "content": f"CONTEXT:\n{context_text}\n\nOPERATOR:\n{message}"}]}
        result = await asyncio.to_thread(_request_json, endpoint, api_key=config["api_key"], provider=config["provider"], method="POST", payload=payload)
        try:
            reply = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("The model endpoint returned no readable response") from exc
        if not isinstance(reply, str) or not reply.strip():
            raise ValueError('The model endpoint returned an empty text response')
    return {"reply": str(reply), "provider": config["provider"], "model": config["model"], "advisory_only": True}
