"""
API Key management handler
Handles API Key creation, deletion, and management
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from .models import (
    CreateApiKeyRequest, CreateApiKeyResponse, ApiKeyInfo,
    ApiKeyListResponse, DeleteApiKeyResponse
)
from .auth import get_current_token
from utils.redis_client import get_redis_client
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api-keys", tags=["API Key Management"])


class ApiKeyManager:
    """API Key management service"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.key_prefix = "api_key:"
        self.key_list_prefix = "api_key_list:"
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        return f"ms_{secrets.token_urlsafe(32)}"
    
    def create_api_key(self, name: str, expires_in_days: Optional[int] = None, 
                      permissions: List[str] = None) -> ApiKeyInfo:
        """Create a new API key"""
        try:
            key_id = str(uuid.uuid4())
            api_key = self.generate_api_key()
            created_at = datetime.now()
            
            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = created_at + timedelta(days=expires_in_days)
            
            # Prepare API key data
            key_data = {
                'key_id': key_id,
                'name': name,
                'key': api_key,
                'created_at': created_at.isoformat(),
                'last_used_at': None,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'permissions': permissions or []
            }
            
            # Store in Redis
            redis_key = f"{self.key_prefix}{key_id}"
            expiration_seconds = None
            if expires_in_days:
                expiration_seconds = expires_in_days * 24 * 3600
            
            if expiration_seconds:
                self.redis_client._redis_client.setex(
                    redis_key,
                    expiration_seconds,
                    self._serialize_key_data(key_data)
                )
            else:
                self.redis_client._redis_client.set(
                    redis_key,
                    self._serialize_key_data(key_data)
                )
            
            # Add to key list
            self.redis_client._redis_client.sadd(self.key_list_prefix, key_id)
            
            logger.info(f"Created API key: {name} ({key_id})")
            return ApiKeyInfo(**key_data)
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def list_api_keys(self) -> List[ApiKeyInfo]:
        """List all API keys"""
        try:
            key_ids = self.redis_client._redis_client.smembers(self.key_list_prefix)
            api_keys = []
            
            for key_id in key_ids:
                redis_key = f"{self.key_prefix}{key_id}"
                key_data_str = self.redis_client._redis_client.get(redis_key)
                
                if key_data_str:
                    key_data = self._deserialize_key_data(key_data_str)
                    
                    # Check if expired
                    if key_data.get('expires_at'):
                        expires_at = datetime.fromisoformat(key_data['expires_at'])
                        if datetime.now() > expires_at:
                            # Remove expired key
                            self.redis_client._redis_client.delete(redis_key)
                            self.redis_client._redis_client.srem(self.key_list_prefix, key_id)
                            continue
                    
                    api_keys.append(ApiKeyInfo(**key_data))
            
            return api_keys
            
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []
    
    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        try:
            redis_key = f"{self.key_prefix}{key_id}"
            result = self.redis_client._redis_client.delete(redis_key)
            
            if result > 0:
                self.redis_client._redis_client.srem(self.key_list_prefix, key_id)
                logger.info(f"Deleted API key: {key_id}")
                return True
            else:
                logger.warning(f"API key not found for deletion: {key_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete API key: {e}")
            return False
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return key info"""
        try:
            key_ids = self.redis_client._redis_client.smembers(self.key_list_prefix)
            
            for key_id in key_ids:
                redis_key = f"{self.key_prefix}{key_id}"
                key_data_str = self.redis_client._redis_client.get(redis_key)
                
                if key_data_str:
                    key_data = self._deserialize_key_data(key_data_str)
                    
                    if key_data.get('key') == api_key:
                        # Check if expired
                        if key_data.get('expires_at'):
                            expires_at = datetime.fromisoformat(key_data['expires_at'])
                            if datetime.now() > expires_at:
                                # Remove expired key
                                self.redis_client._redis_client.delete(redis_key)
                                self.redis_client._redis_client.srem(self.key_list_prefix, key_id)
                                return None
                        
                        # Update last used time
                        key_data['last_used_at'] = datetime.now().isoformat()
                        self.redis_client._redis_client.set(
                            redis_key,
                            self._serialize_key_data(key_data)
                        )
                        
                        return key_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None
    
    def _serialize_key_data(self, key_data: Dict[str, Any]) -> str:
        """Serialize key data to JSON string"""
        import json
        return json.dumps(key_data)
    
    def _deserialize_key_data(self, key_data_str: str) -> Dict[str, Any]:
        """Deserialize key data from JSON string"""
        import json
        return json.loads(key_data_str)


# Global API key manager instance
api_key_manager = ApiKeyManager()


@router.post("/create", response_model=CreateApiKeyResponse)
async def create_api_key(
    request: CreateApiKeyRequest,
    token: Optional[str] = Depends(get_current_token)
):
    """
    Create a new API key
    
    - **name**: API key name
    - **expires_in_days**: Expiration in days (optional for permanent)
    - **permissions**: API key permissions (optional)
    """
    try:
        logger.info(f"Creating API key: {request.name}")
        
        api_key_info = api_key_manager.create_api_key(
            name=request.name,
            expires_in_days=request.expires_in_days,
            permissions=request.permissions
        )
        
        return CreateApiKeyResponse(
            success=True,
            message="API key created successfully",
            api_key=api_key_info
        )
        
    except Exception as e:
        logger.error(f"Failed to create API key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/list", response_model=ApiKeyListResponse)
async def list_api_keys(
    token: Optional[str] = Depends(get_current_token)
):
    """
    List all API keys
    """
    try:
        api_keys = api_key_manager.list_api_keys()
        
        return ApiKeyListResponse(
            success=True,
            message="API keys retrieved successfully",
            api_keys=api_keys,
            total=len(api_keys)
        )
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.delete("/{key_id}", response_model=DeleteApiKeyResponse)
async def delete_api_key(
    key_id: str,
    token: Optional[str] = Depends(get_current_token)
):
    """
    Delete an API key
    
    - **key_id**: API key ID to delete
    """
    try:
        success = api_key_manager.delete_api_key(key_id)
        
        if success:
            return DeleteApiKeyResponse(
                success=True,
                message="API key deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="API key not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete API key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete API key: {str(e)}"
        ) 