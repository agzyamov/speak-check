"""
Streamlit Authentication Integration - CEFR Speaking Exam Simulator

Integration layer between the FastAPI authentication system and Streamlit frontend.
Provides authentication UI components and session management for Streamlit.
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import json
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/auth"


class StreamlitAuth:
    """Streamlit authentication manager."""
    
    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize Streamlit session state for authentication."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        
        if 'auth_token' not in st.session_state:
            st.session_state.auth_token = None
        
        if 'show_auth' not in st.session_state:
            st.session_state.show_auth = False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return st.session_state.authenticated and st.session_state.auth_token is not None
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Get current user data."""
        return st.session_state.user_data
    
    def get_auth_token(self) -> Optional[str]:
        """Get current authentication token."""
        return st.session_state.auth_token
    
    def api_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        Make API request to authentication endpoints.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            data: Request data for POST/PUT requests
            
        Returns:
            Tuple of (success, response_data)
        """
        url = f"{self.api_base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authorization header if token exists
        if st.session_state.auth_token:
            headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            response_data = response.json()
            return response.status_code < 400, response_data
        
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return False, {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return False, {"error": "Invalid response format"}
    
    def register_user(self, email: str, password: str, confirm_password: str, name: str) -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password
            confirm_password: Password confirmation
            name: User name
            
        Returns:
            Tuple of (success, message)
        """
        data = {
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "name": name,
        }
        
        success, response = self.api_request("/register", method="POST", data=data)
        
        if success and response.get("success"):
            # Store authentication data
            st.session_state.authenticated = True
            st.session_state.auth_token = response.get("token")
            st.session_state.user_data = {
                "user_id": response.get("user_id"),
                "email": response.get("email"),
                "name": response.get("name"),
            }
            return True, response.get("message", "Registration successful")
        else:
            error_msg = response.get("message", "Registration failed")
            if response.get("errors"):
                error_details = []
                for field, error in response["errors"].items():
                    error_details.append(f"{field}: {error}")
                error_msg += " - " + ", ".join(error_details)
            return False, error_msg
    
    def login_user(self, email: str, password: str, remember_me: bool = False) -> Tuple[bool, str]:
        """
        Login user with credentials.
        
        Args:
            email: User email
            password: User password
            remember_me: Remember login
            
        Returns:
            Tuple of (success, message)
        """
        data = {
            "email": email,
            "password": password,
            "remember_me": remember_me,
        }
        
        success, response = self.api_request("/login", method="POST", data=data)
        
        if success and response.get("success"):
            # Store authentication data
            st.session_state.authenticated = True
            st.session_state.auth_token = response.get("token")
            st.session_state.user_data = {
                "user_id": response.get("user_id"),
                "email": response.get("email"),
                "name": response.get("name"),
                "is_verified": response.get("is_verified"),
                "last_login": response.get("last_login"),
            }
            return True, response.get("message", "Login successful")
        else:
            error_msg = response.get("message", "Login failed")
            if response.get("errors"):
                error_details = []
                for field, error in response["errors"].items():
                    error_details.append(error)
                error_msg = "; ".join(error_details)
            return False, error_msg
    
    def logout_user(self, logout_all: bool = False) -> Tuple[bool, str]:
        """
        Logout current user.
        
        Args:
            logout_all: Whether to logout from all devices
            
        Returns:
            Tuple of (success, message)
        """
        data = {
            "token": st.session_state.auth_token,
            "logout_all": logout_all,
        }
        
        success, response = self.api_request("/logout", method="POST", data=data)
        
        # Clear session state regardless of API response
        st.session_state.authenticated = False
        st.session_state.auth_token = None
        st.session_state.user_data = None
        
        if success:
            return True, response.get("message", "Logout successful")
        else:
            return False, response.get("message", "Logout completed (with errors)")
    
    def validate_token(self) -> bool:
        """
        Validate current authentication token.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not st.session_state.auth_token:
            return False
        
        data = {"token": st.session_state.auth_token}
        success, response = self.api_request("/validate-token", method="POST", data=data)
        
        if success and response.get("success") and response.get("valid"):
            return True
        else:
            # Token is invalid, clear session
            st.session_state.authenticated = False
            st.session_state.auth_token = None
            st.session_state.user_data = None
            return False
    
    def update_profile(self, name: Optional[str] = None, preferences: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Update user profile.
        
        Args:
            name: New name
            preferences: New preferences
            
        Returns:
            Tuple of (success, message)
        """
        data = {}
        if name is not None:
            data["name"] = name
        if preferences is not None:
            data["preferences"] = preferences
        
        if not data:
            return False, "No data provided for update"
        
        success, response = self.api_request("/profile", method="PUT", data=data)
        
        if success and response.get("success"):
            # Update local user data
            if st.session_state.user_data:
                if name is not None:
                    st.session_state.user_data["name"] = response.get("name", name)
                if preferences is not None:
                    st.session_state.user_data["preferences"] = response.get("preferences", preferences)
            
            return True, response.get("message", "Profile updated successfully")
        else:
            error_msg = response.get("message", "Profile update failed")
            return False, error_msg
    
    def render_login_form(self) -> None:
        """Render login form in Streamlit."""
        st.subheader("🔑 Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Remember me")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                if st.form_submit_button("Register Instead", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()
        
        if login_submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return
            
            with st.spinner("Logging in..."):
                success, message = self.login_user(email, password, remember_me)
            
            if success:
                st.success(message)
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
    
    def render_register_form(self) -> None:
        """Render registration form in Streamlit."""
        st.subheader("📝 Create Account")
        
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Your full name")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            # Password requirements info
            st.info("""
            **Password Requirements:**
            - At least 8 characters long
            - Contains uppercase and lowercase letters
            - Contains at least one number
            - Contains at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                register_submitted = st.form_submit_button("Create Account", use_container_width=True)
            with col2:
                if st.form_submit_button("Login Instead", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()
        
        if register_submitted:
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            with st.spinner("Creating account..."):
                success, message = self.register_user(email, password, confirm_password, name)
            
            if success:
                st.success(message)
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
    
    def render_auth_ui(self) -> None:
        """Render authentication UI based on current state."""
        # Initialize show_register if not exists
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        
        if st.session_state.show_register:
            self.render_register_form()
        else:
            self.render_login_form()
    
    def render_user_menu(self) -> None:
        """Render user menu for authenticated users."""
        if not self.is_authenticated():
            return
        
        user_data = self.get_user_data()
        if not user_data:
            return
        
        with st.sidebar:
            st.markdown("---")
            st.subheader(f"👤 {user_data.get('name', 'User')}")
            st.caption(f"📧 {user_data.get('email', '')}")
            
            if st.button("🚪 Logout", use_container_width=True):
                with st.spinner("Logging out..."):
                    success, message = self.logout_user()
                
                if success:
                    st.success(message)
                else:
                    st.warning(message)
                
                time.sleep(1)
                st.rerun()
            
            # Profile settings
            with st.expander("⚙️ Profile Settings"):
                new_name = st.text_input("Name", value=user_data.get('name', ''), key="profile_name")
                
                if st.button("Update Profile"):
                    if new_name != user_data.get('name', ''):
                        with st.spinner("Updating profile..."):
                            success, message = self.update_profile(name=new_name)
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    
    def require_auth(self) -> bool:
        """
        Require authentication for the current page.
        
        Returns:
            True if user is authenticated, False otherwise
        """
        # Validate current token
        if self.is_authenticated():
            if not self.validate_token():
                st.warning("Your session has expired. Please log in again.")
                st.stop()
        
        if not self.is_authenticated():
            st.title("🎤 CEFR Speaking Exam Simulator")
            st.markdown("Please log in or create an account to continue.")
            
            self.render_auth_ui()
            st.stop()
        
        return True


# Create global auth instance
streamlit_auth = StreamlitAuth()