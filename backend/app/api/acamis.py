from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.acamis import model_gateway, service
from app.api.routes import manager

router = APIRouter(prefix="/api/simulations/{sim_id}/acamis", tags=["acamis"])

class AutonomyRequest(BaseModel):
    mode: str

class ModelConnectionRequest(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: str | None = None

class ModelChatRequest(BaseModel):
    message: str

class ProcedureRequest(BaseModel):
    human_verified: bool = False

def _simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim

async def _automatic_model_review(sim, trigger: str) -> None:
    gateway = model_gateway.public_status(sim)
    has_operational_change = getattr(sim, "acamis_scenario", None) or getattr(sim, "acamis_last_resolution", None)
    if not gateway["connected"] or getattr(sim, "acamis_autonomy", "OBSERVE") != "AUTONOMOUS_SIMULATION" or not has_operational_change:
        return
    context = service.status(sim)
    context.pop("snapshot", None)
    try:
        result = await model_gateway.ask(sim, "Review ACAMIS's autonomous response, identify residual risk, and state whether human verification remains required.", context)
        sim.acamis_last_model_advisory = {**result, "trigger": trigger}
        service._audit(sim, "MODEL_AUTONOMOUS_REVIEW_RECEIVED", f"{result['provider']} / {result['model']} reviewed the autonomous response.")
    except ValueError as exc:
        service._audit(sim, "MODEL_AUTONOMOUS_REVIEW_FAILED", f"Deterministic recovery continued after model review failed: {exc}", "WARNING")

@router.get("/status")
async def get_acamis_status(sim_id: str):
    return service.status(_simulation(sim_id))

@router.post("/scenarios/reset")
async def reset_scenario(sim_id: str):
    return service.clear_scenario(_simulation(sim_id))

@router.post("/scenarios/{scenario}")
async def inject_scenario(sim_id: str, scenario: str):
    try:
        sim = _simulation(sim_id)
        service.inject_scenario(sim, scenario)
        await _automatic_model_review(sim, "SCENARIO_INJECTED")
        return service.status(sim)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@router.post("/autonomy")
async def update_autonomy(sim_id: str, request: AutonomyRequest):
    try:
        sim = _simulation(sim_id)
        service.set_autonomy(sim, request.mode.upper())
        await _automatic_model_review(sim, "AUTONOMY_ENABLED")
        return service.status(sim)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@router.post("/procedures/{procedure}")
async def execute_procedure(sim_id: str, procedure: str, request: ProcedureRequest | None = None):
    try:
        return service.execute_procedure(_simulation(sim_id), procedure, human_verified=bool(request and request.human_verified))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@router.post("/model/connect")
async def connect_model(sim_id: str, request: ModelConnectionRequest):
    try:
        sim = _simulation(sim_id)
        result = await model_gateway.connect(sim, request.provider, request.model, request.api_key, request.base_url)
        service._audit(sim, "MODEL_CONNECTION_VERIFIED", f"Verified advisory model connection: {result['provider']} / {result['model']}.")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@router.post("/model/disconnect")
async def disconnect_model(sim_id: str):
    sim = _simulation(sim_id)
    model_gateway.disconnect(sim)
    service._audit(sim, "MODEL_DISCONNECTED", "External advisory model disconnected and its transient API key discarded.")
    return service.status(sim)

@router.post("/model/chat")
async def model_chat(sim_id: str, request: ModelChatRequest):
    try:
        sim = _simulation(sim_id)
        context = service.status(sim)
        context.pop("snapshot", None)
        result = await model_gateway.ask(sim, request.message, context)
        service._audit(sim, "MODEL_ADVISORY_RECEIVED", f"Received advisory analysis from {result['provider']} / {result['model']}.")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
