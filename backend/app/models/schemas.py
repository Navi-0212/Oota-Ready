"""
Pydantic Models for Request/Response Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class RecommendationRequest(BaseModel):
    """Request model for restaurant recommendations"""
    
    location: str = Field(..., description="Restaurant location", min_length=1, max_length=100)
    budget: str = Field(..., description="Budget category: low, medium, high")
    cuisine: str = Field(..., description="Cuisine type", min_length=1, max_length=100)
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating (0-5)")
    additional_preferences: str = Field(default="", max_length=500, description="Additional preferences")
    
    @validator('budget')
    def validate_budget(cls, v):
        """Validate budget category"""
        valid_budgets = ['low', 'medium', 'high']
        if v.lower() not in valid_budgets:
            raise ValueError(f"Budget must be one of: {', '.join(valid_budgets)}")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": "family-friendly, outdoor seating"
            }
        }


class RestaurantResponse(BaseModel):
    """Response model for a single restaurant"""
    
    id: int
    name: str
    location: str
    cuisine: str
    cost_for_two: float
    rating: float
    votes: Optional[int] = None
    reviews: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    budget_category: Optional[str] = None
    rating_category: Optional[str] = None
    match_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Match score (0-1)")
    explanation: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Restaurant Name",
                "location": "Delhi",
                "cuisine": "Italian",
                "cost_for_two": 1500.0,
                "rating": 4.5,
                "votes": 100,
                "reviews": "Great food",
                "address": "123 Main St",
                "phone": "+91-1234567890",
                "url": "http://restaurant.com",
                "budget_category": "medium",
                "rating_category": "very_good",
                "match_score": 0.95,
                "explanation": "This restaurant matches your preferences well..."
            }
        }


class RecommendationResponse(BaseModel):
    """Response model for recommendation endpoint"""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "recommendations": [
                        {
                            "id": 1,
                            "name": "Restaurant Name",
                            "location": "Delhi",
                            "cuisine": "Italian",
                            "cost_for_two": 1500.0,
                            "rating": 4.5,
                            "match_score": 0.95,
                            "explanation": "This restaurant matches your preferences..."
                        }
                    ],
                    "summary": "Based on your preferences...",
                    "total_results": 10
                },
                "error": None
            }
        }


class LocationResponse(BaseModel):
    """Response model for locations endpoint"""
    
    success: bool
    data: Optional[List[str]] = None
    error: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": ["Delhi", "Bangalore", "Mumbai"],
                "error": None
            }
        }


class CuisineResponse(BaseModel):
    """Response model for cuisines endpoint"""
    
    success: bool
    data: Optional[List[str]] = None
    error: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": ["Italian", "North Indian", "Chinese"],
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "recommendation-api",
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    success: bool = False
    error: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Validation Error",
                "message": "Invalid input data",
                "details": {
                    "field": "location",
                    "message": "This field is required"
                }
            }
        }
