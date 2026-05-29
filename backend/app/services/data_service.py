"""
Data Service for Restaurant Recommendation System
Handles dataset loading, caching, and CRUD operations for restaurant data
"""

import logging
import os
from typing import Optional, List, Dict, Any
import pandas as pd
from datasets import load_dataset
import redis
import json
from datetime import datetime

from ..db.connection import get_database
from ..db.models import Restaurant, MenuItem

logger = logging.getLogger(__name__)


class DataService:
    """Service for managing restaurant data operations"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize data service
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
        
        self.dataset_cache = None
        self.dataset_cache_key = "zomato:dataset:cached"
    
    def load_zomato_dataset(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load Zomato dataset from Hugging Face
        
        Args:
            use_cache: Whether to use cached dataset if available
            
        Returns:
            DataFrame containing restaurant data
            
        Raises:
            ConnectionError: If dataset cannot be loaded
            DatasetEmptyError: If dataset is empty
        """
        try:
            # Check cache first (only if Redis is available)
            if use_cache and self.redis_client:
                try:
                    cached_data = self.redis_client.get(self.dataset_cache_key)
                    if cached_data:
                        logger.info("Loading dataset from cache")
                        self.dataset_cache = pd.read_json(cached_data)
                        return self.dataset_cache
                except Exception as e:
                    logger.warning(f"Failed to read from cache: {e}")
            
            # Load from Hugging Face
            logger.info("Loading dataset from Hugging Face...")
            dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
            
            # Convert to pandas DataFrame
            if "train" in dataset:
                df = dataset["train"].to_pandas()
            else:
                df = dataset.to_pandas()
            
            # Validate dataset
            if df.empty:
                raise DatasetEmptyError("Dataset is empty")
            
            logger.info(f"Loaded {len(df)} restaurants from dataset")
            
            # Cache the dataset (only if Redis is available)
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        self.dataset_cache_key,
                        86400,  # 24 hours TTL
                        df.to_json()
                    )
                    logger.info("Dataset cached successfully")
                except Exception as e:
                    logger.warning(f"Failed to cache dataset: {e}")
            
            self.dataset_cache = df
            return df
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise ConnectionError(f"Failed to load dataset: {str(e)}")
    
    def save_dataset_locally(self, df: pd.DataFrame, filepath: str = "backend/data/zomato_dataset.csv"):
        """
        Save dataset locally to avoid repeated downloads
        
        Args:
            df: DataFrame to save
            filepath: Path to save the dataset
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            df.to_csv(filepath, index=False)
            logger.info(f"Dataset saved locally to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save dataset locally: {e}")
            raise
    
    def load_dataset_from_local(self, filepath: str = "backend/data/zomato_dataset.csv") -> Optional[pd.DataFrame]:
        """
        Load dataset from local file
        
        Args:
            filepath: Path to local dataset file
            
        Returns:
            DataFrame if file exists, None otherwise
        """
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"Loaded {len(df)} restaurants from local file")
                return df
            return None
        except Exception as e:
            logger.error(f"Failed to load local dataset: {e}")
            return None
    
    def get_restaurant_by_id(self, restaurant_id: int, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Get restaurant by ID
        
        Args:
            restaurant_id: Restaurant ID
            df: DataFrame containing restaurant data
            
        Returns:
            Restaurant data as dictionary, or None if not found
        """
        try:
            restaurant = df[df['id'] == restaurant_id]
            if not restaurant.empty:
                return restaurant.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get restaurant by ID: {e}")
            return None
    
    def get_all_restaurants(self, df: pd.DataFrame, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all restaurants with pagination
        
        Args:
            df: DataFrame containing restaurant data
            limit: Maximum number of restaurants to return
            offset: Number of restaurants to skip
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            restaurants = df.iloc[offset:offset + limit]
            return restaurants.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to get all restaurants: {e}")
            return []
    
    def get_restaurants_by_location(self, location: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get restaurants by location
        
        Args:
            location: Location name
            df: DataFrame containing restaurant data
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            # Case-insensitive search
            restaurants = df[df['location'].str.lower() == location.lower()]
            return restaurants.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to get restaurants by location: {e}")
            return []
    
    def get_restaurants_by_cuisine(self, cuisine: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get restaurants by cuisine
        
        Args:
            cuisine: Cuisine type
            df: DataFrame containing restaurant data
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            # Case-insensitive search
            restaurants = df[df['cuisine'].str.lower() == cuisine.lower()]
            return restaurants.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to get restaurants by cuisine: {e}")
            return []
    
    def get_available_locations(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of available locations
        
        Args:
            df: DataFrame containing restaurant data
            
        Returns:
            List of unique location names
        """
        try:
            locations = df['location'].unique().tolist()
            return sorted([loc for loc in locations if pd.notna(loc)])
        except Exception as e:
            logger.error(f"Failed to get available locations: {e}")
            return []
    
    def get_available_cuisines(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of available cuisines
        
        Args:
            df: DataFrame containing restaurant data
            
        Returns:
            List of unique cuisine names
        """
        try:
            cuisines = df['cuisine'].unique().tolist()
            return sorted([cuisine for cuisine in cuisines if pd.notna(cuisine)])
        except Exception as e:
            logger.error(f"Failed to get available cuisines: {e}")
            return []
    
    def clear_cache(self):
        """Clear the dataset cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(self.dataset_cache_key)
                logger.info("Dataset cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    # Database-integrated CRUD operations
    
    def get_restaurant_by_id_db(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get restaurant by ID from database
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            Restaurant data as dictionary, or None if not found
        """
        try:
            db = get_database()
            with db.get_session() as session:
                restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
                if restaurant:
                    return restaurant.to_dict()
                return None
        except Exception as e:
            logger.error(f"Failed to get restaurant by ID from database: {e}")
            return None
    
    def get_all_restaurants_db(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all restaurants from database with pagination
        
        Args:
            limit: Maximum number of restaurants to return
            offset: Number of restaurants to skip
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                restaurants = session.query(Restaurant).offset(offset).limit(limit).all()
                return [restaurant.to_dict() for restaurant in restaurants]
        except Exception as e:
            logger.error(f"Failed to get all restaurants from database: {e}")
            return []
    
    def get_restaurants_by_location_db(self, location: str) -> List[Dict[str, Any]]:
        """
        Get restaurants by location from database
        
        Args:
            location: Location name
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                restaurants = session.query(Restaurant).filter(
                    Restaurant.location.ilike(f"%{location}%")
                ).all()
                return [restaurant.to_dict() for restaurant in restaurants]
        except Exception as e:
            logger.error(f"Failed to get restaurants by location from database: {e}")
            return []
    
    def get_restaurants_by_cuisine_db(self, cuisine: str) -> List[Dict[str, Any]]:
        """
        Get restaurants by cuisine from database
        
        Args:
            cuisine: Cuisine type
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                restaurants = session.query(Restaurant).filter(
                    Restaurant.cuisine.ilike(f"%{cuisine}%")
                ).all()
                return [restaurant.to_dict() for restaurant in restaurants]
        except Exception as e:
            logger.error(f"Failed to get restaurants by cuisine from database: {e}")
            return []
    
    def get_restaurants_by_rating_db(self, min_rating: float) -> List[Dict[str, Any]]:
        """
        Get restaurants by minimum rating from database
        
        Args:
            min_rating: Minimum rating threshold
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                restaurants = session.query(Restaurant).filter(
                    Restaurant.rating >= min_rating
                ).all()
                return [restaurant.to_dict() for restaurant in restaurants]
        except Exception as e:
            logger.error(f"Failed to get restaurants by rating from database: {e}")
            return []
    
    def get_available_locations_db(self) -> List[str]:
        """
        Get list of available locations from database
        
        Returns:
            List of unique location names
        """
        try:
            cache_key = "zomato:locations"
            if self.redis_client:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            db = get_database()
            with db.get_session() as session:
                locations = session.query(Restaurant.location).distinct().all()
                location_list = sorted([loc[0] for loc in locations if loc[0]])
                
                if self.redis_client:
                    self.redis_client.setex(cache_key, 3600, json.dumps(location_list))
                
                return location_list
        except Exception as e:
            logger.error(f"Failed to get available locations from database: {e}")
            return []
    
    def get_available_cuisines_db(self) -> List[str]:
        """
        Get list of available cuisines from database
        
        Returns:
            List of unique cuisine names
        """
        try:
            cache_key = "zomato:cuisines"
            if self.redis_client:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            db = get_database()
            with db.get_session() as session:
                cuisines = session.query(Restaurant.cuisine).distinct().all()
                cuisine_list = sorted([cuisine[0] for cuisine in cuisines if cuisine[0]])
                
                if self.redis_client:
                    self.redis_client.setex(cache_key, 3600, json.dumps(cuisine_list))
                
                return cuisine_list
        except Exception as e:
            logger.error(f"Failed to get available cuisines from database: {e}")
            return []
    
    def search_restaurants_db(
        self,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        budget_category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search restaurants with multiple filters from database
        
        Args:
            location: Location filter
            cuisine: Cuisine filter
            min_rating: Minimum rating filter
            budget_category: Budget category filter (low, medium, high)
            limit: Maximum number of results
            
        Returns:
            List of restaurant dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                query = session.query(Restaurant)
                
                if location:
                    query = query.filter(Restaurant.location.ilike(f"%{location}%"))
                
                if cuisine:
                    query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
                
                if min_rating is not None:
                    query = query.filter(Restaurant.rating >= min_rating)
                
                if budget_category:
                    query = query.filter(Restaurant.budget_category == budget_category)
                
                restaurants = query.limit(limit).all()
                return [restaurant.to_dict() for restaurant in restaurants]
        except Exception as e:
            logger.error(f"Failed to search restaurants in database: {e}")
            return []
    
    def get_menu_items_by_restaurant_db(self, restaurant_id: int) -> List[Dict[str, Any]]:
        """
        Get menu items for a specific restaurant from database
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            List of menu item dictionaries
        """
        try:
            db = get_database()
            with db.get_session() as session:
                menu_items = session.query(MenuItem).filter(
                    MenuItem.restaurant_id == restaurant_id,
                    MenuItem.is_available == 1
                ).all()
                return [item.to_dict() for item in menu_items]
        except Exception as e:
            logger.error(f"Failed to get menu items from database: {e}")
            return []


class DatasetEmptyError(Exception):
    """Raised when dataset is empty"""
    pass


class DatasetLoadError(Exception):
    """Raised when dataset cannot be loaded"""
    pass