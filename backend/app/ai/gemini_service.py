"""
Gemini AI Service — Orbital Nexus

Provides AI-powered natural language guidance using Google's Gemini model.
Falls back gracefully to template-based responses when API key is missing
or the API is unreachable — demo NEVER crashes.

Provides Gemini-driven crop recommendations based on current season,
geological conditions, mandi prices, and geopolitical circumstances.
Only recommends crops with rising demand expected to continue increasing.

Usage:
  Set GEMINI_API_KEY in .env or environment variables.
  The service will auto-detect and use Gemini when available.
"""

import json
import os
import logging
import datetime
from typing import Any

logger = logging.getLogger("orbital.gemini")

# ── Gemini Client (lazy init) ──────────────────────────────────────
_client = None
_model_id = "gemini-2.0-flash"


def _get_client():
    """Lazily initialize the Gemini client."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — AI guidance will use templates")
        return None

    try:
        from google import genai

        _client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized (model: %s)", _model_id)
        return _client
    except Exception as exc:
        logger.error("Failed to init Gemini client: %s", exc)
        return None


# ── System prompt ───────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Orbital Nexus AI — an expert agricultural advisor powered by multi-satellite data fusion.

Your role:
- Provide actionable, location-specific farming guidance for Indian farmers
- Explain satellite data (NDVI, soil moisture, weather) in simple terms
- Recommend crops based on soil nutrients (N-P-K), weather, and market trends
- Warn about risks (flood, drought, pest pressure) with mitigation steps
- Reference the actual data values provided to you (don't make up numbers)

Tone: Professional but approachable. Use Hindi terms occasionally (Rabi, Kharif, MSP).
Format: 2-3 concise paragraphs. Use bullet points for recommendations.
Always end with a specific, actionable next step the farmer can take today.
Never use markdown headers (#). Keep it conversational."""


def _build_context_prompt(
    query: str,
    intent: str,
    fused_data: dict[str, Any],
    live_context: dict[str, Any],
) -> str:
    """Build a rich context prompt with all satellite + soil + crop data."""
    weather = live_context.get("weather", {})
    soil = live_context.get("soil", {})
    crop_prediction = live_context.get("crop_prediction", [])
    land = live_context.get("land_classification", "Unknown")
    sources = live_context.get("data_sources", [])

    crops_str = ""
    if crop_prediction:
        lines = []
        for i, p in enumerate(crop_prediction[:5]):
            line = f"  {i+1}. {p['crop'].capitalize()} — {int(p['confidence']*100)}% match"
            m = p.get("market")
            if m and m.get("msp") is not None and m.get("price_min") is not None and m.get("price_max") is not None:
                line += f" | MSP ₹{m['msp']:,}/qtl, Range ₹{m['price_min']:,}-{m['price_max']:,}/qtl"
            lines.append(line)
        crops_str = "\n".join(lines)

    return f"""User Query: "{query}"
Detected Intent: {intent}

=== SATELLITE DATA (LIVE) ===
Region: {fused_data.get('region', 'Unknown')}
Coordinates: {fused_data.get('lat', 28.47)}°N, {fused_data.get('lon', 77.50)}°E
Temperature: {weather.get('temp', 'N/A')}°C
Humidity: {weather.get('humidity', 'N/A')}%
Rainfall: {weather.get('rain', 'N/A')} mm
Soil Moisture: {weather.get('moisture', 'N/A')}
NDVI: {fused_data.get('ndvi_avg', 'N/A')}
Land Classification: {land}

=== SOIL PROFILE ===
Type: {soil.get('type', 'Unknown')} | Texture: {soil.get('texture', 'Unknown')}
pH: {soil.get('ph', 'N/A')}
Nitrogen: {soil.get('nitrogen_kg_ha', 'N/A')} kg/ha
Phosphorus: {soil.get('phosphorus_kg_ha', 'N/A')} kg/ha
Potassium: {soil.get('potassium_kg_ha', 'N/A')} kg/ha
Organic Carbon: {soil.get('organic_carbon_pct', 'N/A')}%

=== GEMINI CROP PREDICTIONS (Rising Demand) ===
{crops_str or "No crop predictions available"}

=== DATA SOURCES ===
{', '.join(sources)}

Based on this fused satellite data, provide expert agricultural guidance."""


async def generate_ai_guidance(
    query: str,
    intent: str,
    fused_data: dict[str, Any],
    live_context: dict[str, Any],
) -> str | None:
    """
    Generate AI-powered guidance using Gemini.

    Returns:
        AI-generated text if successful, None if fallback needed.
    """
    client = _get_client()
    if client is None:
        return None

    context_prompt = _build_context_prompt(query, intent, fused_data, live_context)

    try:
        response = client.models.generate_content(
            model=_model_id,
            contents=context_prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 512,
                "temperature": 0.7,
            },
        )

        text = response.text
        if text:
            logger.info("Gemini generated %d chars of guidance", len(text))
            return text.strip()

        logger.warning("Gemini returned empty response")
        return None

    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return None


def is_ai_available() -> bool:
    """Check if AI (Gemini) is configured and available."""
    return bool(os.getenv("GEMINI_API_KEY", ""))


# ── Gemini-Powered Crop Recommendation Cache ───────────────────────
_crop_cache: dict[str, dict[str, Any]] = {}
_CROP_CACHE_MAX = 200


# ── Seasonal fallback data ─────────────────────────────────────────
_SEASONAL_FALLBACK: dict[str, list[dict[str, Any]]] = {
    "rabi": [
        {"crop": "wheat", "confidence": 0.92, "demand_score": 88, "demand_trend": "rising", "reasoning": "Peak Rabi season. Strong MSP procurement and rising mandi prices.", "season": "Rabi (Oct–Mar)", "expected_season": "Rabi", "recommended_action": "increase acreage"},
        {"crop": "chickpea", "confidence": 0.85, "demand_score": 82, "demand_trend": "rising", "reasoning": "High pulse demand. Import duty keeping domestic prices firm.", "season": "Rabi (Oct–Mar)", "expected_season": "Rabi", "recommended_action": "book forward contract"},
        {"crop": "lentil", "confidence": 0.78, "demand_score": 75, "demand_trend": "rising", "reasoning": "Domestic prices strengthening. Reduced import dependency.", "season": "Rabi (Oct–Mar)", "expected_season": "Rabi", "recommended_action": "increase acreage"},
    ],
    "kharif": [
        {"crop": "rice", "confidence": 0.90, "demand_score": 90, "demand_trend": "rising", "reasoning": "Monsoon season staple. Government procurement ensures floor price.", "season": "Kharif (Jun–Oct)", "expected_season": "Kharif", "recommended_action": "increase acreage"},
        {"crop": "maize", "confidence": 0.82, "demand_score": 78, "demand_trend": "rising", "reasoning": "Feed industry demand steady. Ethanol blending creating new markets.", "season": "Kharif (Jun–Oct)", "expected_season": "Kharif", "recommended_action": "store & wait"},
        {"crop": "soybean", "confidence": 0.75, "demand_score": 72, "demand_trend": "rising", "reasoning": "Oilseed demand rising. Processing industry expansion.", "season": "Kharif (Jun–Oct)", "expected_season": "Kharif", "recommended_action": "increase acreage"},
    ],
    "summer": [
        {"crop": "mungbean", "confidence": 0.88, "demand_score": 85, "demand_trend": "rising", "reasoning": "Short-duration summer pulse. High domestic consumption.", "season": "Summer (Mar–Jun)", "expected_season": "Summer", "recommended_action": "increase acreage"},
        {"crop": "groundnut", "confidence": 0.80, "demand_score": 76, "demand_trend": "rising", "reasoning": "Edible oil demand rising. Strong export market.", "season": "Summer (Mar–Jun)", "expected_season": "Summer", "recommended_action": "book forward contract"},
        {"crop": "sugarcane", "confidence": 0.75, "demand_score": 70, "demand_trend": "rising", "reasoning": "Ethanol blending policy driving demand. Year-round crop.", "season": "Perennial (harvest Oct–Apr)", "expected_season": "Perennial", "recommended_action": "store & wait"},
    ],
}


def _get_current_season() -> str:
    """Determine the current Indian agricultural season."""
    month = datetime.datetime.now().month
    if month in (11, 12, 1, 2, 3):
        return "rabi"
    elif month in (6, 7, 8, 9, 10):
        return "kharif"
    else:
        return "summer"


def _get_seasonal_fallback(
    region: str, soil: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Seasonal + soil-aware fallback when Gemini is unavailable.

    Picks the right season, then adjusts crops based on soil type/pH.
    """
    season = _get_current_season()
    base_crops = _SEASONAL_FALLBACK.get(season, _SEASONAL_FALLBACK["rabi"])

    # Adjust based on soil properties
    soil_type = soil.get("type", "").lower()
    ph = soil.get("ph", 7.0)
    recommended = soil.get("recommended_crops", [])

    # If soil DB has specific recommendations, blend them in
    if recommended:
        # Interleave soil-recommended crops with seasonal defaults
        blended: list[dict[str, Any]] = []
        for i, soil_crop in enumerate(recommended[:2]):
            blended.append({
                "crop": soil_crop.lower(),
                "confidence": round(0.90 - i * 0.05, 2),
                "demand_score": round(85 - i * 5, 1),
                "demand_trend": "rising",
                "reasoning": f"Ideal for {soil.get('type', 'local')} soil (pH {ph}). Suited to current {season.capitalize()} season.",
                "season": base_crops[0]["season"] if base_crops else "Current",
                "expected_season": base_crops[0].get("expected_season", season.capitalize()) if base_crops else season.capitalize(),
                "recommended_action": "increase acreage",
            })
        # Add one seasonal pick
        if base_crops:
            blended.append(base_crops[0])
        return blended[:3]

    return base_crops


CROP_ADVISOR_SYSTEM = """You are an expert Indian agricultural market analyst and crop advisor.
You must respond ONLY with valid JSON — no markdown, no explanation, no text outside the JSON.

Your response MUST be a JSON array of exactly 3 crop objects.
Return ONLY crops whose current demand is rising AND expected to continue increasing.

[
  {
    "crop": "crop_name_lowercase",
    "confidence": 0.85,
    "demand_score": 82,
    "demand_trend": "rising",
    "reasoning": "One sentence explaining why this crop's demand is rising and will stay rising",
    "season": "Rabi (Oct-Mar)",
    "expected_season": "Rabi",
    "recommended_action": "increase acreage"
  }
]

Rules:
- crop: lowercase single word (e.g. "wheat", "rice", "chickpea", "maize", "cotton", "sugarcane")
- confidence: number between 0.5 and 0.95
- demand_score: 0–100, how strong the demand signal is
- demand_trend: MUST be "rising" — only return crops with rising demand
- reasoning: include current mandi price trend, arrivals data, government policy, or export demand
- season: one of "Rabi (Oct-Mar)", "Kharif (Jun-Oct)", "Summer (Mar-Jun)", or "Perennial"
- expected_season: one of "Rabi", "Kharif", "Summer", "Perennial"
- recommended_action: short farmer action (e.g. "increase acreage", "store & wait", "harvest early", "book forward contract")
- Crops MUST be appropriate for the given soil, weather, and region
- Crops MUST be seasonally correct for the current month
- Consider current geopolitical factors (export bans, MSP hikes, trade agreements)
- Consider mandi price trends and arrival quantities when available"""


async def generate_gemini_crop_recommendation(
    region: str,
    soil: dict[str, Any],
    weather: dict[str, Any],
    lat: float,
    lon: float,
    mandi_snapshot: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]] | None:
    """
    Ask Gemini for demand-driven, profit-optimised crop recommendations.

    Returns ONLY crops whose demand is currently rising and expected to
    continue increasing. Uses mandi snapshot for real market context.

    Returns:
        List of 3 crop dicts with demand fields, or None if unavailable.
    """
    client = _get_client()
    if client is None:
        return None

    # Cache key: region + rounded coordinates + current month
    now = datetime.datetime.now()
    cache_key = f"{region}|{round(lat,1)}|{round(lon,1)}|{now.month}-{now.year}"
    if cache_key in _crop_cache:
        logger.info("Gemini crop cache hit: %s", cache_key)
        return _crop_cache[cache_key].get("crops")

    season = _get_current_season()
    month_name = now.strftime("%B %Y")

    # Format mandi snapshot if available
    mandi_str = "No mandi data available."
    if mandi_snapshot:
        mandi_lines = []
        for m in mandi_snapshot[:8]:
            mandi_lines.append(
                f"  {m.get('commodity','?')}: ₹{m.get('modal_price','?')}/qtl, "
                f"arrivals {m.get('arrivals_ton','?')}t at {m.get('mandi','?')} ({m.get('date','?')})"
            )
        mandi_str = "\n".join(mandi_lines)

    prompt = f"""Current Date: {month_name}
Current Season: {season.capitalize()} season in India

Region: {region}
Coordinates: {lat}°N, {lon}°E
Temperature: {weather.get('temp', 28)}°C
Humidity: {weather.get('humidity', 60)}%
Rainfall: {weather.get('rain', 0)} mm

Soil Type: {soil.get('type', 'Unknown')} | Texture: {soil.get('texture', 'Loam')}
pH: {soil.get('ph', 7.0)}
Nitrogen: {soil.get('nitrogen_kg_ha', 200)} kg/ha
Phosphorus: {soil.get('phosphorus_kg_ha', 15)} kg/ha
Potassium: {soil.get('potassium_kg_ha', 220)} kg/ha

=== MANDI (WHOLESALE MARKET) SNAPSHOT ===
{mandi_str}

According to current & upcoming 4 months' geological & geopolitical circumstances, which crop will give better profit to the farmer?

Return ONLY crops whose demand is currently RISING and is expected to CONTINUE INCREASING.

Consider:
- Current Indian government MSP policies and procurement plans
- Export/import restrictions on agricultural commodities
- Monsoon forecast and climate patterns for this region
- Current mandi price trends and arrival quantities (falling arrivals = scarcity = rising demand)
- This specific soil's nutrient profile and what grows best in it
- Which crops a farmer should increase acreage for maximum profit

Return exactly 3 rising-demand crops as a JSON array. Each crop must be suitable for {soil.get('type', 'this')} soil with pH {soil.get('ph', 7.0)} in the {season} season."""

    try:
        response = client.models.generate_content(
            model=_model_id,
            contents=prompt,
            config={
                "system_instruction": CROP_ADVISOR_SYSTEM,
                "max_output_tokens": 600,
                "temperature": 0.3,
            },
        )

        text = response.text
        if not text:
            logger.warning("Gemini crop advisor returned empty response")
            return None

        # Parse JSON from response (handle markdown code fences)
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                l for l in lines if not l.strip().startswith("```")
            )

        crops = json.loads(cleaned)

        if not isinstance(crops, list) or len(crops) == 0:
            logger.warning("Gemini crop advisor: invalid response structure")
            return None

        # Normalise and validate each crop — enforce demand fields
        validated: list[dict[str, Any]] = []
        for c in crops[:3]:
            if not isinstance(c, dict) or "crop" not in c:
                continue
            validated.append({
                "crop": str(c["crop"]).lower().strip(),
                "confidence": max(0.5, min(0.95, float(c.get("confidence", 0.75)))),
                "demand_score": max(0, min(100, float(c.get("demand_score", 70)))),
                "demand_trend": str(c.get("demand_trend", "rising")),
                "reasoning": str(c.get("reasoning", "AI-recommended: rising demand for current conditions")),
                "season": str(c.get("season", "Current")),
                "expected_season": str(c.get("expected_season", season.capitalize())),
                "recommended_action": str(c.get("recommended_action", "increase acreage")),
            })

        if not validated:
            logger.warning("Gemini crop advisor: no valid crops in response")
            return None

        # Cache the result
        if len(_crop_cache) >= _CROP_CACHE_MAX:
            oldest = next(iter(_crop_cache))
            del _crop_cache[oldest]
        _crop_cache[cache_key] = {"crops": validated}

        logger.info(
            "Gemini crop advisor for %s: %s",
            region,
            ", ".join(f"{c['crop']}(demand:{c['demand_score']})" for c in validated),
        )
        return validated

    except json.JSONDecodeError as exc:
        logger.error("Gemini crop advisor: JSON parse error — %s", exc)
        return None
    except Exception as exc:
        logger.error("Gemini crop advisor error: %s", exc)
        return None


# ── Market Brain: Gemini-powered mandi demand analysis ─────────────
_market_cache: dict[str, Any] = {}
_MARKET_CACHE_MAX = 100

MARKET_ADVISOR_SYSTEM = """You are an agricultural market analyst for Indian farmers.

Analyze mandi (wholesale market) data and recommend crops based on:
- Current market prices and arrival quantities
- Seasonal demand patterns
- Upcoming 4-month geological & geopolitical circumstances
- Regional market conditions

Return ONLY a valid JSON array (no markdown, no explanations) with 5 crop recommendations:
[
  {
    "name": "Wheat",
    "demand_score": 85,
    "demand_trend": "rising",
    "confidence": "high",
    "reasoning": "Strong MSP support, low arrivals indicate scarcity"
  }
]

Rules:
- demand_score: 0-100 (higher = better profit potential)
- demand_trend: "rising" | "falling" | "stable"
- confidence: "high" | "medium" | "low"
- reasoning: one concise sentence explaining the market dynamics
"""


async def generate_gemini_market_analysis(
    prompt: str, region: str, lat: float, lon: float
) -> list[dict[str, Any]] | None:
    """
    Query Gemini for market demand analysis and crop profitability recommendations.
    
    Returns structured list of commodities with demand scores, trends, and reasoning.
    Uses same caching strategy as crop recommendations.
    """
    client = _get_client()
    if client is None:
        logger.warning("Gemini unavailable for market analysis")
        return None

    # Cache by region + month
    now = datetime.datetime.now()
    cache_key = f"{region}|{round(lat, 2)}|{round(lon, 2)}|{now.year}-{now.month}"
    
    if cache_key in _market_cache:
        logger.info("Market analysis cache hit: %s", cache_key)
        return _market_cache[cache_key]["commodities"]

    try:
        full_prompt = f"{MARKET_ADVISOR_SYSTEM}\n\n{prompt}"
        
        response = client.models.generate_content(
            model=_model_id,
            contents=full_prompt,
            config={
                "temperature": 0.4,  # Slightly higher for market variability
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
        )

        if not response or not response.text:
            logger.error("Empty Gemini market analysis response")
            return None

        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        parsed = json.loads(text)
        
        if not isinstance(parsed, list):
            logger.error("Market analysis response not a list")
            return None

        # Validate structure
        validated = []
        for item in parsed[:10]:  # Top 10 max
            if not isinstance(item, dict):
                continue
            if "name" not in item or "demand_score" not in item:
                continue
            
            validated.append({
                "name": item.get("name", "Unknown"),
                "demand_score": min(100, max(0, float(item.get("demand_score", 50)))),
                "demand_trend": item.get("demand_trend", "stable"),
                "confidence": item.get("confidence", "medium"),
                "reasoning": item.get("reasoning", "Market analysis")
            })

        if not validated:
            logger.error("No valid market commodities in Gemini response")
            return None

        # Cache the result
        if len(_market_cache) >= _MARKET_CACHE_MAX:
            oldest = next(iter(_market_cache))
            del _market_cache[oldest]
        _market_cache[cache_key] = {"commodities": validated}

        logger.info(
            "Gemini market analysis for %s: %s",
            region,
            ", ".join(f"{c['name']}({c['demand_score']})" for c in validated[:5]),
        )
        return validated

    except json.JSONDecodeError as exc:
        logger.error("Gemini market analysis: JSON parse error — %s", exc)
        return None
    except Exception as exc:
        logger.error("Gemini market analysis error: %s", exc)
        return None
