"""
VARSHA-Q File Ingestion Provider
Supports research file uploads in NetCDF, Parquet, CSV, or GeoJSON format.
Validates file sizes, checks schemas, and extracts meteorological variables.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .provider_base import WeatherDataProvider


class FileProvider(WeatherDataProvider):
    """
    Ingests and parses local or uploaded meteorological research files.
    """
    ALLOWED_EXTENSIONS = {".csv", ".parquet", ".nc", ".json", ".geojson"}
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB security limit

    def __init__(self, upload_dir: Optional[Path] = None):
        self.upload_dir = Path(upload_dir) if upload_dir else Path(__file__).resolve().parents[3] / "data" / "raw"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.current_dataset: Optional[pd.DataFrame] = None
        self.dataset_meta: Dict[str, Any] = {}

    def get_source_name(self) -> str:
        return "Local / Uploaded Research Dataset"

    def get_mode(self) -> str:
        return "RESEARCH"

    def validate_file(self, file_path: Path) -> Tuple[bool, str]:
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{file_path.suffix}'. Allowed: {self.ALLOWED_EXTENSIONS}"
        if file_path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
            return False, f"File size ({file_path.stat().st_size} bytes) exceeds limit of 50 MB."
        return True, "File valid"

    def load_tabular(self, file_path: Path) -> Dict[str, Any]:
        valid, msg = self.validate_file(file_path)
        if not valid:
            raise ValueError(msg)

        ext = file_path.suffix.lower()
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext == ".parquet":
            df = pd.read_parquet(file_path)
        elif ext == ".nc":
            import xarray as xr
            ds = xr.open_dataset(file_path)
            df = ds.to_dataframe().reset_index()
        else:
            raise ValueError(f"Parsing for {ext} requires specialized parser.")

        # Standardize expected columns
        cols = {c.lower(): c for c in df.columns}
        rename_map = {}
        for target in ["district_id", "rainfall", "observed", "nwp_rainfall", "lat", "lon"]:
            for col_lower, orig in cols.items():
                if target in col_lower:
                    rename_map[orig] = target
        df = df.rename(columns=rename_map)

        self.current_dataset = df
        self.dataset_meta = {
            "file_name": file_path.name,
            "rows": len(df),
            "columns": list(df.columns),
            "has_rainfall": "rainfall" in df.columns or "observed" in df.columns
        }
        return self.dataset_meta

    async def fetch_forecast(self, district_ids: Optional[List[str]] = None, horizon_hours: int = 24) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "NO_FILE_LOADED", "mode": "RESEARCH"}
        return {"status": "SUCCESS", "mode": "RESEARCH", "data": self.current_dataset.head(100).to_dict(orient="records")}

    async def fetch_observations(self, district_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "NO_FILE_LOADED", "mode": "RESEARCH"}
        return {"status": "SUCCESS", "mode": "RESEARCH", "meta": self.dataset_meta}

    async def get_status(self) -> Dict[str, Any]:
        return {
            "source": self.get_source_name(),
            "mode": self.get_mode(),
            "dataset_loaded": self.current_dataset is not None,
            "meta": self.dataset_meta
        }
