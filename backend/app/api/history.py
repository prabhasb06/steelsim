from fastapi import APIRouter, HTTPException, Query
from app.api.routes import manager

router = APIRouter(prefix="/api/history", tags=["operations history"])


def require_run(run_id):
    result = manager.history.detail(run_id)
    if result is None:
        raise HTTPException(404, "Run not found")
    return result


@router.get("/runs")
def runs(limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0)):
    return manager.history.runs(limit, offset)


@router.get("/runs/{run_id}")
def detail(run_id: str):
    result = require_run(run_id)
    result.pop("checkpoint")
    return result


@router.get("/runs/{run_id}/frames")
def frames(run_id: str, after: int = Query(0, ge=0), limit: int = Query(500, ge=1, le=500)):
    require_run(run_id)
    return manager.history.frames(run_id, after, limit)


@router.get("/runs/{run_id}/report")
def report(run_id: str):
    result = require_run(run_id)
    checkpoint = result.pop("checkpoint")
    result["latest_state"] = checkpoint["state"]
    result["latest_signal_findings"] = checkpoint["signal_monitor"]["findings"]
    result["last_resolution"] = checkpoint["acamis_last_resolution"]
    result["scope"] = "SteelSim simulated operational evidence; no physical plant control."
    result["contract_version"] = "operations-report.v1"
    return result


@router.post("/runs/{run_id}/restore")
async def restore(run_id: str):
    require_run(run_id)
    try:
        sim = manager.history.restore(run_id, manager)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    return sim.get_state()
