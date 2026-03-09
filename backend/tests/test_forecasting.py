"""
Unit tests for forecasting engine.
Tests price forecasting, trend analysis, and prediction generation.
"""

import pytest
from datetime import datetime, timedelta
from backend.models import Location
from backend.forecasting.engine import (
    generate_price_forecast,
    analyze_price_trends,
    calculate_confidence_interval,
)


class TestPriceForecasting:
    """Test price forecasting functionality."""
    
    def test_generate_price_forecast(self):
        """Test basic price forecast generation."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        forecast = generate_price_forecast("wheat", loc, horizon_days=7)
        
        assert forecast is not None
        assert forecast.crop == "wheat"
        assert len(forecast.predictions) == 7
        assert all(p.price > 0 for p in forecast.predictions)
    
    def test_forecast_confidence_levels(self):
        """Test that forecasts include confidence levels."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        forecast = generate_price_forecast("rice", loc, horizon_days=30)
        
        assert 0 <= forecast.confidenceLevel <= 1
        assert all(p.confidence is not None for p in forecast.predictions)
    
    def test_forecast_factors(self):
        """Test that forecasts include influencing factors."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        forecast = generate_price_forecast("wheat", loc, horizon_days=7)
        
        assert len(forecast.factors) > 0
        assert all(hasattr(f, "name") for f in forecast.factors)
        assert all(hasattr(f, "impact") for f in forecast.factors)
    
    def test_forecast_dates_sequential(self):
        """Test that forecast dates are sequential."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        forecast = generate_price_forecast("wheat", loc, horizon_days=7)
        
        dates = [p.date for p in forecast.predictions]
        for i in range(len(dates) - 1):
            assert dates[i] < dates[i + 1]
    
    def test_different_crops_different_forecasts(self):
        """Test that different crops produce different forecasts."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        
        forecast_wheat = generate_price_forecast("wheat", loc, horizon_days=7)
        forecast_rice = generate_price_forecast("rice", loc, horizon_days=7)
        
        # Forecasts should differ
        wheat_prices = [p.price for p in forecast_wheat.predictions]
        rice_prices = [p.price for p in forecast_rice.predictions]
        
        assert wheat_prices != rice_prices


class TestTrendAnalysis:
    """Test price trend analysis."""
    
    def test_analyze_price_trends(self):
        """Test price trend analysis."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        trends = analyze_price_trends("wheat", loc, days=30)
        
        assert "trend" in trends
        assert "direction" in trends
        assert trends["direction"] in ["up", "down", "stable"]
    
    def test_trend_with_different_periods(self):
        """Test trend analysis with different time periods."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        
        trends_7 = analyze_price_trends("wheat", loc, days=7)
        trends_30 = analyze_price_trends("wheat", loc, days=30)
        
        assert trends_7 is not None
        assert trends_30 is not None


class TestConfidenceCalculation:
    """Test confidence interval calculations."""
    
    def test_calculate_confidence_interval(self):
        """Test confidence interval calculation."""
        prices = [100, 105, 110, 108, 112]
        lower, upper = calculate_confidence_interval(prices, confidence=0.95)
        
        assert lower < upper
        assert lower > 0
    
    def test_confidence_interval_contains_mean(self):
        """Test that confidence interval contains the mean."""
        prices = [100, 105, 110, 108, 112]
        mean = sum(prices) / len(prices)
        lower, upper = calculate_confidence_interval(prices, confidence=0.95)
        
        assert lower <= mean <= upper
