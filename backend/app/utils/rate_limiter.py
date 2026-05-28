"""
Rate Limiting Middleware
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import os

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(
        self,
        requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100)),
        period: int = int(os.getenv("RATE_LIMIT_PERIOD", 60))
    ):
        """
        Initialize rate limiter
        
        Args:
            requests: Maximum number of requests allowed
            period: Time period in seconds
        """
        self.requests = requests
        self.period = period
        self.requests_history: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for the given client
        
        Args:
            client_id: Client identifier (IP address or API key)
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        # Get request history for this client
        history = self.requests_history[client_id]
        
        # Remove old requests outside the time window
        history[:] = [req_time for req_time in history if current_time - req_time < self.period]
        
        # Check if under limit
        if len(history) < self.requests:
            history.append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """
        Get remaining requests for the given client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        history = self.requests_history[client_id]
        history[:] = [req_time for req_time in history if current_time - req_time < self.period]
        return max(0, self.requests - len(history))
    
    def reset(self, client_id: str):
        """
        Reset rate limit for the given client
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.requests_history:
            del self.requests_history[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    
    Args:
        request: Incoming request
        call_next: Next middleware or route handler
        
    Returns:
        Response or rate limit error
    """
    # Check if rate limiting is enabled
    if os.getenv("RATE_LIMIT_ENABLED", "true").lower() != "true":
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_id = request.client.host if request.client else "unknown"
    
    # Check if request is allowed
    if not rate_limiter.is_allowed(client_id):
        remaining = rate_limiter.get_remaining_requests(client_id)
        logger.warning(f"Rate limit exceeded for client: {client_id}")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": "Rate Limit Exceeded",
                "message": f"Too many requests. Please try again later.",
                "remaining_requests": remaining
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = rate_limiter.get_remaining_requests(client_id)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + rate_limiter.period))
    
    return response
