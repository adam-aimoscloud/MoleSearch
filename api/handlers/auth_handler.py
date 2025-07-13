"""
Authentication handler
Handles user login and token generation
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import LoginRequest, LoginResponse, UserInfo
from utils.config import get_config_manager
from utils.redis_client import get_redis_client
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# HTTP Bearer scheme for token authentication
security = HTTPBearer(auto_error=False)

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.redis_client = get_redis_client()
        self._users = None
    
    def _get_users(self) -> list:
        """Get users from configuration"""
        if self._users is None:
            user_config = self.config_manager.get_config('security.user_auth', {})
            self._users = user_config.get('users', [])
        return self._users
    
    def is_user_auth_enabled(self) -> bool:
        """Check if user authentication is enabled"""
        user_config = self.config_manager.get_config('security.user_auth', {})
        return user_config.get('enable', False)
    
    def validate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Validate user credentials"""
        users = self._get_users()
        
        for user in users:
            if user.get('username') == username and user.get('password') == password:
                return {
                    'username': user.get('username'),
                    'role': user.get('role', 'user')
                }
        
        return None
    
    def generate_token(self, user_info: Dict[str, Any]) -> str:
        """Generate authentication token"""
        # Generate a random token
        token = secrets.token_urlsafe(32)
        
        # Store token in Redis with expiration
        if self.redis_client.store_token(token, user_info, expiration_hours=24):
            logger.info(f"Generated token for user: {user_info['username']}")
            return token
        else:
            logger.error(f"Failed to store token in Redis for user: {user_info['username']}")
            raise Exception("Failed to store token")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token and return user info"""
        token_data = self.redis_client.get_token_data(token)
        
        if token_data:
            return token_data['user_info']
        
        # If not a user token, check if it's an API key
        try:
            from .api_key_handler import api_key_manager
            api_key_data = api_key_manager.validate_api_key(token)
            if api_key_data:
                # Return API key info as user info for compatibility
                return {
                    'username': f"api_key_{api_key_data.get('name', 'unknown')}",
                    'role': 'api_key',
                    'api_key_id': api_key_data.get('key_id'),
                    'api_key_name': api_key_data.get('name')
                }
        except Exception as e:
            logger.warning(f"Error validating API key: {e}")
        
        return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        return self.redis_client.revoke_token(token)
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens (Redis handles this automatically)"""
        return self.redis_client.cleanup_expired_tokens()


# Global auth service instance
auth_service = AuthService()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login interface
    
    - **username**: Username
    - **password**: Password
    
    Returns authentication token and user information
    """
    try:
        logger.info(f"Login attempt for user: {request.username}")
        
        # Check if user authentication is enabled
        if not auth_service.is_user_auth_enabled():
            raise HTTPException(
                status_code=400,
                detail="User authentication is disabled"
            )
        
        # Validate user credentials
        user_info = auth_service.validate_user(request.username, request.password)
        
        if not user_info:
            logger.warning(f"Login failed for user: {request.username}")
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Generate token
        token = auth_service.generate_token(user_info)
        
        logger.info(f"Login successful for user: {request.username}")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            token=token,
            user_info={
                "username": user_info['username'],
                "role": user_info['role'],
                "login_time": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Login service error: {str(e)}"
        )


@router.post("/logout")
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    User logout interface
    
    Revokes the current authentication token
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )
        
        token = credentials.credentials
        
        if auth_service.revoke_token(token):
            return {
                "success": True,
                "message": "Logout successful"
            }
        else:
            return {
                "success": False,
                "message": "Token not found or already expired"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Logout service error: {str(e)}"
        )


@router.get("/me")
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user information
    
    Returns the current user's information based on the authentication token
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )
        
        token = credentials.credentials
        user_info = auth_service.validate_token(token)
        
        if not user_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        return {
            "success": True,
            "user_info": {
                "username": user_info['username'],
                "role": user_info['role']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Get current user service error: {str(e)}"
        )


async def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Dependency for user token authentication
    
    Returns the user info if authentication is successful, None if disabled
    """
    if not auth_service.is_user_auth_enabled():
        return None
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    
    token = credentials.credentials
    user_info = auth_service.validate_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return user_info


# Cleanup expired tokens periodically
def cleanup_tokens():
    """Cleanup expired tokens (call this periodically)"""
    auth_service.cleanup_expired_tokens() 