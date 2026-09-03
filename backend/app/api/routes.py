import asyncio
import base64
import os
import secrets

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List

from pydantic import BaseModel, Field
from app.models.schemas import (
    SimulationConfiguration, SimulationState, SimulationSnapshot, 
    SimulationEvent, ChangeSpeedRequest
)
from app.manager.simulation_manager import SimulationManager
from app.engine.topology_validator import validate_topology

router = APIRouter(prefix="/api")

manager = SimulationManager()


def require_runnable_topology(sim) -> None:
    validation = validate_topology(sim.config.plant)
    if sim.config.plant.nodes and not validation.is_valid:
        blocking = sum(1 for issue in validation.issues if issue.blocks_simulation)
        raise ValueError(f"Simulation blocked by {blocking} topology issue{'s' if blocking != 1 else ''}")

class CommandRequest(BaseModel):
    command: str
    payload: dict = Field(default_factory=dict)

@router.get("/health")
async def health():
    return {"status": "ok", "service": "steelsim-backend"}

@router.get("/simulations", response_model=List[SimulationState])
async def list_simulations():
    return manager.list_simulations()

@router.post("/simulations", response_model=SimulationState)
async def create_simulation(config: SimulationConfiguration):
    try:
        sim = manager.create_simulation(config)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return sim.get_state()

@router.get("/simulations/{sim_id}", response_model=SimulationState)
async def get_simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.get_state()

@router.post("/simulations/{sim_id}/command", response_model=SimulationSnapshot)
async def execute_command(sim_id: str, req: CommandRequest):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    cmd = req.command.lower()
    try:
        if cmd in ("start", "run"):
            require_runnable_topology(sim)
            sim.start()
        elif cmd == "resume":
            if sim.status.value != "PAUSED":
                raise ValueError(f"Cannot resume from {sim.status}")
            require_runnable_topology(sim)
            sim.start()
        elif cmd == "pause":
            sim.pause()
        elif cmd == "reset":
            sim.reset()
        elif cmd == "set_speed":
            speed = req.payload.get("speed", "1x")
            if not isinstance(speed, str):
                raise ValueError("Speed must be a string")
            sim.set_speed(speed)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown command: {req.command}")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return sim.get_snapshot()

@router.post("/simulations/{sim_id}/start", response_model=SimulationState)
async def start_simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    try:
        require_runnable_topology(sim)
        sim.start()
        return sim.get_state()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulations/{sim_id}/pause", response_model=SimulationState)
async def pause_simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    try:
        sim.pause()
        return sim.get_state()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulations/{sim_id}/resume", response_model=SimulationState)
async def resume_simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    try:
        if sim.status.value != "PAUSED":
            raise ValueError(f"Cannot resume from {sim.status}")
        require_runnable_topology(sim)
        sim.start()
        return sim.get_state()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulations/{sim_id}/reset", response_model=SimulationState)
async def reset_simulation(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    sim.reset()
    return sim.get_state()

@router.post("/simulations/{sim_id}/speed", response_model=SimulationState)
async def change_speed(sim_id: str, request: ChangeSpeedRequest):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    try:
        sim.set_speed(request.speed)
        return sim.get_state()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/simulations/{sim_id}/state", response_model=SimulationState)
async def get_state(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.get_state()

@router.get("/simulations/{sim_id}/events", response_model=List[SimulationEvent])
async def get_events(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.events

@router.get("/simulations/{sim_id}/snapshot", response_model=SimulationSnapshot)
async def get_snapshot(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.get_snapshot()


@router.delete("/simulations/{sim_id}")
async def delete_simulation(sim_id: str):
    if not manager.delete_simulation(sim_id):
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"deleted": True, "simulation_id": sim_id}

@router.get("/simulations/{sim_id}/snapshots", response_model=List[SimulationSnapshot])
async def get_snapshots(sim_id: str):
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.get_snapshots()

@router.websocket("/simulations/{sim_id}/stream")
async def stream_simulation(websocket: WebSocket, sim_id: str):
    api_key = os.getenv("STEELSIM_API_KEY", "").strip()
    requested_protocols = [
        value.strip()
        for value in websocket.headers.get("sec-websocket-protocol", "").split(",")
        if value.strip()
    ]
    encoded_key = next(
        (value.removeprefix("steelsim-key.") for value in requested_protocols if value.startswith("steelsim-key.")),
        "",
    )
    try:
        supplied_key = base64.urlsafe_b64decode(encoded_key + "=" * (-len(encoded_key) % 4)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        supplied_key = ""
    if api_key and not secrets.compare_digest(supplied_key, api_key):
        await websocket.close(code=4401, reason="Invalid or missing SteelSim API key")
        return
    selected_protocol = "steelsim" if "steelsim" in requested_protocols else None
    await websocket.accept(subprotocol=selected_protocol)
    sim = manager.get_simulation(sim_id)
    if not sim:
        await websocket.close(code=4404, reason="Simulation not found")
        return

    queue = sim.subscribe()
    await websocket.send_json(sim.get_snapshot().model_dump(mode="json"))
    try:
        while True:
            try:
                snapshot = await asyncio.wait_for(queue.get(), timeout=15.0)
            except asyncio.TimeoutError:
                snapshot = sim.get_snapshot()
            await websocket.send_json(snapshot.model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    finally:
        sim.unsubscribe(queue)
