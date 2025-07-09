import logging
import sys
from typing import Optional

# Global logger configuration
_logger_initialized = False

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger
    
    Args:
        name: Logger name, if None, use the name of the calling module
    
    Returns:
        Configured logger
    """
    global _logger_initialized
    
    if not _logger_initialized:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
            ]
        )
        _logger_initialized = True
    
    if name is None:
        name = __name__
    
    return logging.getLogger(name)

# For backward compatibility, keep the original logger variable
logger = get_logger(__name__)