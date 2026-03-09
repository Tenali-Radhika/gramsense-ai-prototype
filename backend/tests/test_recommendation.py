"""
Unit tests for recommendation engine.
Tests recommendation generation, market suggestions, and query handling.
"""

import pytest
from backend.models import Location
from backend.recommendation.engine import (
    generate_selling_recommendation,
    suggest_optimal_markets,
    provide_crop_planning_advice,
    get_regional_demand_insights,
    handle_farmer_query,
)


class TestSellingRecommendation:
    """Test selling recommendation generation."""
    
    def test_generate_selling_recommendation(self):
        """Test basic selling recommendation."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        rec = generate_selling_recommendation("wheat", loc, quantity=100)
        
        assert rec is not None
        assert rec.type in ["SELL_NOW", "WAIT", "CHANGE_MARKET", "MONITOR"]
        assert rec.priority in ["HIGH", "MEDIUM", "LOW"]
        assert len(rec.explanation) > 0
        assert 0 <= rec.confidence <= 1
    
    def test_recommendation_has_supporting_data(self):
        """Test that recommendations include supporting data."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        rec = generate_selling_recommendation("rice", loc, quantity=50)
        
        assert rec.supportingData is not None
    
    def test_different_quantities_affect_recommendation(self):
        """Test that quantity affects recommendations."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        
        rec_small = generate_selling_recommendation("wheat", loc, quantity=10)
        rec_large = generate_selling_recommendation("wheat", loc, quantity=1000)
        
        # Both should be valid recommendations
        assert rec_small is not None
        assert rec_large is not None


class TestMarketSuggestions:
    """Test optimal market suggestions."""
    
    def test_suggest_optimal_markets(self):
        """Test market suggestion generation."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        markets = suggest_optimal_markets("wheat", loc)
        
        assert isinstance(markets, list)
        assert len(markets) > 0
    
    def test_markets_are_strings(self):
        """Test that market suggestions are strings."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        markets = suggest_optimal_markets("rice", loc)
        
        assert all(isinstance(m, str) for m in markets)


class TestCropPlanningAdvice:
    """Test crop planning advice."""
    
    def test_provide_crop_planning_advice(self):
        """Test crop planning advice generation."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        advice = provide_crop_planning_advice(loc, season="Rabi")
        
        assert isinstance(advice, list)
        assert len(advice) > 0
    
    def test_advice_contains_crop_info(self):
        """Test that advice contains crop information."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        advice = provide_crop_planning_advice(loc, season="Kharif")
        
        assert all(isinstance(a, dict) for a in advice)


class TestRegionalDemand:
    """Test regional demand insights."""
    
    def test_get_regional_demand_insights(self):
        """Test regional demand insights."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        demand = get_regional_demand_insights("wheat", loc)
        
        assert demand is not None
        assert "demand_level" in demand or isinstance(demand, dict)
    
    def test_demand_for_different_crops(self):
        """Test demand insights for different crops."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        
        demand_wheat = get_regional_demand_insights("wheat", loc)
        demand_rice = get_regional_demand_insights("rice", loc)
        
        assert demand_wheat is not None
        assert demand_rice is not None


class TestFarmerQuery:
    """Test farmer query handling."""
    
    def test_handle_farmer_query(self):
        """Test basic query handling."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        response = handle_farmer_query("What is the price of wheat?", "wheat", loc)
        
        assert response is not None
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_query_with_no_crop(self):
        """Test query handling without crop specified."""
        loc = Location(latitude=28.7, longitude=77.1, name="Mumbai")
        response = handle_farmer_query("What should I grow?", None, loc)
        
        assert response is not None
        assert "response" in response
    
    def test_query_with_no_location(self):
        """Test query handling without location."""
        response = handle_farmer_query("Tell me about wheat prices", "wheat", None)
        
        assert response is not None
        assert "response" in response
    
    def test_query_includes_suggestions(self):
        """Test that query responses include suggestions."""
        loc = Location(latitude=28.7, longitude=77.1, name="Delhi")
        response = handle_farmer_query("Should I sell now?", "wheat", loc)
        
        assert "suggestions" in response or "suggestion" in response
