"""
Unit tests for Data Preprocessor
"""

import pytest
import pandas as pd
import numpy as np
from app.services.data_preprocessor import DataPreprocessor, SchemaError, DataValidationError


@pytest.fixture
def preprocessor():
    """Create a DataPreprocessor instance"""
    return DataPreprocessor()


@pytest.fixture
def sample_dirty_data():
    """Create sample dirty data for testing"""
    return pd.DataFrame({
        'name': ['Restaurant A', 'Restaurant B', 'Restaurant C', '', 'Restaurant E'],
        'location': ['Delhi', 'BANGALORE', 'Mumbai', 'Chennai', 'Pune'],
        'cuisine': ['Italian', 'North Indian', 'Chinese', 'South Indian', 'Continental'],
        'rating': [4.5, 3.8, 4.2, 5.5, -1.0],  # Invalid ratings
        'cost_for_two': [1000, 800, 1200, -500, 0],  # Invalid costs
        'votes': [100, 200, None, 400, 500],
        'reviews': ['Great food', None, 'Good service', 'Nice place', None]
    })


@pytest.fixture
def sample_clean_data():
    """Create sample clean data for testing"""
    return pd.DataFrame({
        'name': ['Restaurant A', 'Restaurant B', 'Restaurant C'],
        'location': ['Delhi', 'Bangalore', 'Mumbai'],
        'cuisine': ['Italian', 'North Indian', 'Chinese'],
        'rating': [4.5, 3.8, 4.2],
        'cost_for_two': [1000, 800, 1200],
        'votes': [100, 200, 300],
        'reviews': ['Great food', 'Good service', 'Nice place']
    })


class TestDataPreprocessor:
    """Test cases for DataPreprocessor class"""
    
    def test_remove_duplicates(self, preprocessor, sample_clean_data):
        """Test duplicate removal"""
        # Add duplicate
        data_with_dup = pd.concat([sample_clean_data, sample_clean_data.iloc[[0]]], ignore_index=True)
        
        result = preprocessor._remove_duplicates(data_with_dup)
        
        assert len(result) == len(sample_clean_data)
    
    def test_handle_missing_values(self, preprocessor, sample_dirty_data):
        """Test missing value handling"""
        result = preprocessor._handle_missing_values(sample_dirty_data)
        
        # Should remove rows with empty name
        assert '' not in result['name'].values
        
        # Should fill missing votes with 0
        assert result['votes'].isna().sum() == 0
    
    def test_validate_data_types(self, preprocessor, sample_dirty_data):
        """Test data type validation"""
        result = preprocessor._validate_data_types(sample_dirty_data)
        
        # Check rating is numeric
        assert pd.api.types.is_numeric_dtype(result['rating'])
        
        # Check cost is numeric
        assert pd.api.types.is_numeric_dtype(result['cost_for_two'])
    
    def test_remove_invalid_records(self, preprocessor, sample_dirty_data):
        """Test invalid record removal"""
        result = preprocessor._remove_invalid_records(sample_dirty_data)
        
        # Should remove invalid ratings (not in 0-5 range)
        assert all(result['rating'] >= 0)
        assert all(result['rating'] <= 5)
        
        # Should remove invalid costs (must be positive)
        assert all(result['cost_for_two'] > 0)
    
    def test_clean_data(self, preprocessor, sample_dirty_data):
        """Test complete data cleaning pipeline"""
        result = preprocessor.clean_data(sample_dirty_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert '' not in result['name'].values
        assert all(result['rating'] >= 0)
        assert all(result['rating'] <= 5)
        assert all(result['cost_for_two'] > 0)
    
    def test_normalize_text_fields(self, preprocessor, sample_clean_data):
        """Test text field normalization"""
        data = sample_clean_data.copy()
        data['name'] = ['  restaurant a  ', 'RESTAURANT B', 'Restaurant c']
        
        result = preprocessor._normalize_text_fields(data)
        
        # Check whitespace is stripped
        assert all(result['name'].str.strip() == result['name'])
    
    def test_standardize_locations(self, preprocessor):
        """Test location standardization"""
        data = pd.DataFrame({
            'location': ['New Delhi', 'Bangalore', 'Bombay', 'Noida']
        })
        
        result = preprocessor._standardize_locations(data)
        
        # Check standardization
        assert 'Delhi' in result['location'].values
        assert 'Mumbai' in result['location'].values
    
    def test_standardize_cuisines(self, preprocessor):
        """Test cuisine standardization"""
        data = pd.DataFrame({
            'cuisine': ['North Indian, Mughlai', 'Chinese, Thai', 'Italian, Pizza']
        })
        
        result = preprocessor._standardize_cuisines(data)
        
        # Check standardization
        assert 'North Indian' in result['cuisine'].values
    
    def test_categorize_budget(self, preprocessor):
        """Test budget categorization"""
        assert preprocessor._categorize_budget(300) == 'low'
        assert preprocessor._categorize_budget(1000) == 'medium'
        assert preprocessor._categorize_budget(2000) == 'high'
    
    def test_categorize_rating(self, preprocessor):
        """Test rating categorization"""
        assert preprocessor._categorize_rating(4.7) == 'excellent'
        assert preprocessor._categorize_rating(4.2) == 'very_good'
        assert preprocessor._categorize_rating(3.7) == 'good'
        assert preprocessor._categorize_rating(3.2) == 'average'
        assert preprocessor._categorize_rating(2.5) == 'below_average'
    
    def test_validate_data_success(self, preprocessor, sample_clean_data):
        """Test successful data validation"""
        is_valid, errors = preprocessor.validate_data(sample_clean_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_data_failure_empty(self, preprocessor):
        """Test validation failure with empty data"""
        empty_data = pd.DataFrame()
        
        is_valid, errors = preprocessor.validate_data(empty_data)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_data_failure_missing_field(self, preprocessor):
        """Test validation failure with missing required field"""
        data = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi']
            # Missing 'cuisine', 'rating', 'cost_for_two'
        })
        
        is_valid, errors = preprocessor.validate_data(data)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_data_failure_invalid_rating(self, preprocessor):
        """Test validation failure with invalid rating range"""
        data = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [6.0],  # Invalid: > 5
            'cost_for_two': [1000]
        })
        
        is_valid, errors = preprocessor.validate_data(data)
        
        assert is_valid is False
        assert any('rating' in error.lower() for error in errors)
    
    def test_transform_data(self, preprocessor, sample_clean_data):
        """Test complete data transformation"""
        result = preprocessor.transform_data(sample_clean_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'budget_category' in result.columns
        assert 'rating_category' in result.columns
    
    def test_get_preprocessing_stats(self, preprocessor, sample_dirty_data):
        """Test preprocessing statistics"""
        preprocessor.clean_data(sample_dirty_data)
        
        stats = preprocessor.get_preprocessing_stats()
        
        assert 'cleaning' in stats
        assert 'initial_count' in stats['cleaning']
        assert 'final_count' in stats['cleaning']
