"""
API Endpoints for Restaurant Recommendations
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    LocationResponse,
    CuisineResponse,
    HealthResponse
)
from app.services.data_service import DataService
from app.services.filtering_service import FilteringService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recommendations"])

# Initialize services
data_service = DataService()
filtering_service = FilteringService()
llm_service = LLMService()


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized restaurant recommendations based on user preferences
    
    Args:
        request: Recommendation request with location, budget, cuisine, etc.
        
    Returns:
        List of recommended restaurants with match scores and explanations
    """
    try:
        logger.info(f"Received recommendation request: location={request.location}, budget={request.budget}, cuisine={request.cuisine}")
        
        # Get restaurants from database
        restaurants = data_service.search_restaurants_db(
            location=request.location,
            cuisine=request.cuisine,
            min_rating=request.min_rating,
            budget_category=request.budget,
            limit=100
        )
        
        if not restaurants:
            logger.warning(f"No restaurants found for the given criteria")
            return RecommendationResponse(
                success=False,
                data=None,
                error="No restaurants found matching your criteria"
            )
        
        # Apply filtering and ranking
        filtered_restaurants = filtering_service.apply_filters(
            restaurants=restaurants,
            location=request.location,
            budget=request.budget,
            cuisine=request.cuisine,
            min_rating=request.min_rating,
            preferences=request.additional_preferences
        )
        
        # Use LLM to generate explanations and rankings
        try:
            user_preferences = {
                'location': request.location,
                'budget': request.budget,
                'cuisine': request.cuisine,
                'min_rating': request.min_rating,
                'additional_preferences': request.additional_preferences
            }
            
            # Rank with LLM
            ranked_restaurants = llm_service.rank_with_llm(filtered_restaurants, user_preferences)
            
            # Generate LLM summary
            summary = llm_service.summarize_recommendations(ranked_restaurants, user_preferences)
            
        except Exception as e:
            logger.warning(f"LLM ranking failed, using fallback: {e}")
            ranked_restaurants = filtered_restaurants
            # Generate explanations using filtering service as fallback
            for restaurant in ranked_restaurants:
                restaurant['explanation'] = filtering_service.generate_explanation(
                    restaurant,
                    request.budget,
                    request.cuisine,
                    request.additional_preferences
                )
            summary = f"Found {len(filtered_restaurants)} restaurants matching your preferences. Showing top {len(ranked_restaurants)} recommendations."
        
        # Limit results to top 10
        top_restaurants = filtering_service.paginate_results(
            ranked_restaurants,
            limit=10,
            offset=0
        )
        
        logger.info(f"Returning {len(top_restaurants)} recommendations")
        
        return RecommendationResponse(
            success=True,
            data={
                "recommendations": top_restaurants,
                "summary": summary,
                "total_results": len(filtered_restaurants)
            },
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.get("/locations", response_model=LocationResponse)
async def get_locations():
    """
    Get list of available restaurant locations
    
    Returns:
        List of unique location names
    """
    try:
        logger.info("Fetching available locations")
        
        locations = data_service.get_available_locations_db()
        
        if not locations:
            logger.warning("No locations found")
            return LocationResponse(
                success=False,
                data=None,
                error="No locations available"
            )
        
        logger.info(f"Returning {len(locations)} locations")
        
        return LocationResponse(
            success=True,
            data=locations,
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get locations")


@router.get("/cuisines", response_model=CuisineResponse)
async def get_cuisines():
    """
    Get list of available cuisine types
    
    Returns:
        List of unique cuisine names
    """
    try:
        logger.info("Fetching available cuisines")
        
        cuisines = data_service.get_available_cuisines_db()
        
        if not cuisines:
            logger.warning("No cuisines found")
            return CuisineResponse(
                success=False,
                data=None,
                error="No cuisines available"
            )
        
        logger.info(f"Returning {len(cuisines)} cuisines")
        
        return CuisineResponse(
            success=True,
            data=cuisines,
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error getting cuisines: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cuisines")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status of the API
    """
    try:
        # Test database connection
        db = data_service.get_database() if hasattr(data_service, 'get_database') else None
        if db:
            db_healthy = db.test_connection()
        else:
            from app.db.connection import get_database
            db = get_database()
            db_healthy = db.test_connection()
        
        if db_healthy:
            return HealthResponse(
                status="healthy",
                service="recommendation-api"
            )
        else:
            return HealthResponse(
                status="degraded",
                service="recommendation-api"
            )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="recommendation-api"
        )


@router.get("/restaurant/{restaurant_id}")
async def get_restaurant_by_id(restaurant_id: int):
    """
    Get a specific restaurant by ID
    
    Args:
        restaurant_id: Restaurant ID
        
    Returns:
        Restaurant details
    """
    try:
        logger.info(f"Fetching restaurant with ID: {restaurant_id}")
        
        restaurant = data_service.get_restaurant_by_id_db(restaurant_id)
        
        if not restaurant:
            logger.warning(f"Restaurant with ID {restaurant_id} not found")
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        logger.info(f"Returning restaurant: {restaurant['name']}")
        
        return {
            "success": True,
            "data": restaurant
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting restaurant: {e}")
        raise HTTPException(status_code=500, detail="Failed to get restaurant")
