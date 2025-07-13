"""
MoleSearch FastAPI Application
Multimodal search engine API service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from handlers.search_handler import router as search_router
from handlers.file_handler import router as file_router
from handlers.auth_handler import router as auth_router
from handlers.api_key_handler import router as api_key_router
from utils.logger import get_logger
from utils.config import init_config
from utils.redis_client import init_redis

logger = get_logger(__name__)

# Global variable to store application state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Execute when starting
    logger.info("MoleSearch API starting...")
    
    # Initialize configuration
    init_config()
    
    # Initialize Redis connection
    if init_redis():
        logger.info("Redis connection established")
    else:
        logger.warning("Failed to connect to Redis - authentication may not work properly")
    
    # Log authentication status
    logger.info("User authentication is enabled")
    
    logger.info("MoleSearch API started")
    
    yield
    
    # Execute when closing
    logger.info("MoleSearch API closed")

# Create FastAPI application
app = FastAPI(
    title="MoleSearch API",
    description="Multimodal search system API - supports text, image, and video search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, should set specific domain names
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router)
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(file_router, prefix="/api/v1", tags=["files"])
app.include_router(api_key_router, prefix="/api/v1", tags=["api-keys"])

# Mount static files for uploaded files
try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except Exception as e:
    logger.warning(f"Could not mount uploads directory: {e}")

@app.get("/")
async def root():
    """Root path health check"""
    return {
        "message": "MoleSearch API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check interface"""
    return {
        "status": "healthy",
        "service": "MoleSearch API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 