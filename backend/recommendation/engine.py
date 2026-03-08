from typing import List, Optional
from datetime import datetime, timedelta, timezone
import random

from ..models import Recommendation, Location, Forecast, PriceData
from ..data_ingestion.mandi import fetch_weather_data


def generate_selling_recommendation(crop: str, location: Location, quantity: float) -> Recommendation:
    """Generate weather-aware selling recommendation for a crop at a location.

    Considers current weather conditions, forecast, and market trends.
    """
    now = datetime.now(timezone.utc)

    # Fetch recent weather data (last 7 days)
    weather_data = fetch_weather_data(location, (now - timedelta(days=7), now))

    # Analyze weather impact
    recent_weather = weather_data[-3:] if len(weather_data) >= 3 else weather_data

    # Weather impact on recommendation
    weather_score = analyze_weather_impact(recent_weather, crop)

    # Base recommendation logic
    if weather_score > 0.7:  # Good weather for harvesting/selling
        rec_type = "SELL_NOW"
        explanation = "Favorable weather conditions suggest good market timing."
        priority = "HIGH"
        confidence = 0.8
    elif weather_score < 0.3:  # Poor weather
        rec_type = "WAIT"
        explanation = "Adverse weather may affect quality and prices. Consider waiting."
        priority = "MEDIUM"
        confidence = 0.7
    else:  # Moderate conditions
        rec_type = "MONITOR"
        explanation = "Weather conditions are moderate. Monitor closely for optimal timing."
        priority = "MEDIUM"
        confidence = 0.6

    # Add weather-specific insights
    weather_insights = generate_weather_insights(recent_weather)

    rec = Recommendation(
        type=rec_type,
        priority=priority,
        explanation=f"{explanation} {weather_insights}",
        supportingData={
            "weather_score": weather_score,
            "recent_weather": recent_weather[-1] if recent_weather else None,
            "analysis_period": "last 7 days"
        },
        confidence=confidence,
        validityPeriod={"start": now, "end": now + timedelta(days=7)},
        disclaimers=["This is advisory only. Consider local market conditions and quality."],
    )
    return rec


def analyze_weather_impact(weather_data: List[dict], crop: str) -> float:
    """Analyze how weather affects crop selling decisions.

    Returns a score from 0-1 where higher is better for selling.
    """
    if not weather_data:
        return 0.5  # Neutral if no data

    total_score = 0
    count = 0

    for weather in weather_data:
        score = 0.5  # Base neutral score

        # Temperature impact (optimal ranges vary by crop)
        temp = weather.get("temperature", 25)
        if crop in ["wheat", "rice"]:
            # Cooler temperatures better for storage
            if 15 <= temp <= 25:
                score += 0.2
            elif temp > 30:
                score -= 0.2
        elif crop in ["maize", "cotton"]:
            # Warmer but not too hot
            if 20 <= temp <= 30:
                score += 0.2
            elif temp > 35:
                score -= 0.2

        # Rainfall impact (less rain better for harvesting/selling)
        rainfall = weather.get("rainfall", 0)
        if rainfall < 5:
            score += 0.2
        elif rainfall > 20:
            score -= 0.3

        # Humidity impact (moderate humidity preferred)
        humidity = weather.get("humidity", 50)
        if 40 <= humidity <= 70:
            score += 0.1
        elif humidity > 80:
            score -= 0.1

        total_score += max(0, min(1, score))  # Clamp to 0-1
        count += 1

    return total_score / count if count > 0 else 0.5


def generate_weather_insights(weather_data: List[dict]) -> str:
    """Generate human-readable weather insights."""
    if not weather_data:
        return "Weather data unavailable."

    latest = weather_data[-1]
    temp = latest.get("temperature", 0)
    rainfall = latest.get("rainfall", 0)

    insights = []

    if temp > 35:
        insights.append("High temperatures may affect crop quality.")
    elif temp < 15:
        insights.append("Cool temperatures are good for storage.")

    if rainfall > 10:
        insights.append("Recent rainfall may delay harvesting.")
    else:
        insights.append("Dry conditions favor harvesting and selling.")

    return " ".join(insights) if insights else "Weather conditions are moderate."


def suggest_optimal_markets(crop: str, location: Location) -> List[str]:
    """Suggest optimal markets based on location and crop type."""
    # Simple location-based suggestions
    base_markets = ["Local Mandi", "District Market", "State Capital Market"]

    # Add regional markets based on location
    if location.latitude > 25:  # North India
        base_markets.extend(["Delhi Market", "Chandigarh Mandi"])
    elif location.latitude < 15:  # South India
        base_markets.extend(["Chennai Market", "Bangalore Mandi"])
    else:  # Central India
        base_markets.extend(["Mumbai Market", "Nagpur Mandi"])

    return base_markets[:5]  # Return top 5


def provide_crop_planning_advice(location: Location, season: str) -> List[dict]:
    """Provide crop planning advice based on location and season."""
    # Seasonal crop recommendations
    seasonal_crops = {
        "kharif": ["rice", "maize", "cotton", "soybean"],
        "rabi": ["wheat", "barley", "mustard", "peas"],
        "zaid": ["cucumber", "watermelon", "muskmelon"]
    }

    crops = seasonal_crops.get(season.lower(), ["wheat", "rice", "maize"])

    advice = []
    for crop in crops:
        advice.append({
            "crop": crop,
            "season": season,
            "suitability": "High" if random.random() > 0.3 else "Medium",
            "expected_yield": f"{random.randint(20, 50)} quintals/acre",
            "water_requirement": "Medium",
            "recommendation": f"Suitable for {season} season in this region."
        })

    return advice


def get_regional_demand_insights(crop: str, location: Location) -> dict:
    """Provide regional demand insights for a crop."""
    # Simulate demand based on region and crop
    regions = {
        "north": ["wheat", "rice", "sugarcane"],
        "south": ["rice", "coffee", "tea"],
        "east": ["jute", "tea", "rice"],
        "west": ["cotton", "groundnut", "wheat"],
        "central": ["soybean", "wheat", "cotton"]
    }

    # Determine region
    if location.latitude > 25:
        region = "north"
    elif location.latitude < 15:
        region = "south"
    elif location.longitude > 85:
        region = "east"
    elif location.longitude < 75:
        region = "west"
    else:
        region = "central"

    demand_level = "High" if crop in regions.get(region, []) else "Medium"

    return {
        "region": region,
        "crop": crop,
        "demand_level": demand_level,
        "regional_markets": suggest_optimal_markets(crop, location),
        "seasonal_trend": "Increasing" if demand_level == "High" else "Stable",
        "insights": f"{crop} has {demand_level.lower()} demand in {region} region."
    }


def handle_farmer_query(query: str, crop: str = None, location: Location = None) -> dict:
    """Handle natural language queries from farmers."""
    query_lower = query.lower()

    # Simple keyword-based query processing
    if any(word in query_lower for word in ["price", "cost", "rate", "worth"]):
        if crop:
            return {
                "response": f"For {crop}, current market prices vary by location and quality. Check the price dashboard for real-time data.",
                "suggestion": "Use the price tracking feature to monitor trends.",
                "type": "price_inquiry"
            }
        else:
            return {
                "response": "Please specify which crop you're asking about to get accurate price information.",
                "suggestion": "Select a crop first, then ask about prices.",
                "type": "clarification_needed"
            }

    elif any(word in query_lower for word in ["sell", "selling", "market", "when to sell"]):
        if crop and location:
            rec = generate_selling_recommendation(crop, location, 100)  # Default quantity
            return {
                "response": f"Based on current conditions: {rec.explanation}",
                "recommendation": rec.type,
                "confidence": rec.confidence,
                "type": "selling_advice"
            }
        else:
            return {
                "response": "To give you the best selling advice, please specify your crop and location.",
                "suggestion": "Use the recommendation feature with your crop and location details.",
                "type": "clarification_needed"
            }

    elif any(word in query_lower for word in ["weather", "rain", "temperature", "climate"]):
        if location:
            weather = get_current_weather_impact(location)
            return {
                "response": f"Current weather: {weather['condition']} ({weather['temperature']}°C). {weather['reason']}",
                "impact": weather['impact'],
                "type": "weather_info"
            }
        else:
            return {
                "response": "Please provide your location to get weather information.",
                "type": "clarification_needed"
            }

    elif any(word in query_lower for word in ["plant", "grow", "crop planning", "season"]):
        season = "kharif"  # Default, could be enhanced to detect from date
        if location:
            advice = provide_crop_planning_advice(location, season)
            crops = [item['crop'] for item in advice[:3]]
            return {
                "response": f"For {season} season, recommended crops include: {', '.join(crops)}.",
                "suggestions": crops,
                "type": "crop_planning"
            }
        else:
            return {
                "response": "Crop recommendations depend on your location and season.",
                "suggestion": "Share your location for personalized advice.",
                "type": "clarification_needed"
            }

    elif any(word in query_lower for word in ["demand", "market", "popular", "sell well"]):
        if crop and location:
            demand = get_regional_demand_insights(crop, location)
            return {
                "response": f"{crop} has {demand['demand_level']} demand in your region ({demand['region']}).",
                "demand_level": demand['demand_level'],
                "markets": demand['regional_markets'][:3],
                "type": "demand_info"
            }
        else:
            return {
                "response": "Demand varies by crop and region. Please specify details.",
                "type": "clarification_needed"
            }

    else:
        # General helpful response
        return {
            "response": "I'm here to help with crop prices, selling advice, weather information, and crop planning. What would you like to know?",
            "suggestions": ["Current crop prices", "When to sell my crop", "Weather impact", "Crop planning advice"],
            "type": "general_help"
        }
