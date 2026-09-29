"""
VARSHA-Q Main Application Entrypoint
FastAPI application with REST endpoints, WebSocket streaming, CORS, and lifecycle management.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import init_db
from .api.endpoints import router as api_router
from .api.websocket import ws_router
from .services.forecast_service import forecast_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database initialization and model pre-warming."""
    # 1. Initialize SQLite / PostgreSQL tables
    try:
        await init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database init warning (running in memory-only fallback if needed): {e}")

    # 2. Pre-warm default demo forecast so UI loads instantaneously
    try:
        await forecast_service.get_latest_forecast()
        print("Forecast pipeline pre-warmed successfully.")
    except Exception as e:
        print(f"Warning pre-warming pipeline: {e}")

    yield

    print("VARSHA-Q shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.FULL_TITLE}\nProblem Statement: {settings.PROBLEM_STATEMENT}\nTeam: {settings.TEAM_NAME}",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development & demo across ports 3000 / 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "title": settings.FULL_TITLE,
        "team": settings.TEAM_NAME,
        "problem_statement": settings.PROBLEM_STATEMENT,
        "docs_url": "/docs",
        "api_status": "/api/system/status",
        "latest_forecast": "/api/forecast/latest",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
