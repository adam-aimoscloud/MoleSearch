"""
Authentication middleware
Handles token-based authentication for API endpoints
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from utils.config import get_config_manager
from utils.redis_client import get_redis_client
from utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer scheme for token authentication
security = HTTPBearer(auto_error=False)


class TokenAuth:
    """Token authentication handler"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.redis_client = get_redis_client()
    
    def is_token_auth_enabled(self) -> bool:
        """Check if token authentication is enabled"""
        return True  # Always enabled for user authentication
    
    def get_token_header(self) -> str:
        """Get token header name"""
        return 'Authorization'
    
    def get_token_prefix(self) -> str:
        """Get token prefix"""
        return 'Bearer '
    
    def validate_token(self, token: str) -> bool:
        """Validate token"""
        if not token:
            return False
        
        # Remove prefix if present
        prefix = self.get_token_prefix()
        if token.startswith(prefix):
            token = token[len(prefix):]
        
        # Check if token exists in Redis
        token_data = self.redis_client.get_token_data(token)
        return token_data is not None
    
    async def authenticate(self, request: Request) -> Optional[str]:
        """Authenticate request"""
        if not self.is_token_auth_enabled():
            return None
        
        # Get token from header
        header_name = self.get_token_header()
        token = request.headers.get(header_name)
        
        if not token:
            logger.warning(f"Missing {header_name} header")
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )
        
        # Validate token
        if not self.validate_token(token):
            logger.warning("Invalid token provided")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        logger.debug("Token authentication successful")
        return token


# Global token auth instance
token_auth = TokenAuth()


async def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Dependency for token authentication
    
    Returns the token if authentication is successful, None if disabled
    """
    if not token_auth.is_token_auth_enabled():
        return None
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    
    token = credentials.credentials
    if not token_auth.validate_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return token


def require_auth():
    """Decorator to require authentication"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check if auth is enabled
            if token_auth.is_token_auth_enabled():
                # Get request object (assuming it's the first argument)
                if args and hasattr(args[0], 'headers'):
                    request = args[0]
                    await token_auth.authenticate(request)
            return await func(*args, **kwargs)
        return wrapper
    return decorator 