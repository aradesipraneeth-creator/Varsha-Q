# VARSHA-Q Data Ingestion, Alignment & Feature Pipeline

**Project:** VARSHA-Q  
**Team:** QUANTUM LEAPERS  

---

## 1. Modular Provider Interface

VARSHA-Q ingests meteorological and geospatial data through the abstract `WeatherDataProvider` contract:

```python
class WeatherDataProvider(ABC):
    @abstractmethod
    def get_source_name(self) -> str: ...
    @abstractmethod
    def get_mode(self) -> str: ... # 'LIVE', 'RESEARCH', 'DEMO'
    @abstractmethod
    async def fetch_forecast(self, district_ids=None, horizon_hours=24): ...
    @abstractmethod
    async def fetch_observations(self, district_ids=None): ...
    @abstractmethod
    async def get_status(self): ...
```

### Supported Concrete Adapters:
1. **`OpenMeteoProvider` (`LIVE`):** Connects asynchronously to Open-Meteo REST API for ECMWF IFS 0.25° and GFS numerical precipitation fields. Implements timeout protection, HTTP retries, and non-fatal degradation.
2. **`IMDProvider` (`LIVE` / `RESEARCH_FALLBACK`):** Interfaces with official IMD MoES API endpoints using bearer tokens configured via environment variables (`IMD_API_KEY`). Protects credentials and falls back gracefully when unconfigured.
3. **`FileProvider` (`RESEARCH`):** Ingests local NetCDF (`.nc`), Parquet (`.parquet`), or CSV (`.csv`) datasets. Validates file sizes (< 50MB security limit) and schema variables.
4. **`DemoProvider` (`DEMO`):** Provides fully offline, deterministic, multi-regime spatiotemporal tensors simulating realistic Indian weather patterns with known NWP biases.

---

## 2. Spatial Alignment & Quality Assurance

Disparate station observations and NWP grid points are aligned to district administrative polygons via great-circle distance:

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

### Quality Flags:
- `PASSED`: Verified station observation within reasonable physical boundaries ($0 \le R \le 650 \text{ mm}$).
- `IMPUTED_MISSING`: Missing value or negative reading imputed using regional neighbor median.
- `EXTREME_CLIPPED`: Physically implausible sensor spikes ($> 650 \text{ mm}$) clipped and flagged for meteorologist audit.

---

## 3. Spatiotemporal Feature Engineering

For each district $i$ at cycle $t$, the pipeline constructs:
1. **Raw NWP Precipitation:** Forecast accumulation in mm.
2. **Temporal Sequence (LNN Input):** 6-step temporal sequence $[R_{t-5}, \dots, R_t]$ incorporating lagged rainfall, 2m temperature, relative humidity, surface pressure, and wind speed components.
3. **Spatial Node Attributes (GNN Input):** Normalized rainfall, SRTM digital elevation ($z/2000 \text{ m}$), distance to coastline ($d_{\text{coast}}/500 \text{ km}$), topographic slope roughness, latitude, longitude, and seasonal monsoon phase index.
4. **Day-of-Year Cyclic Harmonics:**
   $$\text{sin\_doy} = \sin\left(\frac{2\pi \cdot \text{DOY}}{365.25}\right), \quad \text{cos\_doy} = \cos\left(\frac{2\pi \cdot \text{DOY}}{365.25}\right)$$
