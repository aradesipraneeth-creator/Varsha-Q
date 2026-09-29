"""
Integration and End-to-End Tests for FastAPI Web Endpoints
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VARSHA-Q"

def test_system_status():
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_healthy"] is True
    assert "data_sources" in data
    assert "models_status" in data

def test_forecast_latest():
    resp = client.get("/api/forecast/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert "regime_intelligence" in data
    assert "district_forecasts" in data
    assert len(data["district_forecasts"]) > 0

def test_districts_geojson():
    resp = client.get("/api/districts/geojson")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0

def test_verification_endpoint():
    resp = client.get("/api/verification")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall" in data
    assert "regime_wise" in data
    assert len(data["regime_wise"]) == 5

def test_optimization_benchmark_endpoint():
    resp = client.post("/api/optimization/run")
    assert resp.status_code == 200
    data = resp.json()
    assert "classical_baseline" in data
    assert "quantum_inspired" in data
    assert "energy_delta" in data
