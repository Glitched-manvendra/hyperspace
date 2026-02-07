"""
Gemini AI Service — Orbital Nexus

Provides AI-powered natural language guidance using Google's Gemini model.
Falls back gracefully to template-based responses when API key is missing
or the API is unreachable — demo NEVER crashes.

Usage:
  Set GEMINI_API_KEY in .env or environment variables.
  The service will auto-detect and use Gemini when available.
"""

import os
import logging
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

=== KNN CROP PREDICTIONS ===
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
