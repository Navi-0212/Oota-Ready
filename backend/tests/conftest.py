"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_restaurant_data():
    """Sample restaurant data for testing"""
    return {
        'id': 1,
        'name': 'Test Restaurant',
        'location': 'Delhi',
        'cuisine': 'Italian',
        'cost_for_two': 1000.0,
        'rating': 4.5,
        'votes': 100,
        'reviews': 'Great food',
        'address': '123 Test Street',
        'phone': '+91-1234567890',
        'url': 'http://test.com',
        'budget_category': 'medium',
        'rating_category': 'very_good'
    }
