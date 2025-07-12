"""
Search service - Core business logic integrating MMExtractor and Elasticsearch
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import uuid

from processor.core.pipeline import PipelineParam
from processor.pipelines.mm_extractor import MMExtractor
from processor.core.data import DataIO, MMData, TextItem, ImageItem, VideoItem
from search_engine.base import SearchEngineFactory, SearchEngineParam, SearchInput, InsertData, EmbeddingInfo
from search_engine.elasticsearch.es import ESSearchEngine
from .models import InsertDataRequest
from .exceptions import (
    MoleSearchException, ValidationException, MediaProcessingException,
    ServiceException, NotFoundException, InvalidMediaFormatException,
    MediaDownloadException
)
from utils.logger import get_logger
from utils.config import get_config_manager

logger = get_logger(__name__)


class SearchService:
    """Search service class"""
    
    def __init__(self):
        self.mm_extractor = None
        self.search_engine = None
        self.initialized = False

    def __del__(self):
        if self.search_engine:
            asyncio.run(self.search_engine.close())
    
    async def initialize(self):
        """Initialize search service"""
        if self.initialized:
            return
        
        try:
            logger.info("Initializing search service...")
            
            # Initialize MMExtractor
            await self._init_mm_extractor()
            
            # Initialize search engine
            self._init_search_engine()
            
            self.initialized = True
            logger.info("Search service initialized")
            
        except Exception as e:
            logger.error(f"Search service initialization failed: {str(e)}")
            raise
    
    async def _init_mm_extractor(self):
        """Initialize MMExtractor"""
        try:
            # Get configuration from configuration manager
            config_manager = get_config_manager()
            mmextractor_config = config_manager.get_mmextractor_config()
            
            # Create temporary configuration file for MMExtractor
            config_path = "temp_mm_extractor_config.yaml"
            await self._create_config_from_settings(config_path, mmextractor_config.plugins)
            
            # Create MMExtractor instance
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            pipeline_param = PipelineParam.from_dict(config_data)
            self.mm_extractor = MMExtractor(pipeline_param)
            
            # Clean up temporary configuration file
            if os.path.exists(config_path):
                os.remove(config_path)
            
            logger.info("MMExtractor initialized")
            
        except Exception as e:
            logger.error(f"MMExtractor initialization failed: {str(e)}")
            raise
    
    def _init_search_engine(self):
        """Initialize search engine"""
        try:
            # Get ES configuration from configuration manager
            config_manager = get_config_manager()
            es_config = config_manager.get_elasticsearch_config()
            
            # Create ES search engine
            es_param = SearchEngineParam(
                type='es',
                param={
                    'host': es_config.get('host', 'localhost'),
                    'port': es_config.get('port', 9200),
                    'index': es_config.get('index', 'mmretriever'),
                    'username': es_config.get('username', ''),
                    'password': es_config.get('password', ''),
                    'scheme': es_config.get('scheme', 'http'),
                    'vector_dimensions': es_config.get('vector_dimensions', {
                        'text_embedding': 1024,
                        'image_embedding': 1024,
                        'video_embedding': 1024
                    })
                }
            )
            
            factory = SearchEngineFactory(es_param)
            self.search_engine = factory.get_search_engine()
            
            logger.info("Search engine initialized")
            
        except Exception as e:
            logger.error(f"Search engine initialization failed: {str(e)}")
            raise
    
    async def _create_config_from_settings(self, config_path: str, plugins_config: Dict[str, Any]):
        """Create temporary configuration file from configuration settings"""
        import yaml
        
        try:
            # Build configuration structure
            config_data = {
                'name': 'MMExtractor',
                'type': 'extraction',
                'enable': True,
                'plugins': {}
            }
            
            # Convert plugin configuration
            for plugin_name, plugin_config in plugins_config.items():
                config_data['plugins'][plugin_name] = plugin_config
            
            # Write to YAML file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Created temporary configuration file: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to create configuration file: {str(e)}")
            raise
    
    async def search_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Text search"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use MMExtractor to process text
            mm_data = MMData(text=TextItem(text=query))
            result = await self.mm_extractor.forward(mm_data)
            
            # Build search input
            embeddings = []
            if result.text and result.text.text_embeddings:
                embeddings.append(EmbeddingInfo(
                    label='text_embedding',
                    embedding=result.text.text_embeddings[0]
                ))
            
            search_input = SearchInput(
                text=query,
                embeddings=embeddings,
                topk=top_k
            )
            
            # Execute search
            search_result = await self.search_engine.search(search_input)
            
            # Convert result format
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),  # Generate temporary ID
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'image_text': item.image_text,
                    'video_text': item.video_text,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")
            raise
    
    async def search_image(self, image_url: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Image search"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use MMExtractor to process image
            mm_data = MMData(image=ImageItem(image=image_url))
            result = await self.mm_extractor.forward(mm_data)
            
            # Build search input
            embeddings = []
            if result.image and result.image.image_embedding:
                embeddings.append(EmbeddingInfo(
                    label='image_embedding',
                    embedding=result.image.image_embedding
                ))
            
            # Add image text embedding search
            if result.image and result.image.text_embeddings:
                embeddings.append(EmbeddingInfo(
                    label='image_text_embedding',
                    embedding=result.image.text_embeddings[0]
                ))
            
            search_input = SearchInput(
                text='',
                embeddings=embeddings,
                topk=top_k
            )
            
            # Execute search
            search_result = await self.search_engine.search(search_input)
            
            # Convert result format
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'image_text': item.image_text,
                    'video_text': item.video_text,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Image search failed: {str(e)}")
            raise
    
    async def search_video(self, video_url: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Video search"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use MMExtractor to process video
            mm_data = MMData(video=VideoItem(video=video_url))
            result = await self.mm_extractor.forward(mm_data)
            
            # Build search input
            embeddings = []
            if result.video and result.video.video_embedding:
                embeddings.append(EmbeddingInfo(
                    label='video_embedding',
                    embedding=result.video.video_embedding
                ))
            
            # Add video text embedding search
            if result.video and result.video.text_embeddings:
                embeddings.append(EmbeddingInfo(
                    label='video_text_embedding',
                    embedding=result.video.text_embeddings[0]
                ))
            
            search_input = SearchInput(
                text='',
                embeddings=embeddings,
                topk=top_k
            )
            
            # Execute search
            search_result = await self.search_engine.search(search_input)
            
            # Convert result format
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'image_text': item.image_text,
                    'video_text': item.video_text,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Video search failed: {str(e)}")
            raise
    
    async def search_multimodal(self, text: Optional[str] = None, 
                               image_url: Optional[str] = None,
                               video_url: Optional[str] = None,
                               top_k: int = 10) -> List[Dict[str, Any]]:
        """Multimodal search"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build multimodal input
            mm_data = MMData(
                text=TextItem(text=text or '') if text else None,
                image=ImageItem(image=image_url or '') if image_url else None,
                video=VideoItem(video=video_url or '') if video_url else None
            )
            
            # Use MMExtractor to process multimodal data
            result = await self.mm_extractor.forward(mm_data)
            
            # Build search input
            embeddings = []
            search_text = text or ''
            
            # Add all available embedding
            if result.text and result.text.text_embeddings:
                embeddings.append(EmbeddingInfo(
                    label='text_embedding',
                    embedding=result.text.text_embeddings[0]
                ))
            
            if result.image and result.image.image_embedding:
                embeddings.append(EmbeddingInfo(
                    label='image_embedding',
                    embedding=result.image.image_embedding
                ))
            
            if result.video and result.video.video_embedding:
                embeddings.append(EmbeddingInfo(
                    label='video_embedding',
                    embedding=result.video.video_embedding
                ))
            
            search_input = SearchInput(
                text=search_text,
                embeddings=embeddings,
                topk=top_k
            )
            
            # Execute search
            search_result = await self.search_engine.search(search_input)
            
            # Convert result format
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'image_text': item.image_text,
                    'video_text': item.video_text,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Multimodal search failed: {error_msg}")
            
            # Convert plugin error to custom exception
            if "image format is illegal" in error_msg or "cannot be opened" in error_msg:
                raise InvalidMediaFormatException("Image", image_url or "", error_msg)
            elif "Video URL download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("Video", video_url or "", error_msg)
            elif "QwenIEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"Image processing failed: {error_msg}")
            elif "QwenVEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"Video processing failed: {error_msg}")
            else:
                raise ServiceException(f"Multimodal search service exception: {error_msg}")
    
    async def insert_data(self, text: str = '', image_url: str = '', video_url: str = ''):
        """Insert single data"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build input data
            mm_data = MMData(
                text=TextItem(text=text) if text else None,
                image=ImageItem(image=image_url) if image_url else None,
                video=VideoItem(video=video_url) if video_url else None
            )
            
            # Use MMExtractor to process data
            result = await self.mm_extractor.forward(mm_data)
            logger.info(f"mm_extractor result: {result}")
            
            # Build insert data
            embeddings = []
            image_text = ''
            video_text = ''
            if result.text and result.text.text_embeddings:
                embeddings.append(EmbeddingInfo(
                    label='text_embedding',
                    embedding=result.text.text_embeddings[0]
                ))
            
            if result.image and result.image.image_embedding:
                embeddings.append(EmbeddingInfo(
                    label='image_embedding',
                    embedding=result.image.image_embedding
                ))
                image_text = result.image.text
                # Add image text embedding
                if result.image.text_embeddings:
                    embeddings.append(EmbeddingInfo(
                        label='image_text_embedding',
                        embedding=result.image.text_embeddings[0]
                    ))
            
            if result.video and result.video.video_embedding:
                embeddings.append(EmbeddingInfo(
                    label='video_embedding',
                    embedding=result.video.video_embedding
                ))
                video_text = result.video.text
                # Add video text embedding
                if result.video.text_embeddings:
                    embeddings.append(EmbeddingInfo(
                        label='video_text_embedding',
                        embedding=result.video.text_embeddings[0]
                    ))
            insert_data = InsertData(
                text=text,
                image=image_url,
                video=video_url,
                embeddings=embeddings,
                image_text=image_text,
                video_text=video_text
            )
            
            # Execute insert
            await self.search_engine.insert(insert_data)
            
            logger.info("Data insertion successful")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Data insertion failed: {error_msg}")
            
            # Convert plugin error to custom exception
            if "image format is illegal" in error_msg or "cannot be opened" in error_msg:
                raise InvalidMediaFormatException("Image", image_url, error_msg)
            elif "Video URL download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("Video", video_url, error_msg)
            elif "QwenIEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"Image processing failed: {error_msg}")
            elif "QwenVEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"Video processing failed: {error_msg}")
            else:
                raise ServiceException(f"Data insertion service exception: {error_msg}")
    
    async def batch_insert_data(self, data_list: List[InsertDataRequest]) -> int:
        """Batch insert data"""
        if not self.initialized:
            await self.initialize()
        
        try:
            insert_data_list = []
            
            for data_request in data_list:
                # Build input data
                mm_data = MMData(
                    text=TextItem(text=data_request.text) if data_request.text else None,
                    image=ImageItem(image=data_request.image_url) if data_request.image_url else None,
                    video=VideoItem(video=data_request.video_url) if data_request.video_url else None
                )
                
                # Use MMExtractor to process data
                result = await self.mm_extractor.forward(mm_data)
                
                # Build insert data
                embeddings = []
                image_text = ''
                video_text = ''
                if result.text and result.text.text_embeddings:
                    embeddings.append(EmbeddingInfo(
                        label='text_embedding',
                        embedding=result.text.text_embeddings[0]
                    ))
                
                if result.image and result.image.image_embedding:
                    embeddings.append(EmbeddingInfo(
                        label='image_embedding',
                        embedding=result.image.image_embedding
                    ))
                    image_text = result.image.text
                    # Add image text embedding
                    if result.image.text_embeddings:
                        embeddings.append(EmbeddingInfo(
                            label='image_text_embedding',
                            embedding=result.image.text_embeddings[0]
                        ))
                if result.video and result.video.video_embedding:
                    embeddings.append(EmbeddingInfo(
                        label='video_embedding',
                        embedding=result.video.video_embedding
                    ))
                    video_text = result.video.text
                    # Add video text embedding
                    if result.video.text_embeddings:
                        embeddings.append(EmbeddingInfo(
                            label='video_text_embedding',
                            embedding=result.video.text_embeddings[0]
                        ))
                insert_data = InsertData(
                    text=data_request.text,
                    image=data_request.image_url,
                    video=data_request.video_url,
                    embeddings=embeddings,
                    image_text=image_text,
                    video_text=video_text
                )
                
                insert_data_list.append(insert_data)
            
            # Execute batch insert
            await self.search_engine.batch_insert(insert_data_list)
            
            logger.info(f"Batch insert completed, total {len(insert_data_list)} data")
            return len(insert_data_list)
            
        except Exception as e:
            logger.error(f"Batch insert failed: {str(e)}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'initialized': self.initialized,
                'mm_extractor': self.mm_extractor is not None,
                'search_engine': self.search_engine is not None
            }
            
            # Check search engine connection status
            if self.search_engine:
                try:
                    # Try to execute a simple search to check connection
                    test_search = SearchInput(text='test', embeddings=[], topk=1)
                    await self.search_engine.search(test_search)
                    status['search_engine_connected'] = True
                except Exception as e:
                    status['search_engine_connected'] = False
                    status['search_engine_error'] = str(e)
            
            return status
            
        except Exception as e:
            logger.error(f"Get status failed: {str(e)}")
            raise
    
    async def list_data(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get all data with paging"""
        if not self.initialized:
            await self.initialize()
        try:
            # Get data through search engine interface
            result = await self.search_engine.list_data(page=page, page_size=page_size)
            
            # Convert result format
            items = []
            for item in result.items:
                items.append({
                    'id': str(uuid.uuid4()),  # Generate temporary ID
                    'text': item.text,
                    'image_url': item.image,
                    'video_url': item.video,
                    'image_text': item.image_text,
                    'video_text': item.video_text
                })
            
            logger.info(f"Full data paging query successful, total: {result.total}, current page: {page}, page size: {page_size}, return items: {len(items)}")
            
            return {
                'total': result.total,
                'items': items
            }
        except Exception as e:
            logger.error(f"Full data paging query failed: {str(e)}")
            raise ServiceException(f"Full data paging query failed: {str(e)}") 