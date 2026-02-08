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
import time as _time
from pathlib import Path
from typing import Any

import httpx

from app.services.sisindia_soil import fetch_sisindia_soil

logger = logging.getLogger("orbital.fusion")

# ── API Keys ────────────────────────────────────────────────────────
AGRO_GEOCODING_KEY = os.getenv("AGRO_GEOCODING_KEY")
AGRO_SATELLITE_KEY = os.getenv("AGRO_SATELLITE_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # weatherapi.com free tier

logger = logging.getLogger("orbital.fusion")

# ── Weather cache (avoid hitting Open-Meteo rate limits) ────────────
# Key: rounded (lat, lon) → Value: (timestamp, weather_dict)
_weather_cache: dict[tuple[float, float], tuple[float, dict[str, Any]]] = {}
_WEATHER_CACHE_TTL = 600  # 10 minutes — weather doesn't change that fast

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
    Gathers weather, soil, land classification, satellite NDVI, and market brain for a coordinate pair.

    Returns:
        {
            "weather": { "temp": 28.5, "humidity": 60, "rain": 0, "moisture": 0.32 },
            "soil": { "type": "Loamy", "ph": 7.2, ... },
            "land_classification": "Verified Agriculture (ISRO Bhuvan)",
            "satellite": { "ndvi": 0.62, "source": "Agromonitoring" },
            "market_brain": { "top_commodities": [...], "source": "Gemini AI", ... },
            "region": "Greater Noida, Uttar Pradesh",
            "data_sources": ["Open-Meteo", "ISRO Bhuvan LULC", "Agromonitoring", "Soil Database", "Market Brain"]
        }
    """
    import asyncio
    from app.services.market_brain import get_market_brain

    weather_task = asyncio.create_task(_fetch_weather(lat, lon))
    bhuvan_task = asyncio.create_task(_check_bhuvan_land_use(lat, lon))
    agro_task = asyncio.create_task(_fetch_agro_satellite(lat, lon))
    sisindia_task = asyncio.create_task(fetch_sisindia_soil(lat, lon))

    weather = await weather_task
    land_class = await bhuvan_task
    satellite = await agro_task
    live_soil = await sisindia_task
    
    # Get region name early for market brain
    region = _get_region_name(lat, lon)
    
    # Fetch market brain data (with Gemini analysis)
    market_brain = await get_market_brain(lat, lon, region)

    # Soil source priority: SISIndia (live) → offline soil_database.json
    if live_soil is not None:
        soil = live_soil
        soil_source = "SISIndia API (Live)"
        logger.info("Using live soil data from SISIndia for (%.4f, %.4f)", lat, lon)
    else:
        soil = _lookup_soil(lat, lon)
        soil_source = "Soil Database (Offline)"
        logger.info("SISIndia unavailable — using offline soil DB for (%.4f, %.4f)", lat, lon)

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
        sat_source = satellite.get("source", "Satellite")
        data_sources.append(sat_source)
    else:
        data_sources.append("NDVI (Estimate)")

    data_sources.append(soil_source)
    
    # Add market brain to data sources
    if market_brain:
        data_sources.append(f"Market Brain ({market_brain.get('source', 'Analysis')})")

    # Remove internal flags before returning
    weather.pop("_live", None)
    satellite.pop("_live", None)
    soil.pop("_source", None)

    return {
        "weather": weather,
        "soil": soil,
        "land_classification": land_class,
        "satellite": satellite,
        "market_brain": market_brain,
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

    Uses an in-memory cache (10 min TTL) to avoid hitting the daily rate limit.
    Fallback: Returns location-aware estimates if API is unreachable.
    """
    # Round to 2 decimals for cache key (~1 km precision)
    cache_key = (round(lat, 2), round(lon, 2))

    # Check cache first
    if cache_key in _weather_cache:
        cached_ts, cached_data = _weather_cache[cache_key]
        if _time.time() - cached_ts < _WEATHER_CACHE_TTL:
            logger.info("Weather cache hit for (%.2f, %.2f)", lat, lon)
            return {**cached_data}  # return a copy

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

        # Open-Meteo returns {"error": true} when rate-limited
        if data.get("error"):
            raise ValueError(data.get("reason", "Open-Meteo error response"))

        current = data.get("current", {})
        result = {
            "temp": current.get("temperature_2m", 30.0),
            "humidity": current.get("relative_humidity_2m", 55),
            "rain": current.get("rain", 0.0),
            "moisture": current.get("soil_moisture_0_to_1cm", 0.30),
            "_live": True,
        }

        # Store in cache
        _weather_cache[cache_key] = (_time.time(), {**result})
        return result

    except (httpx.HTTPError, httpx.TimeoutException, KeyError, ValueError, Exception) as exc:
        logger.warning("Open-Meteo API failed (%s) — trying WeatherAPI fallback", exc)

    # ── Fallback: WeatherAPI.com (free tier, 1M calls/month) ──
    if WEATHER_API_KEY:
        try:
            result = await _fetch_weatherapi(lat, lon)
            _weather_cache[cache_key] = (_time.time(), {**result})
            return result
        except Exception as exc2:
            logger.warning("WeatherAPI also failed (%s) — using estimates", exc2)

    return _estimate_weather(lat, lon)


async def _fetch_weatherapi(lat: float, lon: float) -> dict[str, Any]:
    """
    Fetch current weather from WeatherAPI.com (free tier fallback).

    Endpoint: https://api.weatherapi.com/v1/current.json?key=KEY&q=lat,lon
    """
    url = (
        f"https://api.weatherapi.com/v1/current.json"
        f"?key={WEATHER_API_KEY}&q={lat},{lon}"
    )
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current", {})
    # WeatherAPI provides precip_mm (last hour), humidity, temp_c
    # It does NOT provide soil moisture — estimate from humidity + rain
    humidity = current.get("humidity", 55)
    precip = current.get("precip_mm", 0.0)
    moisture = round(0.15 + (humidity / 100) * 0.25 + precip * 0.02, 2)
    moisture = min(0.60, max(0.05, moisture))

    result = {
        "temp": current.get("temp_c", 30.0),
        "humidity": humidity,
        "rain": precip,
        "moisture": moisture,
        "_live": True,
    }
    logger.info("WeatherAPI.com success for (%.4f, %.4f): %.1f°C", lat, lon, result["temp"])
    return result


def _estimate_weather(lat: float, lon: float) -> dict[str, Any]:
    """
    Estimate weather based on latitude, longitude, and month.

    Uses simple climate heuristics so that different locations
    get meaningfully different fallback values instead of identical ones.
    """
    import datetime

    month = datetime.datetime.now().month
    abs_lat = abs(lat)

    # ── Temperature estimate ──
    # Base: equator ~30°C, drops ~0.6°C per degree of latitude
    base_temp = 30.0 - (abs_lat - 10) * 0.55

    # Seasonal adjustment (Northern Hemisphere focus for India)
    if lat > 0:  # Northern hemisphere
        if month in (12, 1, 2):       # Winter
            base_temp -= 8.0
        elif month in (3, 4, 5):      # Summer / pre-monsoon
            base_temp += 4.0
        elif month in (6, 7, 8, 9):   # Monsoon
            base_temp += 1.0
        else:                          # Post-monsoon
            base_temp -= 2.0

    # Altitude proxy: higher lat in India = more hilly (rough)
    if abs_lat > 30:
        base_temp -= 3.0

    # Coastal moderation: lon near coasts (< 74 or > 85 in India)
    if 72 < lon < 74 or 85 < lon < 90:
        base_temp = base_temp * 0.95 + 1.0  # moderate towards ~26°C

    # Add small deterministic variation from lon so nearby cities differ
    micro_variation = math.sin(lat * 3.7 + lon * 2.3) * 1.5
    temp = round(base_temp + micro_variation, 1)
    temp = max(5.0, min(48.0, temp))  # clamp

    # ── Humidity estimate ──
    # Coastal → higher, inland → lower; monsoon months → higher
    base_humidity = 50.0
    if month in (6, 7, 8, 9):
        base_humidity += 20.0
    elif month in (12, 1, 2):
        base_humidity -= 10.0

    # Coastal bump
    if lon < 74 or lon > 86:
        base_humidity += 12.0

    humidity_variation = math.cos(lat * 2.1 + lon * 1.8) * 5.0
    humidity = round(base_humidity + humidity_variation, 1)
    humidity = max(15.0, min(95.0, humidity))

    # ── Rainfall estimate ──
    rain = 0.0
    if month in (6, 7, 8, 9):
        rain = round(2.0 + abs(math.sin(lon * 0.5)) * 6.0, 1)

    # ── Soil moisture ──
    moisture = round(0.20 + (humidity - 40) * 0.003 + rain * 0.01, 2)
    moisture = max(0.05, min(0.60, moisture))

    return {
        "temp": temp,
        "humidity": humidity,
        "rain": rain,
        "moisture": moisture,
        "_live": False,
    }


# =====================================================================
#  SOURCE 2: SATELLITE NDVI (MODIS → AgroMonitoring → Estimate)
# =====================================================================

# ── NDVI Cache (avoid hammering APIs) ───────────────────────────────
# Key: rounded (lat, lon) → Value: (timestamp, result_dict)
_ndvi_cache: dict[tuple[float, float], tuple[float, dict[str, Any]]] = {}
_NDVI_CACHE_TTL = 600  # 10 minutes


async def _fetch_agro_satellite(lat: float, lon: float) -> dict[str, Any]:
    """
    Fetch NDVI for a coordinate pair.

    3-tier resolution:
      1. Cache (10 min TTL)
      2. NASA MODIS ORNL DAAC — free, no key, real satellite data
      3. AgroMonitoring polygon API — if key is valid
      4. Location-aware estimate (last resort)
    """
    # ── Cache check ─────────────────────────────────────────────────
    cache_key = (round(lat, 2), round(lon, 2))
    if cache_key in _ndvi_cache:
        ts, cached = _ndvi_cache[cache_key]
        if _time.time() - ts < _NDVI_CACHE_TTL:
            logger.info("NDVI cache hit for (%.2f, %.2f)", lat, lon)
            return cached

    # ── Tier 1: NASA MODIS ORNL DAAC (free, no API key) ─────────────
    modis_result = await _fetch_modis_ndvi(lat, lon)
    if modis_result is not None:
        _ndvi_cache[cache_key] = (_time.time(), modis_result)
        return modis_result

    # ── Tier 2: AgroMonitoring (if API key present & valid) ─────────
    if AGRO_SATELLITE_KEY:
        agro_result = await _fetch_agromonitoring_ndvi(lat, lon)
        if agro_result is not None:
            _ndvi_cache[cache_key] = (_time.time(), agro_result)
            return agro_result

    # ── Tier 3: Location-aware estimate ─────────────────────────────
    est = _estimate_ndvi(lat, lon)
    _ndvi_cache[cache_key] = (_time.time(), est)
    return est


async def _fetch_modis_ndvi(lat: float, lon: float) -> dict[str, Any] | None:
    """
    Fetch latest NDVI from NASA MODIS ORNL DAAC (MOD13Q1 product).

    Free, no API key. Returns 250m resolution NDVI from MODIS Terra.
    The API returns scaled integers: NDVI = value / 10000.
    Valid range: -2000 to 10000 (i.e. -0.2 to 1.0).
    """
    import datetime

    # Search last 60 days for the most recent 16-day composite
    today = datetime.datetime.now(datetime.timezone.utc)
    start_date = today - datetime.timedelta(days=60)
    start_str = start_date.strftime("A%Y%j")  # e.g. "A2026001"
    end_str = today.strftime("A%Y%j")

    url = "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset"
    params = {
        "latitude": lat,
        "longitude": lon,
        "startDate": start_str,
        "endDate": end_str,
        "kmAboveBelow": 0,
        "kmLeftRight": 0,
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
            resp = await client.get(url, params=params, headers={"Accept": "application/json"})
        if resp.status_code != 200:
            logger.warning("MODIS API returned HTTP %d", resp.status_code)
            return None

        data = resp.json()
        subsets = data.get("subset", [])

        # Find the most recent NDVI band entry
        ndvi_entries = [
            s for s in subsets
            if s.get("band") == "250m_16_days_NDVI"
        ]
        if not ndvi_entries:
            logger.warning("MODIS response has no NDVI band data")
            return None

        # Pick the most recent entry (last in list)
        latest = ndvi_entries[-1]
        raw_values = latest.get("data", [])
        if not raw_values:
            return None

        # MODIS NDVI is scaled by 10000. Filter out fill values (> 10000 or < -2000)
        valid = [v for v in raw_values if -2000 <= v <= 10000]
        if not valid:
            logger.warning("MODIS NDVI: all values are fill/invalid")
            return None

        mean_scaled = sum(valid) / len(valid)
        ndvi = round(mean_scaled / 10000.0, 4)
        # Clamp to valid range
        ndvi = max(-0.2, min(1.0, ndvi))

        calendar_date = latest.get("calendar_date", "unknown")
        logger.info(
            "MODIS NDVI for (%.2f, %.2f): %.4f [date=%s, tile=%s]",
            lat, lon, ndvi, calendar_date, latest.get("tile", "?"),
        )

        return {
            "ndvi": round(ndvi, 3),
            "ndvi_min": round(ndvi - 0.08, 3),
            "ndvi_max": round(ndvi + 0.1, 3),
            "source": "NASA MODIS (Live)",
            "date": calendar_date,
            "_live": True,
        }

    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        logger.warning("MODIS API timeout/connection error: %s", exc)
        return None
    except Exception as exc:
        logger.warning("MODIS API error: %s", exc)
        return None


async def _fetch_agromonitoring_ndvi(lat: float, lon: float) -> dict[str, Any] | None:
    """
    Fetch NDVI from AgroMonitoring polygon API (requires valid appid).
    Returns None on any failure so caller can fall through to next tier.
    """
    import time

    end_ts = int(time.time())
    start_ts = end_ts - (7 * 86400)  # Last 7 days

    try:
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
            resp = await client.get(poly_url, params={"appid": AGRO_SATELLITE_KEY})
            if resp.status_code == 401:
                logger.warning("AgroMonitoring API key invalid (401)")
                return None
            polygons = resp.json() if resp.status_code == 200 else []

            poly_id = None
            if isinstance(polygons, list) and len(polygons) > 0:
                # Find polygon closest to our coordinates
                poly_id = polygons[0].get("id")

            if not poly_id:
                resp = await client.post(
                    poly_url, json=polygon_body, params={"appid": AGRO_SATELLITE_KEY}
                )
                if resp.status_code in (200, 201):
                    poly_id = resp.json().get("id")

            if poly_id:
                sat_resp = await client.get(
                    "http://api.agromonitoring.com/agro/1.0/ndvi/history",
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

        return None

    except (httpx.HTTPError, httpx.TimeoutException, Exception) as exc:
        logger.warning("AgroMonitoring API failed (%s)", exc)
        return None


def _estimate_ndvi(lat: float, lon: float) -> dict[str, Any]:
    """
    Estimate NDVI based on season, latitude, longitude, and regional characteristics.
    Produces meaningfully different values for different locations.
    """
    import datetime

    month = datetime.datetime.now().month

    # Base seasonal NDVI for Indian agriculture
    if month in (7, 8, 9, 10):    # Kharif (monsoon) — peak greenness
        base = 0.58
    elif month in (11, 12, 1, 2): # Rabi (winter) — moderate
        base = 0.42
    else:                          # Summer / lean — low
        base = 0.28

    # Regional adjustments based on agriculture/climate zones
    # Indo-Gangetic Plain (high irrigation, high NDVI)
    if 24 <= lat <= 31 and 75 <= lon <= 88:
        base += 0.12
    # Punjab/Haryana (heavily irrigated wheat belt)
    elif 29 <= lat <= 33 and 74 <= lon <= 78:
        base += 0.15
    # Western Rajasthan (arid/desert — low NDVI)
    elif 24 <= lat <= 30 and 68 <= lon <= 74:
        base -= 0.18
    # Coastal Maharashtra/Konkan (moderate)
    elif 15 <= lat <= 20 and 72 <= lon <= 74:
        base += 0.05
    # Deccan Plateau (moderate-dry)
    elif 15 <= lat <= 22 and 74 <= lon <= 80:
        base -= 0.04
    # Kerala/Coastal Karnataka (tropical, high NDVI)
    elif 8 <= lat <= 14 and 74 <= lon <= 78:
        base += 0.16
    # Tamil Nadu coast (moderate)
    elif 8 <= lat <= 14 and 78 <= lon <= 81:
        base += 0.06
    # Northeast India (high rainfall, dense vegetation)
    elif 22 <= lat <= 28 and 88 <= lon <= 97:
        base += 0.18
    # Central India / Madhya Pradesh
    elif 22 <= lat <= 26 and 76 <= lon <= 82:
        base += 0.04

    # Fine-grained variation using coordinates (prevents two nearby cities from being identical)
    micro = math.sin(lat * 5.3 + lon * 3.7) * 0.04
    base += micro

    # Clamp to valid range
    ndvi = max(0.05, min(0.85, round(base, 3)))

    return {
        "ndvi": ndvi,
        "ndvi_min": round(max(0.0, ndvi - 0.12), 3),
        "ndvi_max": round(min(1.0, ndvi + 0.15), 3),
        "source": "Estimated (Regional + Seasonal)",
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
