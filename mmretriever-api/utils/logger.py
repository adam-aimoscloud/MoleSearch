import logging
import sys
from typing import Optional

# 全局日志配置
_logger_initialized = False

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，如果为None则使用调用模块的名称
    
    Returns:
        配置好的日志记录器
    """
    global _logger_initialized
    
    if not _logger_initialized:
        # 配置根日志记录器
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

# 为向后兼容保留原有的logger变量
logger = get_logger(__name__)