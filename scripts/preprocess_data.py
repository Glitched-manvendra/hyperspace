"""
Data Preprocessing Script — Orbital Nexus

Cleans raw CSV datasets and outputs standardized formats.
Run from project root: python scripts/preprocess_data.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"


def preprocess_weather():
    """Clean and standardize weather.csv"""
    print("📡 Preprocessing weather data...")
    # TODO: Load raw weather CSV, handle missing values, standardize columns
    # Example: df = pd.read_csv(DATA_RAW / "weather.csv", comment="#")
    print("   → Skipped (no raw data yet)")


def preprocess_soil():
    """Clean and standardize soil_moisture.csv"""
    print("🌍 Preprocessing soil moisture data...")
    # TODO: Load raw soil moisture CSV, interpolate gaps
    print("   → Skipped (no raw data yet)")


def preprocess_ndvi():
    """Clean and standardize ndvi.csv"""
    print("🌿 Preprocessing NDVI data...")
    # TODO: Load raw NDVI CSV, filter outliers, normalize
    print("   → Skipped (no raw data yet)")


def preprocess_crops():
    """Clean and standardize crop_stats.csv"""
    print("🌾 Preprocessing crop statistics...")
    # TODO: Load raw crop CSV, filter to target districts
    print("   → Skipped (no raw data yet)")


def main():
    print("=" * 50)
    print("Orbital Nexus — Data Preprocessing")
    print("=" * 50)
    print(f"Raw data dir:       {DATA_RAW}")
    print(f"Processed data dir: {DATA_PROCESSED}")
    print()

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    preprocess_weather()
    preprocess_soil()
    preprocess_ndvi()
    preprocess_crops()

    print()
    print("✅ Preprocessing complete!")


if __name__ == "__main__":
    main()
