"""
Custom exception classes for better error handling and status code mapping
"""

from typing import Optional

class MoleSearchException(Exception):
    """Base exception class"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class ValidationException(MoleSearchException):
    """Validation exception - corresponds to 422 status code"""
    pass

class MediaProcessingException(MoleSearchException):
    """Media processing exception - corresponds to 422 status code"""
    pass

class ServiceException(MoleSearchException):
    """Service exception - corresponds to 500 status code"""
    pass

class NotFoundException(MoleSearchException):
    """Resource not found exception - corresponds to 404 status code"""
    pass

class InvalidMediaFormatException(MediaProcessingException):
    """Invalid media format exception"""
    def __init__(self, media_type: str, url: str, details: Optional[str] = None):
        message = f"Invalid {media_type} format or inaccessible URL: {url}"
        super().__init__(message, details)

class MediaDownloadException(MediaProcessingException):
    """Media download exception"""
    def __init__(self, media_type: str, url: str, details: Optional[str] = None):
        message = f"Failed to download {media_type} file: {url}"
        super().__init__(message, details)

class ConfigurationException(ServiceException):
    """Configuration exception"""
    pass

class DatabaseException(ServiceException):
    """Database exception"""
    pass 