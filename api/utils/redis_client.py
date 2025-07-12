"""
Redis client utility
Handles Redis connection and token storage operations
"""

import json
import redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.config import get_config_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client for token storage"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self._redis_client = None
        self._connected = False
    
    def _get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return self.config_manager.get_config('security.user_auth.redis', {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
            'decode_responses': True
        })
    
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            config = self._get_redis_config()
            
            self._redis_client = redis.Redis(
                host=config.get('host', 'localhost'),
                port=config.get('port', 6379),
                db=config.get('db', 0),
                password=config.get('password'),
                decode_responses=config.get('decode_responses', True),
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self._redis_client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {config.get('host')}:{config.get('port')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self._connected or not self._redis_client:
            return False
        
        try:
            self._redis_client.ping()
            return True
        except Exception:
            self._connected = False
            return False
    
    def store_token(self, token: str, user_info: Dict[str, Any], expiration_hours: int = 24) -> bool:
        """Store token in Redis with expiration"""
        try:
            if not self.is_connected():
                logger.error("Redis not connected")
                return False
            
            # Prepare token data
            token_data = {
                'user_info': user_info,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=expiration_hours)).isoformat()
            }
            
            # Store in Redis with expiration
            key = f"auth_token:{token}"
            expiration_seconds = expiration_hours * 3600
            
            result = self._redis_client.setex(
                key,
                expiration_seconds,
                json.dumps(token_data)
            )
            
            if result:
                logger.info(f"Token stored in Redis for user: {user_info.get('username')}")
                return True
            else:
                logger.error("Failed to store token in Redis")
                return False
                
        except Exception as e:
            logger.error(f"Error storing token in Redis: {e}")
            return False
    
    def get_token_data(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token data from Redis"""
        try:
            if not self.is_connected():
                logger.error("Redis not connected")
                return None
            
            key = f"auth_token:{token}"
            token_data_str = self._redis_client.get(key)
            
            if not token_data_str:
                return None
            
            token_data = json.loads(token_data_str)
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                # Remove expired token
                self._redis_client.delete(key)
                return None
            
            return token_data
            
        except Exception as e:
            logger.error(f"Error getting token data from Redis: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token by removing it from Redis"""
        try:
            if not self.is_connected():
                logger.error("Redis not connected")
                return False
            
            key = f"auth_token:{token}"
            result = self._redis_client.delete(key)
            
            if result > 0:
                logger.info(f"Token revoked: {token[:8]}...")
                return True
            else:
                logger.warning(f"Token not found for revocation: {token[:8]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking token from Redis: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens (Redis handles this automatically with TTL)"""
        try:
            if not self.is_connected():
                logger.error("Redis not connected")
                return 0
            
            # Redis automatically removes expired keys, so we just log the cleanup
            logger.info("Redis automatically handles token expiration")
            return 0
            
        except Exception as e:
            logger.error(f"Error during token cleanup: {e}")
            return 0
    
    def get_token_count(self) -> int:
        """Get count of active tokens"""
        try:
            if not self.is_connected():
                return 0
            
            pattern = "auth_token:*"
            keys = self._redis_client.keys(pattern)
            return len(keys)
            
        except Exception as e:
            logger.error(f"Error getting token count: {e}")
            return 0
    
    def get_user_tokens(self, username: str) -> list:
        """Get all tokens for a specific user"""
        try:
            if not self.is_connected():
                return []
            
            pattern = "auth_token:*"
            keys = self._redis_client.keys(pattern)
            user_tokens = []
            
            for key in keys:
                token_data_str = self._redis_client.get(key)
                if token_data_str:
                    token_data = json.loads(token_data_str)
                    if token_data.get('user_info', {}).get('username') == username:
                        token = key.replace('auth_token:', '')
                        user_tokens.append(token)
            
            return user_tokens
            
        except Exception as e:
            logger.error(f"Error getting user tokens: {e}")
            return []


# Global Redis client instance
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """Get Redis client instance"""
    global redis_client
    if not redis_client.is_connected():
        redis_client.connect()
    return redis_client


def init_redis():
    """Initialize Redis connection"""
    return get_redis_client().connect() 