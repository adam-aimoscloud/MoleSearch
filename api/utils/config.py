"""
Config manager
Responsible for reading and parsing the config.yaml file
"""

import os
import yaml
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    dev_mode: bool = False
    access_log: bool = True
    cors_origins: List[str] = None
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class SearchEngineConfig:
    """Search engine configuration"""
    type: str = "elasticsearch"
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class MMExtractorConfig:
    """MMExtractor configuration"""
    name: str = "MMExtractor"
    type: str = "extraction"
    enable: bool = True
    plugins: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.plugins is None:
            self.plugins = {}


class ConfigManager:
    """Config manager"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Parse YAML
            self._config = yaml.safe_load(config_content)
            
            # Validate configuration
            self._validate_config()
            
            logger.info(f"Configuration file loaded successfully: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Configuration file loading failed: {e}")
            raise
    

    
    def _validate_config(self):
        """Validate configuration file"""
        if not self._config:
            raise ValueError("Configuration file is empty")
        
        # Basic configuration validation
        required_sections = ['server', 'mmextractor', 'search_engine']
        missing_sections = []
        
        for section in required_sections:
            if section not in self._config:
                missing_sections.append(section)
        
        if missing_sections:
            raise ValueError(f"Missing required configuration sections: {missing_sections}")
        
        # Validate API keys in plugin configuration
        self._validate_api_keys()
        
        logger.info("Configuration validation passed")
    
    def _validate_api_keys(self):
        """Validate API key configuration"""
        plugins = self._config.get('mmextractor', {}).get('plugins', {})
        
        for plugin_name, plugin_config in plugins.items():
            param = plugin_config.get('param', {})
            api_key = param.get('api_key', '')
            
            # Check if it's still a placeholder
            if isinstance(api_key, str) and (api_key.startswith('your_') and api_key.endswith('_here')):
                logger.warning(f"API key for plugin {plugin_name} is still a placeholder, please configure a real API key")
            elif isinstance(api_key, str) and len(api_key) < 10:
                logger.warning(f"API key for plugin {plugin_name} is too short, please check the configuration")
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration"""
        server_config = self._config.get('server', {})
        return ServerConfig(
            host=server_config.get('host', '0.0.0.0'),
            port=server_config.get('port', 8000),
            log_level=server_config.get('log_level', 'INFO'),
            dev_mode=server_config.get('dev_mode', False),
            access_log=server_config.get('access_log', True),
            cors_origins=server_config.get('cors_origins', ['*']),
            docs_url=server_config.get('docs_url', '/docs'),
            redoc_url=server_config.get('redoc_url', '/redoc')
        )
    
    def get_mmextractor_config(self) -> MMExtractorConfig:
        """Get MMExtractor configuration"""
        mmextractor_config = self._config.get('mmextractor', {})
        return MMExtractorConfig(
            name=mmextractor_config.get('name', 'MMExtractor'),
            type=mmextractor_config.get('type', 'extraction'),
            enable=mmextractor_config.get('enable', True),
            plugins=mmextractor_config.get('plugins', {})
        )
    
    def get_search_engine_config(self) -> SearchEngineConfig:
        """Get search engine configuration"""
        search_engine_config = self._config.get('search_engine', {})
        return SearchEngineConfig(
            type=search_engine_config.get('type', 'elasticsearch'),
            config=search_engine_config.get('config', {})
        )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration item"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_elasticsearch_config(self) -> Dict[str, Any]:
        """Get Elasticsearch configuration"""
        return self.get_config('search_engine.config', {})
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.get_config(f'mmextractor.plugins.{plugin_name}', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.get_config('performance', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get_config('logging', {})
    
    def get_data_processing_config(self) -> Dict[str, Any]:
        """Get data processing configuration"""
        return self.get_config('data_processing', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration"""
        return self.get_config('storage', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get_config('security', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.get_config('monitoring', {})
    
    def get_file_handler_config(self) -> Dict[str, Any]:
        """Get file handler configuration"""
        return self.get_config('file_handler', {})
    
    def reload_config(self):
        """Reload configuration"""
        self._load_config()
        logger.info("Configuration reloaded")
    



# Global config manager instance
config_manager = None


def get_config_manager(config_path: str = "config.yaml") -> ConfigManager:
    """Get config manager instance"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager(config_path)
    return config_manager


def init_config(config_path: str = "config.yaml"):
    """Initialize configuration"""
    global config_manager
    config_manager = ConfigManager(config_path)
    return config_manager 