"""
Authentication API Routes - CEFR Speaking Exam Simulator

FastAPI routes for user registration, login, logout, and profile management.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from bson import ObjectId

from auth import auth_service
from db_mongo.models import User
from db_mongo.crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    update_user_last_login,
    create_user_session,
    get_user_session_by_token,
    invalidate_user_session,
    invalidate_user_sessions,
    create_database_indexes,
)
from schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    ProfileRequest,
    ProfileResponse,
    TokenValidationRequest,
    TokenValidationResponse,
    create_success_response,
    create_error_response,
    create_validation_error_response,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security scheme for JWT tokens
security = HTTPBearer()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize database indexes on startup
try:
    create_database_indexes()
    logger.info("Database indexes created successfully")
except Exception as e:
    logger.warning(f"Could not create database indexes: {e}")


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract client information from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tuple of (user_agent, ip_address)
    """
    user_agent = request.headers.get("user-agent")
    
    # Get IP address, considering reverse proxy headers
    ip_address = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip")
        or request.client.host if request.client else None
    )
    
    return user_agent, ip_address


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: JWT token from Authorization header
        
    Returns:
        User object for authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Validate JWT token
    is_valid, payload = auth_service.verify_jwt_token(token)
    if not is_valid:
        error_msg = payload.get("error", "Invalid token") if payload else "Invalid token"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = payload["user_id"]
    user = get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/register", response_model=Dict[str, Any])
@limiter.limit("3/minute")  # Allow 3 registration attempts per minute
async def register_user(request: Request, registration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new user account.
    
    Args:
        request: FastAPI request object
        registration_data: Registration data from request body
        
    Returns:
        Registration response with user data and token
    """
    try:
        # Parse and validate registration data
        reg_request = RegisterRequest(
            email=registration_data.get("email", "").strip().lower(),
            password=registration_data.get("password", ""),
            confirm_password=registration_data.get("confirm_password", ""),
            name=registration_data.get("name", "").strip(),
        )
        
        # Validate request data
        is_valid, error_msg = reg_request.validate()
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        # Validate registration data using auth service
        is_valid, error_msg = auth_service.validate_registration_data(
            reg_request.email,
            reg_request.password,
            reg_request.confirm_password,
            reg_request.name,
        )
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        # Check if user already exists
        existing_user = get_user_by_email(reg_request.email)
        if existing_user:
            return create_error_response(
                message="Registration failed",
                errors={"email": "Email address is already registered"},
                error_code="EMAIL_EXISTS",
            )
        
        # Hash password
        password_hash = auth_service.hash_password(reg_request.password)
        
        # Create user object
        user = User(
            email=reg_request.email,
            password_hash=password_hash,
            name=reg_request.name,
            created_at=datetime.utcnow(),
        )
        
        # Save user to database
        user_id = create_user(user)
        user.id = ObjectId(user_id)
        
        # Generate JWT token
        jwt_token = auth_service.generate_jwt_token(user_id, user.email)
        
        # Create user session
        user_agent, ip_address = get_client_info(request)
        session = auth_service.create_user_session(
            user_id=ObjectId(user_id),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        create_user_session(session)
        
        # Prepare response
        response = RegisterResponse(
            success=True,
            user_id=user_id,
            email=user.email,
            name=user.name,
            token=jwt_token,
            message="User registered successfully",
        )
        
        logger.info(f"User registered successfully: {user.email} (ID: {user_id})")
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return create_error_response(
            message="Registration failed due to server error",
            error_code="SERVER_ERROR",
        )


@router.post("/login", response_model=Dict[str, Any])
@limiter.limit("5/minute")  # Allow 5 login attempts per minute
async def login_user(request: Request, login_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Authenticate user login.
    
    Args:
        request: FastAPI request object
        login_data: Login credentials from request body
        
    Returns:
        Login response with user data and token
    """
    try:
        # Parse and validate login data
        login_request = LoginRequest(
            email=login_data.get("email", "").strip().lower(),
            password=login_data.get("password", ""),
            remember_me=login_data.get("remember_me", False),
        )
        
        # Validate request data
        is_valid, error_msg = login_request.validate()
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        # Find user by email
        user = get_user_by_email(login_request.email)
        if not user:
            return create_error_response(
                message="Login failed",
                errors={"general": "Invalid email or password"},
                error_code="INVALID_CREDENTIALS",
            )
        
        # Check if user is active
        if not user.is_active:
            return create_error_response(
                message="Login failed",
                errors={"general": "Account is deactivated"},
                error_code="ACCOUNT_DEACTIVATED",
            )
        
        # Verify password
        if not auth_service.verify_password(login_request.password, user.password_hash):
            return create_error_response(
                message="Login failed",
                errors={"general": "Invalid email or password"},
                error_code="INVALID_CREDENTIALS",
            )
        
        # Update last login time
        update_user_last_login(str(user.id))
        user.last_login = datetime.utcnow()
        
        # Generate JWT token
        jwt_token = auth_service.generate_jwt_token(str(user.id), user.email)
        
        # Create user session
        user_agent, ip_address = get_client_info(request)
        session = auth_service.create_user_session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        create_user_session(session)
        
        # Prepare response
        response = LoginResponse(
            success=True,
            user_id=str(user.id),
            email=user.email,
            name=user.name,
            token=jwt_token,
            is_verified=user.is_verified,
            last_login=user.last_login.isoformat() if user.last_login else None,
            message="Login successful",
        )
        
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return create_error_response(
            message="Login failed due to server error",
            error_code="SERVER_ERROR",
        )


@router.post("/logout", response_model=Dict[str, Any])
async def logout_user(logout_data: Dict[str, Any], current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Logout user and invalidate session.
    
    Args:
        logout_data: Logout request data
        current_user: Current authenticated user
        
    Returns:
        Logout response
    """
    try:
        # Parse logout request
        logout_request = LogoutRequest(
            token=logout_data.get("token", ""),
            logout_all=logout_data.get("logout_all", False),
        )
        
        # Validate request data
        is_valid, error_msg = logout_request.validate()
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        sessions_invalidated = 0
        
        if logout_request.logout_all:
            # Invalidate all user sessions
            sessions_invalidated = invalidate_user_sessions(str(current_user.id))
        else:
            # Invalidate specific session
            if invalidate_user_session(logout_request.token):
                sessions_invalidated = 1
        
        # Prepare response
        response = LogoutResponse(
            success=True,
            message="Logout successful",
            sessions_invalidated=sessions_invalidated,
        )
        
        logger.info(f"User logged out: {current_user.email} (ID: {current_user.id}), sessions invalidated: {sessions_invalidated}")
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return create_error_response(
            message="Logout failed due to server error",
            error_code="SERVER_ERROR",
        )


@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile data
    """
    try:
        response = ProfileResponse(
            success=True,
            user_id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at.isoformat() if current_user.created_at else None,
            last_login=current_user.last_login.isoformat() if current_user.last_login else None,
            preferences=current_user.preferences,
            profile=current_user.profile,
            message="Profile retrieved successfully",
        )
        
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return create_error_response(
            message="Failed to retrieve profile",
            error_code="SERVER_ERROR",
        )


@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update current user's profile information.
    
    Args:
        profile_data: Profile update data
        current_user: Current authenticated user
        
    Returns:
        Updated user profile data
    """
    try:
        # Parse profile update request
        profile_request = ProfileRequest(
            name=profile_data.get("name"),
            preferences=profile_data.get("preferences"),
            profile=profile_data.get("profile"),
        )
        
        # Validate request data
        is_valid, error_msg = profile_request.validate()
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        # Prepare update data
        update_data = {}
        
        if profile_request.name is not None:
            update_data["name"] = profile_request.name.strip()
        
        if profile_request.preferences is not None:
            update_data["preferences"] = profile_request.preferences
        
        if profile_request.profile is not None:
            update_data["profile"] = profile_request.profile
        
        # Update user in database
        success = update_user(str(current_user.id), update_data)
        if not success:
            return create_error_response(
                message="Failed to update profile",
                error_code="UPDATE_FAILED",
            )
        
        # Get updated user data
        updated_user = get_user_by_id(str(current_user.id))
        if not updated_user:
            return create_error_response(
                message="Failed to retrieve updated profile",
                error_code="RETRIEVAL_FAILED",
            )
        
        # Prepare response
        response = ProfileResponse(
            success=True,
            user_id=str(updated_user.id),
            email=updated_user.email,
            name=updated_user.name,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else None,
            last_login=updated_user.last_login.isoformat() if updated_user.last_login else None,
            preferences=updated_user.preferences,
            profile=updated_user.profile,
            message="Profile updated successfully",
        )
        
        logger.info(f"Profile updated for user: {updated_user.email} (ID: {updated_user.id})")
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return create_error_response(
            message="Failed to update profile due to server error",
            error_code="SERVER_ERROR",
        )


@router.post("/validate-token", response_model=Dict[str, Any])
@limiter.limit("10/minute")  # Allow 10 token validations per minute
async def validate_token(request: Request, token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a JWT token and return user information if valid.
    
    Args:
        token_data: Token validation request data
        
    Returns:
        Token validation response
    """
    try:
        # Parse token validation request
        token_request = TokenValidationRequest(
            token=token_data.get("token", ""),
        )
        
        # Validate request data
        is_valid, error_msg = token_request.validate()
        if not is_valid:
            return create_validation_error_response({"general": error_msg})
        
        # Validate JWT token
        is_valid, payload = auth_service.verify_jwt_token(token_request.token)
        if not is_valid:
            response = TokenValidationResponse(
                success=True,
                valid=False,
                message="Token is invalid or expired",
            )
            return response.to_dict()
        
        # Get user information
        user_id = payload["user_id"]
        user = get_user_by_id(user_id)
        if not user or not user.is_active:
            response = TokenValidationResponse(
                success=True,
                valid=False,
                message="User not found or inactive",
            )
            return response.to_dict()
        
        # Prepare response
        expires_at = datetime.fromtimestamp(payload["exp"]).isoformat()
        response = TokenValidationResponse(
            success=True,
            valid=True,
            user_id=str(user.id),
            email=user.email,
            name=user.name,
            expires_at=expires_at,
            message="Token is valid",
        )
        
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return create_error_response(
            message="Token validation failed due to server error",
            error_code="SERVER_ERROR",
        )


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the authentication API.
    
    Returns:
        Health status information
    """
    return create_success_response(
        data={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "auth-api",
        },
        message="Authentication API is healthy"
    )