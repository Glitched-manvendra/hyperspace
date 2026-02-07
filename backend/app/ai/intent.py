"""
Intent & Location Parser — Orbital Nexus AI Module

Parses natural language queries into structured intents and extracts
location references from the query text.
"""

import json
from pathlib import Path
from typing import Any


# ── Location database (loaded once) ─────────────────────────────────
_SOIL_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "data" / "soil_database.json"
)

try:
    with open(_SOIL_DB_PATH, "r", encoding="utf-8") as f:
        _SOIL_DB: dict[str, Any] = json.load(f)
except FileNotFoundError:
    _SOIL_DB = {"regions": []}


def parse_intent(query: str) -> str:
    """
    Parse user query into one of the supported intents.

    Supported intents:
    - crop_recommendation: User wants crop suggestions
    - weather_analysis: User asks about weather/climate
    - soil_check: User asks about soil conditions
    - flood_risk: User asks about flooding/risk
    - ndvi_analysis: User asks about vegetation health
    - price_analysis: User asks about prices/market
    - general: Catch-all for unrecognized queries

    Uses keyword matching with priority weighting.
    """
    query_lower = query.lower()

    intent_keywords = {
        "crop_recommendation": [
            "crop",
            "grow",
            "plant",
            "harvest",
            "yield",
            "recommend",
            "sow",
            "cultivate",
            "farming",
            "best crop",
            "what should i grow",
            "kharif",
            "rabi",
            "season",
            "suitable",
        ],
        "weather_analysis": [
            "weather",
            "temperature",
            "rain",
            "rainfall",
            "humidity",
            "forecast",
            "climate",
            "wind",
            "hot",
            "cold",
            "monsoon",
        ],
        "soil_check": [
            "soil",
            "moisture",
            "water content",
            "dry",
            "irrigation",
            "nutrient",
            "nitrogen",
            "phosphorus",
            "potassium",
            "npk",
            "ph",
            "organic carbon",
            "fertility",
        ],
        "flood_risk": [
            "flood",
            "risk",
            "danger",
            "warning",
            "waterlog",
            "inundation",
            "drainage",
            "overflow",
            "deluge",
        ],
        "ndvi_analysis": [
            "ndvi",
            "vegetation",
            "greenness",
            "health",
            "biomass",
            "satellite image",
            "green cover",
            "canopy",
        ],
        "price_analysis": [
            "price",
            "mandi",
            "market",
            "msp",
            "cost",
            "sell",
            "profit",
            "income",
            "earning",
            "trade",
        ],
    }

    # Count matches per intent for better accuracy
    scores: dict[str, int] = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[intent] = score

    if scores:
        return max(scores, key=scores.get)  # type: ignore

    return "general"


def _extract_place_names(query: str) -> list[str]:
    """
    Extract ALL place-name candidates from a query string.

    Handles:
      - "crop in Agra and Mathura"
      - "NDVI for Sultanpur, Amethi and Raebareli"
      - "weather near Khatauli"
      - "soil analysis Delhi"
      - Case-insensitive for small towns
    """
    import re

    places: list[str] = []

    # Pattern 1: "in/for/near/at/around/of <Place1>[,/ and <Place2>]*"
    multi_loc = re.search(
        r"\b(?:in|for|near|at|around|of|between)\s+(.+?)(?:\?|$|\.|!)",
        query,
        re.IGNORECASE,
    )
    if multi_loc:
        raw = multi_loc.group(1).strip()
        # Split on " and ", ",", " & "
        parts = re.split(r"\s+and\s+|\s*,\s*|\s*&\s*", raw)
        for p in parts:
            cleaned = p.strip().rstrip("?.!")
            if cleaned and len(cleaned) > 1:
                places.append(cleaned)

    # Pattern 2: "<Place> weather/crop/soil/farm" (place before keyword)
    before_kw = re.findall(
        r"([A-Za-z][A-Za-z .'-]+?)\s+(?:weather|crop|soil|farm|ndvi|analysis)",
        query,
        re.IGNORECASE,
    )
    for p in before_kw:
        cleaned = p.strip()
        if cleaned and cleaned not in places and len(cleaned) > 1:
            places.append(cleaned)

    # Pattern 3: Capitalized words not matching common English words (fallback)
    if not places:
        stop = {
            "what", "which", "show", "give", "tell", "the", "and", "for",
            "crop", "soil", "weather", "ndvi", "analysis", "price",
            "recommendation", "best", "should", "grow", "plant", "complete",
            "me", "my", "how", "can", "will", "does", "near", "from",
        }
        caps = re.findall(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*)\b", query)
        for c in caps:
            if c.lower() not in stop and c not in places:
                places.append(c)

    return places


def _geocode_place(place: str) -> tuple[float, float, str] | None:
    """
    Geocode a single place name.

    Returns (lat, lon, display_name) or None.
    Tries the offline soil DB first, then Nominatim.
    """
    place_lower = place.lower()

    # 1. Offline soil DB
    for region in _SOIL_DB.get("regions", []):
        city = region.get("city", "").lower()
        state = region.get("state", "").lower()
        # Match city name (also handle parenthetical aliases like "Vizag (Visakhapatnam)")
        if city and (city in place_lower or place_lower in city):
            lr, lo = region.get("lat_range", [0, 0]), region.get("lon_range", [0, 0])
            return ((lr[0]+lr[1])/2, (lo[0]+lo[1])/2, f"{region['city']}, {region['state']}")
        if state and state == place_lower:
            lr, lo = region.get("lat_range", [0, 0]), region.get("lon_range", [0, 0])
            return ((lr[0]+lr[1])/2, (lo[0]+lo[1])/2, f"{region['city']}, {region['state']}")

    # 2. Nominatim forward geocode (handles ANY place, including small villages)
    try:
        import httpx
        # Add "India" hint for better results on small Indian towns
        search_q = f"{place}, India" if not any(c in place.lower() for c in ["india", ","]) else place
        url = (
            f"https://nominatim.openstreetmap.org/search"
            f"?q={search_q}&format=json&limit=1&accept-language=en"
        )
        resp = httpx.get(url, timeout=5.0, headers={"User-Agent": "OrbitalNexus/1.0"})
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return (
                    float(results[0]["lat"]),
                    float(results[0]["lon"]),
                    results[0].get("display_name", place),
                )
    except Exception:
        pass

    return None


def extract_location(query: str) -> tuple[float, float] | None:
    """
    Extract a single location from the query (backwards-compatible).

    Returns (lat, lon) for the first location found, or None.
    """
    places = _extract_place_names(query)
    for place in places:
        result = _geocode_place(place)
        if result:
            return (result[0], result[1])
    return None


def extract_locations(query: str) -> list[dict]:
    """
    Extract ALL locations mentioned in a query.

    Supports multi-city queries like:
      - "Show NDVI for Agra and Mathura"
      - "Compare crops in Sultanpur, Amethi and Raebareli"

    Returns:
        [{"lat": ..., "lon": ..., "name": "Agra, Uttar Pradesh"}, ...]
    """
    places = _extract_place_names(query)
    results: list[dict] = []
    seen: set[str] = set()

    for place in places:
        key = place.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        geo = _geocode_place(place)
        if geo:
            results.append({"lat": geo[0], "lon": geo[1], "name": geo[2]})

    return results
