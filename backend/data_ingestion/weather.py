from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta
import random

from ..models import Location
from .cache import cached, weather_cache


@cached(weather_cache, ttl=1800)  # Cache for 30 minutes
def fetch_weather_data(location: Location, date_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
    """Retrieve weather data for a location between the given date range.

    Returns synthetic weather data for demonstration.
    In production, this would integrate with IMD or OpenWeatherMap APIs.
    """
    start_date = date_range[0] if isinstance(date_range[0], datetime) else datetime.fromisoformat(str(date_range[0]))
    end_date = date_range[1] if isinstance(date_range[1], datetime) else datetime.fromisoformat(str(date_range[1]))

    weather_data = []
    current_date = start_date

    while current_date <= end_date:
        # Generate realistic weather patterns
        temp = 25 + random.uniform(-10, 15)  # Temperature in Celsius
        humidity = random.uniform(40, 90)  # Humidity percentage
        rainfall = random.uniform(0, 50) if random.random() < 0.3 else 0  # Rainfall in mm

        weather_entry = {
            "date": current_date.isoformat(),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "condition": get_weather_condition(temp, rainfall),
            "location": location.model_dump()
        }
        weather_data.append(weather_entry)
        current_date += timedelta(days=1)

    return weather_data


def get_weather_condition(temperature: float, rainfall: float) -> str:
    """Determine weather condition based on temperature and rainfall."""
    if rainfall > 20:
        return "Heavy Rain"
    elif rainfall > 5:
        return "Light Rain"
    elif temperature > 35:
        return "Hot"
    elif temperature < 15:
        return "Cold"
    else:
        return "Clear"


@cached(weather_cache, ttl=600)  # Cache for 10 minutes
def get_current_weather_impact(location: Location) -> Dict[str, Any]:
    """Get current weather conditions and their potential impact on crop prices."""
    today = datetime.now().date()
    weather_data = fetch_weather_data(location, (today.isoformat(), today.isoformat()))

    if not weather_data:
        return {"condition": "Unknown", "impact": "neutral"}

    current = weather_data[0]
    condition = current["condition"]

    # Define impact on crop prices
    impacts = {
        "Heavy Rain": {"impact": "negative", "reason": "Excess moisture may damage crops"},
        "Light Rain": {"impact": "positive", "reason": "Beneficial for crop growth"},
        "Hot": {"impact": "negative", "reason": "High temperatures stress crops"},
        "Cold": {"impact": "negative", "reason": "Cold weather slows growth"},
        "Clear": {"impact": "neutral", "reason": "Normal weather conditions"}
    }

    return {
        "condition": condition,
        "temperature": current["temperature"],
        "rainfall": current["rainfall"],
        **impacts.get(condition, {"impact": "neutral", "reason": "Weather conditions normal"})
    }
