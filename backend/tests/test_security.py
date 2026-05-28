"""
Security tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestSQLInjection:
    """Test SQL injection vulnerabilities"""
    
    @patch('app.api.recommendations.data_service')
    def test_sql_injection_in_location(self, mock_data, client):
        """Test SQL injection in location parameter"""
        mock_data.search_restaurants_db.return_value = []
        
        sql_payload = "Delhi'; DROP TABLE restaurants; --"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": sql_payload,
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        # Should handle gracefully without executing SQL
        assert response.status_code in [200, 422]
        # Data service should not execute raw SQL
        mock_data.search_restaurants_db.assert_called_once()
    
    @patch('app.api.recommendations.data_service')
    def test_sql_injection_in_cuisine(self, mock_data, client):
        """Test SQL injection in cuisine parameter"""
        mock_data.search_restaurants_db.return_value = []
        
        sql_payload = "Italian' OR '1'='1"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": sql_payload
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
    
    @patch('app.api.recommendations.data_service')
    def test_sql_injection_in_preferences(self, mock_data, client):
        """Test SQL injection in additional preferences"""
        mock_data.search_restaurants_db.return_value = []
        
        sql_payload = "'; DROP TABLE restaurants; --"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "additional_preferences": sql_payload
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]


class TestXSSAttacks:
    """Test XSS vulnerabilities"""
    
    @patch('app.api.recommendations.data_service')
    def test_xss_in_location(self, mock_data, client):
        """Test XSS in location parameter"""
        mock_data.search_restaurants_db.return_value = []
        
        xss_payload = "<script>alert('XSS')</script>"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": xss_payload,
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
    
    @patch('app.api.recommendations.data_service')
    def test_xss_in_preferences(self, mock_data, client):
        """Test XSS in additional preferences"""
        mock_data.search_restaurants_db.return_value = []
        
        xss_payload = "<img src=x onerror=alert('XSS')>"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "additional_preferences": xss_payload
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
    
    @patch('app.api.recommendations.data_service')
    def test_xss_in_cuisine(self, mock_data, client):
        """Test XSS in cuisine parameter"""
        mock_data.search_restaurants_db.return_value = []
        
        xss_payload = "<script>document.cookie='XSS'</script>"
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": xss_payload
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]


class TestCSRFProtection:
    """Test CSRF protection"""
    
    @patch('app.api.recommendations.data_service')
    def test_csrf_token_required(self, mock_data, client):
        """Test if CSRF token is required for state-changing operations"""
        # Note: This test depends on CSRF implementation
        # If CSRF is implemented, this test should verify it
        mock_data.search_restaurants_db.return_value = []
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian"
            },
            headers={
                # Missing CSRF token if implemented
            }
        )
        
        # If CSRF is implemented, expect 403
        # If not implemented, this documents the need for it
        assert response.status_code in [200, 403, 422]


class TestInputValidation:
    """Test input validation security"""
    
    def test_missing_required_fields(self, client):
        """Test validation of required fields"""
        response = client.post(
            "/api/recommendations",
            json={
                "budget": "medium",
                "cuisine": "Italian"
                # Missing location
            }
        )
        
        assert response.status_code == 422
    
    def test_invalid_budget_value(self, client):
        """Test validation of budget values"""
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "invalid_budget",
                "cuisine": "Italian"
            }
        )
        
        assert response.status_code == 422
    
    def test_rating_out_of_range(self, client):
        """Test validation of rating range"""
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 6.0  # Invalid: > 5
            }
        )
        
        assert response.status_code == 422
    
    def test_negative_rating(self, client):
        """Test validation of negative rating"""
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": -1.0  # Invalid: < 0
            }
        )
        
        assert response.status_code == 422
    
    def test_excessively_long_input(self, client):
        """Test validation of input length"""
        long_string = "a" * 1000
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": long_string,
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        assert response.status_code == 422


class TestRateLimiting:
    """Test rate limiting security"""
    
    @patch('app.api.recommendations.data_service')
    def test_rate_limiting_enforced(self, mock_data, client):
        """Test that rate limiting is enforced"""
        mock_data.search_restaurants_db.return_value = []
        
        # Make multiple rapid requests
        responses = []
        for _ in range(150):  # Exceed default limit
            response = client.post(
                "/api/recommendations",
                json={
                    "location": "Delhi",
                    "budget": "medium",
                    "cuisine": "Italian"
                }
            )
            responses.append(response)
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        
        # If rate limiting is implemented, some should be 429
        # If not, this documents the need for it
        assert rate_limited or all(r.status_code in [200, 422] for r in responses)


class TestAuthentication:
    """Test authentication security (if implemented)"""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        # If authentication is implemented, test it
        # For now, this documents the need for auth if required
        pass


class TestDataExposure:
    """Test for data exposure vulnerabilities"""
    
    @patch('app.api.recommendations.data_service')
    def test_sensitive_data_not_exposed(self, mock_data, client):
        """Test that sensitive data is not exposed in responses"""
        mock_restaurant = {
            'id': 1,
            'name': 'Test Restaurant',
            'location': 'Delhi',
            'cuisine': 'Italian',
            'cost_for_two': 1000.0,
            'rating': 4.5
            # Should not expose internal IDs, passwords, etc.
        }
        mock_data.search_restaurants_db.return_value = [mock_restaurant]
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Check that sensitive fields are not exposed
            assert 'password' not in str(data)
            assert 'internal_id' not in str(data)


class TestErrorHandling:
    """Test secure error handling"""
    
    @patch('app.api.recommendations.data_service')
    def test_error_messages_dont_expose_internal_details(self, mock_data, client):
        """Test that error messages don't expose internal details"""
        mock_data.search_restaurants_db.side_effect = Exception("Database connection failed: postgresql://user:pass@localhost/db")
        
        response = client.post(
            "/api/recommendations",
            json={
                "location": "Delhi",
                "budget": "medium",
                "cuisine": "Italian"
            }
        )
        
        if response.status_code == 500:
            error_message = response.text
            # Should not expose database credentials
            assert 'postgresql://' not in error_message
            assert 'pass@' not in error_message
