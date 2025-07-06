#!/usr/bin/env python3
"""
MMRetriever API服务器启动脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_config():
    """设置配置"""
    try:
        # 导入配置管理器
        from utils.config import init_config
        
        # 初始化配置
        config_manager = init_config()
        
        print("✓ 配置文件加载成功")
        return config_manager
        
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        print("请检查以下事项：")
        print("1. 确保 config.yaml 文件存在")
        print("2. 检查配置文件语法是否正确")
        print("3. 确认所有必需的配置项都已填写")
        print("4. 验证API密钥等凭证信息是否正确")
        sys.exit(1)


def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'elasticsearch',
        'dashscope',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"错误：缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖：")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("✓ 依赖包检查通过")


def start_server(config_manager):
    """启动服务器"""
    import uvicorn
    
    # 获取配置
    server_config = config_manager.get_server_config()
    host = server_config.host
    port = server_config.port
    log_level = server_config.log_level.lower()
    reload = server_config.dev_mode
    access_log = server_config.access_log
    
    # 获取ES配置用于显示
    es_config = config_manager.get_elasticsearch_config()
    es_host = es_config.get('host', 'localhost')
    es_port = es_config.get('port', 9200)
    es_scheme = es_config.get('scheme', 'http')
    
    print(f"🚀 启动MMRetriever API服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   文档: http://{host}:{port}/docs")
    print(f"   日志级别: {log_level}")
    print(f"   Elasticsearch: {es_scheme}://{es_host}:{es_port}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
        access_log=access_log
    )


if __name__ == "__main__":
    print("=" * 60)
    print("MMRetriever API Server")
    print("多模态检索系统API服务")
    print("=" * 60)
    
    try:
        # 加载配置
        config_manager = setup_config()
        check_dependencies()
        
        # 启动服务器
        start_server(config_manager)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1) 