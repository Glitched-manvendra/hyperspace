"""
Market Trends — Static crop price & forecast data

Provides market intelligence for Indian crops: current price ranges,
seasonal trends, and short-term forecasts. Used alongside CropEngine
predictions to give farmers actionable economic context.

Prices in INR per quintal (100 kg) — sourced from typical MSP/mandi rates.
"""

from typing import Any

# ── Crop market data ──────────────────────────────────────────────
MARKET_TRENDS: dict[str, dict[str, Any]] = {
    "rice": {
        "price_min": 2040,
        "price_max": 2600,
        "msp": 2203,
        "trend": "stable",
        "forecast": "Prices expected to remain stable with slight uptick post-harvest.",
        "season": "Kharif (Jun–Oct)",
    },
    "wheat": {
        "price_min": 2125,
        "price_max": 2800,
        "msp": 2275,
        "trend": "rising",
        "forecast": "Government procurement strong. Mandi prices trending above MSP.",
        "season": "Rabi (Oct–Mar)",
    },
    "maize": {
        "price_min": 1962,
        "price_max": 2400,
        "msp": 2090,
        "trend": "stable",
        "forecast": "Demand from feed industry steady. Export potential increasing.",
        "season": "Kharif (Jun–Oct)",
    },
    "chickpea": {
        "price_min": 5335,
        "price_max": 6800,
        "msp": 5440,
        "trend": "rising",
        "forecast": "Strong demand for pulses. Import duty keeping domestic prices up.",
        "season": "Rabi (Oct–Mar)",
    },
    "kidneybeans": {
        "price_min": 6000,
        "price_max": 8500,
        "msp": 6600,
        "trend": "rising",
        "forecast": "Premium market. Export demand growing steadily.",
        "season": "Kharif (Jun–Oct)",
    },
    "pigeonpeas": {
        "price_min": 6600,
        "price_max": 8200,
        "msp": 7000,
        "trend": "stable",
        "forecast": "Government buffer stock purchases supporting prices.",
        "season": "Kharif (Jun–Oct)",
    },
    "mothbeans": {
        "price_min": 7275,
        "price_max": 8500,
        "msp": 7275,
        "trend": "stable",
        "forecast": "Niche market. Prices stable with limited volatility.",
        "season": "Kharif (Jun–Oct)",
    },
    "mungbean": {
        "price_min": 7755,
        "price_max": 9200,
        "msp": 8558,
        "trend": "rising",
        "forecast": "High domestic consumption. Sprout market expanding.",
        "season": "Kharif (Jun–Oct)",
    },
    "blackgram": {
        "price_min": 6600,
        "price_max": 8400,
        "msp": 6950,
        "trend": "stable",
        "forecast": "Steady demand. Good market availability.",
        "season": "Kharif (Jun–Oct)",
    },
    "lentil": {
        "price_min": 5500,
        "price_max": 7200,
        "msp": 6425,
        "trend": "rising",
        "forecast": "Import dependency reducing. Domestic prices strengthening.",
        "season": "Rabi (Oct–Mar)",
    },
    "pomegranate": {
        "price_min": 4000,
        "price_max": 12000,
        "msp": None,
        "trend": "volatile",
        "forecast": "Premium fruit. Season-dependent with high export value.",
        "season": "Perennial",
    },
    "banana": {
        "price_min": 800,
        "price_max": 2500,
        "msp": None,
        "trend": "stable",
        "forecast": "Year-round production. Steady local demand.",
        "season": "Perennial",
    },
    "mango": {
        "price_min": 3000,
        "price_max": 10000,
        "msp": None,
        "trend": "seasonal",
        "forecast": "Peak prices during off-season. Export quality commands premium.",
        "season": "Perennial (harvest Apr–Jul)",
    },
    "grapes": {
        "price_min": 3000,
        "price_max": 8000,
        "msp": None,
        "trend": "rising",
        "forecast": "Wine industry growth driving demand. Export market expanding.",
        "season": "Perennial (harvest Feb–Apr)",
    },
    "watermelon": {
        "price_min": 500,
        "price_max": 2000,
        "msp": None,
        "trend": "seasonal",
        "forecast": "Summer peak demand. Transport logistics key to pricing.",
        "season": "Summer (Mar–Jun)",
    },
    "muskmelon": {
        "price_min": 800,
        "price_max": 3000,
        "msp": None,
        "trend": "seasonal",
        "forecast": "Premium pricing in urban markets. Short season window.",
        "season": "Summer (Mar–Jun)",
    },
    "apple": {
        "price_min": 5000,
        "price_max": 15000,
        "msp": None,
        "trend": "stable",
        "forecast": "Kashmir/HP production steady. Cold storage availability improving.",
        "season": "Perennial (harvest Aug–Nov)",
    },
    "orange": {
        "price_min": 2000,
        "price_max": 5000,
        "msp": None,
        "trend": "stable",
        "forecast": "Nagpur oranges dominant. Juice industry creating new demand.",
        "season": "Perennial (harvest Nov–Mar)",
    },
    "papaya": {
        "price_min": 1000,
        "price_max": 3000,
        "msp": None,
        "trend": "stable",
        "forecast": "Year-round availability. Processing industry expanding.",
        "season": "Perennial",
    },
    "coconut": {
        "price_min": 2500,
        "price_max": 5000,
        "msp": None,
        "trend": "rising",
        "forecast": "Coconut oil and water market booming. South India prices firm.",
        "season": "Perennial",
    },
    "cotton": {
        "price_min": 6080,
        "price_max": 8500,
        "msp": 6620,
        "trend": "volatile",
        "forecast": "Global demand fluctuations. CCI procurement stabilising prices.",
        "season": "Kharif (Jun–Oct)",
    },
    "jute": {
        "price_min": 4750,
        "price_max": 6500,
        "msp": 5050,
        "trend": "stable",
        "forecast": "Government packaging mandate supports demand. Bengal production steady.",
        "season": "Kharif (Jun–Oct)",
    },
    "coffee": {
        "price_min": 8000,
        "price_max": 16000,
        "msp": None,
        "trend": "rising",
        "forecast": "Specialty coffee boom. Indian Robusta gaining international recognition.",
        "season": "Perennial (harvest Nov–Feb)",
    },
    "sugarcane": {
        "price_min": 285,
        "price_max": 380,
        "msp": 315,
        "trend": "stable",
        "forecast": "FRP-based pricing. Ethanol blending policy driving demand.",
        "season": "Perennial (harvest Oct–Apr)",
    },
}


def get_market_info(crop: str) -> dict[str, Any] | None:
    """Look up market data for a crop label. Case-insensitive."""
    return MARKET_TRENDS.get(crop.lower())


def get_price_display(crop: str) -> str:
    """Human-readable price string for a crop."""
    info = get_market_info(crop)
    if not info:
        return "Price data unavailable"
    low = info["price_min"]
    high = info["price_max"]
    trend = info["trend"]
    arrow = {
        "rising": "↑",
        "falling": "↓",
        "stable": "→",
        "volatile": "↕",
        "seasonal": "~",
    }.get(trend, "→")
    return f"₹{low:,}–{high:,}/qtl {arrow} ({trend})"
