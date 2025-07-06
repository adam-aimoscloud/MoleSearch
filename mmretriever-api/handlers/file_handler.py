"""
文件上传处理器
只保留文件上传接口
"""

import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException

from .models import FileUploadResponse
from .exceptions import MMRetrieverException, ValidationException
from utils.oss_uploader import get_oss_uploader
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["文件管理"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    file_type: Optional[str] = None
):
    """
    上传文件到OSS
    
    - **file**: 要上传的文件
    - **file_type**: 文件类型标识（可选，用于路径分类）
    
    返回上传结果，包括文件URL和存储路径
    """
    try:
        logger.info(f"开始处理文件上传: {file.filename}")
        
        # 验证文件
        if not file.filename:
            raise ValidationException("文件名不能为空")
        
        # 检查文件大小（默认限制100MB）
        max_file_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        if len(file_content) > max_file_size:
            raise ValidationException(f"文件大小超过限制: {len(file_content)} > {max_file_size}")
        
        # 获取OSS上传器
        uploader = get_oss_uploader()
        
        # 确定文件类型
        if not file_type:
            # 根据文件扩展名自动分类
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                file_type = "image"
            elif file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                file_type = "video"
            elif file_extension in ['.mp3', '.wav', '.flac', '.aac']:
                file_type = "audio"
            elif file_extension in ['.txt', '.pdf', '.doc', '.docx']:
                file_type = "document"
            else:
                file_type = "file"
        
        # 上传文件到OSS
        upload_result = uploader.upload_file_content(
            file_content=file_content,
            file_name=file.filename,
            file_type=file_type
        )
        
        if not upload_result['success']:
            raise MMRetrieverException(f"文件上传失败: {upload_result.get('error', '未知错误')}")
        
        logger.info(f"文件上传成功: {upload_result['file_url']}")
        
        return FileUploadResponse(
            success=True,
            message="文件上传成功",
            file_url=upload_result['file_url'],
            oss_path=upload_result['oss_path'],
            file_size=upload_result['file_size'],
            file_extension=upload_result['file_extension'],
            upload_time=upload_result['upload_time']
        )
        
    except ValidationException as e:
        logger.warning(f"文件上传验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except MMRetrieverException as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"文件上传异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传服务异常: {str(e)}") 