from fastapi import APIRouter, HTTPException
from typing import List

from ..models import Location, Recommendation
from ..recommendation.engine import (
    generate_selling_recommendation,
    suggest_optimal_markets,
    provide_crop_planning_advice,
    get_regional_demand_insights
)

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


@router.get("/regional_demand")
def get_regional_demand(crop: str, lat: float, lon: float):
    """Get regional demand insights for a crop."""
    from ..recommendation.engine import get_regional_demand_insights
    loc = Location(latitude=lat, longitude=lon)
    return get_regional_demand_insights(crop, loc)


@router.post("/query_assistant")
def query_assistant(query: str, crop: str = None, lat: float = None, lon: float = None):
    """Simple AI query assistant for farmers."""
    from ..recommendation.engine import handle_farmer_query
    loc = Location(latitude=lat, longitude=lon) if lat and lon else None
    return handle_farmer_query(query, crop, loc)


@router.get("/demand_insights")
def get_demand_insights(crop: str, lat: float, lon: float):
    """Get regional demand insights for a crop."""
    loc = Location(latitude=lat, longitude=lon)
    return get_regional_demand_insights(crop, loc)
