from fastapi import APIRouter, HTTPException
from typing import List

from ..models import Location, PriceData
from ..data_ingestion.mandi import fetch_mandi_prices

router = APIRouter()


@router.get("/prices", response_model=List[PriceData])
def get_prices(crop: str, lat: float, lon: float):
    """Return mandi prices for a crop at a specific latitude/longitude."""
    loc = Location(latitude=lat, longitude=lon)
    try:
        data = fetch_mandi_prices(crop, loc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return data
