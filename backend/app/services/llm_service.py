"""
LLM Service for Restaurant Recommendation System
Handles integration with Groq API for generating recommendations and explanations
"""

import logging
import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import redis

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based restaurant recommendations using Groq"""
    
    # System prompt for restaurant recommendations
    SYSTEM_PROMPT = """You are a restaurant recommendation expert. Your task is to analyze user preferences and restaurant data to provide personalized, helpful recommendations.

Consider factors like:
- Cuisine type and quality
- Budget and value for money
- Location convenience
- Rating and reviews
- Additional user preferences (family-friendly, outdoor seating, etc.)

Provide clear, concise explanations for each recommendation (2-3 sentences)."""
    
    # User prompt template
    USER_PROMPT_TEMPLATE = """User Preferences:
- Location: {location}
- Budget: {budget}
- Cuisine: {cuisine}
- Minimum Rating: {min_rating}
- Additional Preferences: {additional_preferences}

Available Restaurants:
{restaurant_data}

Please respond in JSON format with the following structure:
{{
  "rankings": [
    {{
      "id": <restaurant_id>,
      "rank": <1-10>,
      "explanation": "<2-3 sentence explanation>"
    }}
  ],
  "summary": "<brief summary of top 3 recommendations>"
}}"""
    
    def __init__(self):
        """Initialize LLM service with Groq client"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set in environment variables")
        
        self.model = os.getenv("LLM_MODEL", "llama3-70b-8192")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        
        # Initialize Groq client
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Groq client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # Initialize Redis for caching
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis cache for LLM responses")
        except Exception as e:
            logger.warning(f"Could not connect to Redis for caching: {e}")
        
        # Cache TTL in seconds (24 hours)
        self.cache_ttl = int(os.getenv("CACHE_TTL", "86400"))
    
    def _generate_cache_key(self, user_preferences: Dict[str, Any], restaurant_ids: List[int]) -> str:
        """
        Generate cache key for LLM response
        
        Args:
            user_preferences: User preference dictionary
            restaurant_ids: List of restaurant IDs
            
        Returns:
            Cache key string
        """
        # Create a hash of preferences and restaurant IDs
        data = json.dumps({
            "preferences": user_preferences,
            "restaurants": sorted(restaurant_ids)
        }, sort_keys=True)
        hash_key = hashlib.md5(data.encode()).hexdigest()
        return f"llm:recommendations:{hash_key}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached LLM response
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None
        """
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("LLM response cache hit")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Failed to get cached response: {e}")
        
        return None
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """
        Cache LLM response
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(response))
            logger.info("LLM response cached successfully")
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    def _format_restaurant_data(self, restaurants: List[Dict[str, Any]], limit: int = 10) -> str:
        """
        Format restaurant data for LLM prompt
        
        Args:
            restaurants: List of restaurant dictionaries
            limit: Maximum number of restaurants to include
            
        Returns:
            Formatted string
        """
        formatted = []
        for i, restaurant in enumerate(restaurants[:limit], 1):
            formatted.append(f"""
{i}. ID: {restaurant.get('id')}
   Name: {restaurant.get('name')}
   Location: {restaurant.get('location')}
   Cuisine: {restaurant.get('cuisine')}
   Rating: {restaurant.get('rating')}
   Cost for Two: {restaurant.get('cost_for_two')}
   Budget Category: {restaurant.get('budget_category')}
   Reviews: {restaurant.get('reviews', 'N/A')}
""")
        return "\n".join(formatted)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_llm(self, prompt: str) -> str:
        """
        Call Groq API with retry logic
        
        Args:
            prompt: The prompt to send
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If API call fails after retries
        """
        if not self.client:
            raise Exception("Groq client not initialized")
        
        try:
            logger.info(f"Calling Groq API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response
        
        Args:
            response_text: Raw LLM response text
            
        Returns:
            Parsed response dictionary
            
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            response = json.loads(response_text)
            
            # Validate structure
            if "rankings" not in response:
                raise ValueError("Response missing 'rankings' field")
            
            if not isinstance(response["rankings"], list):
                raise ValueError("'rankings' must be a list")
            
            return response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"Invalid JSON response: {response_text}")
    
    def generate_recommendations(
        self,
        user_preferences: Dict[str, Any],
        restaurants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate LLM-based restaurant recommendations
        
        Args:
            user_preferences: User preference dictionary
            restaurants: List of restaurant dictionaries
            
        Returns:
            Dictionary with rankings and summary
        """
        if not self.client:
            logger.warning("Groq client not initialized, using fallback")
            return self._fallback_recommendation(restaurants)
        
        # Check cache
        restaurant_ids = [r.get('id') for r in restaurants]
        cache_key = self._generate_cache_key(user_preferences, restaurant_ids)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        try:
            # Format restaurant data
            restaurant_data = self._format_restaurant_data(restaurants, limit=10)
            
            # Build prompt
            prompt = self.USER_PROMPT_TEMPLATE.format(
                location=user_preferences.get('location', ''),
                budget=user_preferences.get('budget', ''),
                cuisine=user_preferences.get('cuisine', ''),
                min_rating=user_preferences.get('min_rating', 0),
                additional_preferences=user_preferences.get('additional_preferences', ''),
                restaurant_data=restaurant_data
            )
            
            # Call LLM
            response_text = self._call_llm(prompt)
            
            # Parse response
            parsed_response = self._parse_llm_response(response_text)
            
            # Cache response
            self._cache_response(cache_key, parsed_response)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Failed to generate LLM recommendations: {e}")
            return self._fallback_recommendation(restaurants)
    
    def generate_explanation(
        self,
        restaurant: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for a single restaurant
        
        Args:
            restaurant: Restaurant dictionary
            user_preferences: User preference dictionary
            
        Returns:
            Explanation text
        """
        try:
            prompt = f"""Generate a brief explanation (2-3 sentences) for why this restaurant is recommended:

Restaurant: {restaurant.get('name')}
Location: {restaurant.get('location')}
Cuisine: {restaurant.get('cuisine')}
Rating: {restaurant.get('rating')}
Cost for Two: {restaurant.get('cost_for_two')}
Budget Category: {restaurant.get('budget_category')}

User Preferences:
- Budget: {user_preferences.get('budget')}
- Cuisine: {user_preferences.get('cuisine')}
- Additional: {user_preferences.get('additional_preferences', 'None')}

Provide a concise explanation."""
            
            if not self.client:
                return f"This restaurant has a rating of {restaurant.get('rating')} and serves {restaurant.get('cuisine')} cuisine."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"This restaurant has a rating of {restaurant.get('rating')} and serves {restaurant.get('cuisine')} cuisine."
    
    def rank_with_llm(
        self,
        restaurants: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank restaurants using LLM
        
        Args:
            restaurants: List of restaurant dictionaries
            user_preferences: User preference dictionary
            
        Returns:
            Ranked list of restaurants with LLM rankings
        """
        try:
            response = self.generate_recommendations(user_preferences, restaurants)
            rankings = response.get("rankings", [])
            
            # Create ranking map
            ranking_map = {r["id"]: r for r in rankings}
            
            # Add rankings to restaurants
            for restaurant in restaurants:
                restaurant_id = restaurant.get('id')
                if restaurant_id in ranking_map:
                    restaurant["llm_rank"] = ranking_map[restaurant_id]["rank"]
                    restaurant["llm_explanation"] = ranking_map[restaurant_id]["explanation"]
                else:
                    restaurant["llm_rank"] = 999
                    restaurant["llm_explanation"] = None
            
            # Sort by LLM rank
            ranked = sorted(restaurants, key=lambda x: x.get("llm_rank", 999))
            
            return ranked
            
        except Exception as e:
            logger.error(f"Failed to rank with LLM: {e}")
            return restaurants
    
    def summarize_recommendations(
        self,
        restaurants: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Generate summary of top recommendations
        
        Args:
            restaurants: List of restaurant dictionaries
            user_preferences: User preference dictionary
            
        Returns:
            Summary text
        """
        try:
            response = self.generate_recommendations(user_preferences, restaurants)
            return response.get("summary", "Based on your preferences, these restaurants are highly recommended.")
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Found {len(restaurants)} restaurants matching your preferences."
    
    def _fallback_recommendation(self, restaurants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fallback recommendation when LLM is unavailable
        
        Args:
            restaurants: List of restaurant dictionaries
            
        Returns:
            Fallback response dictionary
        """
        rankings = []
        for i, restaurant in enumerate(restaurants[:10], 1):
            rankings.append({
                "id": restaurant.get('id'),
                "rank": i,
                "explanation": f"This restaurant has a rating of {restaurant.get('rating')} and serves {restaurant.get('cuisine')} cuisine."
            })
        
        return {
            "rankings": rankings,
            "summary": f"Found {len(restaurants)} restaurants matching your preferences."
        }
    
    def clear_cache(self):
        """Clear all LLM response cache"""
        if not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys("llm:recommendations:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached LLM responses")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
