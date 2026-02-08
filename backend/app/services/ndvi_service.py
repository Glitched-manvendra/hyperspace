"""
NDVI Service — AgroMonitoring 2-Step Satellite NDVI Retrieval

Fetches per-polygon NDVI statistics from the AgroMonitoring API using:
  Step 1: /image/search → list of available satellite images (Sentinel-2 / Landsat-8)
  Step 2: GET the stats.ndvi URL from the most recent image → {min, max, mean, median}

Includes:
  - 10-minute in-memory cache keyed by (poly_id, day)
  - Robust error handling (timeouts, 400/401, no-data)
  - Mean clamped to [-1.0, 1.0] for safety
"""

import os
import time
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("orbital.ndvi")

# ── Config ──────────────────────────────────────────────────────────
AGRO_APPID = os.getenv("AGRO_SATELLITE_KEY", "")
_AGRO_BASE = "http://api.agromonitoring.com/agro/1.0"
_TIMEOUT = httpx.Timeout(connect=4.0, read=4.0, write=4.0, pool=4.0)
_SEARCH_WINDOW_SECONDS = 2_592_000  # 30 days

# ── Cache (poly_id, day_str) → (timestamp, result_dict) ────────────
_ndvi_cache: dict[tuple[str, str], tuple[float, dict[str, Any]]] = {}
_CACHE_TTL = 600  # 10 minutes


# =====================================================================
#  PUBLIC API
# =====================================================================


async def fetch_ndvi_stats(poly_id: str) -> dict[str, Any]:
    """
    Fetch the latest NDVI statistics for a polygon.

    Returns:
        {
            "mean_ndvi": 0.452,
            "min_ndvi": 0.12,
            "max_ndvi": 0.81,
            "median_ndvi": 0.47,
            "acquisition_date": "2026-02-01T10:23:00+00:00",
            "satellite_type": "Sentinel-2",
            "poly_id": "...",
            "cached": False,
        }

    Raises:
        NDVIError with appropriate status_code and detail.
    """
    # Cache check
    day_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cache_key = (poly_id, day_key)

    if cache_key in _ndvi_cache:
        ts, cached_data = _ndvi_cache[cache_key]
        if time.time() - ts < _CACHE_TTL:
            logger.info("NDVI cache hit for poly_id=%s", poly_id)
            return {**cached_data, "cached": True}

    # Step 1: Search for satellite images
    images = await _search_images(poly_id)

    # Step 2: Pick most recent image and fetch NDVI stats
    image = _pick_latest_image(images)
    ndvi_data = await _fetch_ndvi_from_image(image)

    # Build result
    acq_ts = image.get("dt", 0)
    acq_date = datetime.fromtimestamp(acq_ts, tz=timezone.utc).isoformat()
    sat_type = image.get("type", "unknown")
    # Map AgroMonitoring type codes to readable names
    sat_name = _SATELLITE_NAMES.get(sat_type, sat_type)

    mean_val = ndvi_data.get("mean")
    if mean_val is None:
        raise NDVIError(502, "NDVI stats response missing 'mean' value")

    mean_clamped = max(-1.0, min(1.0, float(mean_val)))

    result = {
        "mean_ndvi": round(mean_clamped, 4),
        "min_ndvi": round(float(ndvi_data.get("min", 0)), 4),
        "max_ndvi": round(float(ndvi_data.get("max", 0)), 4),
        "median_ndvi": round(float(ndvi_data.get("median", 0)), 4),
        "acquisition_date": acq_date,
        "satellite_type": sat_name,
        "poly_id": poly_id,
        "cached": False,
    }

    # Cache it
    _ndvi_cache[cache_key] = (time.time(), result)
    logger.info(
        "NDVI fetched for poly_id=%s: mean=%.4f, sat=%s, date=%s",
        poly_id, mean_clamped, sat_name, acq_date,
    )
    return result


# =====================================================================
#  STEP 1: Image Search
# =====================================================================


async def _search_images(poly_id: str) -> list[dict[str, Any]]:
    """
    Search AgroMonitoring for satellite images covering the polygon.

    GET /image/search?polyid={poly_id}&start={start}&end={end}&appid={appid}
    """
    end_ts = int(time.time())
    start_ts = end_ts - _SEARCH_WINDOW_SECONDS

    url = f"{_AGRO_BASE}/image/search"
    params = {
        "polyid": poly_id,
        "start": start_ts,
        "end": end_ts,
        "appid": AGRO_APPID,
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
    except httpx.TimeoutException:
        raise NDVIError(502, "AgroMonitoring image search timed out")
    except httpx.ConnectError:
        raise NDVIError(502, "Cannot connect to AgroMonitoring API")

    if resp.status_code == 401:
        raise NDVIError(401, "Invalid AgroMonitoring appid")
    if resp.status_code == 400:
        detail = _extract_error(resp)
        raise NDVIError(400, f"Bad request (check poly_id or polygon limits): {detail}")
    if resp.status_code != 200:
        raise NDVIError(502, f"AgroMonitoring returned HTTP {resp.status_code}")

    data = resp.json()
    if not isinstance(data, list) or len(data) == 0:
        raise NDVIError(404, f"No satellite images found for poly_id={poly_id} in the last 30 days")

    logger.info("Image search: %d images found for poly_id=%s", len(data), poly_id)
    return data


# =====================================================================
#  STEP 2: Fetch NDVI Stats from Image
# =====================================================================


async def _fetch_ndvi_from_image(image: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the NDVI stats URL from an image object and fetch the data.

    The image object contains:
        { "stats": { "ndvi": "https://...json" }, ... }
    """
    stats = image.get("stats")
    if not stats or not isinstance(stats, dict):
        raise NDVIError(502, "Image object missing 'stats' block")

    ndvi_url = stats.get("ndvi")
    if not ndvi_url:
        raise NDVIError(502, "Image stats missing NDVI URL")

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(ndvi_url)
    except httpx.TimeoutException:
        raise NDVIError(502, "NDVI stats fetch timed out")
    except httpx.ConnectError:
        raise NDVIError(502, "Cannot connect to AgroMonitoring stats endpoint")

    if resp.status_code != 200:
        raise NDVIError(502, f"NDVI stats endpoint returned HTTP {resp.status_code}")

    data = resp.json()
    if not isinstance(data, dict):
        raise NDVIError(502, "NDVI stats response is not a JSON object")

    logger.info("NDVI stats fetched: mean=%s, median=%s", data.get("mean"), data.get("median"))
    return data


# =====================================================================
#  HELPERS
# =====================================================================

# AgroMonitoring satellite type codes → human names
_SATELLITE_NAMES: dict[str, str] = {
    "Sentinel-2": "Sentinel-2",
    "Landsat 8": "Landsat-8",
    "l8": "Landsat-8",
    "s2": "Sentinel-2",
}


def _pick_latest_image(images: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the image with the highest acquisition timestamp (dt)."""
    return max(images, key=lambda img: img.get("dt", 0))


def _extract_error(resp: httpx.Response) -> str:
    """Try to extract error detail from an AgroMonitoring error response."""
    try:
        body = resp.json()
        if isinstance(body, dict):
            return body.get("message", body.get("error", resp.text[:200]))
    except Exception:
        pass
    return resp.text[:200]


class NDVIError(Exception):
    """Raised when NDVI fetch fails with a specific HTTP status code."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
