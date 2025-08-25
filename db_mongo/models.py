"""
User Data Models and Database Schema - CEFR Speaking Exam Simulator

Defines user authentication models and database schemas for the application.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from bson import ObjectId


@dataclass
class User:
    """User model for authentication and profile management."""
    
    email: str
    password_hash: str
    name: str
    id: Optional[ObjectId] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_verified: bool = False
    is_active: bool = True
    preferences: Dict[str, Any] = field(default_factory=dict)
    profile: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for MongoDB storage."""
        return {
            "_id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "created_at": self.created_at or datetime.utcnow(),
            "last_login": self.last_login,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "preferences": self.preferences,
            "profile": self.profile,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user object from MongoDB document."""
        return cls(
            id=data.get("_id"),
            email=data["email"],
            password_hash=data["password_hash"],
            name=data["name"],
            created_at=data.get("created_at"),
            last_login=data.get("last_login"),
            is_verified=data.get("is_verified", False),
            is_active=data.get("is_active", True),
            preferences=data.get("preferences", {}),
            profile=data.get("profile", {}),
        )


@dataclass
class UserSession:
    """User session model for authentication state management."""
    
    user_id: ObjectId
    token: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session object to dictionary for MongoDB storage."""
        return {
            "user_id": self.user_id,
            "token": self.token,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session object from MongoDB document."""
        return cls(
            user_id=data["user_id"],
            token=data["token"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            is_active=data.get("is_active", True),
            user_agent=data.get("user_agent"),
            ip_address=data.get("ip_address"),
        )


@dataclass
class PasswordResetToken:
    """Password reset token model for secure password recovery."""
    
    user_id: ObjectId
    token: str
    created_at: datetime
    expires_at: datetime
    used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token object to dictionary for MongoDB storage."""
        return {
            "user_id": self.user_id,
            "token": self.token,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "used": self.used,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PasswordResetToken':
        """Create token object from MongoDB document."""
        return cls(
            user_id=data["user_id"],
            token=data["token"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            used=data.get("used", False),
        )


# Database Schema Constants
USER_COLLECTION = "users"
USER_SESSION_COLLECTION = "user_sessions"
PASSWORD_RESET_COLLECTION = "password_reset_tokens"

# Database Indexes for optimal performance
DATABASE_INDEXES = {
    USER_COLLECTION: [
        {"email": 1},  # Unique index on email
        {"created_at": -1},  # Index for sorting by creation date
    ],
    USER_SESSION_COLLECTION: [
        {"token": 1},  # Unique index on session token
        {"user_id": 1},  # Index for user's sessions
        {"expires_at": 1},  # Index for session cleanup
    ],
    PASSWORD_RESET_COLLECTION: [
        {"token": 1},  # Unique index on reset token
        {"user_id": 1},  # Index for user's reset tokens
        {"expires_at": 1},  # Index for token cleanup
    ],
}

# Validation constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 255
TOKEN_LENGTH = 32
SESSION_DURATION_DAYS = 30
RESET_TOKEN_DURATION_HOURS = 24