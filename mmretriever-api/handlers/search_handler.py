"""
搜索处理器 - 实现多模态搜索API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import time
import traceback

from .models import (
    TextSearchRequest, ImageSearchRequest, VideoSearchRequest, 
    MultimodalSearchRequest, SearchResponse, SearchResultItem,
    InsertDataRequest, BatchInsertRequest, InsertResponse, ErrorResponse
)
from .search_service import SearchService
from .exceptions import (
    MMRetrieverException, ValidationException, MediaProcessingException,
    ServiceException, NotFoundException, InvalidMediaFormatException,
    MediaDownloadException
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# 搜索服务实例
search_service = None

def handle_service_exception(e: Exception) -> HTTPException:
    """处理服务异常，返回合适的HTTP异常"""
    if isinstance(e, ValidationException):
        return HTTPException(status_code=422, detail=str(e))
    elif isinstance(e, MediaProcessingException):
        return HTTPException(status_code=422, detail=str(e))
    elif isinstance(e, InvalidMediaFormatException):
        return HTTPException(status_code=422, detail=str(e))
    elif isinstance(e, MediaDownloadException):
        return HTTPException(status_code=422, detail=str(e))
    elif isinstance(e, NotFoundException):
        return HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, ServiceException):
        return HTTPException(status_code=500, detail=str(e))
    else:
        # 未知异常，返回500
        return HTTPException(status_code=500, detail=f"服务异常: {str(e)}")

async def get_search_service():
    """获取搜索服务实例"""
    global search_service
    if search_service is None:
        search_service = SearchService()
        await search_service.initialize()
    return search_service


@router.post("/search/text", response_model=SearchResponse)
async def search_text(
    request: TextSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    文本搜索接口
    
    - **query**: 搜索查询文本
    - **top_k**: 返回结果数量，默认10，最大100
    """
    start_time = time.time()
    
    try:
        logger.info(f"文本搜索请求: {request.query[:100]}...")
        
        # 执行搜索
        results = await service.search_text(request.query, request.top_k)
        
        # 构建响应
        search_results = []
        for item in results:
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"文本搜索完成，耗时: {query_time:.3f}s，结果数: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="搜索完成",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"文本搜索失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )


@router.post("/search/image", response_model=SearchResponse)
async def search_image(
    request: ImageSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    图像搜索接口
    
    - **image_url**: 图像URL地址
    - **top_k**: 返回结果数量，默认10，最大100
    """
    start_time = time.time()
    
    try:
        logger.info(f"图像搜索请求: {request.image_url}")
        
        # 执行搜索
        results = await service.search_image(request.image_url, request.top_k)
        
        # 构建响应
        search_results = []
        for item in results:
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"图像搜索完成，耗时: {query_time:.3f}s，结果数: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="搜索完成",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"图像搜索失败: {str(e)}")
        if not isinstance(e, MMRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/video", response_model=SearchResponse)
async def search_video(
    request: VideoSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    视频搜索接口
    
    - **video_url**: 视频URL地址
    - **top_k**: 返回结果数量，默认10，最大100
    """
    start_time = time.time()
    
    try:
        logger.info(f"视频搜索请求: {request.video_url}")
        
        # 执行搜索
        results = await service.search_video(request.video_url, request.top_k)
        
        # 构建响应
        search_results = []
        for item in results:
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"视频搜索完成，耗时: {query_time:.3f}s，结果数: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="搜索完成",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"视频搜索失败: {str(e)}")
        if not isinstance(e, MMRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/multimodal", response_model=SearchResponse)
async def search_multimodal(
    request: MultimodalSearchRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    多模态搜索接口
    
    - **text**: 文本查询（可选）
    - **image_url**: 图像URL（可选）
    - **video_url**: 视频URL（可选）
    - **top_k**: 返回结果数量，默认10，最大100
    
    注意：至少需要提供一种类型的输入
    """
    start_time = time.time()
    
    try:
        logger.info(f"多模态搜索请求: text={bool(request.text)}, image={bool(request.image_url)}, video={bool(request.video_url)}")
        
        # 执行搜索
        results = await service.search_multimodal(
            text=request.text,
            image_url=request.image_url,
            video_url=request.video_url,
            top_k=request.top_k
        )
        
        # 构建响应
        search_results = []
        for item in results:
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"多模态搜索完成，耗时: {query_time:.3f}s，结果数: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="搜索完成",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"多模态搜索失败: {str(e)}")
        if not isinstance(e, MMRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/insert", response_model=InsertResponse)
async def insert_data(
    request: InsertDataRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    单条数据插入接口
    
    - **text**: 文本内容（可选）
    - **image_url**: 图像URL（可选）
    - **video_url**: 视频URL（可选）
    
    注意：至少需要提供一种类型的内容
    """
    start_time = time.time()
    
    try:
        logger.info(f"数据插入请求: text={bool(request.text)}, image={bool(request.image_url)}, video={bool(request.video_url)}")
        
        # 执行插入
        await service.insert_data(
            text=request.text,
            image_url=request.image_url,
            video_url=request.video_url
        )
        
        processing_time = time.time() - start_time
        logger.info(f"数据插入完成，耗时: {processing_time:.3f}s")
        
        return InsertResponse(
            success=True,
            message="数据插入成功",
            inserted_count=1,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"数据插入失败: {str(e)}")
        if not isinstance(e, MMRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/batch_insert", response_model=InsertResponse)
async def batch_insert_data(
    request: BatchInsertRequest,
    service: SearchService = Depends(get_search_service)
):
    """
    批量数据插入接口
    
    - **data_list**: 要插入的数据列表，最多100条
    """
    start_time = time.time()
    
    try:
        logger.info(f"批量数据插入请求: {len(request.data_list)} 条数据")
        
        # 执行批量插入
        inserted_count = await service.batch_insert_data(request.data_list)
        
        processing_time = time.time() - start_time
        logger.info(f"批量数据插入完成，耗时: {processing_time:.3f}s，成功插入: {inserted_count} 条")
        
        return InsertResponse(
            success=True,
            message="批量数据插入成功",
            inserted_count=inserted_count,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"批量数据插入失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"批量数据插入失败: {str(e)}"
        )


@router.get("/status")
async def get_status(service: SearchService = Depends(get_search_service)):
    """
    获取搜索服务状态
    """
    try:
        status = await service.get_status()
        return {
            "success": True,
            "message": "服务状态正常",
            "status": status
        }
    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取服务状态失败: {str(e)}"
        ) 