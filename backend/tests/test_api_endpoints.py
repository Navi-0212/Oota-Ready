"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_restaurants():
    """Mock restaurant data"""
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
            'cuisine': 'Italian',
            'cost_for_two': 1200.0,
            'rating': 4.2,
            'votes': 80,
            'reviews': 'Good service',
            'address': '456 Oak Ave',
            'phone': '+91-9876543210',
            'url': 'http://restaurantb.com',
            'budget_category': 'medium',
            'rating_category': 'very_good'
        }
    ]


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Zomato Restaurant Recommendation API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        with patch('app.api.recommendations.get_database') as mock_get_db:
            mock_db = Mock()
            mock_db.test_connection.return_value = True
            mock_get_db.return_value = mock_db
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded", "unhealthy"]
            assert data["service"] == "recommendation-api"
    
    @patch('app.api.recommendations.data_service')
    def test_get_recommendations_success(self, mock_data_service, client, mock_restaurants):
        """Test successful recommendation request"""
        mock_data_service.search_restaurants_db.return_value = mock_restaurants
        
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
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "summary" in data["data"]
        assert "total_results" in data["data"]
    
    @patch('app.api.recommendations.data_service')
    def test_get_recommendations_no_results(self, mock_data_service, client):
        """Test recommendation request with no results"""
        mock_data_service.search_restaurants_db.return_value = []
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Chennai",
                "budget": "low",
                "cuisine": "Thai",
                "min_rating": 4.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
    
    def test_get_recommendations_validation_error(self, client):
        """Test recommendation request with invalid data"""
        response = client.post(
            "/api/recommendations",
            json={
                "location": "",
                "budget": "invalid",
                "cuisine": "Italian"
            }
        )
        
        assert response.status_code == 422
    
    @patch('app.api.recommendations.data_service')
    def test_get_locations_success(self, mock_data_service, client):
        """Test getting locations successfully"""
        mock_data_service.get_available_locations_db.return_value = ["Delhi", "Bangalore", "Mumbai"]
        
        response = client.get("/api/locations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "Delhi" in data["data"]
    
    @patch('app.api.recommendations.data_service')
    def test_get_locations_no_results(self, mock_data_service, client):
        """Test getting locations with no results"""
        mock_data_service.get_available_locations_db.return_value = []
        
        response = client.get("/api/locations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
    
    @patch('app.api.recommendations.data_service')
    def test_get_cuisines_success(self, mock_data_service, client):
        """Test getting cuisines successfully"""
        mock_data_service.get_available_cuisines_db.return_value = ["Italian", "North Indian", "Chinese"]
        
        response = client.get("/api/cuisines")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "Italian" in data["data"]
    
    @patch('app.api.recommendations.data_service')
    def test_get_cuisines_no_results(self, mock_data_service, client):
        """Test getting cuisines with no results"""
        mock_data_service.get_available_cuisines_db.return_value = []
        
        response = client.get("/api/cuisines")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
    
    @patch('app.api.recommendations.data_service')
    def test_get_restaurant_by_id_success(self, mock_data_service, client, mock_restaurants):
        """Test getting restaurant by ID successfully"""
        mock_data_service.get_restaurant_by_id_db.return_value = mock_restaurants[0]
        
        response = client.get("/api/restaurant/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["id"] == 1
    
    @patch('app.api.recommendations.data_service')
    def test_get_restaurant_by_id_not_found(self, mock_data_service, client):
        """Test getting non-existent restaurant by ID"""
        mock_data_service.get_restaurant_by_id_db.return_value = None
        
        response = client.get("/api/restaurant/999")
        
        assert response.status_code == 404
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting headers are present"""
        with patch('app.api.recommendations.get_database') as mock_get_db:
            mock_db = Mock()
            mock_db.test_connection.return_value = True
            mock_get_db.return_value = mock_db
            
            response = client.get("/api/health")
            
            # Check for rate limit headers
            assert "X-RateLimit-Limit" in response.headers or "X-RateLimit-Remaining" in response.headers
    
    def test_process_time_header(self, client):
        """Test process time header is present"""
        response = client.get("/")
        
        assert "X-Process-Time" in response.headers
