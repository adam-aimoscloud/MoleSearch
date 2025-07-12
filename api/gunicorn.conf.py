#!/usr/bin/env python3
"""
Gunicorn configuration file for MoleRetriever API
"""

import multiprocessing
import os
import sys
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def get_bind_config():
    """Get bind configuration from config.yaml"""
    try:
        from utils.config import init_config
        config_manager = init_config()
        server_config = config_manager.get_server_config()
        return f"{server_config.host}:{server_config.port}"
    except Exception as e:
        print(f"Warning: Failed to load config from config.yaml: {e}")
        print("Using default bind configuration: 0.0.0.0:8000")
        return "0.0.0.0:8000"

# Server socket
bind = get_bind_config()
backlog = 2048

# Worker processes
workers = 1  # multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
preload_app = True

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "mole-retriever-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (not used in this configuration)
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """Called just after the server is started."""
    server.log.info("MoleRetriever API server starting...")

def on_reload(server):
    """Called to reload the server configuration."""
    server.log.info("MoleRetriever API server reloading...")

def when_ready(server):
    """Called just after the server is started and the workers have been spawned."""
    server.log.info("MoleRetriever API server is ready to accept connections")

def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    worker.log.info("Worker received SIGINT or SIGQUIT")

def pre_fork(server, worker):
    """Called just before a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")

def worker_abort(worker):
    """Called when a worker has received SIGABRT."""
    worker.log.info("Worker received SIGABRT")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def on_exit(server):
    """Called just after exiting the server."""
    server.log.info("MoleRetriever API server exiting...") 