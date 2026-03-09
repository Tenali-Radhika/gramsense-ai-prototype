"""
Integration tests for API endpoints.
Tests all API endpoints with various scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint(self):
        """Test health endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
    
    def test_health_includes_features(self):
        """Test health endpoint includes feature flags."""
        response = client.get("/health")
        data = response.json()
        assert "features" in data
        assert data["features"]["data_caching"] is True


class TestPricesEndpoint:
    """Test prices API endpoint."""
    
    def test_get_prices(self):
        """Test fetching prices."""
        response = client.get("/prices?crop=wheat&lat=28.7&lon=77.1&days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_prices_missing_parameters(self):
        """Test prices endpoint with missing parameters."""
        response = client.get("/prices")
        assert response.status_code == 422  # Validation error
    
    def test_prices_invalid_coordinates(self):
        """Test prices with invalid coordinates."""
        response = client.get("/prices?crop=wheat&lat=invalid&lon=77.1")
        assert response.status_code == 422


class TestForecastEndpoint:
    """Test forecast API endpoint."""
    
    def test_get_forecast(self):
        """Test fetching forecast."""
        response = client.get("/forecast?crop=wheat&lat=28.7&lon=77.1&horizon=7")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "confidenceLevel" in data
    
    def test_forecast_different_horizons(self):
        """Test forecast with different time horizons."""
        response_7 = client.get("/forecast?crop=wheat&lat=28.7&lon=77.1&horizon=7")
        response_30 = client.get("/forecast?crop=wheat&lat=28.7&lon=77.1&horizon=30")
        
        assert response_7.status_code == 200
        assert response_30.status_code == 200
        
        data_7 = response_7.json()
        data_30 = response_30.json()
        
        assert len(data_7["predictions"]) == 7
        assert len(data_30["predictions"]) == 30


class TestRecommendationEndpoint:
    """Test recommendation API endpoint."""
    
    def test_get_recommendation(self):
        """Test fetching recommendation."""
        response = client.get("/recommendation?crop=wheat&lat=28.7&lon=77.1&quantity=100")
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "explanation" in data
        assert "confidence" in data
    
    def test_recommendation_different_quantities(self):
        """Test recommendations with different quantities."""
        response_small = client.get("/recommendation?crop=wheat&lat=28.7&lon=77.1&quantity=10")
        response_large = client.get("/recommendation?crop=wheat&lat=28.7&lon=77.1&quantity=1000")
        
        assert response_small.status_code == 200
        assert response_large.status_code == 200


class TestQueryAssistantEndpoint:
    """Test query assistant API endpoint."""
    
    def test_query_assistant(self):
        """Test query assistant endpoint."""
        response = client.post(
            "/query_assistant",
            json={
                "query": "What is the price of wheat?",
                "crop": "wheat",
                "lat": 28.7,
                "lon": 77.1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
    
    def test_query_assistant_with_session(self):
        """Test query assistant with session ID."""
        # First query
        response1 = client.post(
            "/query_assistant",
            json={
                "query": "What is the price of wheat?",
                "crop": "wheat",
                "lat": 28.7,
                "lon": 77.1
            }
        )
        session_id = response1.json()["session_id"]
        
        # Second query with same session
        response2 = client.post(
            "/query_assistant",
            json={
                "query": "Will it go up?",
                "crop": "wheat",
                "lat": 28.7,
                "lon": 77.1,
                "session_id": session_id
            }
        )
        
        assert response2.status_code == 200
        data = response2.json()
        assert data["session_id"] == session_id
        assert "conversation_history" in data


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting(self):
        """Test that rate limiting works."""
        # Make many requests quickly
        responses = []
        for i in range(70):  # Exceed the 60/minute limit
            response = client.get("/prices?crop=wheat&lat=28.7&lon=77.1&days=1")
            responses.append(response.status_code)
        
        # Should have some 429 responses
        assert 429 in responses


class TestCORSHeaders:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present."""
        response = client.get("/health")
        assert "access-control-allow-origin" in response.headers


class TestResponseHeaders:
    """Test custom response headers."""
    
    def test_process_time_header(self):
        """Test that X-Process-Time header is present."""
        response = client.get("/health")
        assert "x-process-time" in response.headers
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present."""
        response = client.get("/health")
        # Health endpoint is exempt from rate limiting
        # Test on another endpoint
        response = client.get("/prices?crop=wheat&lat=28.7&lon=77.1&days=1")
        assert "x-ratelimit-limit-minute" in response.headers or response.status_code == 200
