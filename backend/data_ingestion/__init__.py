"""
Data ingestion module with caching support.

This module provides functions to fetch mandi prices, weather data,
and crop calendar information with built-in caching for performance.
"""

from .mandi import (
    fetch_mandi_prices,
    fetch_historical_prices,
    generate_synthetic_price,
)
from .weather import (
    fetch_weather_data,
    get_current_weather_impact,
    get_weather_condition,
)
from .crop_calendar import (
    fetch_crop_calendar,
    get_seasonal_advice,
)
from .cache import (
    get_all_cache_stats,
    clear_all_caches,
    cleanup_all_caches,
    price_cache,
    weather_cache,
    calendar_cache,
)

__all__ = [
    # Mandi/Price functions
    "fetch_mandi_prices",
    "fetch_historical_prices",
    "generate_synthetic_price",
    # Weather functions
    "fetch_weather_data",
    "get_current_weather_impact",
    "get_weather_condition",
    # Crop calendar functions
    "fetch_crop_calendar",
    "get_seasonal_advice",
    # Cache utilities
    "get_all_cache_stats",
    "clear_all_caches",
    "cleanup_all_caches",
    "price_cache",
    "weather_cache",
    "calendar_cache",
]
