"""
File upload handler
Only keep the file upload interface
"""

import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from .models import FileUploadResponse
from .auth import get_current_token
from .exceptions import MoleSearchException, ValidationException
from utils.oss_uploader import get_oss_uploader
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["File Management"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="The file to upload"),
    file_type: Optional[str] = None,
    token: Optional[str] = Depends(get_current_token)
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
        
        # Try OSS upload first, fallback to local storage
        upload_result = None
        try:
            uploader = get_oss_uploader()
            upload_result = uploader.upload_file_content(
                file_content=file_content,
                file_name=file.filename,
                file_type=file_type
            )
        except Exception as e:
            logger.warning(f"OSS upload failed, using local storage: {str(e)}")
            # Fallback to local storage
            upload_result = _save_file_locally(file_content, file.filename, file_type)
        
        if not upload_result['success']:
            raise MoleSearchException(f"File upload failed: {upload_result.get('error', 'Unknown error')}")
        
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
    except MoleSearchException as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"File upload exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload service exception: {str(e)}")

def _save_file_locally(file_content: bytes, file_name: str, file_type: str) -> dict:
    """Save file locally as fallback when OSS is not available"""
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Generate unique filename
        timestamp = str(int(datetime.now().timestamp()))
        unique_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file_name)[1]
        local_filename = f"{timestamp}_{unique_id}{file_extension}"
        
        # Save file
        file_path = os.path.join(uploads_dir, local_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Generate file URL (relative path for local development)
        file_url = f"/uploads/{local_filename}"
        
        return {
            'success': True,
            'file_url': file_url,
            'oss_path': file_path,
            'file_size': len(file_content),
            'file_extension': file_extension,
            'upload_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Local file save failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'file_name': file_name
        } 