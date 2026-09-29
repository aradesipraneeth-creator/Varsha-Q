"""
VARSHA-Q Data Provider Base Architecture
Defines the standard abstract contract for meteorological data ingestion:
- Ingest NWP forecasts (GFS, ECMWF, NCUM)
- Ingest ground observations (AWS, ARG, Rain Gauge, IMERG satellite)
- Ingest terrain and geographic rasters
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class WeatherDataProvider(ABC):
    """Abstract Base Class for weather and meteorological data ingestion providers."""

    @abstractmethod
    def get_source_name(self) -> str:
        """Returns provider identifier name."""
        pass

    @abstractmethod
    def get_mode(self) -> str:
        """Returns operational mode: 'LIVE', 'RESEARCH', or 'DEMO'."""
        pass

    @abstractmethod
    async def fetch_forecast(self, district_ids: Optional[List[str]] = None, horizon_hours: int = 24) -> Dict[str, Any]:
        """
        Fetches NWP forecast rainfall and atmospheric conditions.
        """
        pass

    @abstractmethod
    async def fetch_observations(self, district_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetches observational rainfall (ground truth / rain gauges / AWS / satellite).
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Returns health, freshness timestamp, and latency of data connection.
        """
        pass
