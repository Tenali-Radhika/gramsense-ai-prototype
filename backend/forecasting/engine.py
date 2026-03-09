from datetime import datetime, timedelta, date, timezone
from typing import List
import random

from models import Forecast, PricePrediction, ForecastFactor, Location
from data_ingestion.mandi import fetch_historical_prices, CROP_DATA
from data_ingestion.weather import get_current_weather_impact


def generate_price_forecast(crop: str, location: Location, horizon: int = 30) -> Forecast:
    """Generate a realistic price forecast for the given crop/location.
    
    Uses historical price trends and weather factors to predict future prices.
    """
    # Fetch historical prices for trend analysis
    historical_prices = fetch_historical_prices(crop, location, days=30)
    
    if not historical_prices:
        # Fallback to base price if no historical data
        crop_lower = crop.lower()
        base_price = CROP_DATA.get(crop_lower, {}).get("base_price", 2000)
    else:
        # Use recent average as base
        recent_prices = [p.price for p in historical_prices[:7]]
        base_price = sum(recent_prices) / len(recent_prices)
    
    # Calculate trend from historical data
    if len(historical_prices) >= 7:
        old_avg = sum(p.price for p in historical_prices[-7:]) / 7
        new_avg = sum(p.price for p in historical_prices[:7]) / 7
        trend = (new_avg - old_avg) / old_avg  # Percentage change
    else:
        trend = 0.0
    
    # Get weather impact
    weather_impact = get_current_weather_impact(location)
    weather_factor = {
        "positive": 0.05,
        "negative": -0.05,
        "neutral": 0.0
    }.get(weather_impact.get("impact", "neutral"), 0.0)
    
    # Generate predictions
    start = date.today()
    predictions: List[PricePrediction] = []
    
    current_price = base_price
    for i in range(horizon):
        # Apply trend with some randomness
        daily_change = trend / 30  # Distribute trend over month
        random_variation = random.gauss(0, 0.02)  # 2% daily volatility
        weather_effect = weather_factor * (1 - i / horizon)  # Weather impact decreases over time
        
        # Calculate next day price
        price_change = daily_change + random_variation + weather_effect
        current_price = current_price * (1 + price_change)
        
        # Confidence decreases with time
        confidence = max(0.5, 0.9 - (i / horizon) * 0.4)
        
        predictions.append(
            PricePrediction(
                date=start + timedelta(days=i),
                price=round(current_price, 2),
                confidence=round(confidence, 2)
            )
        )
    
    # Build forecast factors
    factors = []
    
    if abs(trend) > 0.01:
        factors.append(ForecastFactor(
            name="Historical Trend",
            impact=round(trend, 3),
            description=f"{'Increasing' if trend > 0 else 'Decreasing'} trend based on last 30 days"
        ))
    
    if weather_factor != 0:
        factors.append(ForecastFactor(
            name="Weather Impact",
            impact=round(weather_factor, 3),
            description=f"{weather_impact.get('condition', 'Unknown')} weather conditions"
        ))
    
    # Seasonal factor
    crop_lower = crop.lower()
    if crop_lower in CROP_DATA:
        peak_month = CROP_DATA[crop_lower]["seasonal_peak"]
        current_month = datetime.now().month
        distance_to_peak = min(abs(current_month - peak_month), 12 - abs(current_month - peak_month))
        seasonal_impact = (6 - distance_to_peak) / 6 * 0.1  # Max 10% impact
        
        factors.append(ForecastFactor(
            name="Seasonal Pattern",
            impact=round(seasonal_impact, 3),
            description=f"Peak season in month {peak_month}, currently month {current_month}"
        ))
    
    now = datetime.now(timezone.utc)
    avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
    
    forecast = Forecast(
        crop=crop,
        location=location,
        predictions=predictions,
        confidenceLevel=round(avg_confidence, 2),
        methodology="trend-analysis-with-weather",
        factors=factors,
        generatedAt=now,
        validUntil=now + timedelta(days=horizon),
    )
    return forecast


def calculate_confidence_level(forecast: Forecast) -> float:
    """Calculate overall confidence level for a forecast."""
    return forecast.confidenceLevel


def explain_forecast(forecast: Forecast) -> str:
    """Generate human-readable explanation of the forecast."""
    trend_direction = "stable"
    for factor in forecast.factors:
        if factor.name == "Historical Trend":
            if factor.impact > 0.02:
                trend_direction = "upward"
            elif factor.impact < -0.02:
                trend_direction = "downward"
    
    explanation = f"Forecast for {forecast.crop} shows a {trend_direction} trend "
    explanation += f"with {forecast.confidenceLevel:.0%} confidence. "
    
    if forecast.factors:
        explanation += "Key factors: "
        explanation += ", ".join(f"{f.name} ({f.impact:+.1%})" for f in forecast.factors)
    
    return explanation
