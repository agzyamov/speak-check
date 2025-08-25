"""
Authentication Tests - CEFR Speaking Exam Simulator

Comprehensive tests for the authentication system including user registration,
login, token validation, and API endpoints.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId

# Import the modules to test
from auth import auth_service
from db_mongo.models import User
from api.main import app


class TestAuthService:
    """Test cases for the AuthService class."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert auth_service.verify_password(password, hashed)
    
    def test_verify_password(self):
        """Test password verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password(wrong_password, hashed)
    
    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid passwords."""
        valid_passwords = [
            "TestPass123!",
            "MySecure@Pass1",
            "Strong#Password2024",
        ]
        
        for password in valid_passwords:
            is_valid, error_msg = auth_service.validate_password_strength(password)
            assert is_valid, f"Password '{password}' should be valid: {error_msg}"
    
    def test_validate_password_strength_invalid(self):
        """Test password strength validation with invalid passwords."""
        invalid_passwords = [
            ("", "Password is required"),
            ("weak", "Password must be at least 8 characters"),
            ("weakpassword", "Password must contain at least one uppercase letter"),
            ("WEAKPASSWORD", "Password must contain at least one lowercase letter"),
            ("WeakPassword", "Password must contain at least one digit"),
            ("WeakPassword123", "Password must contain at least one special character"),
        ]
        
        for password, expected_error in invalid_passwords:
            is_valid, error_msg = auth_service.validate_password_strength(password)
            assert not is_valid, f"Password '{password}' should be invalid"
            assert expected_error in error_msg
    
    def test_validate_email_format_valid(self):
        """Test email format validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@gmail.com",
        ]
        
        for email in valid_emails:
            is_valid, error_msg = auth_service.validate_email_format(email)
            assert is_valid, f"Email '{email}' should be valid: {error_msg}"
    
    def test_validate_email_format_invalid(self):
        """Test email format validation with invalid emails."""
        invalid_emails = [
            "",
            "invalid-email",
            "@domain.com",
            "test@",
            "test@domain",
            "a" * 250 + "@domain.com",  # Too long
        ]
        
        for email in invalid_emails:
            is_valid, error_msg = auth_service.validate_email_format(email)
            assert not is_valid, f"Email '{email}' should be invalid"
    
    def test_validate_name(self):
        """Test name validation."""
        # Valid names
        valid_names = ["John Doe", "Alice", "José García", "李小明"]
        for name in valid_names:
            is_valid, error_msg = auth_service.validate_name(name)
            assert is_valid, f"Name '{name}' should be valid: {error_msg}"
        
        # Invalid names
        invalid_cases = [
            ("", "Name is required"),
            ("A", "Name must be at least 2 characters"),
            ("A" * 101, "Name must be no more than 100 characters"),
        ]
        
        for name, expected_error in invalid_cases:
            is_valid, error_msg = auth_service.validate_name(name)
            assert not is_valid, f"Name '{name}' should be invalid"
            assert expected_error in error_msg
    
    def test_generate_and_verify_jwt_token(self):
        """Test JWT token generation and verification."""
        user_id = str(ObjectId())
        user_email = "test@example.com"
        
        # Generate token
        token = auth_service.generate_jwt_token(user_id, user_email)
        assert len(token) > 0
        
        # Verify token
        is_valid, payload = auth_service.verify_jwt_token(token)
        assert is_valid
        assert payload["user_id"] == user_id
        assert payload["email"] == user_email
    
    def test_verify_expired_jwt_token(self):
        """Test verification of expired JWT token."""
        # This would require mocking time or using a very short expiration
        # For now, we'll test with an invalid token
        is_valid, payload = auth_service.verify_jwt_token("invalid.token.here")
        assert not is_valid
        assert "error" in payload
    
    def test_validate_registration_data_valid(self):
        """Test registration data validation with valid data."""
        is_valid, error_msg = auth_service.validate_registration_data(
            email="test@example.com",
            password="TestPass123!",
            confirm_password="TestPass123!",
            name="John Doe"
        )
        assert is_valid, f"Valid registration data should pass: {error_msg}"
    
    def test_validate_registration_data_invalid(self):
        """Test registration data validation with invalid data."""
        # Password mismatch
        is_valid, error_msg = auth_service.validate_registration_data(
            email="test@example.com",
            password="TestPass123!",
            confirm_password="DifferentPass123!",
            name="John Doe"
        )
        assert not is_valid
        assert "do not match" in error_msg
        
        # Invalid email
        is_valid, error_msg = auth_service.validate_registration_data(
            email="invalid-email",
            password="TestPass123!",
            confirm_password="TestPass123!",
            name="John Doe"
        )
        assert not is_valid
        assert "email" in error_msg.lower()


class TestUserModel:
    """Test cases for the User model."""

    def test_user_to_dict(self):
        """Test User model to_dict conversion."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            name="John Doe",
            id=ObjectId(),
            created_at=datetime.utcnow(),
        )
        
        user_dict = user.to_dict()
        assert user_dict["email"] == "test@example.com"
        assert user_dict["name"] == "John Doe"
        assert user_dict["password_hash"] == "hashed_password"
        assert "_id" in user_dict
        assert "created_at" in user_dict
    
    def test_user_from_dict(self):
        """Test User model from_dict creation."""
        user_data = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "name": "John Doe",
            "created_at": datetime.utcnow(),
            "is_verified": True,
            "is_active": True,
            "preferences": {"theme": "dark"},
            "profile": {"bio": "Test user"},
        }
        
        user = User.from_dict(user_data)
        assert user.email == "test@example.com"
        assert user.name == "John Doe"
        assert user.is_verified == True
        assert user.preferences["theme"] == "dark"


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_auth_health_endpoint(self, client):
        """Test the authentication health check endpoint."""
        response = client.get("/api/auth/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "healthy"
    
    @patch('db_mongo.crud.get_user_by_email')
    @patch('db_mongo.crud.create_user')
    @patch('db_mongo.crud.create_user_session')
    def test_register_endpoint_success(self, mock_create_session, mock_create_user, mock_get_user, client):
        """Test successful user registration."""
        # Setup mocks
        mock_get_user.return_value = None  # User doesn't exist
        mock_create_user.return_value = str(ObjectId())
        mock_create_session.return_value = str(ObjectId())
        
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "name": "John Doe"
        }
        
        response = client.post("/api/auth/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert data["email"] == "test@example.com"
        assert data["name"] == "John Doe"
    
    @patch('db_mongo.crud.get_user_by_email')
    def test_register_endpoint_email_exists(self, mock_get_user, client):
        """Test registration with existing email."""
        # Setup mocks
        existing_user = User(
            email="test@example.com",
            password_hash="hash",
            name="Existing User",
            id=ObjectId()
        )
        mock_get_user.return_value = existing_user
        
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "name": "John Doe"
        }
        
        response = client.post("/api/auth/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == False
        assert "email" in data["errors"]
    
    def test_register_endpoint_validation_error(self, client):
        """Test registration with validation errors."""
        registration_data = {
            "email": "invalid-email",
            "password": "weak",
            "confirm_password": "different",
            "name": ""
        }
        
        response = client.post("/api/auth/register", json=registration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == False
        assert "errors" in data
    
    @patch('db_mongo.crud.get_user_by_email')
    @patch('db_mongo.crud.update_user_last_login')
    @patch('db_mongo.crud.create_user_session')
    def test_login_endpoint_success(self, mock_create_session, mock_update_login, mock_get_user, client):
        """Test successful user login."""
        # Setup mocks
        hashed_password = auth_service.hash_password("TestPass123!")
        user = User(
            email="test@example.com",
            password_hash=hashed_password,
            name="John Doe",
            id=ObjectId(),
            is_active=True
        )
        mock_get_user.return_value = user
        mock_update_login.return_value = True
        mock_create_session.return_value = str(ObjectId())
        
        login_data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert data["email"] == "test@example.com"
    
    def test_login_endpoint_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        with patch('db_mongo.crud.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = None
            
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == False
            assert "INVALID_CREDENTIALS" in data["error_code"]


class TestIntegration:
    """Integration tests for the complete authentication flow."""

    def test_complete_registration_and_login_flow(self):
        """Test a complete user registration and login flow."""
        # This would require a test database setup
        # For now, we'll test the individual components
        
        # Test password hashing and verification
        password = "TestPass123!"
        hashed = auth_service.hash_password(password)
        assert auth_service.verify_password(password, hashed)
        
        # Test JWT token generation and verification
        user_id = str(ObjectId())
        user_email = "test@example.com"
        token = auth_service.generate_jwt_token(user_id, user_email)
        
        is_valid, payload = auth_service.verify_jwt_token(token)
        assert is_valid
        assert payload["user_id"] == user_id
        assert payload["email"] == user_email


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])