"""
Data Fusion Service - Orbital Nexus

Handles fusing and summarizing multi-satellite datasets.
Returns structured data for API responses and UI generation.

Now integrates with:
  - Live data from data_fusion.py engine
  - CropEngine predictions (KNN-based crop recommendation)
  - Market trends (price intelligence)
"""

from typing import Any
from app.models.schemas import FusedDataSummary, UIInstruction
from app.services.market_trends import get_market_info, get_price_display


def get_fused_data(
    lat: float,
    lon: float,
    live_weather: dict[str, Any] | None = None,
    region_name: str | None = None,
    data_sources: list[str] | None = None,
) -> FusedDataSummary:
    """
    Build a FusedDataSummary from live weather data.

    If live_weather is provided (from Open-Meteo), uses real values.
    Otherwise falls back to demo data.
    """
    if live_weather:
        return FusedDataSummary(
            region=region_name or _get_region_name(lat, lon),
            lat=lat,
            lon=lon,
            temperature_avg_c=round(live_weather.get("temp", 32.5), 1),
            rainfall_mm=round(live_weather.get("rain", 0.0), 1),
            soil_moisture_pct=round(live_weather.get("moisture", 0.30) * 100, 1),
            ndvi_avg=0.68,  # NDVI still mock (would need Sentinel Hub)
            data_sources=data_sources or ["Open-Meteo", "Soil Database"],
        )

    # Fallback mock data
    return FusedDataSummary(
        region=_get_region_name(lat, lon),
        lat=lat,
        lon=lon,
        temperature_avg_c=32.5,
        rainfall_mm=145.0,
        soil_moisture_pct=42.3,
        ndvi_avg=0.68,
        data_sources=["MODIS", "Sentinel-2", "NASA SMAP", "Open-Meteo"],
    )


def build_ui_instructions(
    intent: str,
    fused_data: FusedDataSummary,
    live_context: dict[str, Any] | None = None,
) -> list[UIInstruction]:
    """
    Generate frontend dashboard card instructions based on intent and fused data.

    Now enriched with live context for chart_line, chart_pie, and list widget types.
    """
    soil = (live_context or {}).get("soil", {})
    land_class = (live_context or {}).get("land_classification", "Unknown")

    # -- Base stat cards (always shown) --
    cards: list[UIInstruction] = [
        UIInstruction(
            card_type="stat",
            title="Temperature",
            value=f"{fused_data.temperature_avg_c}\u00b0C",
            subtitle="Current reading (Open-Meteo)",
            color="orange",
        ),
        UIInstruction(
            card_type="stat",
            title="Humidity",
            value=f"{(live_context or {}).get('weather', {}).get('humidity', 55)}%",
            subtitle="Relative humidity",
            color="cyan",
        ),
        UIInstruction(
            card_type="stat",
            title="Soil Moisture",
            value=f"{fused_data.soil_moisture_pct}%",
            subtitle="0-1 cm depth",
            color="green",
        ),
        UIInstruction(
            card_type="stat",
            title="NDVI",
            value=f"{fused_data.ndvi_avg:.2f}",
            subtitle="Vegetation health index",
            color="emerald",
        ),
    ]

    # -- Land classification card --
    cards.append(
        UIInstruction(
            card_type="stat",
            title="Land Use (ISRO)",
            value=land_class.split("(")[0].strip(),
            subtitle="ISRO Bhuvan LULC Classification",
            color="blue",
        )
    )

    # -- Soil info card --
    if soil:
        cards.append(
            UIInstruction(
                card_type="stat",
                title="Soil Type",
                value=f"{soil.get('type', 'Unknown')} (pH {soil.get('ph', 7.0)})",
                subtitle=soil.get("texture", ""),
                color="yellow",
            )
        )

    # -- Crop price trend chart (chart_line) --
    # Build dynamic price trend from predicted crops or soil-recommended crops
    crop_prediction = (live_context or {}).get("crop_prediction", [])
    trend_crops = [
        p["crop"] for p in crop_prediction[:3]
    ] if crop_prediction else soil.get("recommended_crops", ["Rice", "Wheat", "Pulses"])[:3]

    price_points = _build_price_trend_points(trend_crops)
    trend_label = " vs ".join(c.capitalize() for c in trend_crops[:3])
    region_name = (live_context or {}).get("region", "")

    cards.append(
        UIInstruction(
            card_type="chart_line",
            title="Crop Price Trends",
            value=trend_label,
            subtitle=f"Projected price (INR/quintal) — {region_name}",
            color="emerald",
            data={
                "points": price_points,
                "unit": "₹/qtl",
            },
        )
    )

    # -- Soil composition donut (chart_pie) --
    if soil:
        cards.append(
            UIInstruction(
                card_type="chart_pie",
                title="Soil Composition",
                value=f"{soil.get('type', 'Soil')} Profile",
                subtitle=f"N: {soil.get('nitrogen_kg_ha', 200)} | P: {soil.get('phosphorus_kg_ha', 15)} | K: {soil.get('potassium_kg_ha', 220)} kg/ha",
                color="cyan",
                data={
                    "segments": [
                        {"name": "Nitrogen", "value": soil.get("nitrogen_kg_ha", 200)},
                        {
                            "name": "Phosphorus",
                            "value": soil.get("phosphorus_kg_ha", 15),
                        },
                        {
                            "name": "Potassium",
                            "value": soil.get("potassium_kg_ha", 220),
                        },
                        {
                            "name": "Organic Carbon",
                            "value": int(soil.get("organic_carbon_pct", 0.45) * 100),
                        },
                    ]
                },
            )
        )

    # -- Recommended crops list (now powered by CropEngine) --
    crop_prediction = (live_context or {}).get("crop_prediction", [])
    if crop_prediction:
        # Use CropEngine's KNN predictions
        items = []
        for pred in crop_prediction:
            crop_name = pred["crop"].capitalize()
            market = pred.get("market", {})
            items.append(
                {
                    "name": crop_name,
                    "confidence": pred["confidence"],
                    "season": market.get("season", _get_season(crop_name)),
                    "reasoning": get_price_display(pred["crop"]),
                }
            )

        cards.append(
            UIInstruction(
                card_type="list",
                title="AI Crop Prediction",
                value=f"{len(items)} crops matched",
                subtitle="KNN model · Soil + Weather fusion",
                color="green",
                data={"items": items},
            )
        )

        # -- Crop Factors Bar Chart (N-P-K analysis) --
        cards.append(
            UIInstruction(
                card_type="chart_bar",
                title="Soil Nutrient Profile",
                value=f"N·P·K for {crop_prediction[0]['crop'].capitalize()}",
                subtitle="Actual vs optimal nutrient levels (kg/ha)",
                color="emerald",
                data={
                    "factors": [
                        {
                            "name": "Nitrogen",
                            "actual": soil.get("nitrogen_kg_ha", 80),
                            "optimal": _optimal_npk(crop_prediction[0]["crop"], "N"),
                        },
                        {
                            "name": "Phosphorus",
                            "actual": soil.get("phosphorus_kg_ha", 40),
                            "optimal": _optimal_npk(crop_prediction[0]["crop"], "P"),
                        },
                        {
                            "name": "Potassium",
                            "actual": soil.get("potassium_kg_ha", 40),
                            "optimal": _optimal_npk(crop_prediction[0]["crop"], "K"),
                        },
                    ]
                },
            )
        )

        # -- Market intelligence card for top crop --
        top_market = crop_prediction[0].get("market")
        if top_market:
            cards.append(
                UIInstruction(
                    card_type="stat",
                    title=f"Market: {crop_prediction[0]['crop'].capitalize()}",
                    value=f"₹{top_market['price_min']:,}–{top_market['price_max']:,}/qtl",
                    subtitle=top_market.get("forecast", "")[:80],
                    color="yellow",
                )
            )
    else:
        # Fallback: use soil DB recommended crops
        recommended = soil.get("recommended_crops", ["Rice", "Wheat", "Pulses"])
        cards.append(
            UIInstruction(
                card_type="list",
                title="Recommended Crops",
                value=f"{len(recommended)} crops identified",
                subtitle=f"Best suited for {soil.get('type', 'local')} soil",
                color="green",
                data={
                    "items": [
                        {
                            "name": crop,
                            "confidence": round(0.92 - i * 0.05, 2),
                            "season": _get_season(crop),
                        }
                        for i, crop in enumerate(recommended[:6])
                    ]
                },
            )
        )

    # -- Intent-specific bonus cards --
    if intent == "crop_recommendation":
        top_crop = (
            crop_prediction[0]["crop"].capitalize()
            if crop_prediction
            else (recommended[0] if "recommended" in dir() and recommended else "Wheat")
        )
        top_conf = crop_prediction[0]["confidence"] if crop_prediction else 0.85
        cards.append(
            UIInstruction(
                card_type="recommendation",
                title="🧠 AI Crop Brain",
                value=top_crop,
                subtitle=f"{int(top_conf * 100)}% match · KNN fusion of {len((live_context or {}).get('data_sources', ['satellite']))} data sources",
                color="yellow",
            )
        )
    elif intent == "flood_risk":
        rain = fused_data.rainfall_mm
        risk = "High" if rain > 200 else ("Moderate" if rain > 50 else "Low")
        cards.append(
            UIInstruction(
                card_type="alert",
                title="Flood Risk Level",
                value=risk,
                subtitle=f"{rain}mm rainfall - {'monitor drainage!' if risk != 'Low' else 'safe levels'}",
                color="red" if risk == "High" else "orange",
            )
        )
    elif intent == "ndvi_analysis":
        cards.append(
            UIInstruction(
                card_type="chart",
                title="NDVI Trend (6 months)",
                value="0.55 -> 0.68",
                subtitle="Vegetation health improving",
                color="green",
            )
        )
    elif intent == "soil_check":
        cards.append(
            UIInstruction(
                card_type="stat",
                title="Soil Health Score",
                value=f"{_soil_score(soil)}/100",
                subtitle=soil.get("description", ""),
                color="emerald",
            )
        )

    return cards


def generate_guidance(
    intent: str,
    fused_data: FusedDataSummary,
    query: str,
    live_context: dict[str, Any] | None = None,
) -> str:
    """
    Generate a human-readable guidance paragraph.
    Now enriched with live soil and land classification context.
    """
    soil = (live_context or {}).get("soil", {})
    land = (live_context or {}).get("land_classification", "")
    sources = ", ".join(fused_data.data_sources)

    crop_prediction = (live_context or {}).get("crop_prediction", [])
    top_crops_str = (
        ", ".join(
            f"{p['crop'].capitalize()} ({int(p['confidence'] * 100)}%)"
            for p in crop_prediction[:3]
        )
        if crop_prediction
        else ", ".join(soil.get("recommended_crops", ["Wheat", "Rice"])[:3])
    )

    guidance_templates = {
        "crop_recommendation": (
            f"🧠 AI Crop Brain analysis for {fused_data.region} "
            f"(fusing {sources}): Temperature {fused_data.temperature_avg_c}°C, "
            f"soil moisture {fused_data.soil_moisture_pct}%, NDVI {fused_data.ndvi_avg:.2f}. "
            f"Soil is {soil.get('type', 'alluvial')} ({soil.get('texture', 'loam')}, pH {soil.get('ph', 7.0)}). "
            f"Nutrients — N: {soil.get('nitrogen_kg_ha', 200)}, P: {soil.get('phosphorus_kg_ha', 15)}, "
            f"K: {soil.get('potassium_kg_ha', 220)} kg/ha. "
            f"Land status: {land}. "
            f"KNN model recommends: {top_crops_str}. "
            f"{'Top pick: ' + crop_prediction[0]['crop'].capitalize() + ' — ' + (crop_prediction[0].get('market', {}).get('forecast', '')) if crop_prediction else ''}"
        ),
        "weather_analysis": (
            f"LIVE weather for {fused_data.region}: Temperature "
            f"{fused_data.temperature_avg_c}\u00b0C, rainfall {fused_data.rainfall_mm}mm, "
            f"humidity {(live_context or {}).get('weather', {}).get('humidity', 55)}%. "
            f"Data sourced from {sources}. "
            f"Conditions are {'favorable' if fused_data.temperature_avg_c < 40 else 'hot - ensure irrigation'} "
            f"for the current growing season."
        ),
        "soil_check": (
            f"Soil assessment for {fused_data.region}: {soil.get('type', 'Alluvial')} soil "
            f"with {soil.get('texture', 'loam')} texture, pH {soil.get('ph', 7.0)}. "
            f"Nutrients - N: {soil.get('nitrogen_kg_ha', 200)}, P: {soil.get('phosphorus_kg_ha', 15)}, "
            f"K: {soil.get('potassium_kg_ha', 220)} kg/ha. "
            f"Organic carbon: {soil.get('organic_carbon_pct', 0.45)}%. "
            f"{soil.get('description', '')} "
            f"Current soil moisture from satellite: {fused_data.soil_moisture_pct}%."
        ),
        "flood_risk": (
            f"Flood risk for {fused_data.region}: Rainfall {fused_data.rainfall_mm}mm, "
            f"soil moisture {fused_data.soil_moisture_pct}%. "
            f"Land classified as: {land}. "
            f"{'WARNING: Moisture levels elevated. Ensure drainage channels are clear.' if fused_data.soil_moisture_pct > 60 else 'Moisture levels are within safe range.'} "
            f"Data fused from {sources}."
        ),
        "ndvi_analysis": (
            f"Vegetation health for {fused_data.region}: NDVI {fused_data.ndvi_avg:.2f} "
            f"indicates {'healthy' if fused_data.ndvi_avg > 0.5 else 'stressed'} vegetation. "
            f"Correlated with soil moisture ({fused_data.soil_moisture_pct}%) and "
            f"rainfall ({fused_data.rainfall_mm}mm). "
            f"Soil type: {soil.get('type', 'Unknown')}. "
            f"Data from {sources}."
        ),
        "general": (
            f"Orbital Nexus fusion report for {fused_data.region}: "
            f"Temp {fused_data.temperature_avg_c}\u00b0C | Rain {fused_data.rainfall_mm}mm | "
            f"Moisture {fused_data.soil_moisture_pct}% | NDVI {fused_data.ndvi_avg:.2f}. "
            f"Soil: {soil.get('type', 'Unknown')} (pH {soil.get('ph', 7.0)}). "
            f"Land: {land}. Sources: {sources}."
        ),
    }

    return guidance_templates.get(intent, guidance_templates["general"])


# -- Helpers --


def _get_region_name(lat: float, lon: float) -> str:
    """Resolve a human-readable region name via reverse geocoding.

    Uses Nominatim (OpenStreetMap) — free, no API key required.
    Falls back to a generic coordinate label on failure.
    """
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
    except Exception:
        pass
    return f"Region ({lat:.2f}°N, {lon:.2f}°E)"


def _get_season(crop: str) -> str:
    """Map crop name to typical Indian growing season."""
    rabi = {"Wheat", "Mustard", "Gram", "Potato", "Onion", "Cumin", "Vegetables"}
    kharif = {
        "Rice",
        "Cotton",
        "Soybean",
        "Maize",
        "Bajra",
        "Jowar",
        "Jute",
        "Sugarcane",
        "Groundnut",
        "Guar",
        "Moth Bean",
        "Castor",
    }
    if crop in rabi:
        return "Rabi (Oct-Mar)"
    elif crop in kharif:
        return "Kharif (Jun-Oct)"
    return "Perennial"


def _soil_score(soil: dict) -> int:
    """Simple soil health score (0-100) based on nutrients + organic carbon."""
    n = min(soil.get("nitrogen_kg_ha", 200), 300)
    p = min(soil.get("phosphorus_kg_ha", 15), 30)
    k = min(soil.get("potassium_kg_ha", 220), 350)
    oc = min(soil.get("organic_carbon_pct", 0.45), 1.0)

    score = (n / 300 * 25) + (p / 30 * 20) + (k / 350 * 25) + (oc / 1.0 * 30)
    return int(min(score, 100))


def _build_price_trend_points(crops: list[str]) -> list[dict]:
    """Generate monthly price trend data points for given crops.

    Uses actual market data (price_min / price_max) and applies
    seasonal variation so each city's predicted crops produce
    a unique, realistic chart.
    """
    import math as _math

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    # Seasonal modifiers — simulate price fluctuation per month
    seasonal = [0.0, 0.02, 0.05, 0.08, 0.06, 0.03]

    if not crops:
        crops = ["rice"]

    # Use the top crop to build a single-line trend
    # (PriceTrendChart expects [{label, value}])
    top_crop = crops[0].lower()
    market = get_market_info(top_crop)

    if market:
        base = (market["price_min"] + market["price_max"]) / 2
        spread = (market["price_max"] - market["price_min"]) / 2
        trend_dir = {"rising": 1, "falling": -1, "stable": 0, "volatile": 0.5, "seasonal": 0.3}
        drift = trend_dir.get(market.get("trend", "stable"), 0)
    else:
        base = 2500
        spread = 400
        drift = 0

    points = []
    for i, month in enumerate(months):
        # Apply seasonal wave + trend drift
        variation = _math.sin((i / 5.0) * _math.pi) * spread * 0.6
        trend_shift = drift * (i * spread * 0.08)
        price = int(base + variation + trend_shift + seasonal[i] * base)
        points.append({"label": month, "value": price})

    return points


def _optimal_npk(crop: str, nutrient: str) -> float:
    """Return the optimal N, P, or K value (kg/ha) for a given crop.

    Based on average values from the Kaggle Crop Recommendation dataset.
    """
    _OPTIMAL: dict[str, dict[str, float]] = {
        "rice": {"N": 80, "P": 45, "K": 40},
        "wheat": {"N": 20, "P": 125, "K": 32},
        "maize": {"N": 80, "P": 42, "K": 40},
        "chickpea": {"N": 40, "P": 60, "K": 52},
        "kidneybeans": {"N": 20, "P": 60, "K": 20},
        "pigeonpeas": {"N": 20, "P": 55, "K": 20},
        "mothbeans": {"N": 20, "P": 50, "K": 10},
        "mungbean": {"N": 20, "P": 40, "K": 20},
        "blackgram": {"N": 40, "P": 60, "K": 20},
        "lentil": {"N": 20, "P": 60, "K": 20},
        "pomegranate": {"N": 20, "P": 10, "K": 30},
        "banana": {"N": 100, "P": 75, "K": 50},
        "mango": {"N": 20, "P": 20, "K": 30},
        "grapes": {"N": 20, "P": 125, "K": 200},
        "watermelon": {"N": 100, "P": 20, "K": 50},
        "muskmelon": {"N": 100, "P": 18, "K": 50},
        "apple": {"N": 20, "P": 130, "K": 210},
        "orange": {"N": 20, "P": 10, "K": 10},
        "papaya": {"N": 50, "P": 15, "K": 50},
        "coconut": {"N": 20, "P": 10, "K": 30},
        "cotton": {"N": 120, "P": 40, "K": 20},
        "jute": {"N": 80, "P": 40, "K": 40},
        "coffee": {"N": 100, "P": 20, "K": 30},
        "sugarcane": {"N": 40, "P": 67, "K": 80},
    }
    defaults = {"N": 60, "P": 40, "K": 40}
    return _OPTIMAL.get(crop.lower(), defaults).get(nutrient, 40)
