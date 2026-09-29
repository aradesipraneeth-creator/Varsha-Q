from fastapi.testclient import TestClient
from backend.app.main import app

def test_single_service():
    with TestClient(app) as client:
        # 1. Test root / serves HTML
        res_root = client.get("/")
        print(f"Root / status: {res_root.status_code}, content-type: {res_root.headers.get('content-type')}")
        assert res_root.status_code == 200
        assert "VARSHA-Q" in res_root.text

        # 2. Test assets
        res_js = client.get("/assets/index-B1t4n_Lh.js")
        print(f"JS asset status: {res_js.status_code}, size: {len(res_js.content)} bytes")
        assert res_js.status_code == 200

        # 3. Test /health
        res_health = client.get("/health")
        print(f"Health status: {res_health.status_code}, json: {res_health.json()['status']}")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

        # 4. Test API latest forecast
        res_api = client.get("/api/forecast/latest")
        districts = res_api.json().get("district_forecasts", [])
        print(f"API latest forecast status: {res_api.status_code}, districts count: {len(districts)}")
        assert res_api.status_code == 200
        assert len(districts) == 37

        # 5. Test SPA sub-route
        res_spa = client.get("/forecast/regimes")
        print(f"SPA sub-route status: {res_spa.status_code}")
        assert res_spa.status_code == 200
        assert "VARSHA-Q" in res_spa.text

    print("\nSUCCESS: All single-service hosting checks passed perfectly!")

if __name__ == "__main__":
    test_single_service()
