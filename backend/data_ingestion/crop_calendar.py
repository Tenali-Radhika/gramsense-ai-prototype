from typing import Dict, List, Optional
from datetime import datetime

from .cache import cached, calendar_cache


# Comprehensive crop calendar data for major Indian crops
CROP_CALENDAR_DATA = {
    "wheat": {
        "sowing_season": "Rabi",
        "sowing_months": [10, 11, 12],  # October-December
        "sowing_period": "October-December",
        "harvesting_months": [3, 4, 5],  # March-May
        "harvesting_period": "March-May",
        "growing_duration_days": 120,
        "peak_price_month": 4,  # April (harvest time)
        "best_selling_months": [5, 6, 7],  # Post-harvest
        "climate": "Cool, dry weather",
        "regions": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"],
        "soil_type": "Loamy soil with good drainage",
        "water_requirement": "Medium (4-5 irrigations)",
    },
    "rice": {
        "sowing_season": "Kharif",
        "sowing_months": [6, 7, 8],  # June-August
        "sowing_period": "June-August",
        "harvesting_months": [10, 11, 12],  # October-December
        "harvesting_period": "October-December",
        "growing_duration_days": 120,
        "peak_price_month": 11,  # November (harvest time)
        "best_selling_months": [12, 1, 2],  # Post-harvest
        "climate": "Warm, humid with good rainfall",
        "regions": ["West Bengal", "Punjab", "Uttar Pradesh", "Andhra Pradesh", "Tamil Nadu"],
        "soil_type": "Clayey loam soil",
        "water_requirement": "High (standing water required)",
    },
    "cotton": {
        "sowing_season": "Kharif",
        "sowing_months": [4, 5, 6],  # April-June
        "sowing_period": "April-June",
        "harvesting_months": [10, 11, 12, 1],  # October-January
        "harvesting_period": "October-January",
        "growing_duration_days": 180,
        "peak_price_month": 12,  # December (harvest time)
        "best_selling_months": [1, 2, 3],  # Post-harvest
        "climate": "Warm with moderate rainfall",
        "regions": ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Haryana"],
        "soil_type": "Black cotton soil",
        "water_requirement": "Medium (6-8 irrigations)",
    },
    "sugarcane": {
        "sowing_season": "Year-round",
        "sowing_months": [1, 2, 3, 9, 10, 11],  # Jan-Mar, Sep-Nov
        "sowing_period": "January-March, September-November",
        "harvesting_months": [12, 1, 2, 3, 4],  # December-April
        "harvesting_period": "December-April",
        "growing_duration_days": 365,
        "peak_price_month": 1,  # January (harvest time)
        "best_selling_months": [1, 2, 3],  # Harvest season
        "climate": "Tropical, hot and humid",
        "regions": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh"],
        "soil_type": "Deep, well-drained loamy soil",
        "water_requirement": "Very High (regular irrigation)",
    },
    "potato": {
        "sowing_season": "Rabi",
        "sowing_months": [10, 11, 12],  # October-December
        "sowing_period": "October-December",
        "harvesting_months": [1, 2, 3],  # January-March
        "harvesting_period": "January-March",
        "growing_duration_days": 90,
        "peak_price_month": 2,  # February (harvest time)
        "best_selling_months": [3, 4, 5],  # Post-harvest
        "climate": "Cool weather",
        "regions": ["Uttar Pradesh", "West Bengal", "Bihar", "Punjab", "Madhya Pradesh"],
        "soil_type": "Sandy loam with good drainage",
        "water_requirement": "Medium (4-6 irrigations)",
    },
    "onion": {
        "sowing_season": "Rabi & Kharif",
        "sowing_months": [6, 7, 10, 11],  # June-July, Oct-Nov
        "sowing_period": "June-July (Kharif), October-November (Rabi)",
        "harvesting_months": [1, 2, 3, 10, 11],  # Jan-Mar, Oct-Nov
        "harvesting_period": "January-March (Rabi), October-November (Kharif)",
        "growing_duration_days": 120,
        "peak_price_month": 3,  # March (Rabi harvest)
        "best_selling_months": [4, 5, 6, 12],  # Post-harvest periods
        "climate": "Cool to moderate",
        "regions": ["Maharashtra", "Karnataka", "Gujarat", "Madhya Pradesh", "Bihar"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Medium (regular irrigation)",
    },
    "tomato": {
        "sowing_season": "Year-round",
        "sowing_months": [1, 2, 3, 7, 8, 9],  # Jan-Mar, Jul-Sep
        "sowing_period": "January-March, July-September",
        "harvesting_months": [4, 5, 6, 10, 11, 12],  # Apr-Jun, Oct-Dec
        "harvesting_period": "April-June, October-December",
        "growing_duration_days": 75,
        "peak_price_month": 6,  # June (summer harvest)
        "best_selling_months": [6, 7, 12, 1],  # Peak demand periods
        "climate": "Warm with moderate rainfall",
        "regions": ["Andhra Pradesh", "Karnataka", "Maharashtra", "Madhya Pradesh", "Gujarat"],
        "soil_type": "Well-drained sandy loam",
        "water_requirement": "Medium (regular irrigation)",
    },
    "soybean": {
        "sowing_season": "Kharif",
        "sowing_months": [6, 7],  # June-July
        "sowing_period": "June-July",
        "harvesting_months": [9, 10, 11],  # September-November
        "harvesting_period": "September-November",
        "growing_duration_days": 100,
        "peak_price_month": 10,  # October (harvest time)
        "best_selling_months": [11, 12, 1],  # Post-harvest
        "climate": "Warm with good monsoon rainfall",
        "regions": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Medium (monsoon dependent)",
    },
    "maize": {
        "sowing_season": "Kharif & Rabi",
        "sowing_months": [2, 3, 6, 7],  # Feb-Mar, Jun-Jul
        "sowing_period": "February-March (Rabi), June-July (Kharif)",
        "harvesting_months": [5, 6, 9, 10],  # May-Jun, Sep-Oct
        "harvesting_period": "May-June (Rabi), September-October (Kharif)",
        "growing_duration_days": 90,
        "peak_price_month": 9,  # September (Kharif harvest)
        "best_selling_months": [10, 11, 6, 7],  # Post-harvest periods
        "climate": "Warm with moderate rainfall",
        "regions": ["Karnataka", "Madhya Pradesh", "Rajasthan", "Uttar Pradesh", "Bihar"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Medium (4-6 irrigations)",
    },
    "groundnut": {
        "sowing_season": "Kharif",
        "sowing_months": [6, 7],  # June-July
        "sowing_period": "June-July",
        "harvesting_months": [10, 11, 12],  # October-December
        "harvesting_period": "October-December",
        "growing_duration_days": 120,
        "peak_price_month": 11,  # November (harvest time)
        "best_selling_months": [12, 1, 2],  # Post-harvest
        "climate": "Warm with moderate rainfall",
        "regions": ["Gujarat", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Rajasthan"],
        "soil_type": "Well-drained sandy loam",
        "water_requirement": "Low to Medium (drought tolerant)",
    },
    # NEW CROPS ADDED
    "chickpea": {
        "sowing_season": "Rabi",
        "sowing_months": [10, 11],  # October-November
        "sowing_period": "October-November",
        "harvesting_months": [2, 3, 4],  # February-April
        "harvesting_period": "February-April",
        "growing_duration_days": 120,
        "peak_price_month": 3,
        "best_selling_months": [4, 5, 6],
        "climate": "Cool, dry weather",
        "regions": ["Madhya Pradesh", "Rajasthan", "Maharashtra", "Karnataka", "Andhra Pradesh"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Low (drought tolerant)",
    },
    "mustard": {
        "sowing_season": "Rabi",
        "sowing_months": [10, 11],  # October-November
        "sowing_period": "October-November",
        "harvesting_months": [2, 3],  # February-March
        "harvesting_period": "February-March",
        "growing_duration_days": 120,
        "peak_price_month": 3,
        "best_selling_months": [3, 4, 5],
        "climate": "Cool weather",
        "regions": ["Rajasthan", "Uttar Pradesh", "Haryana", "Madhya Pradesh", "Gujarat"],
        "soil_type": "Loamy soil",
        "water_requirement": "Low to Medium",
    },
    "barley": {
        "sowing_season": "Rabi",
        "sowing_months": [10, 11, 12],  # October-December
        "sowing_period": "October-December",
        "harvesting_months": [3, 4],  # March-April
        "harvesting_period": "March-April",
        "growing_duration_days": 120,
        "peak_price_month": 4,
        "best_selling_months": [4, 5, 6],
        "climate": "Cool, dry weather",
        "regions": ["Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Haryana", "Punjab"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Low to Medium",
    },
    "turmeric": {
        "sowing_season": "Kharif",
        "sowing_months": [5, 6, 7],  # May-July
        "sowing_period": "May-July",
        "harvesting_months": [1, 2, 3],  # January-March (next year)
        "harvesting_period": "January-March",
        "growing_duration_days": 240,
        "peak_price_month": 2,
        "best_selling_months": [3, 4, 5],
        "climate": "Warm, humid with good rainfall",
        "regions": ["Telangana", "Andhra Pradesh", "Tamil Nadu", "Maharashtra", "Karnataka"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "High (regular irrigation)",
    },
    "chilli": {
        "sowing_season": "Kharif & Rabi",
        "sowing_months": [6, 7, 10, 11],  # June-July, Oct-Nov
        "sowing_period": "June-July (Kharif), October-November (Rabi)",
        "harvesting_months": [2, 3, 4, 9, 10],  # Feb-Apr, Sep-Oct
        "harvesting_period": "February-April (Rabi), September-October (Kharif)",
        "growing_duration_days": 150,
        "peak_price_month": 3,
        "best_selling_months": [4, 5, 10, 11],
        "climate": "Warm with moderate rainfall",
        "regions": ["Andhra Pradesh", "Telangana", "Karnataka", "Maharashtra", "Tamil Nadu"],
        "soil_type": "Well-drained loamy soil",
        "water_requirement": "Medium (regular irrigation)",
    },
}


@cached(calendar_cache, ttl=86400)  # Cache for 24 hours (static data)
def fetch_crop_calendar(crop: str, region: str = None) -> Dict:
    """Return crop calendar data for the specified crop and region.
    
    Args:
        crop: Name of the crop (case-insensitive)
        region: Optional region name (currently not used for filtering)
    
    Returns:
        Dictionary containing seasonal information including:
        - Sowing and harvesting periods
        - Growing duration
        - Best selling months
        - Climate requirements
        - Suitable regions
        - Soil and water requirements
    """
    crop_lower = crop.lower()
    
    if crop_lower not in CROP_CALENDAR_DATA:
        # Return generic calendar for unknown crops
        return {
            "crop": crop,
            "sowing_season": "Unknown",
            "sowing_period": "Data not available",
            "harvesting_period": "Data not available",
            "growing_duration_days": 0,
            "best_selling_months": [],
            "climate": "Varies by region",
            "regions": [],
            "soil_type": "Consult local agricultural expert",
            "water_requirement": "Varies",
            "data_available": False,
        }
    
    calendar_data = CROP_CALENDAR_DATA[crop_lower].copy()
    calendar_data["crop"] = crop
    calendar_data["data_available"] = True
    
    # Add current month context
    current_month = datetime.now().month
    calendar_data["current_month"] = current_month
    calendar_data["is_sowing_season"] = current_month in calendar_data["sowing_months"]
    calendar_data["is_harvesting_season"] = current_month in calendar_data["harvesting_months"]
    calendar_data["is_best_selling_period"] = current_month in calendar_data["best_selling_months"]
    
    return calendar_data


@cached(calendar_cache, ttl=3600)  # Cache for 1 hour
def get_seasonal_advice(crop: str, region: str = None) -> Dict:
    """Get seasonal advice for a crop based on current month.
    
    Args:
        crop: Name of the crop
        region: Optional region name
    
    Returns:
        Dictionary with seasonal advice and recommendations
    """
    calendar = fetch_crop_calendar(crop, region)
    
    if not calendar.get("data_available", False):
        return {
            "advice": "Crop calendar data not available. Please consult local agricultural experts.",
            "action": "CONSULT_EXPERT",
        }
    
    current_month = datetime.now().month
    advice = []
    action = "MONITOR"
    
    if calendar["is_sowing_season"]:
        advice.append(f"This is the sowing season for {crop}.")
        advice.append(f"Sowing period: {calendar['sowing_period']}")
        action = "SOW_NOW"
    elif calendar["is_harvesting_season"]:
        advice.append(f"This is the harvesting season for {crop}.")
        advice.append(f"Harvesting period: {calendar['harvesting_period']}")
        action = "HARVEST_NOW"
    elif calendar["is_best_selling_period"]:
        advice.append(f"This is a good time to sell {crop}.")
        advice.append("Market demand is typically higher during this period.")
        action = "SELL_NOW"
    else:
        # Calculate next important period
        next_sowing = min(calendar["sowing_months"], key=lambda m: (m - current_month) % 12)
        months_until_sowing = (next_sowing - current_month) % 12
        advice.append(f"Next sowing season for {crop} is in {months_until_sowing} month(s).")
        action = "PLAN_AHEAD"
    
    return {
        "crop": crop,
        "current_month": current_month,
        "advice": " ".join(advice),
        "action": action,
        "calendar": calendar,
    }
