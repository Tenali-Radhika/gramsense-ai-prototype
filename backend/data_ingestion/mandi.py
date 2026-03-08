from typing import List
from datetime import datetime, timezone, timedelta
import random

from ..models import PriceData, Location


# Placeholder implementation: in a real system this would fetch from Agmarknet or cache

def fetch_mandi_prices(crop: str, location: Location, days_back: int = 0) -> List[PriceData]:
    """Retrieve mandi prices for a given crop and location.

    Args:
        crop: Crop name
        location: Location object
        days_back: Number of days of historical data (0 for current only)

    This stub returns synthetic data for demonstration and testing.
    """
    now = datetime.now(timezone.utc)
    prices = []

    for i in range(days_back + 1):
        date = now - timedelta(days=i)
        # Simulate price variation
        base_price = 100.0
        variation = random.uniform(-20, 20)  # ±20% variation
        price = max(50, base_price + variation)

        price_data = PriceData(
            crop=crop,
            market="Example Market",
            location=location,
            price=round(price, 2),
            unit="kg",
            timestamp=date,
            source="synthetic",
            quality="A",
        )
        prices.append(price_data)

    return prices


def fetch_historical_prices(crop: str, location: Location, days: int = 30) -> List[PriceData]:
    """Fetch historical price data for analysis."""
    return fetch_mandi_prices(crop, location, days_back=days)


def fetch_weather_data(location: Location, date_range: tuple) -> List[dict]:
    # stub
    return []


def fetch_crop_calendar(crop: str, region: str) -> dict:
    # stub
    return {}
