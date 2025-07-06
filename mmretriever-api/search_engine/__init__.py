"""
搜索引擎模块初始化
"""

from .base import BaseSearchEngine, SearchEngineFactory, SearchEngineParam
from .elasticsearch.es import ESSearchEngine

# 自动注册所有搜索引擎
__all__ = ['BaseSearchEngine', 'SearchEngineFactory', 'SearchEngineParam', 'ESSearchEngine']
