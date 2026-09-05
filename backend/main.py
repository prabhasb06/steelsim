import os
import secrets

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.api.plant import router as plant_router
from app.api.acamis import router as acamis_router

app = FastAPI(title="SteelSim Backend")


def configured_api_key() -> str:
    return os.getenv("STEELSIM_API_KEY", "").strip()


@app.middleware("http")
async def protect_api(request: Request, call_next):
    api_key = configured_api_key()
    public_path = request.url.path == "/api/health" or request.method == "OPTIONS"
    if api_key and request.url.path.startswith("/api/") and not public_path:
        supplied = request.headers.get("x-steelsim-api-key", "")
        if not secrets.compare_digest(supplied, api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing SteelSim API key"})
    return await call_next(request)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "STEELSIM_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(plant_router)
app.include_router(acamis_router)

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
