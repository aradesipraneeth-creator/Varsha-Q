"""
VARSHA-Q District Service
Exposes district metadata, topological neighbors, and GeoJSON geometry.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from data.geo.districts_metadata import DISTRICTS_DATA


class DistrictService:
    def __init__(self):
        self.districts = DISTRICTS_DATA
        self.geojson_path = Path(__file__).resolve().parents[3] / "data" / "geo" / "india_districts.geojson"
        self._geojson = None

    def get_all_districts(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        if state:
            return [d for d in self.districts if d["state"].lower() == state.lower()]
        return self.districts

    def get_district_by_id(self, district_id: str) -> Optional[Dict[str, Any]]:
        for d in self.districts:
            if d["id"].lower() == district_id.lower():
                return d
        return None

    def get_states(self) -> List[str]:
        states = sorted(list({d["state"] for d in self.districts}))
        return states

    def get_geojson(self) -> Dict[str, Any]:
        if self._geojson is None and self.geojson_path.exists():
            with open(self.geojson_path, "r", encoding="utf-8") as f:
                self._geojson = json.load(f)
        return self._geojson if self._geojson else {"type": "FeatureCollection", "features": []}


district_service = DistrictService()
