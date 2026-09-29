"""
VARSHA-Q Core Configuration
Handles environment variables, default paths, database connection strings, and runtime operational mode.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "VARSHA-Q"
    FULL_TITLE: str = "Quantum-Inspired Spatiotemporal AI for Regime-Aware Rainfall Forecast Correction"
    VERSION: str = "1.0.0"
    TEAM_NAME: str = "QUANTUM LEAPERS"
    PROBLEM_STATEMENT: str = "SIH PS 26080"

    # Operational Mode: 'LIVE', 'RESEARCH', 'DEMO'
    DEFAULT_MODE: str = os.getenv("VARSHA_MODE", "DEMO")

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parents[3]
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    REPORTS_DIR: Path = BASE_DIR / "reports"

    # Database: Async PostgreSQL / PostGIS or SQLite fallback
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite+aiosqlite:///{BASE_DIR / 'varsha_q.db'}"
    )

    # API Security & CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # IMD / Open-Meteo credentials
    IMD_API_KEY: str = os.getenv("IMD_API_KEY", "")
    IMD_BASE_URL: str = os.getenv("IMD_BASE_URL", "https://api.imd.gov.in/v1")
    OPEN_METEO_URL: str = os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast")

    # Ingestion Schedule
    INGESTION_INTERVAL_MINUTES: int = int(os.getenv("INGESTION_INTERVAL_MINUTES", "15"))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
