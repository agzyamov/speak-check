"""
Authentication Request/Response Schemas - CEFR Speaking Exam Simulator

Defines request and response schemas for authentication endpoints using
dataclasses for type safety and validation.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class RegisterRequest:
    """Request schema for user registration."""
    
    email: str
    password: str
    confirm_password: str
    name: str
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate registration request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not all([self.email, self.password, self.confirm_password, self.name]):
            return False, "All fields are required"
        
        if self.password != self.confirm_password:
            return False, "Passwords do not match"
        
        return True, ""


@dataclass
class RegisterResponse:
    """Response schema for user registration."""
    
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    token: Optional[str] = None
    message: str = ""
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.success:
            result.update({
                "user_id": self.user_id,
                "email": self.email,
                "name": self.name,
                "token": self.token,
            })
        else:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class LoginRequest:
    """Request schema for user login."""
    
    email: str
    password: str
    remember_me: bool = False
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate login request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.email:
            return False, "Email is required"
        
        if not self.password:
            return False, "Password is required"
        
        return True, ""


@dataclass
class LoginResponse:
    """Response schema for user login."""
    
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    token: Optional[str] = None
    is_verified: Optional[bool] = None
    last_login: Optional[str] = None
    message: str = ""
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.success:
            result.update({
                "user_id": self.user_id,
                "email": self.email,
                "name": self.name,
                "token": self.token,
                "is_verified": self.is_verified,
                "last_login": self.last_login,
            })
        else:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class LogoutRequest:
    """Request schema for user logout."""
    
    token: str
    logout_all: bool = False  # If True, logout from all devices
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate logout request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.token:
            return False, "Token is required"
        
        return True, ""


@dataclass
class LogoutResponse:
    """Response schema for user logout."""
    
    success: bool
    message: str = ""
    sessions_invalidated: int = 0
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.success:
            result["sessions_invalidated"] = self.sessions_invalidated
        else:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class ProfileRequest:
    """Request schema for profile updates."""
    
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate profile update request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # At least one field must be provided for update
        if not any([self.name, self.preferences, self.profile]):
            return False, "At least one field must be provided for update"
        
        # Validate name if provided
        if self.name is not None:
            name = self.name.strip()
            if len(name) < 2:
                return False, "Name must be at least 2 characters"
            if len(name) > 100:
                return False, "Name must be no more than 100 characters"
        
        return True, ""


@dataclass
class ProfileResponse:
    """Response schema for profile operations."""
    
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    is_verified: Optional[bool] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    message: str = ""
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.success:
            result.update({
                "user_id": self.user_id,
                "email": self.email,
                "name": self.name,
                "is_verified": self.is_verified,
                "created_at": self.created_at,
                "last_login": self.last_login,
                "preferences": self.preferences,
                "profile": self.profile,
            })
        else:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class PasswordResetRequest:
    """Request schema for password reset."""
    
    email: str
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate password reset request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.email:
            return False, "Email is required"
        
        return True, ""


@dataclass
class PasswordResetResponse:
    """Response schema for password reset."""
    
    success: bool
    message: str = ""
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if not self.success:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class PasswordResetConfirmRequest:
    """Request schema for password reset confirmation."""
    
    token: str
    new_password: str
    confirm_password: str
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate password reset confirmation request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.token:
            return False, "Reset token is required"
        
        if not self.new_password:
            return False, "New password is required"
        
        if not self.confirm_password:
            return False, "Password confirmation is required"
        
        if self.new_password != self.confirm_password:
            return False, "Passwords do not match"
        
        return True, ""


@dataclass
class TokenValidationRequest:
    """Request schema for token validation."""
    
    token: str
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate token validation request data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.token:
            return False, "Token is required"
        
        return True, ""


@dataclass
class TokenValidationResponse:
    """Response schema for token validation."""
    
    success: bool
    valid: bool = False
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    expires_at: Optional[str] = None
    message: str = ""
    errors: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "valid": self.valid,
            "message": self.message,
        }
        
        if self.success and self.valid:
            result.update({
                "user_id": self.user_id,
                "email": self.email,
                "name": self.name,
                "expires_at": self.expires_at,
            })
        elif not self.success:
            result["errors"] = self.errors or {}
        
        return result


@dataclass
class ApiErrorResponse:
    """Generic API error response schema."""
    
    success: bool = False
    message: str = "An error occurred"
    error_code: Optional[str] = None
    errors: Optional[Dict[str, str]] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.error_code:
            result["error_code"] = self.error_code
        
        if self.errors:
            result["errors"] = self.errors
        
        if self.timestamp:
            result["timestamp"] = self.timestamp
        else:
            result["timestamp"] = datetime.utcnow().isoformat()
        
        return result


# Helper functions for schema creation

def create_success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Standardized success response dictionary
    """
    return {
        "success": True,
        "message": message,
        **data
    }


def create_error_response(
    message: str = "An error occurred",
    errors: Optional[Dict[str, str]] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        errors: Field-specific errors
        error_code: Error code for client handling
        
    Returns:
        Standardized error response dictionary
    """
    response = ApiErrorResponse(
        message=message,
        errors=errors,
        error_code=error_code
    )
    return response.to_dict()


def create_validation_error_response(errors: Dict[str, str]) -> Dict[str, Any]:
    """
    Create a validation error response.
    
    Args:
        errors: Validation errors by field
        
    Returns:
        Standardized validation error response dictionary
    """
    return create_error_response(
        message="Validation failed",
        errors=errors,
        error_code="VALIDATION_ERROR"
    )