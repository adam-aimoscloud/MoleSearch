"""
自定义异常类定义
用于更好的错误处理和状态码映射
"""

from typing import Optional

class MMRetrieverException(Exception):
    """基础异常类"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class ValidationException(MMRetrieverException):
    """验证异常 - 对应422状态码"""
    pass

class MediaProcessingException(MMRetrieverException):
    """媒体处理异常 - 对应422状态码"""
    pass

class ServiceException(MMRetrieverException):
    """服务异常 - 对应500状态码"""
    pass

class NotFoundException(MMRetrieverException):
    """资源未找到异常 - 对应404状态码"""
    pass

class InvalidMediaFormatException(MediaProcessingException):
    """无效媒体格式异常"""
    def __init__(self, media_type: str, url: str, details: Optional[str] = None):
        message = f"无效的{media_type}格式或无法访问的URL: {url}"
        super().__init__(message, details)

class MediaDownloadException(MediaProcessingException):
    """媒体下载异常"""
    def __init__(self, media_type: str, url: str, details: Optional[str] = None):
        message = f"无法下载{media_type}文件: {url}"
        super().__init__(message, details)

class ConfigurationException(ServiceException):
    """配置异常"""
    pass

class DatabaseException(ServiceException):
    """数据库异常"""
    pass 