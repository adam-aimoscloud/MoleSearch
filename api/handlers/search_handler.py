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
    DataListRequest, DataListResponse, DataListItem
)
from .search_service import SearchService
from .exceptions import (
    MoleRetrieverException, ValidationException, MediaProcessingException,
    ServiceException, NotFoundException, InvalidMediaFormatException,
    MediaDownloadException
)
from utils.logger import get_logger

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
    service: SearchService = Depends(get_search_service)
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
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
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
    service: SearchService = Depends(get_search_service)
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
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
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
        if not isinstance(e, MoleRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/video", response_model=SearchResponse)
async def search_video(
    request: VideoSearchRequest,
    service: SearchService = Depends(get_search_service)
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
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
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
        if not isinstance(e, MoleRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/search/multimodal", response_model=SearchResponse)
async def search_multimodal(
    request: MultimodalSearchRequest,
    service: SearchService = Depends(get_search_service)
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
            search_results.append(SearchResultItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image', ''),
                video_url=item.get('video', ''),
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
        if not isinstance(e, MoleRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/insert", response_model=InsertResponse)
async def insert_data(
    request: InsertDataRequest,
    service: SearchService = Depends(get_search_service)
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
        if not isinstance(e, MoleRetrieverException):
            logger.error(traceback.format_exc())
        raise handle_service_exception(e)


@router.post("/data/batch_insert", response_model=InsertResponse)
async def batch_insert_data(
    request: BatchInsertRequest,
    service: SearchService = Depends(get_search_service)
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
        "service": "MoleRetriever Search Service",
        "version": "1.0.0"
    }


@router.get("/status")
async def get_status(service: SearchService = Depends(get_search_service)):
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
    service: SearchService = Depends(get_search_service)
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
            items.append(DataListItem(
                id=item.get('id', ''),
                text=item.get('text', ''),
                image_url=item.get('image_url', ''),
                video_url=item.get('video_url', ''),
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