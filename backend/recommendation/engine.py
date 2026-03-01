from typing import List, Optional
from datetime import datetime, timedelta

from ..models import Recommendation, Location, Forecast, PriceData


def generate_selling_recommendation(crop: str, location: Location, quantity: float) -> Recommendation:
    # simplistic heuristic: always "WAIT"
    rec = Recommendation(
        type="WAIT",
        priority="MEDIUM",
        explanation="Market conditions seem stable; consider waiting.",
        supportingData={},
        confidence=0.6,
        validityPeriod={"start": datetime.utcnow(), "end": datetime.utcnow() + timedelta(days=7)},
        disclaimers=["This is advisory only."],
    )
    return rec


def suggest_optimal_markets(crop: str, location: Location) -> List[str]:
    return ["Example Market"]


def provide_crop_planning_advice(location: Location, season: str) -> List[dict]:
    return [{"advice": "Plant maize", "season": season}]
