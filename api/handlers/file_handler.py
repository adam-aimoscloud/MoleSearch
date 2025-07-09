"""
File upload handler
Only keep the file upload interface
"""

import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException

from .models import FileUploadResponse
from .exceptions import MoleRetrieverException, ValidationException
from utils.oss_uploader import get_oss_uploader
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["File Management"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="The file to upload"),
    file_type: Optional[str] = None
):
    """
    Upload file to OSS
    
    - **file**: The file to upload
    - **file_type**: File type identifier (optional, for path classification)
    
    Returns upload result, including file URL and storage path
    """
    try:
        logger.info(f"Starting file upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise ValidationException("File name cannot be empty")
        
        # Check file size (default limit 100MB)
        max_file_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        if len(file_content) > max_file_size:
            raise ValidationException(f"File size exceeds limit: {len(file_content)} > {max_file_size}")
        
        # Get OSS uploader
        uploader = get_oss_uploader()
        
        # Determine file type
        if not file_type:
            # Automatically classify by file extension
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
        
        # Upload file to OSS
        upload_result = uploader.upload_file_content(
            file_content=file_content,
            file_name=file.filename,
            file_type=file_type
        )
        
        if not upload_result['success']:
            raise MoleRetrieverException(f"File upload failed: {upload_result.get('error', 'Unknown error')}")
        
        logger.info(f"File upload successful: {upload_result['file_url']}")
        
        return FileUploadResponse(
            success=True,
            message="File upload successful",
            file_url=upload_result['file_url'],
            oss_path=upload_result['oss_path'],
            file_size=upload_result['file_size'],
            file_extension=upload_result['file_extension'],
            upload_time=upload_result['upload_time']
        )
        
    except ValidationException as e:
        logger.warning(f"File upload validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except MoleRetrieverException as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"File upload exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload service exception: {str(e)}") 