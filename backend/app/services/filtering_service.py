"""
Filtering Service for Restaurant Recommendation System
Handles filtering, ranking, and scoring of restaurant recommendations
"""

import logging
from typing import List, Dict, Any, Optional
from fuzzywuzzy import fuzz
import re

logger = logging.getLogger(__name__)


class FilteringService:
    """Service for filtering and ranking restaurants"""
    
    def __init__(self):
        """Initialize filtering service"""
        self.budget_weights = {
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7
        }
        self.rating_weight = 0.4
        self.preference_weight = 0.3
    
    def filter_by_location(self, restaurants: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
        """
        Filter restaurants by location with fuzzy matching
        
        Args:
            restaurants: List of restaurant dictionaries
            location: Location to filter by
            
        Returns:
            Filtered list of restaurants
        """
        if not location:
            return restaurants
        
        location_lower = location.lower()
        filtered = []
        
        for restaurant in restaurants:
            rest_location = restaurant.get('location', '').lower()
            
            # Exact match
            if location_lower == rest_location:
                filtered.append(restaurant)
            # Fuzzy match (allowing for typos)
            elif fuzz.ratio(location_lower, rest_location) > 70:
                filtered.append(restaurant)
            # Partial match (location contains search term or vice versa)
            elif location_lower in rest_location or rest_location in location_lower:
                filtered.append(restaurant)
        
        logger.info(f"Location filter: {len(restaurants)} -> {len(filtered)} restaurants")
        return filtered
    
    def filter_by_budget(self, restaurants: List[Dict[str, Any]], budget: str) -> List[Dict[str, Any]]:
        """
        Filter restaurants by budget category
        
        Args:
            restaurants: List of restaurant dictionaries
            budget: Budget category (low, medium, high)
            
        Returns:
            Filtered list of restaurants
        """
        if not budget:
            return restaurants
        
        budget_lower = budget.lower()
        filtered = []
        
        for restaurant in restaurants:
            rest_budget = restaurant.get('budget_category', '').lower()
            
            if rest_budget == budget_lower:
                filtered.append(restaurant)
        
        logger.info(f"Budget filter: {len(restaurants)} -> {len(filtered)} restaurants")
        return filtered
    
    def filter_by_cuisine(self, restaurants: List[Dict[str, Any]], cuisine: str) -> List[Dict[str, Any]]:
        """
        Filter restaurants by cuisine with fuzzy matching
        
        Args:
            restaurants: List of restaurant dictionaries
            cuisine: Cuisine to filter by
            
        Returns:
            Filtered list of restaurants
        """
        if not cuisine:
            return restaurants
        
        cuisine_lower = cuisine.lower()
        filtered = []
        
        for restaurant in restaurants:
            rest_cuisine = restaurant.get('cuisine', '').lower()
            
            # Exact match
            if cuisine_lower == rest_cuisine:
                filtered.append(restaurant)
            # Fuzzy match
            elif fuzz.ratio(cuisine_lower, rest_cuisine) > 70:
                filtered.append(restaurant)
            # Partial match (handle multi-cuisine like "North Indian, Mughlai")
            elif cuisine_lower in rest_cuisine or rest_cuisine in cuisine_lower:
                filtered.append(restaurant)
        
        logger.info(f"Cuisine filter: {len(restaurants)} -> {len(filtered)} restaurants")
        return filtered
    
    def filter_by_rating(self, restaurants: List[Dict[str, Any]], min_rating: float) -> List[Dict[str, Any]]:
        """
        Filter restaurants by minimum rating
        
        Args:
            restaurants: List of restaurant dictionaries
            min_rating: Minimum rating threshold
            
        Returns:
            Filtered list of restaurants
        """
        if min_rating is None or min_rating <= 0:
            return restaurants
        
        filtered = [
            restaurant for restaurant in restaurants
            if restaurant.get('rating', 0) >= min_rating
        ]
        
        logger.info(f"Rating filter: {len(restaurants)} -> {len(filtered)} restaurants")
        return filtered
    
    def apply_additional_filters(
        self,
        restaurants: List[Dict[str, Any]],
        preferences: str
    ) -> List[Dict[str, Any]]:
        """
        Apply additional preference-based filters
        
        Args:
            restaurants: List of restaurant dictionaries
            preferences: Additional preferences text
            
        Returns:
            Filtered list of restaurants with preference scores
        """
        if not preferences:
            return restaurants
        
        preferences_lower = preferences.lower()
        
        # Extract keywords from preferences
        keywords = self._extract_keywords(preferences_lower)
        
        for restaurant in restaurants:
            score = 0
            restaurant_text = (
                restaurant.get('name', '').lower() + ' ' +
                restaurant.get('reviews', '').lower() + ' ' +
                restaurant.get('cuisine', '').lower()
            )
            
            # Check for keyword matches
            for keyword in keywords:
                if keyword in restaurant_text:
                    score += 1
            
            restaurant['preference_score'] = score
        
        # Sort by preference score
        restaurants.sort(key=lambda x: x.get('preference_score', 0), reverse=True)
        
        logger.info(f"Applied preference filters to {len(restaurants)} restaurants")
        return restaurants
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from preference text
        
        Args:
            text: Preference text
            
        Returns:
            List of keywords
        """
        # Common keywords to look for
        common_keywords = [
            'family', 'kid', 'child', 'outdoor', 'terrace', 'rooftop',
            'romantic', 'couple', 'date', 'quiet', 'peaceful',
            'party', 'loud', 'music', 'live', 'bar', 'pub',
            'quick', 'fast', 'delivery', 'takeaway',
            'vegan', 'vegetarian', 'gluten', 'allergy',
            'parking', 'wifi', 'ac', 'air conditioned',
            'seafood', 'breakfast', 'brunch', 'dinner', 'lunch'
        ]
        
        keywords = []
        for keyword in common_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    def calculate_match_score(
        self,
        restaurant: Dict[str, Any],
        budget: str,
        min_rating: float,
        preferences: str
    ) -> float:
        """
        Calculate overall match score for a restaurant
        
        Args:
            restaurant: Restaurant dictionary
            budget: Requested budget category
            min_rating: Minimum rating threshold
            preferences: Additional preferences
            
        Returns:
            Match score between 0 and 1
        """
        score = 0.0
        
        # Rating score (0-1)
        rating = restaurant.get('rating', 0)
        rating_score = rating / 5.0
        score += rating_score * self.rating_weight
        
        # Budget match score (0-1)
        rest_budget = restaurant.get('budget_category', '').lower()
        if rest_budget == budget.lower():
            score += self.budget_weights.get(budget.lower(), 0.5)
        
        # Preference score (0-1)
        preference_score = restaurant.get('preference_score', 0)
        if preference_score > 0:
            # Normalize preference score (assuming max 5 keywords)
            normalized_preference = min(preference_score / 5.0, 1.0)
            score += normalized_preference * self.preference_weight
        
        # Normalize to 0-1 range
        max_possible_score = self.rating_weight + self.budget_weights.get(budget.lower(), 0.5) + self.preference_weight
        final_score = min(score / max_possible_score, 1.0)
        
        return round(final_score, 2)
    
    def rank_restaurants(
        self,
        restaurants: List[Dict[str, Any]],
        budget: str,
        min_rating: float,
        preferences: str
    ) -> List[Dict[str, Any]]:
        """
        Rank restaurants by match score
        
        Args:
            restaurants: List of restaurant dictionaries
            budget: Requested budget category
            min_rating: Minimum rating threshold
            preferences: Additional preferences
            
        Returns:
            Ranked list of restaurants with match scores
        """
        for restaurant in restaurants:
            match_score = self.calculate_match_score(
                restaurant, budget, min_rating, preferences
            )
            restaurant['match_score'] = match_score
        
        # Sort by match score (descending)
        restaurants.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"Ranked {len(restaurants)} restaurants by match score")
        return restaurants
    
    def apply_filters(
        self,
        restaurants: List[Dict[str, Any]],
        location: str,
        budget: str,
        cuisine: str,
        min_rating: float,
        preferences: str
    ) -> List[Dict[str, Any]]:
        """
        Apply all filters in sequence
        
        Args:
            restaurants: List of restaurant dictionaries
            location: Location filter
            budget: Budget filter
            cuisine: Cuisine filter
            min_rating: Rating filter
            preferences: Additional preferences
            
        Returns:
            Filtered and ranked list of restaurants
        """
        logger.info(f"Starting filtering with {len(restaurants)} restaurants")
        
        # Apply filters
        filtered = self.filter_by_location(restaurants, location)
        filtered = self.filter_by_cuisine(filtered, cuisine)
        filtered = self.filter_by_budget(filtered, budget)
        filtered = self.filter_by_rating(filtered, min_rating)
        
        # Apply additional preference filters
        if preferences:
            filtered = self.apply_additional_filters(filtered, preferences)
        
        # Rank by match score
        ranked = self.rank_restaurants(filtered, budget, min_rating, preferences)
        
        logger.info(f"Filtering complete: {len(restaurants)} -> {len(ranked)} restaurants")
        return ranked
    
    def paginate_results(
        self,
        restaurants: List[Dict[str, Any]],
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Paginate restaurant results
        
        Args:
            restaurants: List of restaurant dictionaries
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            Paginated list of restaurants
        """
        total = len(restaurants)
        paginated = restaurants[offset:offset + limit]
        
        logger.info(f"Pagination: total={total}, returned={len(paginated)}, offset={offset}, limit={limit}")
        return paginated
    
    def generate_explanation(
        self,
        restaurant: Dict[str, Any],
        budget: str,
        cuisine: str,
        preferences: str
    ) -> str:
        """
        Generate explanation for why a restaurant was recommended
        
        Args:
            restaurant: Restaurant dictionary
            budget: Requested budget category
            cuisine: Requested cuisine
            preferences: Additional preferences
            
        Returns:
            Explanation text
        """
        explanations = []
        
        # Rating explanation
        rating = restaurant.get('rating', 0)
        if rating >= 4.5:
            explanations.append(f"It has an excellent rating of {rating}")
        elif rating >= 4.0:
            explanations.append(f"It has a very good rating of {rating}")
        elif rating >= 3.5:
            explanations.append(f"It has a good rating of {rating}")
        
        # Budget explanation
        rest_budget = restaurant.get('budget_category', '')
        if rest_budget.lower() == budget.lower():
            explanations.append(f"It fits your {budget} budget perfectly")
        
        # Cuisine explanation
        rest_cuisine = restaurant.get('cuisine', '')
        if cuisine.lower() in rest_cuisine.lower():
            explanations.append(f"It serves {rest_cuisine} cuisine")
        
        # Preference explanation
        if preferences and restaurant.get('preference_score', 0) > 0:
            explanations.append("It matches your additional preferences")
        
        # Combine explanations
        if explanations:
            explanation = "This restaurant is recommended because " + ", ".join(explanations) + "."
        else:
            explanation = "This restaurant matches your search criteria."
        
        return explanation
