"""
OSS文件上传工具
支持文件上传到阿里云OSS，使用指定的路径格式
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
    """OSS文件上传器"""
    
    def __init__(self):
        """初始化OSS上传器"""
        config_manager = get_config_manager()
        credentials = config_manager.get_config('credentials.oss', {})
        
        self.access_key_id = credentials.get('access_key_id', '')
        self.access_key_secret = credentials.get('access_key_secret', '')
        self.endpoint = credentials.get('endpoint', '')
        self.bucket_name = credentials.get('bucket_name', '')
        
        if not all([self.access_key_id, self.access_key_secret, self.endpoint, self.bucket_name]):
            raise ValueError("OSS配置不完整，请检查credentials.oss配置")
        
        # 初始化OSS客户端
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        
        logger.info(f"OSS上传器初始化完成，Bucket: {self.bucket_name}")
    
    def upload_file(self, file_path: str, file_type: str = "file") -> Dict[str, Any]:
        """
        上传文件到OSS
        
        Args:
            file_path: 本地文件路径
            file_type: 文件类型标识（用于路径分类）
            
        Returns:
            Dict包含上传结果信息
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1]
            
            # 生成OSS路径
            oss_path = self._generate_oss_path(file_type, file_extension)
            
            logger.info(f"开始上传文件: {file_path} -> {oss_path}")
            
            # 上传文件到OSS
            result = self.bucket.put_object_from_file(oss_path, file_path)
            
            if result.status != 200:
                raise Exception(f"OSS上传失败，状态码: {result.status}")
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{oss_path}"
            
            upload_info = {
                'success': True,
                'file_url': file_url,
                'oss_path': oss_path,
                'file_size': file_size,
                'file_extension': file_extension,
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"文件上传成功: {file_url}")
            return upload_info
            
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def upload_file_content(self, file_content: bytes, file_name: str, file_type: str = "file") -> Dict[str, Any]:
        """
        上传文件内容到OSS
        
        Args:
            file_content: 文件内容字节
            file_name: 文件名
            file_type: 文件类型标识
            
        Returns:
            Dict包含上传结果信息
        """
        try:
            # 获取文件扩展名
            file_extension = os.path.splitext(file_name)[1]
            
            # 生成OSS路径
            oss_path = self._generate_oss_path(file_type, file_extension)
            
            logger.info(f"开始上传文件内容: {file_name} -> {oss_path}")
            
            # 上传文件内容到OSS
            result = self.bucket.put_object(oss_path, file_content)
            
            if result.status != 200:
                raise Exception(f"OSS上传失败，状态码: {result.status}")
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{oss_path}"
            
            upload_info = {
                'success': True,
                'file_url': file_url,
                'oss_path': oss_path,
                'file_size': len(file_content),
                'file_extension': file_extension,
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"文件内容上传成功: {file_url}")
            return upload_info
            
        except Exception as e:
            logger.error(f"文件内容上传失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_name': file_name
            }
    
    def _generate_oss_path(self, file_type: str, file_extension: str) -> str:
        """
        生成OSS存储路径
        
        Args:
            file_type: 文件类型标识
            file_extension: 文件扩展名
            
        Returns:
            OSS存储路径
        """
        # 获取当前日期
        today = datetime.now().strftime("%Y%m%d")
        
        # 生成时间戳和UUID
        timestamp = str(int(datetime.now().timestamp()))
        unique_id = str(uuid.uuid4())
        
        # 构建路径: /mmretriever/当天时间/timestamp+uuid
        oss_path = f"mmretriever/{today}/{timestamp}_{unique_id}{file_extension}"
        
        return oss_path
    
    def delete_file(self, oss_path: str) -> bool:
        """
        删除OSS文件
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            是否删除成功
        """
        try:
            self.bucket.delete_object(oss_path)
            logger.info(f"文件删除成功: {oss_path}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {oss_path}, 错误: {str(e)}")
            return False
    
    def get_file_info(self, oss_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            文件信息字典
        """
        try:
            # 获取文件元信息
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
            logger.warning(f"文件不存在: {oss_path}")
            return None
        except Exception as e:
            logger.error(f"获取文件信息失败: {oss_path}, 错误: {str(e)}")
            return None


def get_oss_uploader() -> OSSUploader:
    """获取OSS上传器实例"""
    return OSSUploader() 