from typing import List, Dict
from datetime import datetime, timezone, timedelta
import random
import math

from ..models import PriceData, Location
from .cache import cached, price_cache


# Crop base prices (INR per kg) and seasonal patterns
CROP_DATA = {
    "wheat": {"base_price": 2500, "volatility": 0.15, "seasonal_peak": 4},  # April
    "rice": {"base_price": 3000, "volatility": 0.12, "seasonal_peak": 11},  # November
    "cotton": {"base_price": 6000, "volatility": 0.20, "seasonal_peak": 12},  # December
    "sugarcane": {"base_price": 300, "volatility": 0.10, "seasonal_peak": 1},  # January
    "potato": {"base_price": 2000, "volatility": 0.25, "seasonal_peak": 2},  # February
    "onion": {"base_price": 2500, "volatility": 0.30, "seasonal_peak": 3},  # March
    "tomato": {"base_price": 3000, "volatility": 0.35, "seasonal_peak": 6},  # June
    "soybean": {"base_price": 4500, "volatility": 0.18, "seasonal_peak": 10},  # October
    "maize": {"base_price": 2000, "volatility": 0.16, "seasonal_peak": 9},  # September
    "groundnut": {"base_price": 5500, "volatility": 0.17, "seasonal_peak": 11},  # November
}

# Regional market multipliers
REGIONAL_MULTIPLIERS = {
    "Delhi": 1.15,
    "Mumbai": 1.20,
    "Bangalore": 1.10,
    "Kolkata": 1.05,
    "Chennai": 1.08,
    "Hyderabad": 1.06,
    "Pune": 1.12,
    "Ahmedabad": 1.07,
    "Jaipur": 1.03,
    "Lucknow": 1.04,
}


def _get_seasonal_factor(month: int, peak_month: int) -> float:
    """Calculate seasonal price factor based on distance from peak month."""
    distance = min(abs(month - peak_month), 12 - abs(month - peak_month))
    # Prices are highest at peak, lowest 6 months away
    return 1.0 + (0.3 * (1 - distance / 6))


def _get_trend_factor(days_ago: int, trend_direction: float = 0.0) -> float:
    """Calculate price trend over time (slight upward/downward drift)."""
    return 1.0 + (trend_direction * days_ago / 365)


def generate_synthetic_price(
    crop: str,
    location: Location,
    date: datetime,
    seed: int = None
) -> float:
    """Generate realistic synthetic price for a crop at a specific date."""
    if seed is not None:
        random.seed(seed)
    
    crop_lower = crop.lower()
    if crop_lower not in CROP_DATA:
        # Default for unknown crops
        base_price = 2000
        volatility = 0.20
        seasonal_peak = 6
    else:
        crop_info = CROP_DATA[crop_lower]
        base_price = crop_info["base_price"]
        volatility = crop_info["volatility"]
        seasonal_peak = crop_info["seasonal_peak"]
    
    # Apply seasonal factor
    seasonal_factor = _get_seasonal_factor(date.month, seasonal_peak)
    
    # Apply regional multiplier
    region_name = location.name or "Delhi"
    regional_multiplier = REGIONAL_MULTIPLIERS.get(region_name, 1.0)
    
    # Apply random daily variation
    daily_variation = random.gauss(0, volatility)
    
    # Calculate final price
    price = base_price * seasonal_factor * regional_multiplier * (1 + daily_variation)
    
    # Ensure price stays positive and reasonable
    price = max(price, base_price * 0.5)
    
    return round(price, 2)


# Placeholder implementation: in a real system this would fetch from Agmarknet or cache

@cached(price_cache, ttl=300)  # Cache for 5 minutes
def fetch_mandi_prices(crop: str, location: Location, days_back: int = 0) -> List[PriceData]:
    """Retrieve mandi prices for a given crop and location.

    Args:
        crop: Crop name
        location: Location object
        days_back: Number of days of historical data (0 for current only)

    This returns synthetic data with realistic variations based on:
    - Crop-specific base prices
    - Seasonal patterns
    - Regional market differences
    - Daily volatility
    """
    now = datetime.now(timezone.utc)
    prices = []
    
    # Use location as seed for consistency
    seed_base = hash(f"{crop}{location.name}") % 10000

    for i in range(days_back + 1):
        date = now - timedelta(days=i)
        
        # Generate realistic price
        price = generate_synthetic_price(crop, location, date, seed=seed_base + i)
        
        # Determine market name based on location
        market_name = f"{location.name or 'Regional'} Mandi"
        
        # Quality varies slightly
        qualities = ["A", "A", "A", "B", "B", "C"]  # Weighted toward A
        quality = random.choice(qualities)

        price_data = PriceData(
            crop=crop,
            market=market_name,
            location=location,
            price=price,
            unit="quintal",  # Standard Indian agricultural unit
            timestamp=date,
            source="synthetic",
            quality=quality,
        )
        prices.append(price_data)

    return prices


@cached(price_cache, ttl=600)  # Cache for 10 minutes
def fetch_historical_prices(crop: str, location: Location, days: int = 30) -> List[PriceData]:
    """Fetch historical price data for analysis."""
    return fetch_mandi_prices(crop, location, days_back=days)


def fetch_weather_data(location: Location, date_range: tuple) -> List[dict]:
    # stub
    return []


def fetch_crop_calendar(crop: str, region: str) -> dict:
    # stub
    return {}
