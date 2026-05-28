"""
Unit tests for Filtering Service
"""

import pytest
from app.services.filtering_service import FilteringService


@pytest.fixture
def filtering_service():
    """Create a FilteringService instance"""
    return FilteringService()


@pytest.fixture
def sample_restaurants():
    """Create sample restaurant data for testing"""
    return [
        {
            'id': 1,
            'name': 'Restaurant A',
            'location': 'Delhi',
            'cuisine': 'Italian',
            'cost_for_two': 1000,
            'rating': 4.5,
            'budget_category': 'medium',
            'reviews': 'Great food, family-friendly'
        },
        {
            'id': 2,
            'name': 'Restaurant B',
            'location': 'Bangalore',
            'cuisine': 'North Indian',
            'cost_for_two': 500,
            'rating': 3.8,
            'budget_category': 'low',
            'reviews': 'Good service'
        },
        {
            'id': 3,
            'name': 'Restaurant C',
            'location': 'Delhi',
            'cuisine': 'Chinese',
            'cost_for_two': 2000,
            'rating': 4.2,
            'budget_category': 'high',
            'reviews': 'Nice place, outdoor seating'
        },
        {
            'id': 4,
            'name': 'Restaurant D',
            'location': 'Mumbai',
            'cuisine': 'Italian',
            'cost_for_two': 800,
            'rating': 4.0,
            'budget_category': 'medium',
            'reviews': 'Romantic atmosphere'
        }
    ]


class TestFilteringService:
    """Test cases for FilteringService class"""
    
    def test_filter_by_location_exact_match(self, filtering_service, sample_restaurants):
        """Test filtering by location with exact match"""
        result = filtering_service.filter_by_location(sample_restaurants, 'Delhi')
        
        assert len(result) == 2
        assert all(r['location'] == 'Delhi' for r in result)
    
    def test_filter_by_location_case_insensitive(self, filtering_service, sample_restaurants):
        """Test filtering by location with case insensitivity"""
        result = filtering_service.filter_by_location(sample_restaurants, 'delhi')
        
        assert len(result) == 2
    
    def test_filter_by_location_no_match(self, filtering_service, sample_restaurants):
        """Test filtering by location with no match"""
        result = filtering_service.filter_by_location(sample_restaurants, 'Chennai')
        
        assert len(result) == 0
    
    def test_filter_by_location_empty(self, filtering_service, sample_restaurants):
        """Test filtering by location with empty string"""
        result = filtering_service.filter_by_location(sample_restaurants, '')
        
        assert len(result) == len(sample_restaurants)
    
    def test_filter_by_budget(self, filtering_service, sample_restaurants):
        """Test filtering by budget category"""
        result = filtering_service.filter_by_budget(sample_restaurants, 'medium')
        
        assert len(result) == 2
        assert all(r['budget_category'] == 'medium' for r in result)
    
    def test_filter_by_budget_case_insensitive(self, filtering_service, sample_restaurants):
        """Test filtering by budget with case insensitivity"""
        result = filtering_service.filter_by_budget(sample_restaurants, 'MEDIUM')
        
        assert len(result) == 2
    
    def test_filter_by_cuisine_exact_match(self, filtering_service, sample_restaurants):
        """Test filtering by cuisine with exact match"""
        result = filtering_service.filter_by_cuisine(sample_restaurants, 'Italian')
        
        assert len(result) == 2
        assert all('Italian' in r['cuisine'] for r in result)
    
    def test_filter_by_cuisine_case_insensitive(self, filtering_service, sample_restaurants):
        """Test filtering by cuisine with case insensitivity"""
        result = filtering_service.filter_by_cuisine(sample_restaurants, 'italian')
        
        assert len(result) == 2
    
    def test_filter_by_cuisine_no_match(self, filtering_service, sample_restaurants):
        """Test filtering by cuisine with no match"""
        result = filtering_service.filter_by_cuisine(sample_restaurants, 'Thai')
        
        assert len(result) == 0
    
    def test_filter_by_rating(self, filtering_service, sample_restaurants):
        """Test filtering by minimum rating"""
        result = filtering_service.filter_by_rating(sample_restaurants, 4.0)
        
        assert len(result) == 3
        assert all(r['rating'] >= 4.0 for r in result)
    
    def test_filter_by_rating_no_filter(self, filtering_service, sample_restaurants):
        """Test filtering by rating with no minimum (0)"""
        result = filtering_service.filter_by_rating(sample_restaurants, 0)
        
        assert len(result) == len(sample_restaurants)
    
    def test_filter_by_rating_none(self, filtering_service, sample_restaurants):
        """Test filtering by rating with None"""
        result = filtering_service.filter_by_rating(sample_restaurants, None)
        
        assert len(result) == len(sample_restaurants)
    
    def test_apply_additional_filters(self, filtering_service, sample_restaurants):
        """Test applying additional preference filters"""
        result = filtering_service.apply_additional_filters(sample_restaurants, 'family-friendly')
        
        assert len(result) == len(sample_restaurants)
        assert result[0]['preference_score'] >= 0
    
    def test_apply_additional_filters_empty(self, filtering_service, sample_restaurants):
        """Test applying additional filters with empty preferences"""
        result = filtering_service.apply_additional_filters(sample_restaurants, '')
        
        assert len(result) == len(sample_restaurants)
    
    def test_calculate_match_score(self, filtering_service, sample_restaurants):
        """Test calculating match score"""
        restaurant = sample_restaurants[0]
        score = filtering_service.calculate_match_score(
            restaurant, 'medium', 4.0, 'family-friendly'
        )
        
        assert 0 <= score <= 1
    
    def test_rank_restaurants(self, filtering_service, sample_restaurants):
        """Test ranking restaurants"""
        result = filtering_service.rank_restaurants(
            sample_restaurants, 'medium', 4.0, 'family-friendly'
        )
        
        assert len(result) == len(sample_restaurants)
        assert all('match_score' in r for r in result)
        # Check if sorted by match score (descending)
        scores = [r['match_score'] for r in result]
        assert scores == sorted(scores, reverse=True)
    
    def test_apply_filters_all(self, filtering_service, sample_restaurants):
        """Test applying all filters"""
        result = filtering_service.apply_filters(
            sample_restaurants,
            location='Delhi',
            budget='medium',
            cuisine='Italian',
            min_rating=4.0,
            preferences='family-friendly'
        )
        
        assert len(result) >= 0
        assert all('match_score' in r for r in result)
    
    def test_paginate_results(self, filtering_service, sample_restaurants):
        """Test result pagination"""
        result = filtering_service.paginate_results(sample_restaurants, limit=2, offset=0)
        
        assert len(result) == 2
    
    def test_paginate_results_offset(self, filtering_service, sample_restaurants):
        """Test result pagination with offset"""
        result = filtering_service.paginate_results(sample_restaurants, limit=2, offset=2)
        
        assert len(result) == 2
    
    def test_paginate_results_exceeds(self, filtering_service, sample_restaurants):
        """Test pagination when limit exceeds available results"""
        result = filtering_service.paginate_results(sample_restaurants, limit=10, offset=0)
        
        assert len(result) == len(sample_restaurants)
    
    def test_generate_explanation(self, filtering_service, sample_restaurants):
        """Test generating explanation"""
        restaurant = sample_restaurants[0]
        explanation = filtering_service.generate_explanation(
            restaurant, 'medium', 'Italian', 'family-friendly'
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_extract_keywords(self, filtering_service):
        """Test keyword extraction"""
        text = "family-friendly outdoor seating with good food"
        keywords = filtering_service._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert 'family' in keywords or 'family-friendly' in keywords
        assert 'outdoor' in keywords
    
    def test_budget_weights(self, filtering_service):
        """Test budget weight configuration"""
        assert 'low' in filtering_service.budget_weights
        assert 'medium' in filtering_service.budget_weights
        assert 'high' in filtering_service.budget_weights
