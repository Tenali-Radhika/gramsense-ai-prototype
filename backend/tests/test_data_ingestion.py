"""
Unit tests for data ingestion functions.
Tests data generation, caching, and crop calendar functionality.
"""

import pytest
from datetime import datetime, timedelta
from backend.models import Location
from backend.data_ingestion import (
    fetch_mandi_prices,
    fetch_historical_prices,
    generate_synthetic_price,
    fetch_weather_data,
    get_current_weather_impact,
    fetch_crop_calendar,
    get_seasonal_advice,
    clear_all_caches,
)


class TestMandiPrices:
    """Test mandi price generation and caching."""
    
    def setup_method(self):
        """Clear caches before each test."""
        clear_all_caches()
    
    def test_fetch_mandi_prices_returns_data(self):
        """Test that fetch_mandi_prices returns price data."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        prices = fetch_mandi_prices("wheat", loc, days_back=5)
        
        assert len(prices) == 6  # 5 days back + today
        assert all(p.crop == "wheat" for p in prices)
        assert all(p.location.name == "Delhi" for p in prices)
        assert all(p.price > 0 for p in prices)
    
    def test_generate_synthetic_price_consistency(self):
        """Test that synthetic prices are consistent with same seed."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        date = datetime.now()
        
        price1 = generate_synthetic_price("wheat", loc, date, seed=42)
        price2 = generate_synthetic_price("wheat", loc, date, seed=42)
        
        assert price1 == price2
    
    def test_generate_synthetic_price_variability(self):
        """Test that synthetic prices vary without seed."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        date = datetime.now()
        
        prices = [generate_synthetic_price("wheat", loc, date) for _ in range(10)]
        
        # Prices should vary
        assert len(set(prices)) > 1
        # All prices should be positive
        assert all(p > 0 for p in prices)
    
    def test_fetch_historical_prices(self):
        """Test historical price fetching."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        prices = fetch_historical_prices("rice", loc, days=30)
        
        assert len(prices) == 31  # 30 days + today
        assert all(p.crop == "rice" for p in prices)
    
    def test_price_caching(self):
        """Test that prices are cached correctly."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        
        # First call
        prices1 = fetch_mandi_prices("wheat", loc, days_back=5)
        
        # Second call (should hit cache)
        prices2 = fetch_mandi_prices("wheat", loc, days_back=5)
        
        # Should return same data
        assert len(prices1) == len(prices2)
        assert prices1[0].price == prices2[0].price


class TestWeatherData:
    """Test weather data generation."""
    
    def setup_method(self):
        """Clear caches before each test."""
        clear_all_caches()
    
    def test_fetch_weather_data(self):
        """Test weather data fetching."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        start = datetime.now()
        end = start + timedelta(days=7)
        
        weather = fetch_weather_data(loc, (start, end))
        
        assert len(weather) == 8  # 7 days + today
        assert all("temperature" in w for w in weather)
        assert all("humidity" in w for w in weather)
        assert all("rainfall" in w for w in weather)
    
    def test_get_current_weather_impact(self):
        """Test current weather impact calculation."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        impact = get_current_weather_impact(loc)
        
        assert "condition" in impact
        assert "impact" in impact
        assert impact["impact"] in ["positive", "negative", "neutral"]


class TestCropCalendar:
    """Test crop calendar functionality."""
    
    def setup_method(self):
        """Clear caches before each test."""
        clear_all_caches()
    
    def test_fetch_crop_calendar_known_crop(self):
        """Test fetching calendar for known crop."""
        calendar = fetch_crop_calendar("wheat")
        
        assert calendar["crop"] == "wheat"
        assert calendar["data_available"] is True
        assert "sowing_period" in calendar
        assert "harvesting_period" in calendar
        assert len(calendar["sowing_months"]) > 0
    
    def test_fetch_crop_calendar_unknown_crop(self):
        """Test fetching calendar for unknown crop."""
        calendar = fetch_crop_calendar("banana")
        
        assert calendar["crop"] == "banana"
        assert calendar["data_available"] is False
    
    def test_get_seasonal_advice(self):
        """Test seasonal advice generation."""
        advice = get_seasonal_advice("rice")
        
        assert "crop" in advice
        assert "advice" in advice
        assert "action" in advice
        assert advice["action"] in ["SOW_NOW", "HARVEST_NOW", "SELL_NOW", "PLAN_AHEAD", "CONSULT_EXPERT"]
    
    def test_crop_calendar_caching(self):
        """Test that crop calendar is cached."""
        # First call
        calendar1 = fetch_crop_calendar("wheat")
        
        # Second call (should hit cache)
        calendar2 = fetch_crop_calendar("wheat")
        
        assert calendar1 == calendar2


class TestDataValidation:
    """Test data validation and error handling."""
    
    def test_invalid_location(self):
        """Test handling of invalid location."""
        loc = Location(latitude=0, longitude=0)
        prices = fetch_mandi_prices("wheat", loc)
        
        # Should still return data (synthetic)
        assert len(prices) > 0
    
    def test_empty_crop_name(self):
        """Test handling of empty crop name."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        prices = fetch_mandi_prices("", loc)
        
        # Should return default data
        assert len(prices) > 0
    
    def test_negative_days_back(self):
        """Test handling of negative days_back."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        prices = fetch_mandi_prices("wheat", loc, days_back=-1)
        
        # Should handle gracefully
        assert isinstance(prices, list)
