"""
Unit tests for Data Service
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from app.services.data_service import DataService, DatasetEmptyError, DatasetLoadError


@pytest.fixture
def data_service():
    """Create a DataService instance"""
    return DataService(redis_host="localhost", redis_port=6379)


@pytest.fixture
def sample_dataframe():
    """Create sample restaurant data"""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Restaurant A', 'Restaurant B', 'Restaurant C'],
        'location': ['Delhi', 'Bangalore', 'Mumbai'],
        'cuisine': ['Italian', 'North Indian', 'Chinese'],
        'rating': [4.5, 3.8, 4.2],
        'cost_for_two': [1000, 800, 1200],
        'votes': [100, 200, 300],
        'reviews': ['Great food', 'Good service', 'Nice place']
    })


class TestDataService:
    """Test cases for DataService class"""
    
    @patch('app.services.data_service.load_dataset')
    def test_load_zomato_dataset_success(self, mock_load_dataset, data_service, sample_dataframe):
        """Test successful dataset loading"""
        mock_dataset = MagicMock()
        mock_dataset.to_pandas.return_value = sample_dataframe
        mock_load_dataset.return_value = mock_dataset
        
        result = data_service.load_zomato_dataset(use_cache=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_dataframe)
        mock_load_dataset.assert_called_once()
    
    @patch('app.services.data_service.load_dataset')
    def test_load_zomato_dataset_empty(self, mock_load_dataset, data_service):
        """Test loading empty dataset"""
        mock_dataset = MagicMock()
        mock_dataset.to_pandas.return_value = pd.DataFrame()
        mock_load_dataset.return_value = mock_dataset
        
        with pytest.raises(ConnectionError):
            data_service.load_zomato_dataset(use_cache=False)
    
    @patch('app.services.data_service.load_dataset')
    def test_load_zomato_dataset_with_cache(self, mock_load_dataset, data_service, sample_dataframe):
        """Test dataset loading with cache"""
        # Mock Redis cache hit
        data_service.redis_client = Mock()
        data_service.redis_client.get.return_value = sample_dataframe.to_json()
        
        result = data_service.load_zomato_dataset(use_cache=True)
        
        assert isinstance(result, pd.DataFrame)
        mock_load_dataset.assert_not_called()
    
    def test_get_restaurant_by_id(self, data_service, sample_dataframe):
        """Test getting restaurant by ID"""
        result = data_service.get_restaurant_by_id(1, sample_dataframe)
        
        assert result is not None
        assert result['name'] == 'Restaurant A'
    
    def test_get_restaurant_by_id_not_found(self, data_service, sample_dataframe):
        """Test getting non-existent restaurant by ID"""
        result = data_service.get_restaurant_by_id(999, sample_dataframe)
        
        assert result is None
    
    def test_get_all_restaurants(self, data_service, sample_dataframe):
        """Test getting all restaurants"""
        result = data_service.get_all_restaurants(sample_dataframe, limit=10)
        
        assert len(result) == len(sample_dataframe)
        assert isinstance(result, list)
    
    def test_get_all_restaurants_with_pagination(self, data_service, sample_dataframe):
        """Test getting restaurants with pagination"""
        result = data_service.get_all_restaurants(sample_dataframe, limit=2, offset=0)
        
        assert len(result) == 2
    
    def test_get_restaurants_by_location(self, data_service, sample_dataframe):
        """Test getting restaurants by location"""
        result = data_service.get_restaurants_by_location('Delhi', sample_dataframe)
        
        assert len(result) == 1
        assert result[0]['location'] == 'Delhi'
    
    def test_get_restaurants_by_location_case_insensitive(self, data_service, sample_dataframe):
        """Test case-insensitive location search"""
        result = data_service.get_restaurants_by_location('delhi', sample_dataframe)
        
        assert len(result) == 1
    
    def test_get_restaurants_by_cuisine(self, data_service, sample_dataframe):
        """Test getting restaurants by cuisine"""
        result = data_service.get_restaurants_by_cuisine('Italian', sample_dataframe)
        
        assert len(result) == 1
        assert result[0]['cuisine'] == 'Italian'
    
    def test_get_restaurants_by_cuisine_case_insensitive(self, data_service, sample_dataframe):
        """Test case-insensitive cuisine search"""
        result = data_service.get_restaurants_by_cuisine('italian', sample_dataframe)
        
        assert len(result) == 1
    
    def test_get_available_locations(self, data_service, sample_dataframe):
        """Test getting available locations"""
        result = data_service.get_available_locations(sample_dataframe)
        
        assert isinstance(result, list)
        assert 'Delhi' in result
        assert 'Bangalore' in result
        assert 'Mumbai' in result
    
    def test_get_available_cuisines(self, data_service, sample_dataframe):
        """Test getting available cuisines"""
        result = data_service.get_available_cuisines(sample_dataframe)
        
        assert isinstance(result, list)
        assert 'Italian' in result
        assert 'North Indian' in result
        assert 'Chinese' in result
    
    @patch('os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_dataset_locally(self, mock_to_csv, mock_makedirs, data_service, sample_dataframe):
        """Test saving dataset locally"""
        data_service.save_dataset_locally(sample_dataframe, 'test_path.csv')
        
        mock_makedirs.assert_called_once()
        mock_to_csv.assert_called_once()
    
    @patch('os.path.exists')
    @patch('pandas.read_csv')
    def test_load_dataset_from_local(self, mock_read_csv, mock_exists, data_service, sample_dataframe):
        """Test loading dataset from local file"""
        mock_exists.return_value = True
        mock_read_csv.return_value = sample_dataframe
        
        result = data_service.load_dataset_from_local('test_path.csv')
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)
    
    @patch('os.path.exists')
    def test_load_dataset_from_local_not_found(self, mock_exists, data_service):
        """Test loading non-existent local file"""
        mock_exists.return_value = False
        
        result = data_service.load_dataset_from_local('test_path.csv')
        
        assert result is None
    
    def test_clear_cache(self, data_service):
        """Test clearing cache"""
        data_service.redis_client = Mock()
        
        data_service.clear_cache()
        
        data_service.redis_client.delete.assert_called_once()
