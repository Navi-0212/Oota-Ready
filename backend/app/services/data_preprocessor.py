"""
Data Preprocessor for Restaurant Recommendation System
Handles data cleaning, transformation, and validation
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Class for preprocessing restaurant data"""
    
    REQUIRED_FIELDS = ['name', 'location', 'cuisine', 'rating', 'cost_for_two']
    
    def __init__(self):
        """Initialize data preprocessor"""
        self.preprocessing_stats = {}
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the dataset by handling missing values, duplicates, and invalid data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning...")
        initial_count = len(df)
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove duplicates
        df_clean = self._remove_duplicates(df_clean)
        
        # Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # Validate and clean data types
        df_clean = self._validate_data_types(df_clean)
        
        # Remove invalid records
        df_clean = self._remove_invalid_records(df_clean)
        
        final_count = len(df_clean)
        removed_count = initial_count - final_count
        
        logger.info(f"Data cleaning completed. Removed {removed_count} records. Remaining: {final_count}")
        
        self.preprocessing_stats['cleaning'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'removed_count': removed_count
        }
        
        return df_clean
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records based on name and location
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        
        # Check for duplicates based on name and location
        duplicates = df.duplicated(subset=['name', 'location'], keep='first')
        
        if duplicates.any():
            df = df[~duplicates]
            removed = duplicates.sum()
            logger.warning(f"Removed {removed} duplicate records")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        # Check for missing required fields
        for field in self.REQUIRED_FIELDS:
            if field not in df.columns:
                logger.error(f"Required field '{field}' not found in dataset")
                raise SchemaError(f"Missing required field: {field}")
        
        # Drop rows with missing required fields
        initial_count = len(df)
        df = df.dropna(subset=self.REQUIRED_FIELDS)
        removed = initial_count - len(df)
        
        if removed > 0:
            logger.warning(f"Removed {removed} records with missing required fields")
        
        # Fill optional fields with defaults
        if 'votes' in df.columns:
            df['votes'] = df['votes'].fillna(0)
        
        if 'reviews' in df.columns:
            df['reviews'] = df['reviews'].fillna('')
        
        return df
    
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and convert data types
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with correct data types
        """
        # Convert rating to numeric
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Convert cost to numeric
        if 'cost_for_two' in df.columns:
            df['cost_for_two'] = pd.to_numeric(df['cost_for_two'], errors='coerce')
        
        # Convert votes to numeric
        if 'votes' in df.columns:
            df['votes'] = pd.to_numeric(df['votes'], errors='coerce')
        
        # Ensure text fields are strings
        text_fields = ['name', 'location', 'cuisine', 'address', 'phone', 'url']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str)
        
        return df
    
    def _remove_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove records with invalid data
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with invalid records removed
        """
        initial_count = len(df)
        
        # Remove records with invalid rating (not in range 0-5)
        if 'rating' in df.columns:
            df = df[(df['rating'] >= 0) & (df['rating'] <= 5)]
        
        # Remove records with invalid cost (must be positive)
        if 'cost_for_two' in df.columns:
            df = df[df['cost_for_two'] > 0]
        
        # Remove records with empty name
        if 'name' in df.columns:
            df = df[df['name'].str.strip() != '']
        
        removed = initial_count - len(df)
        if removed > 0:
            logger.warning(f"Removed {removed} records with invalid data")
        
        return df
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data by normalizing text fields and standardizing values
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Transformed DataFrame
        """
        logger.info("Starting data transformation...")
        
        df_transformed = df.copy()
        
        # Normalize text fields
        df_transformed = self._normalize_text_fields(df_transformed)
        
        # Standardize location names
        df_transformed = self._standardize_locations(df_transformed)
        
        # Standardize cuisine names
        df_transformed = self._standardize_cuisines(df_transformed)
        
        # Add derived fields
        df_transformed = self._add_derived_fields(df_transformed)
        
        logger.info("Data transformation completed")
        
        return df_transformed
    
    def _normalize_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize text fields (strip whitespace, title case)
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with normalized text fields
        """
        text_fields = ['name', 'location', 'cuisine', 'address']
        
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].str.strip()
                # Title case for better readability
                if field in ['name', 'location', 'cuisine']:
                    df[field] = df[field].str.title()
        
        return df
    
    def _standardize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize location names (handle common variations)
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with standardized locations
        """
        if 'location' not in df.columns:
            return df
        
        # Common location name variations mapping
        location_mapping = {
            'New Delhi': 'Delhi',
            'Ncr': 'Delhi NCR',
            'Noida': 'Delhi NCR',
            'Gurgaon': 'Delhi NCR',
            'Gurugram': 'Delhi NCR',
            'Bangalore': 'Bengaluru',
            'Bombay': 'Mumbai',
            'Calcutta': 'Kolkata',
            'Pune City': 'Pune',
            'Hyderabad City': 'Hyderabad',
        }
        
        # Apply mapping
        df['location'] = df['location'].replace(location_mapping)
        
        return df
    
    def _standardize_cuisines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize cuisine names (handle common variations)
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with standardized cuisines
        """
        if 'cuisine' not in df.columns:
            return df
        
        # Common cuisine name variations mapping
        cuisine_mapping = {
            'North Indian': 'North Indian',
            'North Indian, Mughlai': 'North Indian',
            'Chinese, Thai': 'Asian',
            'Continental, Italian': 'Continental',
            'Italian, Pizza': 'Italian',
            'Biryani': 'Biryani',
            'South Indian': 'South Indian',
            'Street Food': 'Street Food',
        }
        
        # Apply mapping
        df['cuisine'] = df['cuisine'].replace(cuisine_mapping)
        
        return df
    
    def _add_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add derived fields for analysis
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with derived fields
        """
        # Add budget category based on cost
        if 'cost_for_two' in df.columns:
            df['budget_category'] = df['cost_for_two'].apply(self._categorize_budget)
        
        # Add rating category
        if 'rating' in df.columns:
            df['rating_category'] = df['rating'].apply(self._categorize_rating)
        
        return df
    
    def _categorize_budget(self, cost: float) -> str:
        """
        Categorize budget based on cost for two
        
        Args:
            cost: Cost for two people
            
        Returns:
            Budget category (low, medium, high)
        """
        if pd.isna(cost):
            return 'unknown'
        elif cost <= 500:
            return 'low'
        elif cost <= 1500:
            return 'medium'
        else:
            return 'high'
    
    def _categorize_rating(self, rating: float) -> str:
        """
        Categorize rating
        
        Args:
            rating: Restaurant rating
            
        Returns:
            Rating category
        """
        if pd.isna(rating):
            return 'unrated'
        elif rating >= 4.5:
            return 'excellent'
        elif rating >= 4.0:
            return 'very_good'
        elif rating >= 3.5:
            return 'good'
        elif rating >= 3.0:
            return 'average'
        else:
            return 'below_average'
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate the preprocessed data
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in df.columns:
                errors.append(f"Missing required field: {field}")
            elif df[field].isnull().any():
                errors.append(f"Field '{field}' contains null values")
        
        # Check data ranges
        if 'rating' in df.columns:
            if (df['rating'] < 0).any() or (df['rating'] > 5).any():
                errors.append("Rating values out of range (0-5)")
        
        if 'cost_for_two' in df.columns:
            if (df['cost_for_two'] <= 0).any():
                errors.append("Cost values must be positive")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.error(f"Data validation failed: {errors}")
        
        return is_valid, errors
    
    def get_preprocessing_stats(self) -> Dict:
        """
        Get statistics from preprocessing
        
        Returns:
            Dictionary of preprocessing statistics
        """
        return self.preprocessing_stats


class SchemaError(Exception):
    """Raised when schema validation fails"""
    pass


class DataValidationError(Exception):
    """Raised when data validation fails"""
    pass
