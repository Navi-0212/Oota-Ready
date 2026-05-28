"""
Unit tests for Custom Exceptions
"""

import pytest
from app.utils.exceptions import (
    BaseAPIException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    ServiceUnavailableError,
    RateLimitExceededError,
    DataLoadError,
    FilterError
)


class TestBaseAPIException:
    """Test cases for BaseAPIException"""
    
    def test_base_exception_with_message(self):
        """Test base exception with message"""
        exc = BaseAPIException("Test error")
        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.details == {}
    
    def test_base_exception_with_status_code(self):
        """Test base exception with custom status code"""
        exc = BaseAPIException("Test error", status_code=404)
        assert exc.status_code == 404
    
    def test_base_exception_with_details(self):
        """Test base exception with details"""
        details = {"field": "location", "value": "invalid"}
        exc = BaseAPIException("Test error", details=details)
        assert exc.details == details


class TestValidationError:
    """Test cases for ValidationError"""
    
    def test_validation_error_default(self):
        """Test validation error with default values"""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.status_code == 400
    
    def test_validation_error_with_details(self):
        """Test validation error with details"""
        details = {"field": "budget", "value": "invalid"}
        exc = ValidationError("Invalid budget", details=details)
        assert exc.details == details


class TestNotFoundError:
    """Test cases for NotFoundError"""
    
    def test_not_found_error_default(self):
        """Test not found error with default values"""
        exc = NotFoundError("Resource not found")
        assert exc.message == "Resource not found"
        assert exc.status_code == 404


class TestDatabaseError:
    """Test cases for DatabaseError"""
    
    def test_database_error_default(self):
        """Test database error with default values"""
        exc = DatabaseError("Database connection failed")
        assert exc.message == "Database connection failed"
        assert exc.status_code == 500


class TestServiceUnavailableError:
    """Test cases for ServiceUnavailableError"""
    
    def test_service_unavailable_error_default(self):
        """Test service unavailable error with default values"""
        exc = ServiceUnavailableError("Service temporarily unavailable")
        assert exc.message == "Service temporarily unavailable"
        assert exc.status_code == 503


class TestRateLimitExceededError:
    """Test cases for RateLimitExceededError"""
    
    def test_rate_limit_error_default_message(self):
        """Test rate limit error with default message"""
        exc = RateLimitExceededError()
        assert exc.message == "Rate limit exceeded"
        assert exc.status_code == 429
    
    def test_rate_limit_error_custom_message(self):
        """Test rate limit error with custom message"""
        exc = RateLimitExceededError("Too many requests")
        assert exc.message == "Too many requests"


class TestDataLoadError:
    """Test cases for DataLoadError"""
    
    def test_data_load_error_default(self):
        """Test data load error with default values"""
        exc = DataLoadError("Failed to load dataset")
        assert exc.message == "Failed to load dataset"
        assert exc.status_code == 500


class TestFilterError:
    """Test cases for FilterError"""
    
    def test_filter_error_default(self):
        """Test filter error with default values"""
        exc = FilterError("Filter operation failed")
        assert exc.message == "Filter operation failed"
        assert exc.status_code == 500
