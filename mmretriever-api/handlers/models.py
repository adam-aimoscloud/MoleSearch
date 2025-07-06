"""
API数据模型定义
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union, Any
from enum import Enum


class SearchType(str, Enum):
    """搜索类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class TextSearchRequest(BaseModel):
    """文本搜索请求"""
    query: str = Field(..., description="搜索查询文本", min_length=1, max_length=1000)
    top_k: int = Field(10, description="返回结果数量", ge=1, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "人工智能技术发展",
                "top_k": 10
            }
        }


class ImageSearchRequest(BaseModel):
    """图像搜索请求"""
    image_url: str = Field(..., description="图像URL地址")
    top_k: int = Field(10, description="返回结果数量", ge=1, le=100)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('图像URL必须以http://或https://开头')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "top_k": 10
            }
        }


class VideoSearchRequest(BaseModel):
    """视频搜索请求"""
    video_url: str = Field(..., description="视频URL地址")
    top_k: int = Field(10, description="返回结果数量", ge=1, le=100)
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('视频URL必须以http://或https://开头')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "video_url": "https://example.com/video.mp4",
                "top_k": 10
            }
        }


class MultimodalSearchRequest(BaseModel):
    """多模态搜索请求"""
    text: Optional[str] = Field(None, description="文本查询")
    image_url: Optional[str] = Field(None, description="图像URL")
    video_url: Optional[str] = Field(None, description="视频URL")
    top_k: int = Field(10, description="返回结果数量", ge=1, le=100)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('图像URL必须以http://或https://开头')
        return v
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('视频URL必须以http://或https://开头')
        return v
    
    @validator('video_url')
    def validate_at_least_one_input(cls, v, values):
        # 在最后一个字段上验证，这样可以访问到所有字段
        text = values.get('text')
        image_url = values.get('image_url')
        video_url = v
        
        if not any([text, image_url, video_url]):
            raise ValueError('至少需要提供一种类型的输入（文本、图像或视频）')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "人工智能",
                "image_url": "https://example.com/image.jpg",
                "video_url": "https://example.com/video.mp4",
                "top_k": 10
            }
        }


class SearchResultItem(BaseModel):
    """搜索结果项"""
    id: str = Field(..., description="文档ID")
    text: str = Field("", description="文本内容")
    image_url: str = Field("", description="图像URL")
    video_url: str = Field("", description="视频URL")
    score: float = Field(..., description="相似度分数")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_123",
                "text": "这是一段关于人工智能的描述",
                "image_url": "https://example.com/ai_image.jpg",
                "video_url": "https://example.com/ai_video.mp4",
                "score": 0.95
            }
        }


class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool = Field(True, description="请求是否成功")
    message: str = Field("", description="响应消息")
    total: int = Field(0, description="总结果数量")
    results: List[SearchResultItem] = Field([], description="搜索结果列表")
    query_time: float = Field(0.0, description="查询耗时（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "搜索完成",
                "total": 5,
                "results": [
                    {
                        "id": "doc_123",
                        "text": "人工智能技术发展迅速",
                        "image_url": "https://example.com/ai.jpg",
                        "video_url": "https://example.com/ai.mp4",
                        "score": 0.95
                    }
                ],
                "query_time": 0.123
            }
        }


class InsertDataRequest(BaseModel):
    """数据插入请求"""
    text: str = Field("", description="文本内容")
    image_url: str = Field("", description="图像URL")
    video_url: str = Field("", description="视频URL")
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('图像URL必须以http://或https://开头')
        return v
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('视频URL必须以http://或https://开头')
        return v
    
    @validator('video_url')
    def validate_at_least_one_content(cls, v, values):
        # 在最后一个字段上验证，这样可以访问到所有字段
        text = values.get('text', '')
        image_url = values.get('image_url', '')
        video_url = v
        
        if not any([text, image_url, video_url]):
            raise ValueError('至少需要提供一种类型的内容（文本、图像或视频）')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "这是一段关于人工智能的描述",
                "image_url": "https://example.com/ai_image.jpg",
                "video_url": "https://example.com/ai_video.mp4"
            }
        }


class BatchInsertRequest(BaseModel):
    """批量插入请求"""
    data_list: List[InsertDataRequest] = Field(..., description="要插入的数据列表", min_items=1, max_items=100)
    
    class Config:
        schema_extra = {
            "example": {
                "data_list": [
                    {
                        "text": "人工智能技术",
                        "image_url": "https://example.com/ai1.jpg",
                        "video_url": "https://example.com/ai1.mp4"
                    },
                    {
                        "text": "机器学习算法",
                        "image_url": "https://example.com/ml.jpg",
                        "video_url": "https://example.com/ml.mp4"
                    }
                ]
            }
        }


class InsertResponse(BaseModel):
    """插入响应"""
    success: bool = Field(True, description="请求是否成功")
    message: str = Field("", description="响应消息")
    inserted_count: int = Field(0, description="成功插入的数据数量")
    processing_time: float = Field(0.0, description="处理耗时（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "数据插入成功",
                "inserted_count": 1,
                "processing_time": 2.5
            }
        }


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="请求是否成功")
    error_code: str = Field("", description="错误代码")
    message: str = Field("", description="错误消息")
    details: Optional[Any] = Field(None, description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_INPUT",
                "message": "输入参数无效",
                "details": "文本内容不能为空"
            }
        } 