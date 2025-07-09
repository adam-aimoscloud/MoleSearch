"""
API data model definition
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union, Any
from enum import Enum


class SearchType(str, Enum):
    """Search type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class TextSearchRequest(BaseModel):
    """Text search request"""
    query: str = Field(..., description="Search query text", min_length=1, max_length=1000)
    top_k: int = Field(10, description="Return result count", ge=1, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Artificial intelligence technology development",
                "top_k": 10
            }
        }


class ImageSearchRequest(BaseModel):
    """Image search request"""
    image_url: str = Field(..., description="Image URL address")
    top_k: int = Field(10, description="Return result count", ge=1, le=100)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "top_k": 10
            }
        }


class VideoSearchRequest(BaseModel):
    """Video search request"""
    video_url: str = Field(..., description="Video URL address")
    top_k: int = Field(10, description="Return result count", ge=1, le=100)
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "video_url": "https://example.com/video.mp4",
                "top_k": 10
            }
        }


class MultimodalSearchRequest(BaseModel):
    """Multimodal search request"""
    text: Optional[str] = Field(None, description="Text query")
    image_url: Optional[str] = Field(None, description="Image URL")
    video_url: Optional[str] = Field(None, description="Video URL")
    top_k: int = Field(10, description="Return result count", ge=1, le=100)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return v
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v
    
    @validator('video_url')
    def validate_at_least_one_input(cls, v, values):
        # Validate on the last field, so we can access all fields
        text = values.get('text')
        image_url = values.get('image_url')
        video_url = v
        
        if not any([text, image_url, video_url]):
            raise ValueError('At least one type of input is required (text, image, or video)')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Artificial intelligence",
                "image_url": "https://example.com/image.jpg",
                "video_url": "https://example.com/video.mp4",
                "top_k": 10
            }
        }


class SearchResultItem(BaseModel):
    """Search result item"""
    id: str = Field(..., description="Document ID")
    text: str = Field("", description="Text content")
    image_url: str = Field("", description="Image URL")
    video_url: str = Field("", description="Video URL")
    image_text: str = Field("", description="Image text description")
    video_text: str = Field("", description="Video text description")
    score: float = Field(..., description="Similarity score")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_123",
                "text": "This is a description of artificial intelligence",
                "image_url": "https://example.com/ai_image.jpg",
                "video_url": "https://example.com/ai_video.mp4",
                "image_text": "The image shows the application scenarios of artificial intelligence technology",
                "video_text": "The video content describes the development history of AI technology",
                "score": 0.95
            }
        }


class SearchResponse(BaseModel):
    """Search response"""
    success: bool = Field(True, description="Request success")
    message: str = Field("", description="Response message")
    total: int = Field(0, description="Total result count")
    results: List[SearchResultItem] = Field([], description="Search result list")
    query_time: float = Field(0.0, description="Query time (seconds)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Search completed",
                "total": 5,
                "results": [
                    {
                        "id": "doc_123",
                        "text": "Artificial intelligence technology development rapidly",
                        "image_url": "https://example.com/ai.jpg",
                        "video_url": "https://example.com/ai.mp4",
                        "score": 0.95
                    }
                ],
                "query_time": 0.123
            }
        }


class InsertDataRequest(BaseModel):
    """Data insertion request"""
    text: str = Field("", description="Text content")
    image_url: str = Field("", description="Image URL")
    video_url: str = Field("", description="Video URL")
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return v
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v
    
    @validator('video_url')
    def validate_at_least_one_content(cls, v, values):
        # Validate on the last field, so we can access all fields
        text = values.get('text', '')
        image_url = values.get('image_url', '')
        video_url = v
        
        if not any([text, image_url, video_url]):
            raise ValueError('At least one type of content is required (text, image, or video)')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This is a description of artificial intelligence",
                "image_url": "https://example.com/ai_image.jpg",
                "video_url": "https://example.com/ai_video.mp4"
            }
        }


class BatchInsertRequest(BaseModel):
    """Batch insertion request"""
    data_list: List[InsertDataRequest] = Field(..., description="Data list to insert", min_items=1, max_items=100)
    
    class Config:
        schema_extra = {
            "example": {
                "data_list": [
                    {
                        "text": "Artificial intelligence technology",
                        "image_url": "https://example.com/ai1.jpg",
                        "video_url": "https://example.com/ai1.mp4"
                    },
                    {
                        "text": "Machine learning algorithm",
                        "image_url": "https://example.com/ml.jpg",
                        "video_url": "https://example.com/ml.mp4"
                    }
                ]
            }
        }


class InsertResponse(BaseModel):
    """Insert response"""
    success: bool = Field(True, description="Request success")
    message: str = Field("", description="Response message")
    inserted_count: int = Field(0, description="Successfully inserted data count")
    processing_time: float = Field(0.0, description="Processing time (seconds)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Data insertion successful",
                "inserted_count": 1,
                "processing_time": 2.5
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = Field(False, description="Request success")
    error_code: str = Field("", description="Error code")
    message: str = Field("", description="Error message")
    details: Optional[Any] = Field(None, description="Error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_INPUT",
                "message": "Invalid input parameters",
                "details": "Text content cannot be empty"
            }
        }


class FileUploadResponse(BaseModel):
    """File upload response"""
    success: bool = Field(..., description="Upload success")
    message: str = Field(..., description="Response message")
    file_url: Optional[str] = Field(None, description="File access URL")
    oss_path: Optional[str] = Field(None, description="OSS storage path")
    file_size: Optional[int] = Field(None, description="File size (bytes)")
    file_extension: Optional[str] = Field(None, description="File extension")
    upload_time: Optional[str] = Field(None, description="Upload time")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "File upload successful",
                "file_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/mmretriever/20250107/1704589200_12345678-1234-5678-9abc-123456789abc.jpg",
                "oss_path": "mmretriever/20250107/1704589200_12345678-1234-5678-9abc-123456789abc.jpg",
                "file_size": 1024000,
                "file_extension": ".jpg",
                "upload_time": "2025-01-07T10:30:00"
            }
        }


class FileInfo(BaseModel):
    """File information"""
    oss_path: str = Field(..., description="OSS storage path")
    file_size: int = Field(..., description="File size (bytes)")
    content_type: str = Field(..., description="File MIME type")
    last_modified: Optional[str] = Field(None, description="Last modified time")
    etag: str = Field(..., description="File ETag")
    
    class Config:
        schema_extra = {
            "example": {
                "oss_path": "mmretriever/20250107/1704589200_12345678-1234-5678-9abc-123456789abc.jpg",
                "file_size": 1024000,
                "content_type": "image/jpeg",
                "last_modified": "2025-01-07T10:30:00",
                "etag": "\"abc123def456\""
            }
        }


class FileDeleteResponse(BaseModel):
    """File delete response"""
    success: bool = Field(..., description="Delete success")
    message: str = Field(..., description="Response message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "File delete successful"
            }
        }


class DataListRequest(BaseModel):
    """Full data paging request"""
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(20, description="Number of items per page", ge=1, le=100)


class DataListItem(BaseModel):
    id: str = Field(..., description="Document ID")
    text: Optional[str] = Field('', description="Text content")
    image_url: Optional[str] = Field('', description="Image URL")
    video_url: Optional[str] = Field('', description="Video URL")
    image_text: Optional[str] = Field('', description="Image text description")
    video_text: Optional[str] = Field('', description="Video text description")


class DataListResponse(BaseModel):
    success: bool = Field(True, description="Request success")
    message: str = Field("", description="Response message")
    total: int = Field(0, description="Total data count")
    items: List[DataListItem] = Field([], description="Data list")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page") 