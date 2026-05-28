"""
Custom Exception Classes
"""


class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=404, details=details)


class DatabaseError(BaseAPIException):
    """Raised when database operation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details)


class ServiceUnavailableError(BaseAPIException):
    """Raised when a service is unavailable"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=503, details=details)


class RateLimitExceededError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", details: dict = None):
        super().__init__(message, status_code=429, details=details)


class DataLoadError(BaseAPIException):
    """Raised when data loading fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details)


class FilterError(BaseAPIException):
    """Raised when filtering operation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details)
