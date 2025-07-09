#!/usr/bin/env python3
"""
MoleRetriever API server startup script
"""

import os
import sys
import logging
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_config():
    """Set up configuration"""
    try:
        # Import configuration manager
        from utils.config import init_config
        
        # Initialize configuration
        config_manager = init_config()
        
        print("✓ Configuration file loaded successfully")
        return config_manager
        
    except Exception as e:
        print(f"❌ Configuration file loading failed: {e}")
        print("Please check the following:")
        print("1. Ensure config.yaml file exists")
        print("2. Check configuration file syntax")
        print("3. Ensure all required configuration items are filled")
        print("4. Verify API key and other credential information")
        sys.exit(1)


def check_dependencies():
    """Check dependencies"""
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
        print(f"Error: missing dependencies: {', '.join(missing_packages)}")
        print("Please run the following command to install dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("✓ Dependencies check passed")


def start_server(config_manager):
    """Start server"""
    import uvicorn
    
    # Get configuration
    server_config = config_manager.get_server_config()
    host = server_config.host
    port = server_config.port
    log_level = server_config.log_level.lower()
    reload = server_config.dev_mode
    access_log = server_config.access_log
    
    # Get ES configuration for display
    es_config = config_manager.get_elasticsearch_config()
    es_host = es_config.get('host', 'localhost')
    es_port = es_config.get('port', 9200)
    es_scheme = es_config.get('scheme', 'http')
    
    print(f"🚀 Starting MoleRetriever API server...")
    print(f"   Address: http://{host}:{port}")
    print(f"   Documentation: http://{host}:{port}/docs")
    print(f"   Log level: {log_level}")
    print(f"   Elasticsearch: {es_scheme}://{es_host}:{es_port}")
    
    # Start server
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
    print("MoleRetriever API Server")
    print("Multimodal search system API service")
    print("=" * 60)
    
    try:
        # Load configuration
        config_manager = setup_config()
        check_dependencies()
        
        # Start server
        start_server(config_manager)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1) 