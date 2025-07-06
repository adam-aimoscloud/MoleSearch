"""
MMRetriever FastAPI Application
多模态搜索引擎API服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from handlers.search_handler import router as search_router
from utils.logger import get_logger

logger = get_logger(__name__)

# 全局变量存储应用状态
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("MMRetriever API启动中...")
    
    logger.info("MMRetriever API启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("MMRetriever API关闭")

# 创建FastAPI应用
app = FastAPI(
    title="MMRetriever API",
    description="多模态检索系统API - 支持文本、图像、视频搜索",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(search_router, prefix="/api/v1", tags=["search"])

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "MMRetriever API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "MMRetriever API"
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