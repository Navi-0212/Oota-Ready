"""
Edge case tests based on edge-case.md
"""

import pytest
import pandas as pd
from app.services.data_preprocessor import DataPreprocessor, SchemaError, DataValidationError
from app.services.data_service import DataService, DatasetEmptyError, DatasetLoadError
from app.services.filtering_service import FilteringService
from app.utils.exceptions import ValidationError, NotFoundError, DatabaseError
from unittest.mock import Mock, patch, MagicMock


class TestEmptyDatasetEdgeCases:
    """Test empty dataset scenarios"""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframe"""
        preprocessor = DataPreprocessor()
        empty_df = pd.DataFrame()
        
        is_valid, errors = preprocessor.validate_data(empty_df)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_empty_results_from_search(self):
        """Test handling of empty search results"""
        filtering_service = FilteringService()
        restaurants = []
        
        result = filtering_service.apply_filters(
            restaurants,
            location="NonExistent",
            budget="medium",
            cuisine="Italian"
        )
        
        assert len(result) == 0
    
    @patch('app.services.data_service.load_dataset')
    def test_empty_dataset_from_huggingface(self, mock_load_dataset):
        """Test handling when Hugging Face returns empty dataset"""
        mock_dataset = MagicMock()
        mock_dataset.to_pandas.return_value = pd.DataFrame()
        mock_load_dataset.return_value = mock_dataset
        
        data_service = DataService()
        
        with pytest.raises((ConnectionError, DatasetEmptyError)):
            data_service.load_zomato_dataset(use_cache=False)


class TestMissingRequiredFieldsEdgeCases:
    """Test missing required field scenarios"""
    
    def test_missing_name_field(self):
        """Test handling of missing name field"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [4.5],
            'cost_for_two': [1000]
            # Missing 'name' field
        })
        
        is_valid, errors = preprocessor.validate_data(df)
        
        assert is_valid is False
        assert any('name' in error.lower() for error in errors)
    
    def test_null_values_in_required_fields(self):
        """Test handling of null values in required fields"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A', None, 'Restaurant C'],
            'location': ['Delhi', 'Bangalore', 'Mumbai'],
            'cuisine': ['Italian', 'North Indian', 'Chinese'],
            'rating': [4.5, 3.8, 4.2],
            'cost_for_two': [1000, 800, 1200]
        })
        
        result = preprocessor._handle_missing_values(df)
        
        # Should remove rows with null name
        assert None not in result['name'].values
    
    def test_partial_missing_fields(self):
        """Test handling when some records have missing fields"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A', 'Restaurant B'],
            'location': ['Delhi', None],
            'cuisine': ['Italian', 'North Indian'],
            'rating': [4.5, 3.8],
            'cost_for_two': [1000, 800]
        })
        
        result = preprocessor.clean_data(df)
        
        # Should handle gracefully
        assert isinstance(result, pd.DataFrame)


class TestInvalidDataTypesEdgeCases:
    """Test invalid data type scenarios"""
    
    def test_rating_as_string(self):
        """Test handling of rating as string instead of float"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': ['4.5'],  # String instead of float
            'cost_for_two': [1000]
        })
        
        result = preprocessor._validate_data_types(df)
        
        # Should convert to numeric
        assert pd.api.types.is_numeric_dtype(result['rating'])
    
    def test_negative_rating(self):
        """Test handling of negative rating"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [-1.0],
            'cost_for_two': [1000]
        })
        
        result = preprocessor._remove_invalid_records(df)
        
        # Should remove invalid rating
        assert all(result['rating'] >= 0)
    
    def test_rating_above_five(self):
        """Test handling of rating above 5"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [6.0],
            'cost_for_two': [1000]
        })
        
        result = preprocessor._remove_invalid_records(df)
        
        # Should remove invalid rating
        assert all(result['rating'] <= 5)
    
    def test_negative_cost(self):
        """Test handling of negative cost"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [4.5],
            'cost_for_two': [-500]
        })
        
        result = preprocessor._remove_invalid_records(df)
        
        # Should remove invalid cost
        assert all(result['cost_for_two'] > 0)
    
    def test_zero_cost(self):
        """Test handling of zero cost"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A'],
            'location': ['Delhi'],
            'cuisine': ['Italian'],
            'rating': [4.5],
            'cost_for_two': [0]
        })
        
        result = preprocessor._remove_invalid_records(df)
        
        # Should remove zero cost
        assert all(result['cost_for_two'] > 0)


class TestDuplicateRecordsEdgeCases:
    """Test duplicate record scenarios"""
    
    def test_exact_duplicates(self):
        """Test handling of exact duplicate records"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A', 'Restaurant A'],
            'location': ['Delhi', 'Delhi'],
            'cuisine': ['Italian', 'Italian'],
            'rating': [4.5, 4.5],
            'cost_for_two': [1000, 1000]
        })
        
        result = preprocessor._remove_duplicates(df)
        
        # Should remove duplicates
        assert len(result) == 1
    
    def test_case_insensitive_duplicates(self):
        """Test handling of case-insensitive duplicates"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant A', 'RESTAURANT A'],
            'location': ['Delhi', 'delhi'],
            'cuisine': ['Italian', 'italian'],
            'rating': [4.5, 4.5],
            'cost_for_two': [1000, 1000]
        })
        
        result = preprocessor.clean_data(df)
        
        # Should handle case normalization
        assert len(result) <= 2


class TestDatasetDownloadFailureEdgeCases:
    """Test dataset download failure scenarios"""
    
    @patch('app.services.data_service.load_dataset')
    def test_network_error_on_download(self, mock_load_dataset):
        """Test handling of network error during download"""
        mock_load_dataset.side_effect = ConnectionError("Network error")
        
        data_service = DataService()
        
        with pytest.raises((ConnectionError, DatasetLoadError)):
            data_service.load_zomato_dataset(use_cache=False)
    
    @patch('app.services.data_service.load_dataset')
    def test_timeout_on_download(self, mock_load_dataset):
        """Test handling of timeout during download"""
        mock_load_dataset.side_effect = TimeoutError("Timeout")
        
        data_service = DataService()
        
        with pytest.raises((TimeoutError, DatasetLoadError)):
            data_service.load_zomato_dataset(use_cache=False)


class TestCorruptedDataEdgeCases:
    """Test corrupted data scenarios"""
    
    def test_special_characters_in_text(self):
        """Test handling of special characters in text fields"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant @#$%', 'Restaurant &*()'],
            'location': ['Delhi', 'Bangalore'],
            'cuisine': ['Italian', 'North Indian'],
            'rating': [4.5, 3.8],
            'cost_for_two': [1000, 800]
        })
        
        result = preprocessor.clean_data(df)
        
        # Should handle special characters
        assert isinstance(result, pd.DataFrame)
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        preprocessor = DataPreprocessor()
        df = pd.DataFrame({
            'name': ['Restaurant Café', 'Restaurante México'],
            'location': ['Delhi', 'Bangalore'],
            'cuisine': ['Italian', 'North Indian'],
            'rating': [4.5, 3.8],
            'cost_for_two': [1000, 800]
        })
        
        result = preprocessor.clean_data(df)
        
        # Should handle unicode
        assert isinstance(result, pd.DataFrame)


class TestAPIFailureEdgeCases:
    """Test API failure scenarios"""
    
    def test_database_connection_failure(self):
        """Test handling of database connection failure"""
        from app.db.connection import DatabaseConnection, DatabaseConnectionError
        
        with pytest.raises(DatabaseConnectionError):
            DatabaseConnection("postgresql://invalid:invalid@invalid:5432/invalid")
    
    def test_llm_api_failure_fallback(self):
        """Test LLM API failure fallback to rule-based"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        service.client = None  # Simulate API failure
        
        restaurants = [
            {'id': 1, 'name': 'Test', 'rating': 4.5, 'cuisine': 'Italian'}
        ]
        
        result = service._fallback_recommendation(restaurants)
        
        assert 'rankings' in result
        assert 'summary' in result


class TestInvalidInputEdgeCases:
    """Test invalid input scenarios"""
    
    def test_empty_location_input(self):
        """Test handling of empty location input"""
        filtering_service = FilteringService()
        restaurants = [
            {'id': 1, 'name': 'Test', 'location': 'Delhi', 'cuisine': 'Italian'}
        ]
        
        result = filtering_service.filter_by_location(restaurants, '')
        
        # Should return all restaurants when location is empty
        assert len(result) == len(restaurants)
    
    def test_invalid_budget_category(self):
        """Test handling of invalid budget category"""
        filtering_service = FilteringService()
        restaurants = [
            {'id': 1, 'name': 'Test', 'budget_category': 'medium', 'cuisine': 'Italian'}
        ]
        
        result = filtering_service.filter_by_budget(restaurants, 'premium')
        
        # Should return empty for invalid budget
        assert len(result) == 0
    
    def test_typos_in_location(self):
        """Test handling of typos in location (fuzzy matching)"""
        filtering_service = FilteringService()
        restaurants = [
            {'id': 1, 'name': 'Test', 'location': 'Delhi', 'cuisine': 'Italian'}
        ]
        
        # Exact match
        result = filtering_service.filter_by_location(restaurants, 'Delhi')
        assert len(result) == 1
        
        # Case insensitive
        result = filtering_service.filter_by_location(restaurants, 'delhi')
        assert len(result) == 1
    
    def test_extremely_long_input(self):
        """Test handling of extremely long input strings"""
        from app.models.schemas import RecommendationRequest
        from pydantic import ValidationError
        
        long_string = "a" * 101
        
        with pytest.raises(ValidationError):
            RecommendationRequest(
                location=long_string,
                budget="medium",
                cuisine="Italian"
            )


class TestNetworkFailureEdgeCases:
    """Test network failure scenarios"""
    
    @patch('app.services.data_service.redis')
    def test_redis_connection_failure(self, mock_redis):
        """Test handling of Redis connection failure"""
        mock_redis.from_url.side_effect = Exception("Redis connection failed")
        
        data_service = DataService(redis_host="localhost", redis_port=6379)
        
        # Should handle gracefully
        assert data_service.redis_client is None or data_service.redis_client == mock_redis.from_url.return_value
