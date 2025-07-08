"""
Search engine module initialization
"""

from .base import BaseSearchEngine, SearchEngineFactory, SearchEngineParam
from .elasticsearch.es import ESSearchEngine

# Automatically register all search engines
__all__ = ['BaseSearchEngine', 'SearchEngineFactory', 'SearchEngineParam', 'ESSearchEngine']
