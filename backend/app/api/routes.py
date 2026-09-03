from fastapi import APIRouter, HTTPException
from typing import List

from pydantic import BaseModel, Field
from app.models.schemas import (
    SimulationConfiguration, SimulationState, SimulationSnapshot, 
    SimulationEvent, ChangeSpeedRequest
)
from app.manager.simulation_manager import SimulationManager

router = APIRouter(prefix="/api")

manager = SimulationManager()

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
    sim = manager.create_simulation(config)
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
        if cmd in ("start", "run", "resume"):
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
    # Same logic as start
    sim = manager.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    try:
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
