from typing import List
from datetime import datetime

from ..models import PriceData, Location


# Placeholder implementation: in a real system this would fetch from Agmarknet or cache

def fetch_mandi_prices(crop: str, location: Location) -> List[PriceData]:
    """Retrieve current mandi prices for a given crop and location.

    This stub returns synthetic data for demonstration and testing.
    """
    now = datetime.utcnow()
    dummy = PriceData(
        crop=crop,
        market="Example Market",
        location=location,
        price=100.0,
        unit="kg",
        timestamp=now,
        source="synthetic",
        quality="A",
    )
    return [dummy]


def fetch_weather_data(location: Location, date_range: tuple) -> List[dict]:
    # stub
    return []


def fetch_crop_calendar(crop: str, region: str) -> dict:
    # stub
    return {}
