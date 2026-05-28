"""
Unit tests for Rate Limiter
"""

import pytest
import time
from unittest.mock import Mock, patch
from app.utils.rate_limiter import RateLimiter, rate_limit_middleware
from fastapi import Request
from fastapi.responses import JSONResponse


@pytest.fixture
def rate_limiter():
    """Create a RateLimiter instance for testing"""
    return RateLimiter(requests=5, period=10)


class TestRateLimiter:
    """Test cases for RateLimiter class"""
    
    def test_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(requests=10, period=60)
        assert limiter.requests == 10
        assert limiter.period == 60
        assert len(limiter.requests_history) == 0
    
    def test_is_allowed_first_request(self, rate_limiter):
        """Test first request is always allowed"""
        assert rate_limiter.is_allowed("client1") is True
    
    def test_is_allowed_under_limit(self, rate_limiter):
        """Test requests under limit are allowed"""
        for i in range(5):
            assert rate_limiter.is_allowed("client1") is True
    
    def test_is_allowed_over_limit(self, rate_limiter):
        """Test requests over limit are denied"""
        # Make 5 requests (limit)
        for i in range(5):
            rate_limiter.is_allowed("client1")
        
        # 6th request should be denied
        assert rate_limiter.is_allowed("client1") is False
    
    def test_is_allowed_different_clients(self, rate_limiter):
        """Test different clients have independent limits"""
        # Client 1 makes 5 requests
        for i in range(5):
            rate_limiter.is_allowed("client1")
        
        # Client 1 should be at limit
        assert rate_limiter.is_allowed("client1") is False
        
        # Client 2 should still be allowed
        assert rate_limiter.is_allowed("client2") is True
    
    def test_is_allowed_time_window_reset(self, rate_limiter):
        """Test old requests are removed after time window"""
        # Make 5 requests
        for i in range(5):
            rate_limiter.is_allowed("client1")
        
        # Should be at limit
        assert rate_limiter.is_allowed("client1") is False
        
        # Wait for time window to pass (simulate by modifying history)
        rate_limiter.requests_history["client1"] = []
        
        # Should be allowed again
        assert rate_limiter.is_allowed("client1") is True
    
    def test_get_remaining_requests(self, rate_limiter):
        """Test getting remaining requests"""
        # Initially should have full limit
        assert rate_limiter.get_remaining_requests("client1") == 5
        
        # After 2 requests
        rate_limiter.is_allowed("client1")
        rate_limiter.is_allowed("client1")
        assert rate_limiter.get_remaining_requests("client1") == 3
    
    def test_get_remaining_requests_zero(self, rate_limiter):
        """Test remaining requests when at limit"""
        # Use all requests
        for i in range(5):
            rate_limiter.is_allowed("client1")
        
        assert rate_limiter.get_remaining_requests("client1") == 0
    
    def test_reset(self, rate_limiter):
        """Test resetting rate limit for a client"""
        # Make some requests
        for i in range(3):
            rate_limiter.is_allowed("client1")
        
        # Reset
        rate_limiter.reset("client1")
        
        # Should have full limit again
        assert rate_limiter.is_allowed("client1") is True
        assert rate_limiter.get_remaining_requests("client1") == 4
    
    def test_reset_nonexistent_client(self, rate_limiter):
        """Test resetting non-existent client doesn't raise error"""
        rate_limiter.reset("nonexistent")  # Should not raise error
    
    def test_old_requests_removed(self, rate_limiter):
        """Test old requests outside time window are removed"""
        # Add a request with old timestamp
        old_time = time.time() - 20  # 20 seconds ago (outside 10s window)
        rate_limiter.requests_history["client1"].append(old_time)
        
        # Check remaining should still be 5 (old request removed)
        assert rate_limiter.get_remaining_requests("client1") == 5


class TestRateLimitMiddleware:
    """Test cases for rate limiting middleware"""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request"""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        return request
    
    @pytest.fixture
    def mock_call_next(self):
        """Create a mock call_next function"""
        async def call_next(request):
            response = Mock()
            response.headers = {}
            return response
        return call_next
    
    @patch('app.utils.rate_limiter.os.getenv')
    async def test_middleware_rate_limit_disabled(self, mock_getenv, mock_request, mock_call_next):
        """Test middleware when rate limiting is disabled"""
        mock_getenv.return_value = "false"
        
        response = await rate_limit_middleware(mock_request, mock_call_next)
        
        # Should proceed without rate limiting
        assert response is not None
    
    @patch('app.utils.rate_limiter.os.getenv')
    async def test_middleware_request_allowed(self, mock_getenv, mock_request, mock_call_next):
        """Test middleware when request is allowed"""
        mock_getenv.return_value = "true"
        
        response = await rate_limit_middleware(mock_request, mock_call_next)
        
        # Should proceed and add rate limit headers
        assert response is not None
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    @patch('app.utils.rate_limiter.rate_limiter')
    @patch('app.utils.rate_limiter.os.getenv')
    async def test_middleware_rate_limit_exceeded(self, mock_getenv, mock_rate_limiter, mock_request):
        """Test middleware when rate limit is exceeded"""
        mock_getenv.return_value = "true"
        mock_rate_limiter.is_allowed.return_value = False
        mock_rate_limiter.get_remaining_requests.return_value = 0
        mock_rate_limiter.requests = 100
        
        async def call_next(request):
            return Mock()
        
        response = await rate_limit_middleware(mock_request, call_next)
        
        # Should return rate limit error response
        assert isinstance(response, JSONResponse)
        assert response.status_code == 429
    
    @patch('app.utils.rate_limiter.os.getenv')
    async def test_middleware_no_client_host(self, mock_getenv, mock_request, mock_call_next):
        """Test middleware when request has no client host"""
        mock_getenv.return_value = "true"
        mock_request.client = None
        
        response = await rate_limit_middleware(mock_request, mock_call_next)
        
        # Should still proceed with "unknown" client ID
        assert response is not None
