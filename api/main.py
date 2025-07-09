"""
MoleRetriever FastAPI Application
Multimodal search engine API service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from handlers.search_handler import router as search_router
from handlers.file_handler import router as file_router
from utils.logger import get_logger

logger = get_logger(__name__)

# Global variable to store application state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Execute when starting
    logger.info("MoleRetriever API starting...")
    
    logger.info("MoleRetriever API started")
    
    yield
    
    # Execute when closing
    logger.info("MoleRetriever API closed")

# Create FastAPI application
app = FastAPI(
    title="MoleRetriever API",
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
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(file_router)

@app.get("/")
async def root():
    """Root path health check"""
    return {
        "message": "MoleRetriever API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check interface"""
    return {
        "status": "healthy",
        "service": "MoleRetriever API"
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