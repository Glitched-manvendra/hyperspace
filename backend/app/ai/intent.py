"""
Intent Parser — Orbital Nexus AI Module

Parses natural language queries into structured intents.
Currently uses keyword matching; can be upgraded to LLM-based parsing.
"""


def parse_intent(query: str) -> str:
    """
    Parse user query into one of the supported intents.

    Supported intents:
    - crop_recommendation: User wants crop suggestions
    - weather_analysis: User asks about weather/climate
    - soil_check: User asks about soil conditions
    - flood_risk: User asks about flooding/risk
    - ndvi_analysis: User asks about vegetation health
    - general: Catch-all for unrecognized queries

    Uses simple keyword matching for hackathon speed.
    Production version would use embeddings or LLM classification.
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
        ],
        "weather_analysis": [
            "weather",
            "temperature",
            "rain",
            "rainfall",
            "humidity",
            "forecast",
            "climate",
        ],
        "soil_check": ["soil", "moisture", "water content", "dry", "irrigation"],
        "flood_risk": ["flood", "risk", "danger", "warning", "waterlog", "inundation"],
        "ndvi_analysis": ["ndvi", "vegetation", "greenness", "health", "biomass"],
    }

    for intent, keywords in intent_keywords.items():
        if any(kw in query_lower for kw in keywords):
            return intent

    return "general"
