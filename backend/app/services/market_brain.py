"""
Market Brain Service - Fetches daily mandi prices and analyzes crop demand using Gemini AI.

This service queries real mandi data from data.gov.in (AGMARKNET) and uses Gemini AI to identify
highest-demand commodities based on current & upcoming 4-month geological & geopolitical circumstances.

Data Source: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
API: Free, Government of India Open Data Portal (no key required for basic access)
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

import httpx

logger = logging.getLogger(__name__)

# data.gov.in AGMARKNET API — Current Daily Price of Various Commodities
_AGMARKNET_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
_AGMARKNET_API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"  # Public default key
_AGMARKNET_URL = "https://api.data.gov.in/resource/" + _AGMARKNET_RESOURCE_ID
_TIMEOUT = httpx.Timeout(connect=3.0, read=6.0, write=3.0, pool=3.0)

# Simple in-memory cache (replace with Redis in production)
_market_cache: Dict[str, tuple[Any, datetime]] = {}
CACHE_TTL_HOURS = 6

# ── State mapping: lat/lon → Indian state ──────────────────────────
# Approximate bounding boxes for Indian states (lat_min, lat_max, lon_min, lon_max)
_STATE_BOXES: List[tuple[str, float, float, float, float]] = [
    ("Andhra Pradesh",     12.5, 19.1, 76.7, 84.8),
    ("Assam",              24.0, 28.0, 89.5, 96.0),
    ("Bihar",              24.0, 27.5, 83.3, 88.2),
    ("Chhattisgarh",       17.8, 24.1, 80.2, 84.4),
    ("Delhi",              28.4, 28.9, 76.8, 77.4),
    ("Goa",                14.9, 15.8, 73.6, 74.3),
    ("Gujarat",            20.0, 24.7, 68.1, 74.5),
    ("Haryana",            27.6, 30.9, 74.5, 77.6),
    ("Himachal Pradesh",   30.4, 33.3, 75.5, 79.0),
    ("Jharkhand",          21.9, 25.3, 83.3, 87.9),
    ("Karnataka",          11.6, 18.5, 74.0, 78.6),
    ("Kerala",              8.2, 12.8, 74.8, 77.4),
    ("Madhya Pradesh",     21.1, 26.9, 74.0, 82.8),
    ("Maharashtra",        15.6, 22.0, 72.6, 80.9),
    ("Odisha",             17.8, 22.6, 81.3, 87.5),
    ("Punjab",             29.5, 32.5, 73.8, 76.9),
    ("Rajasthan",          23.0, 30.2, 69.5, 78.3),
    ("Tamil Nadu",          8.0, 13.6, 76.2, 80.4),
    ("Telangana",          15.8, 19.9, 77.2, 81.3),
    ("Uttar Pradesh",      23.5, 30.4, 77.1, 84.7),
    ("Uttarakhand",        28.7, 31.5, 77.5, 81.1),
    ("West Bengal",        21.5, 27.2, 86.0, 89.9),
]


def _get_state_for_coords(lat: float, lon: float) -> Optional[str]:
    """Map lat/lon to an Indian state name using bounding boxes."""
    best_state = None
    best_dist = float("inf")
    for state, lat_min, lat_max, lon_min, lon_max in _STATE_BOXES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            # Inside the box — pick the one whose center is closest
            center_lat = (lat_min + lat_max) / 2
            center_lon = (lon_min + lon_max) / 2
            dist = (lat - center_lat) ** 2 + (lon - center_lon) ** 2
            if dist < best_dist:
                best_dist = dist
                best_state = state
    return best_state


def _extract_state_district(region: str) -> tuple[Optional[str], Optional[str]]:
    """Extract state and district/city from a region string like 'Sultanpur, Uttar Pradesh'."""
    parts = [p.strip() for p in region.split(",")]
    if len(parts) >= 2:
        district = parts[0].replace("Near ", "")
        state = parts[-1]
        return state, district
    if len(parts) == 1:
        return parts[0], None
    return None, None


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    """Get cached market data if not expired."""
    if key in _market_cache:
        data, timestamp = _market_cache[key]
        if datetime.now() - timestamp < timedelta(hours=CACHE_TTL_HOURS):
            logger.info(f"Cache hit for {key}")
            return data
        else:
            del _market_cache[key]
    return None


def _set_cached(key: str, data: Dict[str, Any]):
    """Cache market data with timestamp."""
    _market_cache[key] = (data, datetime.now())


def _fetch_mandi_data(region: str, lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Fetch LIVE mandi price data from data.gov.in AGMARKNET API.

    Strategy:
      1. Extract state + district from region name
      2. Try district-level query first (most specific)
      3. Fall back to state-level query
      4. Fall back to lat/lon → state mapping
      5. Final fallback: demo data with regional variation

    API: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Parse state and district from region
    state, district = _extract_state_district(region)

    # Step 2: Try state from coordinates if not found in region string
    if not state or not any(state.lower() in s.lower() for s, *_ in _STATE_BOXES):
        geo_state = _get_state_for_coords(lat, lon)
        if geo_state:
            state = geo_state

    if not state:
        logger.warning("Cannot determine state for (%s, %.2f, %.2f) — using demo data", region, lat, lon)
        return _demo_mandi_data(region, lat, lon)

    # Step 3: Try fetching from AGMARKNET
    records = _query_agmarknet(state, district)

    if not records:
        logger.info("No AGMARKNET data for district=%s — trying state-level", district)
        records = _query_agmarknet(state, None)

    if not records:
        logger.warning("AGMARKNET returned no data for state=%s — using demo data", state)
        return _demo_mandi_data(region, lat, lon)

    # Step 4: Convert API records to our snapshot format
    snapshot = []
    seen_commodities: set[str] = set()
    for rec in records:
        commodity = rec.get("commodity", "Unknown")
        if commodity in seen_commodities:
            continue
        seen_commodities.add(commodity)

        market_name = rec.get("market", district or state)
        modal = _safe_float(rec.get("modal_price"), 0)
        min_price = _safe_float(rec.get("min_price"), 0)
        max_price = _safe_float(rec.get("max_price"), 0)

        if modal <= 0:
            continue

        snapshot.append({
            "mandi": market_name,
            "commodity": commodity,
            "modal_price": int(modal),
            "price_min": int(min_price),
            "price_max": int(max_price),
            "arrivals_ton": 0,  # not in this API
            "date": rec.get("arrival_date", today),
            "district": rec.get("district", ""),
            "state": rec.get("state", state),
            "variety": rec.get("variety", ""),
        })

    if not snapshot:
        return _demo_mandi_data(region, lat, lon)

    logger.info(
        "AGMARKNET: %d commodities from %s, %s (district=%s)",
        len(snapshot), state, region, district
    )
    return snapshot[:20]  # Cap at 20


def _query_agmarknet(state: str, district: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query data.gov.in AGMARKNET API for mandi prices."""
    params: Dict[str, Any] = {
        "api-key": _AGMARKNET_API_KEY,
        "format": "json",
        "limit": 30,
        "filters[state.keyword]": state,
    }
    if district:
        params["filters[district.keyword]"] = district

    try:
        resp = httpx.get(_AGMARKNET_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        total = data.get("total", 0)
        logger.info("AGMARKNET query: state=%s district=%s → %d/%d records", state, district, len(records), total)
        return records
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        logger.warning("AGMARKNET API failed (%s)", exc)
        return []
    except Exception as exc:
        logger.warning("AGMARKNET parse error (%s)", exc)
        return []


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def _demo_mandi_data(region: str, lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Fallback demo data with regional variation.
    Used when AGMARKNET is unreachable or returns no results.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Demo data with regional variation
    base_commodities = [
        {"commodity": "Wheat", "base_price": 2100, "arrivals": 30},
        {"commodity": "Rice", "base_price": 2800, "arrivals": 25},
        {"commodity": "Cotton", "base_price": 5200, "arrivals": 12},
        {"commodity": "Soybean", "base_price": 4100, "arrivals": 18},
        {"commodity": "Sugarcane", "base_price": 280, "arrivals": 45},
        {"commodity": "Onion", "base_price": 1500, "arrivals": 8},
        {"commodity": "Potato", "base_price": 900, "arrivals": 35},
        {"commodity": "Tomato", "base_price": 1200, "arrivals": 6},
    ]
    
    snapshot = []
    for item in base_commodities:
        # Add regional price variation
        price_var = hash(f"{region}{item['commodity']}") % 400 - 200
        arrival_var = hash(f"{lat}{lon}{item['commodity']}") % 10 - 5
        
        modal_price = max(100, item["base_price"] + price_var)
        arrivals = max(1, item["arrivals"] + arrival_var)
        
        snapshot.append({
            "mandi": f"{region} Mandi",
            "commodity": item["commodity"],
            "modal_price": modal_price,
            "price_min": int(modal_price * 0.95),
            "price_max": int(modal_price * 1.05),
            "arrivals_ton": arrivals,
            "date": today
        })
    
    logger.info(f"Fetched {len(snapshot)} commodity prices for {region}")
    return snapshot


def _calculate_heuristic_score(commodity_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fallback heuristic scoring when Gemini is unavailable.
    
    Score factors:
    - High price = higher demand
    - Low arrivals = scarcity = higher demand
    - Normalize to 0-100 scale
    """
    results = []
    
    for item in commodity_data:
        modal = item.get("modal_price", 1000)
        arrivals = item.get("arrivals_ton", 20)
        
        # Price component (0-60 points): higher price = higher score
        price_score = min(60, (modal / 100))
        
        # Scarcity component (0-40 points): lower arrivals = higher score
        scarcity_score = max(0, 40 - arrivals)
        
        total_score = min(100, price_score + scarcity_score)
        
        # Determine trend based on score
        if total_score >= 70:
            trend = "rising"
        elif total_score <= 40:
            trend = "falling"
        else:
            trend = "stable"
        
        results.append({
            "name": item["commodity"],
            "demand_score": round(total_score, 1),
            "demand_trend": trend,
            "confidence": "low",
            "reasoning": f"Heuristic: ₹{modal}/quintal, {arrivals}t arrivals"
        })
    
    # Sort by demand score descending
    results.sort(key=lambda x: x["demand_score"], reverse=True)
    return results


async def get_market_brain(lat: float, lon: float, region: str) -> Dict[str, Any]:
    """
    Main entry point: Fetch mandi data and analyze demand using Gemini AI.
    
    Returns Market Crop Brain payload for UI display.
    """
    cache_key = f"market_brain:{region}:{round(lat, 2)}:{round(lon, 2)}"
    
    # Check cache first
    cached = _get_cached(cache_key)
    if cached:
        return cached
    
    today = datetime.now().strftime("%Y-%m-%d")
    snapshot = _fetch_mandi_data(region, lat, lon)
    
    # Try Gemini analysis first
    from app.ai.gemini_service import generate_gemini_market_analysis, is_ai_available
    
    top_commodities = []
    source = "Fallback"
    notes = []
    
    if is_ai_available():
        try:
            # Build Gemini prompt
            commodity_list = ", ".join(sorted({s["commodity"] for s in snapshot}))
            snapshot_sample = snapshot[:6]
            
            prompt = (
                f"Region: {region} (lat={lat:.2f}, lon={lon:.2f})\n"
                f"Available commodities: {commodity_list}\n"
                f"Mandi snapshot: {json.dumps(snapshot_sample, indent=2)}\n\n"
                "According to current & upcoming 4 months' geological & geopolitical circumstances, "
                "which crop will give better profit to the farmer?\n\n"
                "Return JSON array of top 5 recommendations with this exact structure:\n"
                '[{"name": "Wheat", "demand_score": 85, "demand_trend": "rising", '
                '"confidence": "high", "reasoning": "one-line explanation"}]'
            )
            
            gemini_result = await generate_gemini_market_analysis(prompt, region, lat, lon)
            
            if gemini_result and isinstance(gemini_result, list) and len(gemini_result) > 0:
                top_commodities = gemini_result[:10]
                source = "Gemini AI"
                logger.info(f"Gemini market analysis successful for {region}")
            else:
                raise ValueError("Invalid Gemini response format")
                
        except Exception as e:
            logger.warning(f"Gemini market analysis failed: {e}. Using fallback.")
            notes.append(f"Gemini analysis unavailable: {str(e)}")
            top_commodities = _calculate_heuristic_score(snapshot)
    else:
        logger.info("Gemini unavailable, using heuristic fallback")
        notes.append("GEMINI_API_KEY not set - using heuristic scoring")
        top_commodities = _calculate_heuristic_score(snapshot)
    
    # Detect whether snapshot came from live API or demo
    is_live = any(r.get("state") or r.get("district") for r in snapshot)
    mandi_source = "AGMARKNET (Live)" if is_live else "Agmarknet (Demo)"
    
    # Build response
    result = {
        "date": today,
        "region": region,
        "lat": lat,
        "lon": lon,
        "sources": [mandi_source, source],
        "snapshot": snapshot,
        "top_commodities": top_commodities,
        "top_demanded": [c["name"] for c in top_commodities],
        "source": source,
        "generated_at": datetime.now().isoformat(),
        "notes": " | ".join(notes) if notes else "Live market analysis"
    }
    
    # Cache the result
    _set_cached(cache_key, result)
    
    return result
