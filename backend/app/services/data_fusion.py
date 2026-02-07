"""
Data Fusion Engine — Orbital Nexus

The "Orbital Fusion" backend: combines five real data sources
into a single location context for AI-powered crop recommendations.

Sources:
  1. Open-Meteo API — Live weather + soil moisture (Free, No Key)
  2. ISRO Bhuvan LULC API — Land-use classification (Agriculture validation)
  3. Agromonitoring API — Satellite imagery, NDVI & polygon-based data
  4. SISIndia REST API (ISRIC) — Live soil nutrient data (pH, N, P, K, OC, etc.)
  5. Offline Soil Database — District-level soil type/nutrient mapping (fallback)

Designed for resilience: every external call has a timeout + fallback
so the demo NEVER crashes on stage.
"""

import json
import math
import logging
import os
from pathlib import Path
from typing import Any

import httpx

from app.services.sisindia_soil import fetch_sisindia_soil

logger = logging.getLogger("orbital.fusion")

# ── API Keys ────────────────────────────────────────────────────────
AGRO_GEOCODING_KEY = os.getenv("AGRO_GEOCODING_KEY")
AGRO_SATELLITE_KEY = os.getenv("AGRO_SATELLITE_KEY")

logger = logging.getLogger("orbital.fusion")

# ── Soil Database (loaded once at import time) ──────────────────────
_SOIL_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "data" / "soil_database.json"
)

try:
    with open(_SOIL_DB_PATH, "r", encoding="utf-8") as f:
        _SOIL_DB: dict[str, Any] = json.load(f)
    logger.info("Soil database loaded: %d regions", len(_SOIL_DB.get("regions", [])))
except FileNotFoundError:
    logger.warning("soil_database.json not found at %s — using defaults", _SOIL_DB_PATH)
    _SOIL_DB = {
        "regions": [],
        "default": {
            "soil_type": "Alluvial",
            "soil_ph": 7.0,
            "soil_texture": "Loam",
            "organic_carbon_pct": 0.45,
            "nitrogen_kg_ha": 200,
            "phosphorus_kg_ha": 15,
            "potassium_kg_ha": 220,
            "recommended_crops": ["Rice", "Wheat", "Pulses"],
            "description": "Default Indian soil profile.",
        },
    }

# ── Timeouts (aggressive — we can't stall the demo) ────────────────
_TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=3.0, pool=3.0)


# =====================================================================
#  PUBLIC API
# =====================================================================


async def get_location_context(lat: float, lon: float) -> dict[str, Any]:
    """
    Master fusion function.
    Gathers weather, soil, land classification, and satellite NDVI for a coordinate pair.

    Returns:
        {
            "weather": { "temp": 28.5, "humidity": 60, "rain": 0, "moisture": 0.32 },
            "soil": { "type": "Loamy", "ph": 7.2, ... },
            "land_classification": "Verified Agriculture (ISRO Bhuvan)",
            "satellite": { "ndvi": 0.62, "source": "Agromonitoring" },
            "region": "Greater Noida, Uttar Pradesh",
            "data_sources": ["Open-Meteo", "ISRO Bhuvan LULC", "Agromonitoring", "Soil Database"]
        }
    """
    import asyncio

    weather_task = asyncio.create_task(_fetch_weather(lat, lon))
    bhuvan_task = asyncio.create_task(_check_bhuvan_land_use(lat, lon))
    agro_task = asyncio.create_task(_fetch_agro_satellite(lat, lon))
    sisindia_task = asyncio.create_task(fetch_sisindia_soil(lat, lon))

    weather = await weather_task
    land_class = await bhuvan_task
    satellite = await agro_task
    live_soil = await sisindia_task

    # Soil source priority: SISIndia (live) → offline soil_database.json
    if live_soil is not None:
        soil = live_soil
        soil_source = "SISIndia API (Live)"
        logger.info("Using live soil data from SISIndia for (%.4f, %.4f)", lat, lon)
    else:
        soil = _lookup_soil(lat, lon)
        soil_source = "Soil Database (Offline)"
        logger.info("SISIndia unavailable — using offline soil DB for (%.4f, %.4f)", lat, lon)

    region = _get_region_name(lat, lon)

    data_sources = []
    if weather.get("_live"):
        data_sources.append("Open-Meteo (Live)")
    else:
        data_sources.append("Open-Meteo (Cached Fallback)")

    if "ISRO" in land_class:
        data_sources.append("ISRO Bhuvan LULC")
    else:
        data_sources.append("Land Use (Default)")

    if satellite.get("_live"):
        data_sources.append("Agromonitoring (Live)")
    else:
        data_sources.append("Agromonitoring (Fallback)")

    data_sources.append(soil_source)

    # Remove internal flags before returning
    weather.pop("_live", None)
    satellite.pop("_live", None)
    soil.pop("_source", None)

    return {
        "weather": weather,
        "soil": soil,
        "land_classification": land_class,
        "satellite": satellite,
        "region": region,
        "data_sources": data_sources,
    }


# =====================================================================
#  SOURCE 1: OPEN-METEO (Free, No Key, Global)
# =====================================================================


async def _fetch_weather(lat: float, lon: float) -> dict[str, Any]:
    """
    Fetch current weather + soil moisture from Open-Meteo.

    Endpoint:
      https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}
        &current=temperature_2m,relative_humidity_2m,rain,soil_moisture_0_to_1cm

    Fallback: Returns plausible Indian summer defaults if API is unreachable.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,rain,soil_moisture_0_to_1cm"
    )

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        return {
            "temp": current.get("temperature_2m", 30.0),
            "humidity": current.get("relative_humidity_2m", 55),
            "rain": current.get("rain", 0.0),
            "moisture": current.get("soil_moisture_0_to_1cm", 0.30),
            "_live": True,
        }

    except (httpx.HTTPError, httpx.TimeoutException, KeyError, Exception) as exc:
        logger.warning("Open-Meteo API failed (%s) — using fallback", exc)
        return {
            "temp": 32.5,
            "humidity": 60,
            "rain": 0.0,
            "moisture": 0.30,
            "_live": False,
        }


# =====================================================================
#  SOURCE 2: AGROMONITORING (Satellite NDVI + Imagery)
# =====================================================================


async def _fetch_agro_satellite(lat: float, lon: float) -> dict[str, Any]:
    """
    Fetch NDVI and satellite data from Agromonitoring API.

    Uses the polygon-free stats endpoint for quick NDVI retrieval.
    Falls back to estimated NDVI based on weather + soil data.
    """
    # Use the satellite imagery search endpoint
    url = "http://api.agromonitoring.com/agro/1.0/ndvi/history"

    # Create a small bounding polygon around the point (~1km radius)
    import time

    end_ts = int(time.time())
    start_ts = end_ts - (7 * 86400)  # Last 7 days

    try:
        # First, try to create a temporary polygon for the point
        poly_url = "http://api.agromonitoring.com/agro/1.0/polygons"
        polygon_body = {
            "name": f"orbital-{lat:.4f}-{lon:.4f}",
            "geo_json": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [lon - 0.01, lat - 0.01],
                            [lon + 0.01, lat - 0.01],
                            [lon + 0.01, lat + 0.01],
                            [lon - 0.01, lat + 0.01],
                            [lon - 0.01, lat - 0.01],
                        ]
                    ],
                },
            },
        }

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            # Try to get existing polygons or create one
            resp = await client.get(poly_url, params={"appid": AGRO_SATELLITE_KEY})
            polygons = resp.json() if resp.status_code == 200 else []

            poly_id = None
            if isinstance(polygons, list) and len(polygons) > 0:
                # Use first polygon for NDVI lookup
                poly_id = polygons[0].get("id")

            if not poly_id:
                # Create a polygon
                resp = await client.post(
                    poly_url, json=polygon_body, params={"appid": AGRO_SATELLITE_KEY}
                )
                if resp.status_code in (200, 201):
                    poly_id = resp.json().get("id")

            if poly_id:
                # Fetch satellite imagery stats
                sat_resp = await client.get(
                    f"http://api.agromonitoring.com/agro/1.0/ndvi/history",
                    params={
                        "polyid": poly_id,
                        "start": start_ts,
                        "end": end_ts,
                        "appid": AGRO_SATELLITE_KEY,
                    },
                )
                if sat_resp.status_code == 200:
                    ndvi_data = sat_resp.json()
                    if isinstance(ndvi_data, list) and len(ndvi_data) > 0:
                        latest = ndvi_data[-1]
                        data_obj = latest.get("data", {})
                        return {
                            "ndvi": round(data_obj.get("mean", 0.45), 3),
                            "ndvi_min": round(data_obj.get("min", 0.1), 3),
                            "ndvi_max": round(data_obj.get("max", 0.8), 3),
                            "source": "Agromonitoring Satellite",
                            "_live": True,
                        }

        logger.warning("Agromonitoring: No NDVI data available — using estimate")
        return _estimate_ndvi(lat, lon)

    except (httpx.HTTPError, httpx.TimeoutException, Exception) as exc:
        logger.warning("Agromonitoring API failed (%s) — using estimate", exc)
        return _estimate_ndvi(lat, lon)


def _estimate_ndvi(lat: float, lon: float) -> dict[str, Any]:
    """Estimate NDVI based on season and region (fallback)."""
    import datetime

    month = datetime.datetime.now().month
    # Rough Indian seasonal NDVI estimates
    if month in (7, 8, 9, 10):  # Kharif (monsoon)
        ndvi = 0.55
    elif month in (11, 12, 1, 2):  # Rabi (winter)
        ndvi = 0.48
    else:  # Summer / lean
        ndvi = 0.32
    return {
        "ndvi": ndvi,
        "ndvi_min": ndvi - 0.15,
        "ndvi_max": ndvi + 0.2,
        "source": "Estimated (Seasonal)",
        "_live": False,
    }


# =====================================================================
#  SOURCE 3: ISRO BHUVAN LULC API
# =====================================================================


async def _check_bhuvan_land_use(lat: float, lon: float) -> str:
    """
    Query ISRO Bhuvan LULC API to validate that the location is agricultural land.

    Bhuvan response codes:
      '2' → Agriculture / Cropland
      '1' → Built-up
      '3' → Forest
      '4' → Water bodies
      Other → Mixed / Unknown

    IMPORTANT: Bhuvan can be very slow or completely down during hackathons.
    The entire call is wrapped in try/except with a 5-second timeout.
    If it fails → return "Default Agriculture" so the demo keeps running.
    """
    bhuvan_url = "https://bhuvan-app1.nrsc.gov.in/api/lulc/curljson.php"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                bhuvan_url,
                params={"lat": lat, "lon": lon},
            )
            resp.raise_for_status()
            data = resp.json()

        code = str(data.get("Code", ""))
        lulc_map = {
            "2": "Verified Farmland (ISRO Bhuvan)",
            "1": "Built-up Area (ISRO Bhuvan)",
            "3": "Forest Land (ISRO Bhuvan)",
            "4": "Water Body (ISRO Bhuvan)",
            "5": "Wasteland (ISRO Bhuvan)",
        }

        classification = lulc_map.get(code, f"Mixed Land — Code {code} (ISRO Bhuvan)")
        logger.info("Bhuvan LULC for (%.4f, %.4f): %s", lat, lon, classification)
        return classification

    except (httpx.HTTPError, httpx.TimeoutException, Exception) as exc:
        logger.warning("Bhuvan API failed (%s) — defaulting to Agriculture", exc)
        return "Default Agriculture (Bhuvan Offline)"


# =====================================================================
#  SOURCE 4: OFFLINE SOIL DATABASE
# =====================================================================


def _lookup_soil(lat: float, lon: float) -> dict[str, Any]:
    """
    Match lat/lon to the closest region in our soil database.
    Uses bounding-box matching first, then falls back to nearest-distance.
    """
    regions = _SOIL_DB.get("regions", [])
    default = _SOIL_DB.get("default", {})

    # 1. Try bounding-box match
    for region in regions:
        lat_range = region.get("lat_range", [0, 0])
        lon_range = region.get("lon_range", [0, 0])
        if lat_range[0] <= lat <= lat_range[1] and lon_range[0] <= lon <= lon_range[1]:
            return _format_soil(region)

    # 2. Find nearest region by center-point distance
    best, best_dist = None, float("inf")
    for region in regions:
        lat_range = region.get("lat_range", [0, 0])
        lon_range = region.get("lon_range", [0, 0])
        center_lat = (lat_range[0] + lat_range[1]) / 2
        center_lon = (lon_range[0] + lon_range[1]) / 2
        dist = _haversine(lat, lon, center_lat, center_lon)
        if dist < best_dist:
            best_dist = dist
            best = region

    # Use nearest if within 150 km, otherwise default
    if best and best_dist < 150:
        result = _format_soil(best)
        result["note"] = f"Nearest match: {best.get('city')} ({best_dist:.0f} km away)"
        return result

    return _format_soil(default)


def _format_soil(region: dict[str, Any]) -> dict[str, Any]:
    """Extract the soil fields we care about from a region record."""
    return {
        "type": region.get("soil_type", "Unknown"),
        "ph": region.get("soil_ph", 7.0),
        "texture": region.get("soil_texture", "Loam"),
        "organic_carbon_pct": region.get("organic_carbon_pct", 0.45),
        "nitrogen_kg_ha": region.get("nitrogen_kg_ha", 200),
        "phosphorus_kg_ha": region.get("phosphorus_kg_ha", 15),
        "potassium_kg_ha": region.get("potassium_kg_ha", 220),
        "recommended_crops": region.get("recommended_crops", []),
        "description": region.get("description", ""),
    }


# =====================================================================
#  HELPERS
# =====================================================================


def _get_region_name(lat: float, lon: float) -> str:
    """Map coordinates to a human-readable region name.

    Strategy:
      1. Check the soil DB for an exact bounding-box match.
      2. Try reverse geocoding via Nominatim (free, no key required).
      3. Fall back to nearest soil DB entry within 150 km.
      4. Return a generic coordinate-based label.
    """
    # 1. Soil DB exact match
    for region in _SOIL_DB.get("regions", []):
        lat_range = region.get("lat_range", [0, 0])
        lon_range = region.get("lon_range", [0, 0])
        if lat_range[0] <= lat <= lat_range[1] and lon_range[0] <= lon <= lon_range[1]:
            return f"{region['city']}, {region['state']}"

    # 2. Reverse geocode via Nominatim (OpenStreetMap — free, no API key)
    try:
        import httpx as _httpx
        url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lon}&format=json&zoom=10&accept-language=en"
        )
        resp = _httpx.get(url, timeout=4.0, headers={"User-Agent": "OrbitalNexus/1.0"})
        if resp.status_code == 200:
            addr = resp.json().get("address", {})
            city = (
                addr.get("city")
                or addr.get("town")
                or addr.get("village")
                or addr.get("county")
                or addr.get("state_district")
            )
            state = addr.get("state", "")
            country = addr.get("country", "")
            if city and state:
                return f"{city}, {state}"
            if city and country:
                return f"{city}, {country}"
            if state:
                return state
    except Exception as exc:
        logger.debug("Reverse geocoding failed (%s) — trying soil DB nearest", exc)

    # 3. Nearest soil DB match
    best, best_dist = None, float("inf")
    for region in _SOIL_DB.get("regions", []):
        lat_range = region.get("lat_range", [0, 0])
        lon_range = region.get("lon_range", [0, 0])
        center_lat = (lat_range[0] + lat_range[1]) / 2
        center_lon = (lon_range[0] + lon_range[1]) / 2
        dist = _haversine(lat, lon, center_lat, center_lon)
        if dist < best_dist:
            best_dist = dist
            best = region

    if best and best_dist < 150:
        return f"Near {best['city']}, {best['state']}"

    # 4. Generic label
    return f"Region ({lat:.2f}°N, {lon:.2f}°E)"


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in km between two lat/lon points."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))
