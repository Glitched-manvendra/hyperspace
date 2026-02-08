"""
API Routes - Orbital Nexus

Defines all HTTP endpoints. Keeps route logic thin;
delegates to services and AI modules.

Powered by the Orbital Fusion Engine:
  - Open-Meteo (live weather)
  - ISRO Bhuvan (land classification)
  - SISIndia / Soil Database (soil nutrients)
  - Gemini AI (demand-driven crop prediction)
  - Market Brain (mandi price intelligence)
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import UserQuery, QueryResponse, NDVIResponse
from app.ai.intent import parse_intent, extract_location, extract_locations
from app.ai.gemini_service import (
    generate_ai_guidance,
    generate_gemini_crop_recommendation,
    is_ai_available,
    _get_seasonal_fallback,
)
from app.services.fusion import get_fused_data, build_ui_instructions, generate_guidance
from app.services.data_fusion import get_location_context
from app.services.market_trends import get_market_info
from app.services.ndvi_service import fetch_ndvi_stats, NDVIError

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def process_query(payload: UserQuery) -> QueryResponse:
    """
    Process a natural language query about satellite data.

    Flow:
    1. Parse user intent from the query text
    2. Fetch LIVE location context (Open-Meteo + Bhuvan + Soil + Market Brain)
    3. Get Gemini AI crop recommendation (rising-demand, profit-optimised)
    4. Build fused data summary from live context
    5. Generate guidance text and UI instructions
    6. Return structured response for the frontend
    """

    # Step 1: Determine what the user is asking about
    intent = parse_intent(payload.query)

    # Step 1b: Extract location from query text (overrides default coords)
    extracted = extract_location(payload.query)
    lat = extracted[0] if extracted else payload.lat
    lon = extracted[1] if extracted else payload.lon

    # Step 2: Fetch real data from fusion engine
    live_context = await get_location_context(lat, lon)

    # Step 3: Get crop recommendations (Gemini AI only — no local ML)
    # Priority: Gemini AI (demand-driven) → Seasonal fallback
    weather = live_context["weather"]
    soil = live_context.get("soil", {})
    region = live_context.get("region", "Unknown")

    # Get mandi snapshot from market brain for Gemini context
    market_brain = live_context.get("market_brain", {})
    mandi_snapshot = market_brain.get("snapshot") if market_brain else None

    # 3a: Gemini AI — demand-driven, rising-demand crops only
    gemini_crops = await generate_gemini_crop_recommendation(
        region=region, soil=soil, weather=weather,
        lat=lat, lon=lon, mandi_snapshot=mandi_snapshot,
    )

    if gemini_crops:
        crop_prediction = gemini_crops
        live_context["crop_source"] = "Gemini AI (Rising Demand)"
    else:
        # 3b: Seasonal fallback (deterministic, no KNN)
        crop_prediction = _get_seasonal_fallback(region, soil)
        live_context["crop_source"] = "Seasonal Fallback"

    # Attach market data to each predicted crop
    for pred in crop_prediction:
        market = get_market_info(pred["crop"])
        if market:
            pred["market"] = market

    # Inject crop prediction into live_context for downstream use
    live_context["crop_prediction"] = crop_prediction

    # Step 4: Build fused data summary using live weather
    fused_data = get_fused_data(
        lat,
        lon,
        live_weather=weather,
        region_name=live_context["region"],
        data_sources=live_context["data_sources"],
        live_context=live_context,
    )

    # Step 5: Build dashboard card instructions for the frontend
    ui_instructions = build_ui_instructions(intent, fused_data, live_context)

    # Step 6: Generate AI-powered guidance (Gemini) with template fallback
    fused_dict = fused_data.model_dump()
    ai_text = await generate_ai_guidance(
        payload.query, intent, fused_dict, live_context
    )
    guidance_text = ai_text or generate_guidance(
        intent, fused_data, payload.query, live_context
    )
    ai_powered = ai_text is not None

    return QueryResponse(
        intent=intent,
        query_echo=payload.query,
        fused_data=fused_data,
        guidance_text=guidance_text,
        ai_powered=ai_powered,
        recommendations=[],
        ui_instructions=ui_instructions,
    )


@router.post("/multi-query")
async def process_multi_query(payload: UserQuery):
    """
    Process a query that may reference multiple locations.

    Returns an array of QueryResponse objects — one per location found.
    Falls back to the standard single-location flow if only one (or zero) locations.
    """
    locations = extract_locations(payload.query)

    # Fall back to single-location if 0 or 1 location found
    if len(locations) <= 1:
        single = await process_query(payload)
        return [single]

    import asyncio

    async def _process_one(loc: dict) -> QueryResponse:
        lat, lon, name = loc["lat"], loc["lon"], loc["name"]
        intent = parse_intent(payload.query)
        live_context = await get_location_context(lat, lon)

        weather = live_context["weather"]
        soil = live_context.get("soil", {})

        # Gemini AI (demand-driven) → seasonal fallback (no KNN)
        market_brain = live_context.get("market_brain", {})
        mandi_snapshot = market_brain.get("snapshot") if market_brain else None

        gemini_crops = await generate_gemini_crop_recommendation(
            region=name, soil=soil, weather=weather,
            lat=lat, lon=lon, mandi_snapshot=mandi_snapshot,
        )
        if gemini_crops:
            crop_prediction = gemini_crops
            live_context["crop_source"] = "Gemini AI (Rising Demand)"
        else:
            crop_prediction = _get_seasonal_fallback(name, soil)
            live_context["crop_source"] = "Seasonal Fallback"

        for pred in crop_prediction:
            market = get_market_info(pred["crop"])
            if market:
                pred["market"] = market

        live_context["crop_prediction"] = crop_prediction

        fused_data = get_fused_data(
            lat, lon,
            live_weather=weather,
            region_name=name,
            data_sources=live_context["data_sources"],
            live_context=live_context,
        )

        ui_instructions = build_ui_instructions(intent, fused_data, live_context)
        guidance_text = generate_guidance(intent, fused_data, payload.query, live_context)

        return QueryResponse(
            intent=intent,
            query_echo=payload.query,
            fused_data=fused_data,
            guidance_text=guidance_text,
            ai_powered=False,
            recommendations=[],
            ui_instructions=ui_instructions,
        )

    tasks = [_process_one(loc) for loc in locations]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions, return successful results
    return [
        r for r in results
        if not isinstance(r, Exception)
    ]


@router.get("/context/{lat}/{lon}")
async def get_context(lat: float, lon: float):
    """Debug endpoint - raw fusion context for a coordinate pair."""
    return await get_location_context(lat, lon)


@router.get("/ndvi/{poly_id}", response_model=NDVIResponse, tags=["ndvi"])
async def get_ndvi(poly_id: str):
    """Fetch latest NDVI statistics for an AgroMonitoring polygon."""
    try:
        result = await fetch_ndvi_stats(poly_id)
        return NDVIResponse(**result)
    except NDVIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"NDVI fetch failed: {exc}")
