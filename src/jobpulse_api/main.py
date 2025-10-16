"""FastAPI application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from jobpulse_api.db import init_db
from jobpulse_api.routes import health, jobs
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    init_db()
    yield
app = FastAPI(
    title="JobPulse API",
    version="0.1.0",
    lifespan=lifespan
)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
app.include_router(health.router, tags=["health"])
app.include_router(jobs.router, tags=["jobs"])
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(str(static_path / "index.html"))
