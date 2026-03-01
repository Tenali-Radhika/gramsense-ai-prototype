from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models import Location, Forecast
from ..forecasting.engine import generate_price_forecast

router = APIRouter()


@router.get("/forecast", response_model=Forecast)
def get_forecast(crop: str, lat: float, lon: float, horizon: Optional[int] = 30):
    loc = Location(latitude=lat, longitude=lon)
    try:
        fc = generate_price_forecast(crop, loc, horizon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return fc
