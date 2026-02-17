"""Error handling utilities for MediaAgent."""

from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """Error codes for MediaAgent."""
    
    # General errors
    UNKNOWN = "ERR000"
    
    # AI errors
    AI_API_ERROR = "AI001"
    AI_RATE_LIMIT = "AI002"
    AI_INVALID_RESPONSE = "AI003"
    
    # Platform errors
    PLATFORM_LOGIN_FAILED = "PL001"
    PLATFORM_POST_FAILED = "PL002"
    PLATFORM_RATE_LIMIT = "PL003"
    PLATFORM_AUTH_REQUIRED = "PL004"
    
    # Database errors
    DB_CONNECTION_ERROR = "DB001"
    DB_QUERY_ERROR = "DB002"
    
    # Validation errors
    VALIDATION_ERROR = "VAL001"


ERROR_MESSAGES = {
    ErrorCode.UNKNOWN: "An unexpected error occurred. Please try again.",
    
    ErrorCode.AI_API_ERROR: "AI service error. Please check your API key.",
    ErrorCode.AI_RATE_LIMIT: "AI rate limit reached. Please wait and try again.",
    ErrorCode.AI_INVALID_RESPONSE: "AI returned an invalid response. Please try again.",
    
    ErrorCode.PLATFORM_LOGIN_FAILED: "Failed to login. Please check your credentials.",
    ErrorCode.PLATFORM_POST_FAILED: "Failed to post. Platform may be unavailable.",
    ErrorCode.PLATFORM_RATE_LIMIT: "Platform rate limit reached. Please wait.",
    ErrorCode.PLATFORM_AUTH_REQUIRED: "Please connect your account in Settings.",
    
    ErrorCode.DB_CONNECTION_ERROR: "Database error. Please restart the application.",
    ErrorCode.DB_QUERY_ERROR: "Database query failed. Please try again.",
    
    ErrorCode.VALIDATION_ERROR: "Invalid input. Please check your entries.",
}


class MediaAgentError(Exception):
    """Base exception for MediaAgent."""
    
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        details: Optional[str] = None,
    ):
        self.message = message
        self.code = code
        self.details = details
        self.user_message = ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.UNKNOWN])
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.code.value}] {self.message}"


class AIError(MediaAgentError):
    """AI-related errors."""
    pass


class PlatformError(MediaAgentError):
    """Platform-related errors."""
    pass


class DatabaseError(MediaAgentError):
    """Database-related errors."""
    pass


class ValidationError(MediaAgentError):
    """Validation errors."""
    pass


def handle_error(error: Exception) -> dict:
    """Handle an exception and return user-friendly error info.
    
    Args:
        error: Exception to handle
        
    Returns:
        Dict with error details
    """
    if isinstance(error, MediaAgentError):
        return {
            "success": False,
            "error_code": error.code.value,
            "message": error.user_message,
            "details": error.details,
        }
    
    # Generic error handling
    return {
        "success": False,
        "error_code": ErrorCode.UNKNOWN.value,
        "message": ERROR_MESSAGES[ErrorCode.UNKNOWN],
        "details": str(error),
    }
