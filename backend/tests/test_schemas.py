"""
Unit tests for Pydantic Schemas
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.schemas import (
    RecommendationRequest,
    RestaurantResponse,
    RecommendationResponse,
    LocationResponse,
    CuisineResponse,
    HealthResponse,
    ErrorResponse
)


class TestRecommendationRequest:
    """Test cases for RecommendationRequest schema"""
    
    def test_valid_request(self):
        """Test valid recommendation request"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_preferences": "family-friendly"
        }
        request = RecommendationRequest(**data)
        
        assert request.location == "Delhi"
        assert request.budget == "medium"
        assert request.cuisine == "Italian"
        assert request.min_rating == 4.0
        assert request.additional_preferences == "family-friendly"
    
    def test_request_with_defaults(self):
        """Test request with default values"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian"
        }
        request = RecommendationRequest(**data)
        
        assert request.min_rating == 0.0
        assert request.additional_preferences == ""
    
    def test_budget_validation_valid(self):
        """Test valid budget categories"""
        valid_budgets = ["low", "medium", "high"]
        for budget in valid_budgets:
            data = {
                "location": "Delhi",
                "budget": budget,
                "cuisine": "Italian"
            }
            request = RecommendationRequest(**data)
            assert request.budget == budget
    
    def test_budget_validation_case_insensitive(self):
        """Test budget validation is case-insensitive"""
        data = {
            "location": "Delhi",
            "budget": "MEDIUM",
            "cuisine": "Italian"
        }
        request = RecommendationRequest(**data)
        assert request.budget == "medium"
    
    def test_budget_validation_invalid(self):
        """Test invalid budget category raises error"""
        data = {
            "location": "Delhi",
            "budget": "premium",
            "cuisine": "Italian"
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_location_min_length(self):
        """Test location minimum length validation"""
        data = {
            "location": "",
            "budget": "medium",
            "cuisine": "Italian"
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_location_max_length(self):
        """Test location maximum length validation"""
        data = {
            "location": "A" * 101,
            "budget": "medium",
            "cuisine": "Italian"
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_cuisine_min_length(self):
        """Test cuisine minimum length validation"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": ""
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_cuisine_max_length(self):
        """Test cuisine maximum length validation"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "A" * 101
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_min_rating_range_valid(self):
        """Test valid rating range"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 3.5
        }
        request = RecommendationRequest(**data)
        assert request.min_rating == 3.5
    
    def test_min_rating_below_minimum(self):
        """Test rating below minimum (0) raises error"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": -0.1
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_min_rating_above_maximum(self):
        """Test rating above maximum (5) raises error"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 5.1
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)
    
    def test_additional_preferences_max_length(self):
        """Test additional preferences maximum length"""
        data = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "additional_preferences": "A" * 501
        }
        with pytest.raises(ValidationError):
            RecommendationRequest(**data)


class TestRestaurantResponse:
    """Test cases for RestaurantResponse schema"""
    
    def test_restaurant_response_required_fields(self):
        """Test restaurant response with required fields"""
        data = {
            "id": 1,
            "name": "Test Restaurant",
            "location": "Delhi",
            "cuisine": "Italian",
            "cost_for_two": 1000.0,
            "rating": 4.5
        }
        response = RestaurantResponse(**data)
        
        assert response.id == 1
        assert response.name == "Test Restaurant"
        assert response.location == "Delhi"
        assert response.cuisine == "Italian"
        assert response.cost_for_two == 1000.0
        assert response.rating == 4.5
    
    def test_restaurant_response_with_optional_fields(self):
        """Test restaurant response with optional fields"""
        data = {
            "id": 1,
            "name": "Test Restaurant",
            "location": "Delhi",
            "cuisine": "Italian",
            "cost_for_two": 1000.0,
            "rating": 4.5,
            "votes": 100,
            "reviews": "Great food",
            "address": "123 Main St",
            "phone": "+91-1234567890",
            "url": "http://test.com",
            "budget_category": "medium",
            "rating_category": "very_good",
            "match_score": 0.95,
            "explanation": "Good match"
        }
        response = RestaurantResponse(**data)
        
        assert response.votes == 100
        assert response.reviews == "Great food"
        assert response.address == "123 Main St"
        assert response.phone == "+91-1234567890"
        assert response.url == "http://test.com"
        assert response.budget_category == "medium"
        assert response.rating_category == "very_good"
        assert response.match_score == 0.95
        assert response.explanation == "Good match"
    
    def test_match_score_range_valid(self):
        """Test valid match score range"""
        data = {
            "id": 1,
            "name": "Test Restaurant",
            "location": "Delhi",
            "cuisine": "Italian",
            "cost_for_two": 1000.0,
            "rating": 4.5,
            "match_score": 0.5
        }
        response = RestaurantResponse(**data)
        assert response.match_score == 0.5
    
    def test_match_score_below_minimum(self):
        """Test match score below minimum (0) raises error"""
        data = {
            "id": 1,
            "name": "Test Restaurant",
            "location": "Delhi",
            "cuisine": "Italian",
            "cost_for_two": 1000.0,
            "rating": 4.5,
            "match_score": -0.1
        }
        with pytest.raises(ValidationError):
            RestaurantResponse(**data)
    
    def test_match_score_above_maximum(self):
        """Test match score above maximum (1) raises error"""
        data = {
            "id": 1,
            "name": "Test Restaurant",
            "location": "Delhi",
            "cuisine": "Italian",
            "cost_for_two": 1000.0,
            "rating": 4.5,
            "match_score": 1.1
        }
        with pytest.raises(ValidationError):
            RestaurantResponse(**data)


class TestRecommendationResponse:
    """Test cases for RecommendationResponse schema"""
    
    def test_success_response(self):
        """Test successful recommendation response"""
        data = {
            "success": True,
            "data": {
                "recommendations": [],
                "summary": "Test summary",
                "total_results": 0
            }
        }
        response = RecommendationResponse(**data)
        
        assert response.success is True
        assert response.data is not None
        assert response.error is None
    
    def test_error_response(self):
        """Test error recommendation response"""
        data = {
            "success": False,
            "error": "No results found"
        }
        response = RecommendationResponse(**data)
        
        assert response.success is False
        assert response.error == "No results found"
        assert response.data is None


class TestLocationResponse:
    """Test cases for LocationResponse schema"""
    
    def test_location_response_success(self):
        """Test successful location response"""
        data = {
            "success": True,
            "data": ["Delhi", "Bangalore", "Mumbai"]
        }
        response = LocationResponse(**data)
        
        assert response.success is True
        assert response.data == ["Delhi", "Bangalore", "Mumbai"]
        assert response.error is None
    
    def test_location_response_error(self):
        """Test error location response"""
        data = {
            "success": False,
            "error": "Database error"
        }
        response = LocationResponse(**data)
        
        assert response.success is False
        assert response.error == "Database error"
        assert response.data is None


class TestCuisineResponse:
    """Test cases for CuisineResponse schema"""
    
    def test_cuisine_response_success(self):
        """Test successful cuisine response"""
        data = {
            "success": True,
            "data": ["Italian", "North Indian", "Chinese"]
        }
        response = CuisineResponse(**data)
        
        assert response.success is True
        assert response.data == ["Italian", "North Indian", "Chinese"]
        assert response.error is None


class TestHealthResponse:
    """Test cases for HealthResponse schema"""
    
    def test_health_response(self):
        """Test health response"""
        data = {
            "status": "healthy",
            "service": "recommendation-api"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"
        assert response.service == "recommendation-api"
        assert isinstance(response.timestamp, datetime)
    
    def test_health_response_with_custom_timestamp(self):
        """Test health response with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "status": "healthy",
            "service": "recommendation-api",
            "timestamp": custom_time
        }
        response = HealthResponse(**data)
        
        assert response.timestamp == custom_time


class TestErrorResponse:
    """Test cases for ErrorResponse schema"""
    
    def test_error_response_basic(self):
        """Test basic error response"""
        data = {
            "error": "Validation Error"
        }
        response = ErrorResponse(**data)
        
        assert response.success is False
        assert response.error == "Validation Error"
        assert response.message is None
        assert response.details is None
    
    def test_error_response_with_message(self):
        """Test error response with message"""
        data = {
            "error": "Validation Error",
            "message": "Invalid input data"
        }
        response = ErrorResponse(**data)
        
        assert response.message == "Invalid input data"
    
    def test_error_response_with_details(self):
        """Test error response with details"""
        data = {
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": {
                "field": "location",
                "message": "This field is required"
            }
        }
        response = ErrorResponse(**data)
        
        assert response.details == {
            "field": "location",
            "message": "This field is required"
        }
