"""
Unit tests for LLM Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    """Create an LLMService instance"""
    with patch.dict('os.environ', {
        'GROQ_API_KEY': 'test_key',
        'LLM_MODEL': 'llama3-70b-8192',
        'LLM_TEMPERATURE': '0.7',
        'LLM_MAX_TOKENS': '1000'
    }):
        service = LLMService()
        return service


@pytest.fixture
def sample_restaurants():
    """Create sample restaurant data for testing"""
    return [
        {
            'id': 1,
            'name': 'Restaurant A',
            'location': 'Delhi',
            'cuisine': 'Italian',
            'rating': 4.5,
            'cost_for_two': 1000,
            'budget_category': 'medium',
            'reviews': 'Great food'
        },
        {
            'id': 2,
            'name': 'Restaurant B',
            'location': 'Delhi',
            'cuisine': 'North Indian',
            'rating': 4.2,
            'cost_for_two': 800,
            'budget_category': 'low',
            'reviews': 'Good service'
        }
    ]


@pytest.fixture
def sample_preferences():
    """Create sample user preferences"""
    return {
        'location': 'Delhi',
        'budget': 'medium',
        'cuisine': 'Italian',
        'min_rating': 4.0,
        'additional_preferences': 'family-friendly'
    }


class TestLLMService:
    """Test cases for LLMService class"""
    
    def test_initialization_with_api_key(self):
        """Test service initialization with API key"""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            service = LLMService()
            assert service.api_key == 'test_key'
            assert service.model == 'llama3-70b-8192'
    
    def test_initialization_without_api_key(self):
        """Test service initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            service = LLMService()
            assert service.api_key is None
            assert service.client is None
    
    def test_generate_cache_key(self, llm_service, sample_preferences):
        """Test cache key generation"""
        restaurant_ids = [1, 2, 3]
        cache_key = llm_service._generate_cache_key(sample_preferences, restaurant_ids)
        
        assert cache_key.startswith('llm:recommendations:')
        assert len(cache_key) > 20  # MD5 hash length
    
    def test_cache_key_consistency(self, llm_service, sample_preferences):
        """Test that cache keys are consistent for same inputs"""
        restaurant_ids = [1, 2, 3]
        key1 = llm_service._generate_cache_key(sample_preferences, restaurant_ids)
        key2 = llm_service._generate_cache_key(sample_preferences, restaurant_ids)
        
        assert key1 == key2
    
    def test_format_restaurant_data(self, llm_service, sample_restaurants):
        """Test restaurant data formatting"""
        formatted = llm_service._format_restaurant_data(sample_restaurants, limit=2)
        
        assert 'Restaurant A' in formatted
        assert 'Restaurant B' in formatted
        assert 'ID: 1' in formatted
        assert 'ID: 2' in formatted
    
    def test_format_restaurant_data_limit(self, llm_service, sample_restaurants):
        """Test restaurant data formatting with limit"""
        formatted = llm_service._format_restaurant_data(sample_restaurants, limit=1)
        
        assert 'Restaurant A' in formatted
        assert 'Restaurant B' not in formatted
    
    def test_parse_llm_response_valid_json(self, llm_service):
        """Test parsing valid JSON response"""
        response_text = '{"rankings": [{"id": 1, "rank": 1, "explanation": "Good food"}], "summary": "Test summary"}'
        parsed = llm_service._parse_llm_response(response_text)
        
        assert 'rankings' in parsed
        assert parsed['rankings'][0]['id'] == 1
        assert parsed['summary'] == 'Test summary'
    
    def test_parse_llm_response_invalid_json(self, llm_service):
        """Test parsing invalid JSON response"""
        response_text = 'not valid json'
        
        with pytest.raises(ValueError):
            llm_service._parse_llm_response(response_text)
    
    def test_parse_llm_response_missing_rankings(self, llm_service):
        """Test parsing response without rankings field"""
        response_text = '{"summary": "Test summary"}'
        
        with pytest.raises(ValueError):
            llm_service._parse_llm_response(response_text)
    
    def test_fallback_recommendation(self, llm_service, sample_restaurants):
        """Test fallback recommendation when LLM is unavailable"""
        result = llm_service._fallback_recommendation(sample_restaurants)
        
        assert 'rankings' in result
        assert 'summary' in result
        assert len(result['rankings']) == len(sample_restaurants)
    
    def test_fallback_recommendation_explanations(self, llm_service, sample_restaurants):
        """Test fallback recommendation explanations"""
        result = llm_service._fallback_recommendation(sample_restaurants)
        
        for ranking in result['rankings']:
            assert 'explanation' in ranking
            assert 'rating' in ranking['explanation']
    
    @patch('app.services.llm_service.LLMService._call_llm')
    def test_generate_recommendations_success(self, mock_call_llm, llm_service, sample_preferences, sample_restaurants):
        """Test successful recommendation generation"""
        mock_response = '{"rankings": [{"id": 1, "rank": 1, "explanation": "Great"}], "summary": "Test"}'
        mock_call_llm.return_value = mock_response
        
        result = llm_service.generate_recommendations(sample_preferences, sample_restaurants)
        
        assert 'rankings' in result
        assert 'summary' in result
        mock_call_llm.assert_called_once()
    
    @patch('app.services.llm_service.LLMService._call_llm')
    def test_generate_recommendations_cache_hit(self, mock_call_llm, llm_service, sample_preferences, sample_restaurants):
        """Test recommendation generation with cache hit"""
        mock_response = '{"rankings": [{"id": 1, "rank": 1, "explanation": "Great"}], "summary": "Test"}'
        mock_call_llm.return_value = mock_response
        
        # First call - should hit API
        result1 = llm_service.generate_recommendations(sample_preferences, sample_restaurants)
        
        # Second call - should hit cache
        result2 = llm_service.generate_recommendations(sample_preferences, sample_restaurants)
        
        # Should only call API once due to caching
        assert mock_call_llm.call_count == 1
    
    @patch('app.services.llm_service.LLMService._call_llm')
    def test_generate_recommendations_fallback_on_error(self, mock_call_llm, llm_service, sample_preferences, sample_restaurants):
        """Test fallback when LLM call fails"""
        mock_call_llm.side_effect = Exception("API error")
        
        result = llm_service.generate_recommendations(sample_preferences, sample_restaurants)
        
        assert 'rankings' in result
        assert 'summary' in result
    
    @patch('app.services.llm_service.LLMService._call_llm')
    def test_generate_explanation_success(self, mock_call_llm, llm_service, sample_restaurants, sample_preferences):
        """Test successful explanation generation"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is a great restaurant."
        mock_call_llm.return_value = mock_response
        
        explanation = llm_service.generate_explanation(sample_restaurants[0], sample_preferences)
        
        assert explanation == "This is a great restaurant."
    
    def test_generate_explanation_fallback(self, llm_service, sample_restaurants, sample_preferences):
        """Test explanation generation fallback when client not initialized"""
        llm_service.client = None
        
        explanation = llm_service.generate_explanation(sample_restaurants[0], sample_preferences)
        
        assert 'rating' in explanation
        assert 'cuisine' in explanation
    
    @patch('app.services.llm_service.LLMService.generate_recommendations')
    def test_rank_with_llm(self, mock_generate, llm_service, sample_restaurants, sample_preferences):
        """Test ranking with LLM"""
        mock_response = {
            'rankings': [
                {'id': 1, 'rank': 1, 'explanation': 'Best'},
                {'id': 2, 'rank': 2, 'explanation': 'Good'}
            ],
            'summary': 'Test'
        }
        mock_generate.return_value = mock_response
        
        ranked = llm_service.rank_with_llm(sample_restaurants, sample_preferences)
        
        assert len(ranked) == len(sample_restaurants)
        assert ranked[0]['llm_rank'] == 1
        assert ranked[1]['llm_rank'] == 2
    
    @patch('app.services.llm_service.LLMService.generate_recommendations')
    def test_rank_with_llm_fallback(self, mock_generate, llm_service, sample_restaurants, sample_preferences):
        """Test ranking with LLM fallback on error"""
        mock_generate.side_effect = Exception("API error")
        
        ranked = llm_service.rank_with_llm(sample_restaurants, sample_preferences)
        
        assert len(ranked) == len(sample_restaurants)
    
    @patch('app.services.llm_service.LLMService.generate_recommendations')
    def test_summarize_recommendations(self, mock_generate, llm_service, sample_restaurants, sample_preferences):
        """Test recommendation summary generation"""
        mock_response = {
            'rankings': [],
            'summary': 'Test summary'
        }
        mock_generate.return_value = mock_response
        
        summary = llm_service.summarize_recommendations(sample_restaurants, sample_preferences)
        
        assert summary == 'Test summary'
    
    def test_summarize_recommendations_fallback(self, llm_service, sample_restaurants, sample_preferences):
        """Test summary generation fallback"""
        llm_service.client = None
        
        summary = llm_service.summarize_recommendations(sample_restaurants, sample_preferences)
        
        assert 'restaurants' in summary.lower()
