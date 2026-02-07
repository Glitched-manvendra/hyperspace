"""
SISIndia Soil Service — Live Soil Data from ISRIC REST API

Fetches real soil nutrient and chemical properties for any lat/lon in India
using the SISIndia REST API (https://rest-sisindia.isric.org/sisindia/v1.0/docs).

Supported properties from the API:
  pH, OC (Organic Carbon), N (Nitrogen), P (Phosphorus), K (Potassium),
  S (Sulphur), Fe (Iron), Zn (Zinc), Cu (Copper), B (Boron),
  Mn (Manganese), EC (Electrical Conductivity)

Strategy:
  1. Try /properties/query/district  (district-level zonal average)
  2. Fallback to /properties/query/gridded  (single pixel)
  3. If both fail → return None so caller uses offline soil_database.json

Includes an in-memory LRU cache keyed on rounded lat/lon to avoid
redundant API calls for nearby points within the same district.
"""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("orbital.sisindia")

# ── Configuration ───────────────────────────────────────────────────
SISINDIA_BASE_URL = "https://rest-sisindia.isric.org/sisindia/v1.0"
SISINDIA_API_KEY = os.getenv("SISINDIA_API_KEY", "")  # optional — API is currently open

# Soil properties we care about
_PROPERTIES = ["pH", "OC", "N", "P", "K", "S", "Fe", "Zn", "Cu", "B", "Mn", "EC"]

# Aggressive timeout — demo cannot stall
_TIMEOUT = httpx.Timeout(connect=4.0, read=8.0, write=3.0, pool=3.0)

# Lat/Lon bounds for India (from the API spec)
_LAT_MIN, _LAT_MAX = 7.9655, 35.4940
_LON_MIN, _LON_MAX = 68.1766, 97.4026


# =====================================================================
#  PUBLIC API
# =====================================================================


async def fetch_sisindia_soil(lat: float, lon: float) -> dict[str, Any] | None:
    """
    Fetch live soil data from SISIndia API for a coordinate pair.

    Returns a dict matching the app's soil format:
        {
            "type": "Alluvial",            # inferred from properties
            "ph": 7.2,
            "texture": "Loam",            # inferred
            "organic_carbon_pct": 0.52,
            "nitrogen_kg_ha": 220,
            "phosphorus_kg_ha": 18,
            "potassium_kg_ha": 245,
            "recommended_crops": [...],    # derived from nutrients
            "description": "...",
            "_source": "SISIndia (Live)"
        }

    Returns None if the API is unreachable or has no data for this location.
    """
    # Bounds check
    if not (_LAT_MIN <= lat <= _LAT_MAX and _LON_MIN <= lon <= _LON_MAX):
        logger.debug("Coordinates (%.4f, %.4f) outside India — skipping SISIndia", lat, lon)
        return None

    # Check the cache first (rounded to ~1 km grid to share district results)
    cache_key = (round(lat, 2), round(lon, 2))
    cached = _get_cached(cache_key)
    if cached is not None:
        logger.info("SISIndia cache hit for (%.2f, %.2f)", lat, lon)
        return cached

    # Try district-level first, then gridded
    raw = await _query_district(lat, lon)
    if raw is None:
        raw = await _query_gridded(lat, lon)

    if raw is None:
        logger.warning("SISIndia: No data for (%.4f, %.4f)", lat, lon)
        return None

    # Convert raw API response → app's soil format
    result = _convert_to_soil_format(raw)
    _set_cached(cache_key, result)
    return result


# =====================================================================
#  API QUERY FUNCTIONS
# =====================================================================


async def _query_district(lat: float, lon: float) -> dict[str, float] | None:
    """Query /properties/query/district for zonal averages."""
    url = f"{SISINDIA_BASE_URL}/properties/query/district"
    params: dict[str, Any] = {
        "lat": lat,
        "lon": lon,
        "properties": _PROPERTIES,
    }
    if SISINDIA_API_KEY:
        params["api_key"] = SISINDIA_API_KEY

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 204:
                logger.info("SISIndia district: no data for (%.4f, %.4f)", lat, lon)
                return None
            resp.raise_for_status()
            return _extract_soil_properties(resp.json())
    except (httpx.HTTPError, httpx.TimeoutException, Exception) as exc:
        logger.warning("SISIndia district query failed: %s", exc)
        return None


async def _query_gridded(lat: float, lon: float) -> dict[str, float] | None:
    """Query /properties/query/gridded for single-pixel data."""
    url = f"{SISINDIA_BASE_URL}/properties/query/gridded"
    params: dict[str, Any] = {
        "lat": lat,
        "lon": lon,
        "properties": _PROPERTIES,
        "nearby": True,  # use nearby pixel if exact one has no data
    }
    if SISINDIA_API_KEY:
        params["api_key"] = SISINDIA_API_KEY

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 204:
                logger.info("SISIndia gridded: no data for (%.4f, %.4f)", lat, lon)
                return None
            resp.raise_for_status()
            return _extract_soil_properties(resp.json())
    except (httpx.HTTPError, httpx.TimeoutException, Exception) as exc:
        logger.warning("SISIndia gridded query failed: %s", exc)
        return None


# =====================================================================
#  RESPONSE PARSING
# =====================================================================


def _extract_soil_properties(geojson: dict[str, Any]) -> dict[str, float] | None:
    """
    Parse a GeoJSON response from SISIndia API.

    Expected shape:
    {
        "type": "FeatureCollection",
        "features": [{
            "properties": {
                "soil_properties": {
                    "pH": 7.2, "OC": 0.52, "N": 220,
                    "P": 18, "K": 245, ...
                }
            },
            "geometry": { "type": "Point", "coordinates": [lon, lat] }
        }]
    }
    """
    try:
        features = geojson.get("features", [])
        if not features:
            return None
        props = features[0].get("properties", {})
        soil_props = props.get("soil_properties", {})
        if not soil_props:
            return None
        # Validate we got at least pH or N
        if soil_props.get("pH") is None and soil_props.get("N") is None:
            return None
        return soil_props
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("SISIndia: Failed to parse response — %s", exc)
        return None


def _convert_to_soil_format(raw: dict[str, float]) -> dict[str, Any]:
    """
    Convert raw SISIndia soil properties to app's internal format.

    SISIndia returns nutrient values; we infer soil type and texture
    from pH + OC + other indicators.
    """
    ph = raw.get("pH", 7.0)
    oc = raw.get("OC", 0.45)
    n = raw.get("N", 200)
    p = raw.get("P", 15)
    k = raw.get("K", 220)
    ec = raw.get("EC", 0.0)
    fe = raw.get("Fe", 0.0)
    s = raw.get("S", 0.0)
    zn = raw.get("Zn", 0.0)

    # Infer soil type from chemical signature
    soil_type = _infer_soil_type(ph, oc, ec, fe)
    texture = _infer_texture(ph, oc, k)

    # Derive recommended crops from nutrients
    recommended = _recommend_crops_from_nutrients(n, p, k, ph, oc)

    # Build description
    description = (
        f"Live soil data from SISIndia (ISRIC). "
        f"pH {ph:.1f}, OC {oc:.2f}%, "
        f"NPK: {n:.0f}/{p:.0f}/{k:.0f} kg/ha. "
        f"Micronutrients — Fe: {fe:.1f}, Zn: {zn:.1f}, S: {s:.1f} ppm."
    )

    return {
        "type": soil_type,
        "ph": round(ph, 1),
        "texture": texture,
        "organic_carbon_pct": round(oc, 2),
        "nitrogen_kg_ha": round(n, 0),
        "phosphorus_kg_ha": round(p, 0),
        "potassium_kg_ha": round(k, 0),
        "ec": round(ec, 2),
        "iron_ppm": round(fe, 1),
        "zinc_ppm": round(zn, 1),
        "sulphur_ppm": round(s, 1),
        "recommended_crops": recommended,
        "description": description,
        "_source": "SISIndia (Live)",
    }


# =====================================================================
#  SOIL TYPE & TEXTURE INFERENCE
# =====================================================================


def _infer_soil_type(ph: float, oc: float, ec: float, fe: float) -> str:
    """Infer broad soil type from chemical properties."""
    if ph < 5.5:
        return "Acidic Laterite"
    if ph < 6.0 and fe > 10:
        return "Red Laterite"
    if ph < 6.5:
        return "Red Soil"
    if 6.5 <= ph <= 7.5 and oc > 0.5:
        return "Alluvial (Fertile)"
    if 6.5 <= ph <= 7.5:
        return "Alluvial"
    if ph > 7.5 and ec > 1.0:
        return "Saline-Alkaline"
    if ph > 7.5 and oc > 0.5:
        return "Black Cotton (Vertisol)"
    if ph > 8.0:
        return "Desert Sandy"
    return "Mixed Soil"


def _infer_texture(ph: float, oc: float, k: float) -> str:
    """Infer soil texture from available properties."""
    if oc > 0.7:
        return "Clay Loam (Organic-rich)"
    if oc > 0.5 and k > 250:
        return "Heavy Clay"
    if oc > 0.4:
        return "Loam"
    if k < 150:
        return "Sandy"
    if ph > 8.0:
        return "Coarse Sand"
    return "Sandy Loam"


# =====================================================================
#  CROP RECOMMENDATION FROM NUTRIENTS
# =====================================================================


def _recommend_crops_from_nutrients(
    n: float, p: float, k: float, ph: float, oc: float
) -> list[str]:
    """
    Derive crop recommendations directly from soil nutrient levels.

    Uses agronomic thresholds for Indian soils:
    - High N (>200): Rice, Sugarcane, Maize
    - High P (>15): Wheat, Potato, Mustard
    - High K (>200): Cotton, Banana, Coconut
    - Acidic (pH < 6.5): Tea, Coffee, Pineapple
    - Alkaline (pH > 7.5): Bajra, Jowar, Castor
    """
    crops: list[str] = []

    # Nitrogen-responsive crops
    if n > 200:
        crops.extend(["Rice", "Sugarcane"])
    elif n > 120:
        crops.extend(["Wheat", "Maize"])
    else:
        crops.append("Bajra")

    # Phosphorus-responsive crops
    if p > 20:
        crops.extend(["Potato", "Mustard"])
    elif p > 12:
        crops.append("Wheat")

    # Potassium-responsive crops
    if k > 250:
        crops.extend(["Cotton", "Banana"])
    elif k > 180:
        crops.append("Vegetables")

    # pH-based adjustments
    if ph < 5.5:
        crops.extend(["Tea", "Coffee"])
    elif ph < 6.5:
        crops.extend(["Ragi", "Groundnut"])
    elif ph > 8.0:
        crops.extend(["Bajra", "Guar"])
    elif ph > 7.5:
        crops.append("Gram")

    # Organic carbon bonus
    if oc > 0.6:
        crops.append("Vegetables")

    # Deduplicate while preserving order, cap at 6
    seen: set[str] = set()
    unique: list[str] = []
    for c in crops:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:6]


# =====================================================================
#  IN-MEMORY CACHE (LRU-style with TTL awareness)
# =====================================================================

# Simple dict cache — survives for the lifetime of the server process.
# Keyed on (rounded_lat, rounded_lon) so nearby points share a cache entry.
_cache: dict[tuple[float, float], dict[str, Any]] = {}
_MAX_CACHE_SIZE = 500


def _get_cached(key: tuple[float, float]) -> dict[str, Any] | None:
    """Retrieve a cached soil result, or None."""
    return _cache.get(key)


def _set_cached(key: tuple[float, float], value: dict[str, Any]) -> None:
    """Store a soil result in cache, evicting oldest if full."""
    if len(_cache) >= _MAX_CACHE_SIZE:
        # Evict first (oldest) entry
        oldest = next(iter(_cache))
        del _cache[oldest]
    _cache[key] = value


def clear_cache() -> None:
    """Clear the soil data cache (useful for testing)."""
    _cache.clear()
