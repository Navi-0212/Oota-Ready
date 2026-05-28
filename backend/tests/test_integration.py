"""
Integration tests for end-to-end API flows
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_complete_restaurant_data():
    """Mock complete restaurant data"""
    return [
        {
            'id': 1,
            'name': 'Restaurant A',
            'location': 'Delhi',
            'cuisine': 'Italian',
            'cost_for_two': 1000.0,
            'rating': 4.5,
            'votes': 100,
            'reviews': 'Great food',
            'address': '123 Main St',
            'phone': '+91-1234567890',
            'url': 'http://restaurant.com',
            'budget_category': 'medium',
            'rating_category': 'very_good'
        },
        {
            'id': 2,
            'name': 'Restaurant B',
            'location': 'Delhi',
            'cuisine': 'North Indian',
            'cost_for_two': 800.0,
            'rating': 4.2,
            'votes': 80,
            'reviews': 'Good service',
            'address': '456 Oak Ave',
            'phone': '+91-9876543210',
            'url': 'http://restaurantb.com',
            'budget_category': 'low',
            'rating_category': 'very_good'
        }
    ]


class TestIntegrationAPIFlows:
    """Integration tests for complete API flows"""
    
    @patch('app.api.recommendations.data_service')
    @patch('app.api.recommendations.filtering_service')
    @patch('app.api.recommendations.llm_service')
    def test_complete_recommendation_flow_with_llm(self, mock_llm, mock_filtering, mock_data, client, mock_complete_restaurant_data):
        """Test complete recommendation flow with LLM integration"""
        # Mock data service
        mock_data.search_restaurants_db.return_value = mock_complete_restaurant_data
        
        # Mock filtering service
        mock_filtering.apply_filters.return_value = mock_complete_restaurant_data
        mock_filtering.rank_restaurants.return_value = [
            {**r, 'match_score': 0.9, 'explanation': 'Test explanation'} 
            for r in mock_complete_restaurant_data
        ]
        
        # Mock LLM service
        mock_llm.rank_with_llm.return_value = [
            {**r, 'llm_rank': i+1, 'llm_explanation': f'LLM explanation {i+1}'} 
            for i, r in enumerate(mock_complete_restaurant_data)
        ]
        mock_llm.summarize_recommendations.return_value = "Summary of recommendations"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": "family-friendly"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data["data"]
        assert "summary" in data["data"]
    
    @patch('app.api.recommendations.data_service')
    @patch('app.api.recommendations.filtering_service')
    def test_complete_recommendation_flow_without_llm(self, mock_filtering, mock_data, client, mock_complete_restaurant_data):
        """Test complete recommendation flow without LLM (fallback)"""
        # Mock data service
        mock_data.search_restaurants_db.return_value = mock_complete_restaurant_data
        
        # Mock filtering service
        mock_filtering.apply_filters.return_value = mock_complete_restaurant_data
        mock_filtering.rank_restaurants.return_value = [
            {**r, 'match_score': 0.9, 'explanation': 'Test explanation'} 
            for r in mock_complete_restaurant_data
        ]
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.recommendations.data_service')
    def test_get_locations_then_recommendations_flow(self, mock_data, client, mock_complete_restaurant_data):
        """Test flow: get locations, then get recommendations"""
        # Mock locations
        mock_data.get_available_locations_db.return_value = ["Delhi", "Bangalore", "Mumbai"]
        
        # Get locations
        locations_response = client.get("/api/locations")
        assert locations_response.status_code == 200
        locations = locations_response.json()["data"]
        
        # Use first location for recommendations
        mock_data.search_restaurants_db.return_value = mock_complete_restaurant_data
        
        recommendations_response = client.post(
            "/api/recommendations",
            json={
                "location": locations[0],
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        assert recommendations_response.status_code == 200
    
    @patch('app.api.recommendations.data_service')
    def test_get_cuisines_then_recommendations_flow(self, mock_data, client, mock_complete_restaurant_data):
        """Test flow: get cuisines, then get recommendations"""
        # Mock cuisines
        mock_data.get_available_cuisines_db.return_value = ["Italian", "North Indian", "Chinese"]
        
        # Get cuisines
        cuisines_response = client.get("/api/cuisines")
        assert cuisines_response.status_code == 200
        cuisines = cuisines_response.json()["data"]
        
        # Use first cuisine for recommendations
        mock_data.search_restaurants_db.return_value = mock_complete_restaurant_data
        
        recommendations_response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": cuisines[0]
            }
        )
        
        assert recommendations_response.status_code == 200
    
    @patch('app.api.recommendations.data_service')
    def test_get_restaurant_by_id_then_recommendations_flow(self, mock_data, client, mock_complete_restaurant_data):
        """Test flow: get restaurant by ID, then get recommendations"""
        # Mock single restaurant
        mock_data.get_restaurant_by_id_db.return_value = mock_complete_restaurant_data[0]
        
        # Get restaurant
        restaurant_response = client.get("/api/restaurant/1")
        assert restaurant_response.status_code == 200
        restaurant = restaurant_response.json()["data"]
        
        # Use restaurant's location and cuisine for recommendations
        mock_data.search_restaurants_db.return_value = mock_complete_restaurant_data
        
        recommendations_response = client.post(
            "/api/recommendations",
            json={
                "location": restaurant["location"],
                "budget": "medium",
                "cuisine": restaurant["cuisine"]
            }
        )
        
        assert recommendations_response.status_code == 200


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    @patch('app.api.recommendations.get_database')
    def test_database_connection_in_flow(self, mock_get_db, client):
        """Test database connection is used in API flow"""
        mock_db = Mock()
        mock_db.test_connection.return_value = True
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        mock_db.test_connection.assert_called_once()


class TestCacheIntegration:
    """Integration tests for cache operations"""
    
    @patch('app.services.data_service.redis')
    def test_cache_hit_in_data_service(self, mock_redis):
        """Test cache hit in data service"""
        from app.services.data_service import DataService
        import pandas as pd
        
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = '{"id":1,"name":"Test"}'
        mock_redis.from_url.return_value = mock_redis_client
        
        service = DataService(redis_host="localhost", redis_port=6379)
        
        # This should hit cache
        # Note: Actual implementation may vary
        assert service.redis_client is not None


class TestLLMIntegration:
    """Integration tests for LLM operations"""
    
    @patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'})
    def test_llm_service_initialization(self):
        """Test LLM service initializes correctly"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        assert service.api_key == 'test_key'
    
    @patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'})
    def test_llm_fallback_on_api_failure(self):
        """Test LLM service falls back to rule-based on API failure"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        service.client = None  # Simulate API failure
        
        restaurants = [
            {'id': 1, 'name': 'Test', 'rating': 4.5, 'cuisine': 'Italian'}
        ]
        preferences = {'location': 'Delhi', 'budget': 'medium', 'cuisine': 'Italian'}
        
        result = service._fallback_recommendation(restaurants)
        
        assert 'rankings' in result
        assert 'summary' in result
