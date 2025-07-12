"""
OSS file upload tool
Supports file upload to Aliyun OSS, using specified path format
"""

import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
import oss2
from .logger import get_logger
from .config import get_config_manager

logger = get_logger(__name__)


class OSSUploader:
    """OSS file uploader"""
    
    def __init__(self):
        """Initialize OSS uploader"""
        config_manager = get_config_manager()
        credentials = config_manager.get_config('file_handler.credentials.oss', {})
        
        self.access_key_id = credentials.get('access_key_id', '')
        self.access_key_secret = credentials.get('access_key_secret', '')
        self.endpoint = credentials.get('endpoint', '')
        self.bucket_name = credentials.get('bucket_name', '')
        
        if not all([self.access_key_id, self.access_key_secret, self.endpoint, self.bucket_name]):
            raise ValueError("OSS configuration is incomplete, please check file_handler.credentials.oss configuration")
        
        # Initialize OSS client
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        
        logger.info(f"OSS uploader initialized, Bucket: {self.bucket_name}")
    
    def upload_file(self, file_path: str, file_type: str = "file") -> Dict[str, Any]:
        """
        Upload file to OSS
        
        Args:
            file_path: Local file path
            file_type: File type identifier (for path classification)
            
        Returns:
            Dict containing upload result information
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file information
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1]
            
            # Generate OSS path
            oss_path = self._generate_oss_path(file_type, file_extension)
            
            logger.info(f"Uploading file: {file_path} -> {oss_path}")
            
            # Upload file to OSS
            result = self.bucket.put_object_from_file(oss_path, file_path)
            
            if result.status != 200:
                raise Exception(f"OSS upload failed, status code: {result.status}")
            
            # Build access URL
            file_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{oss_path}"
            
            upload_info = {
                'success': True,
                'file_url': file_url,
                'oss_path': oss_path,
                'file_size': file_size,
                'file_extension': file_extension,
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"File uploaded successfully: {file_url}")
            return upload_info
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def upload_file_content(self, file_content: bytes, file_name: str, file_type: str = "file") -> Dict[str, Any]:
        """
        Upload file content to OSS
        
        Args:
            file_content: File content bytes
            file_name: File name
            file_type: File type identifier
            
        Returns:
            Dict containing upload result information
        """
        try:
            # Get file extension
            file_extension = os.path.splitext(file_name)[1]
            
            # Generate OSS path
            oss_path = self._generate_oss_path(file_type, file_extension)
            
            logger.info(f"Uploading file content: {file_name} -> {oss_path}")
            
            # Upload file content to OSS
            result = self.bucket.put_object(oss_path, file_content)
            
            if result.status != 200:
                raise Exception(f"OSS upload failed, status code: {result.status}")
            
            # Build access URL
            file_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{oss_path}"
            
            upload_info = {
                'success': True,
                'file_url': file_url,
                'oss_path': oss_path,
                'file_size': len(file_content),
                'file_extension': file_extension,
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"File content uploaded successfully: {file_url}")
            return upload_info
            
        except Exception as e:
            logger.error(f"File content upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_name': file_name
            }
    
    def _generate_oss_path(self, file_type: str, file_extension: str) -> str:
        """
        Generate OSS storage path
        
        Args:
            file_type: File type identifier
            file_extension: File extension
            
        Returns:
            OSS storage path
        """
        # Get current date
        today = datetime.now().strftime("%Y%m%d")
        
        # Generate timestamp and UUID
        timestamp = str(int(datetime.now().timestamp()))
        unique_id = str(uuid.uuid4())
        
        # Build path: /mmretriever/current date/timestamp+uuid
        oss_path = f"mmretriever/{today}/{timestamp}_{unique_id}{file_extension}"
        
        return oss_path
    
    def delete_file(self, oss_path: str) -> bool:
        """
        Delete OSS file
        
        Args:
            oss_path: OSS file path
            
        Returns:
            Whether the deletion is successful
        """
        try:
            self.bucket.delete_object(oss_path)
            logger.info(f"File deleted successfully: {oss_path}")
            return True
        except Exception as e:
            logger.error(f"File deletion failed: {oss_path}, error: {str(e)}")
            return False
    
    def get_file_info(self, oss_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            oss_path: OSS file path
            
        Returns:
            File information dictionary
        """
        try:
            # Get file metadata
            head_result = self.bucket.head_object(oss_path)
            
            file_info = {
                'oss_path': oss_path,
                'file_size': head_result.content_length,
                'content_type': head_result.content_type,
                'last_modified': str(head_result.last_modified),
                'etag': head_result.etag
            }
            
            return file_info
            
        except oss2.exceptions.NoSuchKey:
            logger.warning(f"File not found: {oss_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to get file information: {oss_path}, error: {str(e)}")
            return None


def get_oss_uploader() -> OSSUploader:
    """Get OSS uploader instance"""
    return OSSUploader() 