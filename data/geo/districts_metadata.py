"""
VARSHA-Q District Definitions & GeoJSON Generator
Generates realistic district boundaries and topological adjacencies for Indian meteorological zones.
"""
import json
import math
from pathlib import Path

DISTRICTS_DATA = [
    # Coastal & Marine Monsoon
    {
        "id": "AP_VSKP",
        "name": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "lat": 17.6868,
        "lon": 83.2185,
        "elevation_m": 45.0,
        "coastal_dist_km": 2.0,
        "typical_regime": "COASTAL",
        "neighbors": ["AP_EGOD", "OD_KPT"]
    },
    {
        "id": "AP_EGOD",
        "name": "East Godavari",
        "state": "Andhra Pradesh",
        "lat": 16.9891,
        "lon": 82.2475,
        "elevation_m": 25.0,
        "coastal_dist_km": 5.0,
        "typical_regime": "COASTAL",
        "neighbors": ["AP_VSKP", "AP_KRI"]
    },
    {
        "id": "AP_KRI",
        "name": "Krishna",
        "state": "Andhra Pradesh",
        "lat": 16.1824,
        "lon": 81.1345,
        "elevation_m": 18.0,
        "coastal_dist_km": 10.0,
        "typical_regime": "COASTAL",
        "neighbors": ["AP_EGOD", "AP_GNT", "TG_KMM"]
    },
    {
        "id": "AP_GNT",
        "name": "Guntur",
        "state": "Andhra Pradesh",
        "lat": 16.3067,
        "lon": 80.4365,
        "elevation_m": 33.0,
        "coastal_dist_km": 25.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["AP_KRI", "AP_ATP", "TG_KMM"]
    },
    {
        "id": "AP_ATP",
        "name": "Anantapur",
        "state": "Andhra Pradesh",
        "lat": 14.6819,
        "lon": 77.6006,
        "elevation_m": 335.0,
        "coastal_dist_km": 280.0,
        "typical_regime": "BREAK_MONSOON",
        "neighbors": ["AP_GNT", "TG_HYD"]
    },
    # Odisha - Bay of Bengal Lows
    {
        "id": "OD_PURI",
        "name": "Puri",
        "state": "Odisha",
        "lat": 19.8135,
        "lon": 85.8312,
        "elevation_m": 12.0,
        "coastal_dist_km": 1.0,
        "typical_regime": "DEPRESSION_LOW",
        "neighbors": ["OD_KHD", "OD_BLS"]
    },
    {
        "id": "OD_KHD",
        "name": "Khordha (Bhubaneswar)",
        "state": "Odisha",
        "lat": 20.2961,
        "lon": 85.8245,
        "elevation_m": 45.0,
        "coastal_dist_km": 40.0,
        "typical_regime": "DEPRESSION_LOW",
        "neighbors": ["OD_PURI", "OD_CTC"]
    },
    {
        "id": "OD_CTC",
        "name": "Cuttack",
        "state": "Odisha",
        "lat": 20.4625,
        "lon": 85.8830,
        "elevation_m": 36.0,
        "coastal_dist_km": 65.0,
        "typical_regime": "DEPRESSION_LOW",
        "neighbors": ["OD_KHD", "OD_BLS"]
    },
    {
        "id": "OD_BLS",
        "name": "Balasore",
        "state": "Odisha",
        "lat": 21.4934,
        "lon": 86.9135,
        "elevation_m": 16.0,
        "coastal_dist_km": 15.0,
        "typical_regime": "DEPRESSION_LOW",
        "neighbors": ["OD_PURI", "OD_CTC", "WB_S24P"]
    },
    {
        "id": "OD_KPT",
        "name": "Koraput",
        "state": "Odisha",
        "lat": 18.8135,
        "lon": 82.7118,
        "elevation_m": 870.0,
        "coastal_dist_km": 130.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["AP_VSKP", "TG_KMM"]
    },
    # Telangana - Interior Active Trough
    {
        "id": "TG_HYD",
        "name": "Hyderabad",
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "elevation_m": 542.0,
        "coastal_dist_km": 290.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_WRG", "TG_NZB", "AP_ATP"]
    },
    {
        "id": "TG_WRG",
        "name": "Warangal",
        "state": "Telangana",
        "lat": 17.9689,
        "lon": 79.5941,
        "elevation_m": 266.0,
        "coastal_dist_km": 210.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_HYD", "TG_KMM", "TG_KRM"]
    },
    {
        "id": "TG_KMM",
        "name": "Khammam",
        "state": "Telangana",
        "lat": 17.2473,
        "lon": 80.1514,
        "elevation_m": 107.0,
        "coastal_dist_km": 140.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_WRG", "AP_KRI", "AP_GNT", "OD_KPT"]
    },
    {
        "id": "TG_NZB",
        "name": "Nizamabad",
        "state": "Telangana",
        "lat": 18.6725,
        "lon": 78.0941,
        "elevation_m": 395.0,
        "coastal_dist_km": 360.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_HYD", "TG_KRM", "MH_NGP"]
    },
    {
        "id": "TG_KRM",
        "name": "Karimnagar",
        "state": "Telangana",
        "lat": 18.4386,
        "lon": 79.1288,
        "elevation_m": 265.0,
        "coastal_dist_km": 280.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_NZB", "TG_WRG", "MH_NGP"]
    },
    # Kerala - Western Ghats Orographic
    {
        "id": "KL_WYD",
        "name": "Wayanad",
        "state": "Kerala",
        "lat": 11.6854,
        "lon": 76.1320,
        "elevation_m": 920.0,
        "coastal_dist_km": 55.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["KL_KKD", "KL_IDK"]
    },
    {
        "id": "KL_IDK",
        "name": "Idukki",
        "state": "Kerala",
        "lat": 9.8494,
        "lon": 76.9804,
        "elevation_m": 1200.0,
        "coastal_dist_km": 70.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["KL_WYD", "KL_EKM", "KL_TVM"]
    },
    {
        "id": "KL_EKM",
        "name": "Ernakulam (Kochi)",
        "state": "Kerala",
        "lat": 9.9816,
        "lon": 76.2999,
        "elevation_m": 4.0,
        "coastal_dist_km": 2.0,
        "typical_regime": "COASTAL",
        "neighbors": ["KL_IDK", "KL_KKD", "KL_TVM"]
    },
    {
        "id": "KL_KKD",
        "name": "Kozhikode",
        "state": "Kerala",
        "lat": 11.2588,
        "lon": 75.7804,
        "elevation_m": 10.0,
        "coastal_dist_km": 3.0,
        "typical_regime": "COASTAL",
        "neighbors": ["KL_WYD", "KL_EKM"]
    },
    {
        "id": "KL_TVM",
        "name": "Thiruvananthapuram",
        "state": "Kerala",
        "lat": 8.5241,
        "lon": 76.9366,
        "elevation_m": 15.0,
        "coastal_dist_km": 3.0,
        "typical_regime": "COASTAL",
        "neighbors": ["KL_IDK", "KL_EKM"]
    },
    # Maharashtra - Coastal Konkan to Western Ghats
    {
        "id": "MH_MUM",
        "name": "Mumbai Suburban",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "elevation_m": 14.0,
        "coastal_dist_km": 2.0,
        "typical_regime": "COASTAL",
        "neighbors": ["MH_RTG", "MH_PUN"]
    },
    {
        "id": "MH_RTG",
        "name": "Ratnagiri",
        "state": "Maharashtra",
        "lat": 16.9902,
        "lon": 73.3120,
        "elevation_m": 35.0,
        "coastal_dist_km": 1.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["MH_MUM", "MH_KLP", "MH_PUN"]
    },
    {
        "id": "MH_PUN",
        "name": "Pune",
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "elevation_m": 560.0,
        "coastal_dist_km": 120.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["MH_MUM", "MH_RTG", "MH_KLP"]
    },
    {
        "id": "MH_KLP",
        "name": "Kolhapur",
        "state": "Maharashtra",
        "lat": 16.7050,
        "lon": 74.2433,
        "elevation_m": 569.0,
        "coastal_dist_km": 110.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["MH_RTG", "MH_PUN"]
    },
    {
        "id": "MH_NGP",
        "name": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.1458,
        "lon": 79.0882,
        "elevation_m": 310.0,
        "coastal_dist_km": 680.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["TG_NZB", "TG_KRM", "MP_JBL"]
    },
    # West Bengal - Delta & Foothills
    {
        "id": "WB_KOL",
        "name": "Kolkata",
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "elevation_m": 9.0,
        "coastal_dist_km": 70.0,
        "typical_regime": "DEPRESSION_LOW",
        "neighbors": ["WB_S24P", "WB_MSD"]
    },
    {
        "id": "WB_S24P",
        "name": "South 24 Parganas",
        "state": "West Bengal",
        "lat": 22.1352,
        "lon": 88.5448,
        "elevation_m": 6.0,
        "coastal_dist_km": 5.0,
        "typical_regime": "COASTAL",
        "neighbors": ["WB_KOL", "OD_BLS"]
    },
    {
        "id": "WB_DJL",
        "name": "Darjeeling",
        "state": "West Bengal",
        "lat": 27.0410,
        "lon": 88.2663,
        "elevation_m": 2042.0,
        "coastal_dist_km": 600.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["WB_JPG"]
    },
    {
        "id": "WB_JPG",
        "name": "Jalpaiguri",
        "state": "West Bengal",
        "lat": 26.5414,
        "lon": 88.7196,
        "elevation_m": 89.0,
        "coastal_dist_km": 540.0,
        "typical_regime": "BREAK_MONSOON", # Heavy rain during monsoon breaks as trough shifts north
        "neighbors": ["WB_DJL", "AS_GHY"]
    },
    {
        "id": "WB_MSD",
        "name": "Murshidabad",
        "state": "West Bengal",
        "lat": 24.1754,
        "lon": 88.2802,
        "elevation_m": 19.0,
        "coastal_dist_km": 240.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["WB_KOL", "WB_JPG"]
    },
    # Northeast / Meghalaya (Orographic Extreme)
    {
        "id": "AS_GHY",
        "name": "Kamrup (Guwahati)",
        "state": "Assam",
        "lat": 26.1445,
        "lon": 91.7362,
        "elevation_m": 55.0,
        "coastal_dist_km": 420.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["WB_JPG", "ML_SO"]
    },
    {
        "id": "ML_SO",
        "name": "East Khasi Hills (Sohra/Cherrapunji)",
        "state": "Meghalaya",
        "lat": 25.2986,
        "lon": 91.7328,
        "elevation_m": 1484.0,
        "coastal_dist_km": 320.0,
        "typical_regime": "OROGRAPHIC",
        "neighbors": ["AS_GHY"]
    },
    # Central Trough - Madhya Pradesh
    {
        "id": "MP_BPL",
        "name": "Bhopal",
        "state": "Madhya Pradesh",
        "lat": 23.2599,
        "lon": 77.4126,
        "elevation_m": 527.0,
        "coastal_dist_km": 550.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["MP_JBL", "MH_NGP"]
    },
    {
        "id": "MP_JBL",
        "name": "Jabalpur",
        "state": "Madhya Pradesh",
        "lat": 23.1815,
        "lon": 79.9864,
        "elevation_m": 411.0,
        "coastal_dist_km": 590.0,
        "typical_regime": "ACTIVE_MONSOON",
        "neighbors": ["MP_BPL", "MH_NGP"]
    },
    # Break Monsoon Arid / Rain-Shadow - Rajasthan & Gujarat
    {
        "id": "RJ_JDH",
        "name": "Jodhpur",
        "state": "Rajasthan",
        "lat": 26.2389,
        "lon": 73.0243,
        "elevation_m": 231.0,
        "coastal_dist_km": 410.0,
        "typical_regime": "BREAK_MONSOON",
        "neighbors": ["RJ_BKN", "GJ_AMD"]
    },
    {
        "id": "RJ_BKN",
        "name": "Bikaner",
        "state": "Rajasthan",
        "lat": 28.0229,
        "lon": 73.3119,
        "elevation_m": 242.0,
        "coastal_dist_km": 600.0,
        "typical_regime": "BREAK_MONSOON",
        "neighbors": ["RJ_JDH"]
    },
    {
        "id": "GJ_AMD",
        "name": "Ahmedabad",
        "state": "Gujarat",
        "lat": 23.0225,
        "lon": 72.5714,
        "elevation_m": 53.0,
        "coastal_dist_km": 80.0,
        "typical_regime": "BREAK_MONSOON",
        "neighbors": ["RJ_JDH", "MH_MUM"]
    }
]

def generate_district_polygon(lat: float, lon: float, radius_deg: float = 0.35, points: int = 12, seed_offset: float = 0.0):
    """Generates a realistic smooth polygon boundary around a district centroid."""
    coords = []
    for i in range(points):
        angle = 2.0 * math.pi * (i / points)
        # Small deterministic perturbation for organic look
        r = radius_deg * (0.85 + 0.3 * math.sin(angle * 3.0 + seed_offset))
        p_lon = lon + r * math.cos(angle) / math.cos(math.radians(lat))
        p_lat = lat + r * math.sin(angle)
        coords.append([round(p_lon, 4), round(p_lat, 4)])
    coords.append(coords[0])  # Closed loop
    return [coords]

def create_geojson():
    features = []
    for idx, d in enumerate(DISTRICTS_DATA):
        poly_coords = generate_district_polygon(d["lat"], d["lon"], radius_deg=0.32, seed_offset=idx * 1.3)
        feature = {
            "type": "Feature",
            "id": d["id"],
            "properties": {
                "id": d["id"],
                "name": d["name"],
                "state": d["state"],
                "elevation_m": d["elevation_m"],
                "coastal_dist_km": d["coastal_dist_km"],
                "typical_regime": d["typical_regime"],
                "neighbors": d["neighbors"],
                "lat": d["lat"],
                "lon": d["lon"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": poly_coords
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    out_path = Path(__file__).resolve().parent / "india_districts.geojson"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    print(f"Wrote {len(features)} districts to {out_path}")
    return geojson

if __name__ == "__main__":
    create_geojson()
