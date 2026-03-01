from datetime import datetime, timedelta, date
from typing import List

from ..models import Forecast, PricePrediction, ForecastFactor, Location


def generate_price_forecast(crop: str, location: Location, horizon: int = 30) -> Forecast:
    """Generate a synthetic price forecast for the given crop/location."""
    start = date.today()
    predictions: List[PricePrediction] = []
    for i in range(horizon):
        predictions.append(
            PricePrediction(date=start + timedelta(days=i), price=100.0 + i, confidence=0.8)
        )
    forecast = Forecast(
        crop=crop,
        location=location,
        predictions=predictions,
        confidenceLevel=0.75,
        methodology="synthetic-model",
        factors=[ForecastFactor(name="trend", impact=0.5, description="increasing trend")],
        generatedAt=datetime.utcnow(),
        validUntil=datetime.utcnow() + timedelta(days=horizon),
    )
    return forecast


def calculate_confidence_level(forecast: Forecast) -> float:
    # simple stub returning existing value
    return forecast.confidenceLevel


def explain_forecast(forecast: Forecast) -> str:
    return f"Forecast for {forecast.crop} shows an upward trend with confidence {forecast.confidenceLevel:.0%}."
