from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models import Location, PriceData
from ..data_ingestion.mandi import fetch_mandi_prices

router = APIRouter()


@router.get("/prices", response_model=List[PriceData])
def get_prices(crop: str, lat: float, lon: float, days: Optional[int] = 1):
    """Return mandi prices for a crop at a specific latitude/longitude.

    Parameters:
    - crop: Crop name (wheat, rice, maize, cotton)
    - lat, lon: Location coordinates
    - days: Number of historical days to fetch (default: 1 for current)
    """
    loc = Location(latitude=lat, longitude=lon)
    try:
        data = fetch_mandi_prices(crop, loc, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return data


@router.get("/prices/current", response_model=PriceData)
def get_current_price(crop: str, lat: float, lon: float):
    """Return the most recent mandi price for a crop at a location."""
    loc = Location(latitude=lat, longitude=lon)
    try:
        data = fetch_mandi_prices(crop, loc, 1)
        return data[0] if data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
