"""
API Routes - Orbital Nexus

Defines all HTTP endpoints. Keeps route logic thin;
delegates to services and AI modules.

Now powered by the real Orbital Fusion Engine:
  - Open-Meteo (live weather)
  - ISRO Bhuvan (land classification)
  - Soil Database (offline nutrients)
  - CropEngine (KNN crop prediction)
  - Market Trends (price intelligence)
"""

from fastapi import APIRouter

from app.models.schemas import UserQuery, QueryResponse
from app.ai.intent import parse_intent, extract_location
from app.ai.gemini_service import generate_ai_guidance, is_ai_available
from app.services.fusion import get_fused_data, build_ui_instructions, generate_guidance
from app.services.data_fusion import get_location_context
from app.services.crop_engine import crop_engine
from app.services.market_trends import get_market_info

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def process_query(payload: UserQuery) -> QueryResponse:
    """
    Process a natural language query about satellite data.

    Flow:
    1. Parse user intent from the query text
    2. Fetch LIVE location context (Open-Meteo + Bhuvan + Soil DB)
    3. Run CropEngine prediction using fused soil + weather data
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

    # Step 3: Run CropEngine with fused environmental data
    weather = live_context["weather"]
    soil = live_context.get("soil", {})

    crop_prediction = crop_engine.predict(
        n=soil.get("nitrogen_kg_ha", 80),
        p=soil.get("phosphorus_kg_ha", 40),
        k=soil.get("potassium_kg_ha", 40),
        temperature=weather.get("temp", 28.0),
        humidity=weather.get("humidity", 65.0),
        ph=soil.get("ph", 6.5),
        rainfall=weather.get("rain", 100.0),
    )

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


@router.get("/context/{lat}/{lon}")
async def get_context(lat: float, lon: float):
    """Debug endpoint - raw fusion context for a coordinate pair."""
    return await get_location_context(lat, lon)
