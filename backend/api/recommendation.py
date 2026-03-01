from fastapi import APIRouter, HTTPException
from typing import List

from ..models import Location, Recommendation
from ..recommendation.engine import generate_selling_recommendation, suggest_optimal_markets, provide_crop_planning_advice

router = APIRouter()


@router.get("/recommendation", response_model=Recommendation)
def get_recommendation(crop: str, lat: float, lon: float, quantity: float):
    loc = Location(latitude=lat, longitude=lon)
    try:
        rec = generate_selling_recommendation(crop, loc, quantity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return rec


@router.get("/optimal_markets", response_model=List[str])
def get_optimal_markets(crop: str, lat: float, lon: float):
    loc = Location(latitude=lat, longitude=lon)
    return suggest_optimal_markets(crop, loc)


@router.get("/crop_advice", response_model=List[dict])
def get_crop_advice(lat: float, lon: float, season: str):
    loc = Location(latitude=lat, longitude=lon)
    return provide_crop_planning_advice(loc, season)
