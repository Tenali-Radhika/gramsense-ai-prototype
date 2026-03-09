from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel

from ..models import Location, Recommendation
from ..recommendation.engine import (
    generate_selling_recommendation,
    suggest_optimal_markets,
    provide_crop_planning_advice,
    get_regional_demand_insights,
    handle_farmer_query
)
from ..session_manager import session_manager

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    crop: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    session_id: Optional[str] = None


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
    loc = Location(latitude=lat, longitude=lon)
    return get_regional_demand_insights(crop, loc)


@router.post("/query_assistant")
def query_assistant(request: QueryRequest):
    """AI query assistant for farmers with conversation history support."""
    # Get or create session
    session_id, session = session_manager.get_or_create_session(request.session_id)
    
    # Get location
    loc = Location(latitude=request.lat, longitude=request.lon) if request.lat and request.lon else None
    location_name = loc.name if loc and hasattr(loc, 'name') else None
    
    # Add user message to history
    session_manager.add_message(
        session_id=session_id,
        role="user",
        content=request.query,
        crop=request.crop,
        location=location_name
    )
    
    # Get conversation history for context
    history = session_manager.get_conversation_history(session_id, limit=5)
    
    # Generate response
    response = handle_farmer_query(request.query, request.crop, loc)
    
    # Add assistant response to history
    session_manager.add_message(
        session_id=session_id,
        role="assistant",
        content=response.get("response", ""),
        crop=request.crop,
        location=location_name
    )
    
    # Cleanup expired sessions periodically
    session_manager.cleanup_expired_sessions()
    
    # Add session info to response
    response["session_id"] = session_id
    response["conversation_history"] = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in history
    ]
    
    return response


@router.get("/demand_insights")
def get_demand_insights(crop: str, lat: float, lon: float):
    """Get regional demand insights for a crop."""
    loc = Location(latitude=lat, longitude=lon)
    return get_regional_demand_insights(crop, loc)
