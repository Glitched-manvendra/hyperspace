"""
Dataset Fusion Script — Orbital Nexus

Joins preprocessed satellite datasets into a single fused output.
Spatial join on lat/lon, temporal alignment on date.
Run from project root: python scripts/fuse_datasets.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"


def fuse_for_region(region_name: str, lat: float, lon: float) -> dict:
    """
    Fuse all available datasets for a given region.

    In production: loads preprocessed CSVs, does spatial join, and aggregates.
    For hackathon demo: returns mock fused data structure.
    """
    return {
        "region": region_name,
        "lat": lat,
        "lon": lon,
        "fused_at": "2026-02-07T00:00:00Z",
        "weather": {
            "temperature_avg_c": 32.5,
            "humidity_avg_pct": 58.0,
            "rainfall_mm": 145.0,
            "wind_speed_kmh": 12.3,
        },
        "soil": {
            "moisture_pct": 42.3,
            "depth_cm": 30,
        },
        "ndvi": {
            "current": 0.68,
            "trend_6m": [0.55, 0.58, 0.61, 0.63, 0.66, 0.68],
        },
        "crop_stats": {
            "top_crops": ["Wheat", "Mustard", "Sugarcane"],
            "avg_yield_tonnes_per_ha": 3.2,
        },
        "data_sources": ["MODIS", "Sentinel-2", "NASA SMAP", "Open-Meteo"],
    }


def main():
    print("=" * 50)
    print("Orbital Nexus — Dataset Fusion")
    print("=" * 50)

    # Default: fuse for Greater Noida
    region = "Greater Noida, Uttar Pradesh"
    fused = fuse_for_region(region, lat=28.4744, lon=77.504)

    output_file = DATA_PROCESSED / "fused_greater_noida.json"
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(fused, f, indent=2)

    print(f"✅ Fused data written to: {output_file}")
    print(f"   Region: {region}")
    print(f"   Sources: {', '.join(fused['data_sources'])}")


if __name__ == "__main__":
    main()
