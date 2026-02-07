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


def extract_location(query: str) -> tuple[float, float] | None:
    """
    Extract location coordinates from the query by matching city names
    in the soil database.

    Returns:
        (lat, lon) tuple if a location is found, None otherwise.
    """
    query_lower = query.lower()

    for region in _SOIL_DB.get("regions", []):
        city = region.get("city", "").lower()
        state = region.get("state", "").lower()

        if city and city in query_lower:
            lat_range = region.get("lat_range", [0, 0])
            lon_range = region.get("lon_range", [0, 0])
            lat = (lat_range[0] + lat_range[1]) / 2
            lon = (lon_range[0] + lon_range[1]) / 2
            return (lat, lon)

        # Also check state name
        if state and state in query_lower:
            lat_range = region.get("lat_range", [0, 0])
            lon_range = region.get("lon_range", [0, 0])
            lat = (lat_range[0] + lat_range[1]) / 2
            lon = (lon_range[0] + lon_range[1]) / 2
            return (lat, lon)

    return None
