"""
配置管理器
负责读取和解析 config.yaml 配置文件
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
    """服务器配置"""
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
    """搜索引擎配置"""
    type: str = "elasticsearch"
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class MMExtractorConfig:
    """MMExtractor配置"""
    name: str = "MMExtractor"
    type: str = "extraction"
    enable: bool = True
    plugins: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.plugins is None:
            self.plugins = {}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # 解析YAML
            self._config = yaml.safe_load(config_content)
            
            # 验证配置
            self._validate_config()
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    

    
    def _validate_config(self):
        """验证配置文件"""
        if not self._config:
            raise ValueError("配置文件为空")
        
        # 基本配置验证
        required_sections = ['server', 'mmextractor', 'search_engine']
        missing_sections = []
        
        for section in required_sections:
            if section not in self._config:
                missing_sections.append(section)
        
        if missing_sections:
            raise ValueError(f"缺少必需的配置部分: {missing_sections}")
        
        # 验证插件配置中的API密钥
        self._validate_api_keys()
        
        logger.info("配置验证通过")
    
    def _validate_api_keys(self):
        """验证API密钥配置"""
        plugins = self._config.get('mmextractor', {}).get('plugins', {})
        
        for plugin_name, plugin_config in plugins.items():
            param = plugin_config.get('param', {})
            api_key = param.get('api_key', '')
            
            # 检查是否还是占位符
            if isinstance(api_key, str) and (api_key.startswith('your_') and api_key.endswith('_here')):
                logger.warning(f"插件 {plugin_name} 的API密钥仍为占位符，请配置真实的API密钥")
            elif isinstance(api_key, str) and len(api_key) < 10:
                logger.warning(f"插件 {plugin_name} 的API密钥长度过短，请检查配置")
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置"""
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
        """获取MMExtractor配置"""
        mmextractor_config = self._config.get('mmextractor', {})
        return MMExtractorConfig(
            name=mmextractor_config.get('name', 'MMExtractor'),
            type=mmextractor_config.get('type', 'extraction'),
            enable=mmextractor_config.get('enable', True),
            plugins=mmextractor_config.get('plugins', {})
        )
    
    def get_search_engine_config(self) -> SearchEngineConfig:
        """获取搜索引擎配置"""
        search_engine_config = self._config.get('search_engine', {})
        return SearchEngineConfig(
            type=search_engine_config.get('type', 'elasticsearch'),
            config=search_engine_config.get('config', {})
        )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_elasticsearch_config(self) -> Dict[str, Any]:
        """获取Elasticsearch配置"""
        return self.get_config('search_engine.config', {})
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件配置"""
        return self.get_config(f'mmextractor.plugins.{plugin_name}', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.get_config('performance', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get_config('logging', {})
    
    def get_data_processing_config(self) -> Dict[str, Any]:
        """获取数据处理配置"""
        return self.get_config('data_processing', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return self.get_config('storage', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.get_config('security', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return self.get_config('monitoring', {})
    
    def reload_config(self):
        """重新加载配置"""
        self._load_config()
        logger.info("配置已重新加载")
    



# 全局配置管理器实例
config_manager = None


def get_config_manager(config_path: str = "config.yaml") -> ConfigManager:
    """获取配置管理器实例"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager(config_path)
    return config_manager


def init_config(config_path: str = "config.yaml"):
    """初始化配置"""
    global config_manager
    config_manager = ConfigManager(config_path)
    return config_manager 