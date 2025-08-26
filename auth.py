"""
Authentication Service - CEFR Speaking Exam Simulator

Provides user authentication, password hashing, JWT token management,
and session handling for the application.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import bcrypt
import jwt
from email_validator import validate_email, EmailNotValidError
from bson import ObjectId

from db_mongo.models import User, UserSession, PasswordResetToken
from db_mongo.models import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    TOKEN_LENGTH,
    SESSION_DURATION_DAYS,
    RESET_TOKEN_DURATION_HOURS,
)


class AuthService:
    """Main authentication service class."""
    
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            True if password matches hash, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password meets security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
        
        if len(password) > PASSWORD_MAX_LENGTH:
            return False, f"Password must be no more than {PASSWORD_MAX_LENGTH} characters"
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    def validate_email_format(self, email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > EMAIL_MAX_LENGTH:
            return False, f"Email must be no more than {EMAIL_MAX_LENGTH} characters"
        
        try:
            # Validate email format
            validated = validate_email(email)
            return True, ""
        except EmailNotValidError as e:
            return False, f"Invalid email format: {str(e)}"
    
    def validate_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate user name.
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Name is required"
        
        name = name.strip()
        if len(name) < 2:
            return False, "Name must be at least 2 characters"
        
        if len(name) > NAME_MAX_LENGTH:
            return False, f"Name must be no more than {NAME_MAX_LENGTH} characters"
        
        return True, ""
    
    def generate_jwt_token(self, user_id: str, user_email: str) -> str:
        """
        Generate a JWT token for user authentication.
        
        Args:
            user_id: User ID to include in token
            user_email: User email to include in token
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        payload = {
            "user_id": str(user_id),
            "email": user_email,
            "iat": now,
            "exp": now + timedelta(days=SESSION_DURATION_DAYS),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Tuple of (is_valid, payload_dict)
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}
    
    def generate_secure_token(self, length: int = TOKEN_LENGTH) -> str:
        """
        Generate a cryptographically secure random token.
        
        Args:
            length: Length of token to generate
            
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(length)
    
    def create_password_reset_token(self, user_id: ObjectId) -> PasswordResetToken:
        """
        Create a password reset token for a user.
        
        Args:
            user_id: User ID to create reset token for
            
        Returns:
            PasswordResetToken object
        """
        token = self.generate_secure_token()
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=RESET_TOKEN_DURATION_HOURS)
        
        return PasswordResetToken(
            user_id=user_id,
            token=token,
            created_at=now,
            expires_at=expires_at,
        )
    
    def create_user_session(
        self, 
        user_id: ObjectId, 
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id: User ID to create session for
            user_agent: User agent string from request
            ip_address: IP address from request
            
        Returns:
            UserSession object
        """
        token = self.generate_secure_token()
        now = datetime.utcnow()
        expires_at = now + timedelta(days=SESSION_DURATION_DAYS)
        
        return UserSession(
            user_id=user_id,
            token=token,
            created_at=now,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    
    def validate_registration_data(
        self, 
        email: str, 
        password: str, 
        confirm_password: str, 
        name: str
    ) -> Tuple[bool, str]:
        """
        Validate user registration data.
        
        Args:
            email: User email
            password: User password
            confirm_password: Password confirmation
            name: User name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate email
        email_valid, email_error = self.validate_email_format(email)
        if not email_valid:
            return False, email_error
        
        # Validate name
        name_valid, name_error = self.validate_name(name)
        if not name_valid:
            return False, name_error
        
        # Validate password
        password_valid, password_error = self.validate_password_strength(password)
        if not password_valid:
            return False, password_error
        
        # Check password confirmation
        if password != confirm_password:
            return False, "Passwords do not match"
        
        return True, ""
    
    def prepare_user_response(self, user: User, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Prepare user data for API response.
        
        Args:
            user: User object to prepare
            include_sensitive: Whether to include sensitive data
            
        Returns:
            Dictionary with user data for response
        """
        response = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "preferences": user.preferences,
            "profile": user.profile,
        }
        
        if include_sensitive:
            response["password_hash"] = user.password_hash
        
        return response


# Create global auth service instance
auth_service = AuthService()