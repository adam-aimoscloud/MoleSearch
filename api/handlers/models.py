"""
API request and response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Authentication models
class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class LoginResponse(BaseModel):
    """Login response model"""
    success: bool = Field(..., description="Login success status")
    message: str = Field(..., description="Response message")
    token: Optional[str] = Field(None, description="Authentication token")
    user_info: Optional[Dict[str, Any]] = Field(None, description="User information")

class UserInfo(BaseModel):
    """User information model"""
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    login_time: datetime = Field(..., description="Login time")

# Search models
class TextSearchRequest(BaseModel):
    """Text search request model"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")

class ImageSearchRequest(BaseModel):
    """Image search request model"""
    image_url: str = Field(..., description="Image URL")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")

class VideoSearchRequest(BaseModel):
    """Video search request model"""
    video_url: str = Field(..., description="Video URL")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")

class MultimodalSearchRequest(BaseModel):
    """Multimodal search request model"""
    text: Optional[str] = Field(None, description="Text query")
    image_url: Optional[str] = Field(None, description="Image URL")
    video_url: Optional[str] = Field(None, description="Video URL")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")

class SearchResultItem(BaseModel):
    """Search result item model"""
    id: str = Field(..., description="Result ID")
    text: str = Field("", description="Text content")
    image_url: Optional[str] = Field("", description="Image URL")
    video_url: Optional[str] = Field("", description="Video URL")
    image_text: str = Field("", description="Image description text")
    video_text: str = Field("", description="Video description text")
    score: float = Field(0.0, description="Similarity score")

class SearchResponse(BaseModel):
    """Search response model"""
    success: bool = Field(..., description="Search success status")
    message: str = Field(..., description="Response message")
    total: int = Field(0, description="Total number of results")
    results: List[SearchResultItem] = Field([], description="Search results")
    query_time: float = Field(0.0, description="Query execution time")

# Data management models
class InsertDataRequest(BaseModel):
    """Single data insertion request model"""
    text: Optional[str] = Field(None, description="Text content")
    image_url: Optional[str] = Field(None, description="Image URL")
    video_url: Optional[str] = Field(None, description="Video URL")

class BatchInsertRequest(BaseModel):
    """Batch data insertion request model"""
    data_list: List[InsertDataRequest] = Field(..., description="Data list to insert")

class InsertResponse(BaseModel):
    """Data insertion response model"""
    success: bool = Field(..., description="Insertion success status")
    message: str = Field(..., description="Response message")
    inserted_count: int = Field(0, description="Number of successfully inserted items")
    processing_time: float = Field(0.0, description="Processing time")

class DataListItem(BaseModel):
    """Data list item model"""
    id: str = Field(..., description="Data ID")
    text: str = Field("", description="Text content")
    image_url: Optional[str] = Field("", description="Image URL")
    video_url: Optional[str] = Field("", description="Video URL")
    image_text: str = Field("", description="Image description text")
    video_text: str = Field("", description="Video description text")

class DataListRequest(BaseModel):
    """Data list request model"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")

class DataListResponse(BaseModel):
    """Data list response model"""
    success: bool = Field(..., description="Query success status")
    message: str = Field(..., description="Response message")
    total: int = Field(0, description="Total number of items")
    items: List[DataListItem] = Field([], description="Data items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Items per page")

# File upload models
class FileUploadResponse(BaseModel):
    """File upload response model"""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Response message")
    file_url: str = Field("", description="Uploaded file URL")
    oss_path: str = Field("", description="OSS storage path")
    file_size: int = Field(0, description="File size in bytes")
    file_extension: str = Field("", description="File extension")
    upload_time: str = Field("", description="Upload time (ISO format)")

# Status and health models
class StatusResponse(BaseModel):
    """Service status response model"""
    success: bool = Field(..., description="Status check success")
    message: str = Field(..., description="Response message")
    status: Dict[str, Any] = Field({}, description="Service status information")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")

# Async task models
class AsyncInsertDataRequest(BaseModel):
    """Async data insertion request model"""
    text: Optional[str] = Field(None, description="Text content")
    image_url: Optional[str] = Field(None, description="Image URL")
    video_url: Optional[str] = Field(None, description="Video URL")

class AsyncBatchInsertRequest(BaseModel):
    """Async batch data insertion request model"""
    data_list: List[AsyncInsertDataRequest] = Field(..., description="Data list to insert")

class AsyncTaskResponse(BaseModel):
    """Async task response model"""
    success: bool = Field(..., description="Task creation success status")
    message: str = Field(..., description="Response message")
    task_id: str = Field(..., description="Task ID for tracking")
    estimated_time: Optional[int] = Field(None, description="Estimated processing time in seconds")

class TaskStatus(BaseModel):
    """Task status model"""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status: pending, processing, completed, failed")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field("", description="Status message")
    created_at: str = Field(..., description="Task creation time")
    started_at: Optional[str] = Field(None, description="Task start time")
    completed_at: Optional[str] = Field(None, description="Task completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")

class TaskStatusResponse(BaseModel):
    """Task status response model"""
    success: bool = Field(..., description="Status query success")
    message: str = Field(..., description="Response message")
    task_status: TaskStatus = Field(..., description="Task status information")

class TaskListResponse(BaseModel):
    """Task list response model"""
    success: bool = Field(..., description="Task list query success")
    message: str = Field(..., description="Response message")
    tasks: List[TaskStatus] = Field(..., description="List of tasks")
    total: int = Field(0, description="Total number of tasks")

# API Key management models
class ApiKeyInfo(BaseModel):
    """API Key information model"""
    key_id: str = Field(..., description="API Key ID")
    name: str = Field(..., description="API Key name")
    key: str = Field(..., description="API Key value")
    created_at: str = Field(..., description="Creation time")
    last_used_at: Optional[str] = Field(None, description="Last used time")
    expires_at: Optional[str] = Field(None, description="Expiration time")
    permissions: List[str] = Field([], description="API Key permissions")

class CreateApiKeyRequest(BaseModel):
    """Create API Key request model"""
    name: str = Field(..., description="API Key name")
    expires_in_days: Optional[int] = Field(None, description="Expiration in days (optional for permanent)")
    permissions: List[str] = Field([], description="API Key permissions")

class CreateApiKeyResponse(BaseModel):
    """Create API Key response model"""
    success: bool = Field(..., description="Creation success status")
    message: str = Field(..., description="Response message")
    api_key: ApiKeyInfo = Field(..., description="Created API Key information")

class ApiKeyListResponse(BaseModel):
    """API Key list response model"""
    success: bool = Field(..., description="Query success status")
    message: str = Field(..., description="Response message")
    api_keys: List[ApiKeyInfo] = Field(..., description="List of API Keys")
    total: int = Field(0, description="Total number of API Keys")

class DeleteApiKeyResponse(BaseModel):
    """Delete API Key response model"""
    success: bool = Field(..., description="Deletion success status")
    message: str = Field(..., description="Response message") 