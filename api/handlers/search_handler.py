"""
Search handler - Implement multimodal search API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import time
import traceback

from .models import (
    TextSearchRequest, ImageSearchRequest, VideoSearchRequest, 
    MultimodalSearchRequest, SearchResponse, SearchResultItem,
    InsertDataRequest, BatchInsertRequest, InsertResponse, ErrorResponse,
    DataListRequest, DataListResponse, DataListItem,
    AsyncInsertDataRequest, AsyncBatchInsertRequest, AsyncTaskResponse,
    TaskStatusResponse, TaskStatus, TaskListResponse
)
from .search_service import SearchService
from .auth import get_current_token
from .exceptions import (
    MoleSearchException, ValidationException, MediaProcessingException,
    ServiceException, NotFoundException, InvalidMediaFormatException,
    MediaDownloadException
)
from utils.logger import get_logger
from utils.async_task_manager import get_task_manager

logger = get_logger(__name__)

router = APIRouter()

# Search service instance
search_service = None

def handle_service_exception(e: Exception) -> HTTPException:
    """Handle service exception, return appropriate HTTP exception"""
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
        # Unknown exception, return 500
        return HTTPException(status_code=500, detail=f"Service exception: {str(e)}")

async def get_search_service():
    """Get search service instance"""
    global search_service
    if search_service is None:
        search_service = SearchService()
        await search_service.initialize()
    return search_service


@router.post("/search/text", response_model=SearchResponse)
async def search_text(
    request: TextSearchRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Text search interface
    
    - **query**: Search query text
    - **top_k**: Return result count, default 10, maximum 100
    """
    start_time = time.time()
    
    try:
        logger.info(f"Text search request: {request.query[:100]}...")
        
        # Execute search
        results = await service.search_text(request.query, request.top_k)
        
        # Build response
        search_results = []
        for item in results:
            # Handle None values properly
            image_url = item.get('image')
            video_url = item.get('video')
            text = item.get('text')
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=text if text is not None else '',
                image_url=image_url if image_url is not None else '',
                video_url=video_url if video_url is not None else '',
                image_text=item.get('image_text', ''),
                video_text=item.get('video_text', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"Text search completed, time: {query_time:.3f}s, result count: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="Search completed",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Text search failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/search/image", response_model=SearchResponse)
async def search_image(
    request: ImageSearchRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Image search interface
    
    - **image_url**: Image URL address
    - **top_k**: Return result count, default 10, maximum 100
    """
    start_time = time.time()
    
    try:
        logger.info(f"Image search request: {request.image_url}")
        
        # Execute search
        results = await service.search_image(request.image_url, request.top_k)
        
        # Build response
        search_results = []
        for item in results:
            # Handle None values properly
            image_url = item.get('image')
            video_url = item.get('video')
            text = item.get('text')
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=text if text is not None else '',
                image_url=image_url if image_url is not None else '',
                video_url=video_url if video_url is not None else '',
                image_text=item.get('image_text', ''),
                video_text=item.get('video_text', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"Image search completed, time: {query_time:.3f}s, result count: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="Search completed",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Image search failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/video", response_model=SearchResponse)
async def search_video(
    request: VideoSearchRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Video search interface
    
    - **video_url**: Video URL address
    - **top_k**: Return result count, default 10, maximum 100
    """
    start_time = time.time()
    
    try:
        logger.info(f"Video search request: {request.video_url}")
        
        # Execute search
        results = await service.search_video(request.video_url, request.top_k)
        
        # Build response
        search_results = []
        for item in results:
            # Handle None values properly
            image_url = item.get('image')
            video_url = item.get('video')
            text = item.get('text')
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=text if text is not None else '',
                image_url=image_url if image_url is not None else '',
                video_url=video_url if video_url is not None else '',
                image_text=item.get('image_text', ''),
                video_text=item.get('video_text', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"Video search completed, time: {query_time:.3f}s, result count: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="Search completed",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Video search failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/multimodal", response_model=SearchResponse)
async def search_multimodal(
    request: MultimodalSearchRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Multimodal search interface
    
    - **text**: Text query (optional)
    - **image_url**: Image URL (optional)
    - **video_url**: Video URL (optional)
    - **top_k**: Return result count, default 10, maximum 100
    
    Note: At least one type of input is required
    """
    start_time = time.time()
    
    try:
        logger.info(f"Multimodal search request: text={bool(request.text)}, image={bool(request.image_url)}, video={bool(request.video_url)}")
        
        # Execute search
        results = await service.search_multimodal(
            text=request.text,
            image_url=request.image_url,
            video_url=request.video_url,
            top_k=request.top_k
        )
        
        # Build response
        search_results = []
        for item in results:
            # Handle None values properly
            image_url = item.get('image')
            video_url = item.get('video')
            text = item.get('text')
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=text if text is not None else '',
                image_url=image_url if image_url is not None else '',
                video_url=video_url if video_url is not None else '',
                image_text=item.get('image_text', ''),
                video_text=item.get('video_text', ''),
                score=item.get('score', 0.0)
            ))
        
        query_time = time.time() - start_time
        logger.info(f"Multimodal search completed, time: {query_time:.3f}s, result count: {len(search_results)}")
        
        return SearchResponse(
            success=True,
            message="Search completed",
            total=len(search_results),
            results=search_results,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Multimodal search failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/insert", response_model=InsertResponse)
async def insert_data(
    request: InsertDataRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Single data insertion interface
    
    - **text**: Text content (optional)
    - **image_url**: Image URL (optional)
    - **video_url**: Video URL (optional)
    
    Note: At least one type of content is required
    """
    start_time = time.time()
    
    try:
        logger.info(f"Data insertion request: text={bool(request.text)}, image={bool(request.image_url)}, video={bool(request.video_url)}")
        
        # Execute insertion
        await service.insert_data(
            text=request.text,
            image_url=request.image_url,
            video_url=request.video_url
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Data insertion completed, time: {processing_time:.3f}s")
        
        return InsertResponse(
            success=True,
            message="Data insertion successful",
            inserted_count=1,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Data insertion failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/batch_insert", response_model=InsertResponse)
async def batch_insert_data(
    request: BatchInsertRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Batch data insertion interface
    
    - **data_list**: Data list to insert, maximum 100
    """
    start_time = time.time()
    
    try:
        logger.info(f"Batch data insertion request: {len(request.data_list)} data")
        
        # Execute batch insertion
        inserted_count = await service.batch_insert_data(request.data_list)
        
        processing_time = time.time() - start_time
        logger.info(f"Batch data insertion completed, time: {processing_time:.3f}s, successfully inserted: {inserted_count} data")
        
        return InsertResponse(
            success=True,
            message="Batch data insertion successful",
            inserted_count=inserted_count,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch data insertion failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Batch data insertion failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check interface
    
    Simple health check, used for load balancer and monitoring system
    """
    return {
        "status": "healthy",
        "service": "MoleSearch Search Service",
        "version": "1.0.0"
    }


@router.get("/status")
async def get_status(
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Get search service status
    """
    try:
        status = await service.get_status()
        return {
            "success": True,
            "message": "Service status normal",
            "status": status
        }
    except Exception as e:
        logger.error(f"Get service status failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Get service status failed: {str(e)}"
        )


@router.post("/data/list", response_model=DataListResponse)
async def list_data(
    request: DataListRequest,
    service: SearchService = Depends(get_search_service),
    token: Optional[str] = Depends(get_current_token)
):
    """
    Full data paging query interface
    - **page**: Page number, starting from 1
    - **page_size**: Number of items per page
    """
    try:
        result = await service.list_data(page=request.page, page_size=request.page_size)
        items = []
        for item in result['items']:
            # Handle None values properly
            image_url = item.get('image_url')
            video_url = item.get('video_url')
            text = item.get('text')
            items.append(DataListItem(
                id=item.get('id', ''),
                text=text if text is not None else '',
                image_url=image_url if image_url is not None else '',
                video_url=video_url if video_url is not None else '',
                image_text=item.get('image_text', ''),
                video_text=item.get('video_text', '')
            ))
        return DataListResponse(
            success=True,
            message="Query successful",
            total=result['total'],
            items=items,
            page=request.page,
            page_size=request.page_size
        )
    except Exception as e:
        logger.error(f"Full data paging query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Full data paging query failed: {str(e)}")

# Async data insertion endpoints
@router.post("/data/async_insert", response_model=AsyncTaskResponse)
async def async_insert_data(
    request: AsyncInsertDataRequest,
    token: Optional[str] = Depends(get_current_token)
):
    """
    Async single data insertion interface
    
    - **text**: Text content (optional)
    - **image_url**: Image URL (optional)
    - **video_url**: Video URL (optional)
    
    Returns task ID for tracking insertion progress
    """
    try:
        logger.info(f"Async data insertion request: text={bool(request.text)}, image={bool(request.image_url)}, video={bool(request.video_url)}")
        
        # Validate request
        if not request.text and not request.image_url and not request.video_url:
            raise ValidationException("At least one type of content is required")
        
        # Create async task
        task_manager = get_task_manager()
        task_data = {
            'text': request.text,
            'image_url': request.image_url,
            'video_url': request.video_url
        }
        
        task_id = task_manager.create_task('insert_data', task_data)
        
        logger.info(f"Created async insert task: {task_id}")
        
        return AsyncTaskResponse(
            success=True,
            message="Async data insertion task created",
            task_id=task_id,
            estimated_time=30  # Estimated 30 seconds for single item
        )
        
    except Exception as e:
        logger.error(f"Async data insertion failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/async_batch_insert", response_model=AsyncTaskResponse)
async def async_batch_insert_data(
    request: AsyncBatchInsertRequest,
    token: Optional[str] = Depends(get_current_token)
):
    """
    Async batch data insertion interface
    
    - **data_list**: Data list to insert, maximum 100
    """
    try:
        logger.info(f"Async batch data insertion request: {len(request.data_list)} data")
        
        # Validate request
        if not request.data_list:
            raise ValidationException("Data list cannot be empty")
        
        if len(request.data_list) > 100:
            raise ValidationException("Maximum 100 items allowed per batch")
        
        # Validate each item
        for i, item in enumerate(request.data_list):
            if not item.text and not item.image_url and not item.video_url:
                raise ValidationException(f"Item {i}: At least one type of content is required")
        
        # Create async task
        task_manager = get_task_manager()
        task_data = {
            'data_list': [
                {
                    'text': item.text,
                    'image_url': item.image_url,
                    'video_url': item.video_url
                }
                for item in request.data_list
            ]
        }
        
        task_id = task_manager.create_task('batch_insert_data', task_data)
        
        # Estimate processing time (30 seconds per item)
        estimated_time = len(request.data_list) * 30
        
        logger.info(f"Created async batch insert task: {task_id}")
        
        return AsyncTaskResponse(
            success=True,
            message="Async batch data insertion task created",
            task_id=task_id,
            estimated_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"Async batch data insertion failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    token: Optional[str] = Depends(get_current_token)
):
    """
    Get task status by task ID
    
    - **task_id**: Task ID returned from async insertion
    """
    try:
        task_manager = get_task_manager()
        task_info = task_manager.get_task_status(task_id)
        
        if not task_info:
            raise NotFoundException(f"Task not found: {task_id}")
        
        task_status = TaskStatus(
            task_id=task_info['task_id'],
            status=task_info['status'],
            progress=task_info['progress'],
            message=task_info['message'],
            created_at=task_info['created_at'],
            started_at=task_info.get('started_at'),
            completed_at=task_info.get('completed_at'),
            result=task_info.get('result')
        )
        
        return TaskStatusResponse(
            success=True,
            message="Task status retrieved successfully",
            task_status=task_status
        )
        
    except Exception as e:
        logger.error(f"Get task status failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.get("/tasks/pending", response_model=TaskListResponse)
async def get_pending_tasks(
    token: Optional[str] = Depends(get_current_token)
):
    """
    Get all pending tasks
    
    Returns list of tasks that are currently pending
    """
    try:
        task_manager = get_task_manager()
        pending_tasks = task_manager.get_pending_tasks()
        
        # Convert to TaskStatus objects
        task_status_list = []
        for task_info in pending_tasks:
            task_status = TaskStatus(
                task_id=task_info['task_id'],
                status=task_info['status'],
                progress=task_info['progress'],
                message=task_info['message'],
                created_at=task_info['created_at'],
                started_at=task_info.get('started_at'),
                completed_at=task_info.get('completed_at'),
                result=task_info.get('result')
            )
            task_status_list.append(task_status)
        
        return TaskListResponse(
            success=True,
            message="Pending tasks retrieved successfully",
            tasks=task_status_list,
            total=len(task_status_list)
        )
        
    except Exception as e:
        logger.error(f"Get pending tasks failed: {str(e)}")
        if not isinstance(e, MoleSearchException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e) 