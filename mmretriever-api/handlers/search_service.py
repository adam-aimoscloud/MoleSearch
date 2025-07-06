"""
搜索服务 - 集成MMExtractor和Elasticsearch的核心业务逻辑
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
    MMRetrieverException, ValidationException, MediaProcessingException,
    ServiceException, NotFoundException, InvalidMediaFormatException,
    MediaDownloadException
)
from utils.logger import get_logger
from utils.config import get_config_manager

logger = get_logger(__name__)


class SearchService:
    """搜索服务类"""
    
    def __init__(self):
        self.mm_extractor = None
        self.search_engine = None
        self.initialized = False
    
    async def initialize(self):
        """初始化搜索服务"""
        if self.initialized:
            return
        
        try:
            logger.info("初始化搜索服务...")
            
            # 初始化MMExtractor
            await self._init_mm_extractor()
            
            # 初始化搜索引擎
            self._init_search_engine()
            
            self.initialized = True
            logger.info("搜索服务初始化完成")
            
        except Exception as e:
            logger.error(f"搜索服务初始化失败: {str(e)}")
            raise
    
    async def _init_mm_extractor(self):
        """初始化MMExtractor"""
        try:
            # 从配置管理器获取配置
            config_manager = get_config_manager()
            mmextractor_config = config_manager.get_mmextractor_config()
            
            # 创建临时配置文件给MMExtractor使用
            config_path = "temp_mm_extractor_config.yaml"
            await self._create_config_from_settings(config_path, mmextractor_config.plugins)
            
            # 创建MMExtractor实例
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            pipeline_param = PipelineParam.from_dict(config_data)
            self.mm_extractor = MMExtractor(pipeline_param)
            
            # 清理临时配置文件
            if os.path.exists(config_path):
                os.remove(config_path)
            
            logger.info("MMExtractor初始化完成")
            
        except Exception as e:
            logger.error(f"MMExtractor初始化失败: {str(e)}")
            raise
    
    def _init_search_engine(self):
        """初始化搜索引擎"""
        try:
            # 从配置管理器获取ES配置
            config_manager = get_config_manager()
            es_config = config_manager.get_elasticsearch_config()
            
            # 创建ES搜索引擎
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
            
            logger.info("搜索引擎初始化完成")
            
        except Exception as e:
            logger.error(f"搜索引擎初始化失败: {str(e)}")
            raise
    
    async def _create_config_from_settings(self, config_path: str, plugins_config: Dict[str, Any]):
        """从配置设置创建临时配置文件"""
        import yaml
        
        try:
            # 构建配置结构
            config_data = {
                'name': 'MMExtractor',
                'type': 'extraction',
                'enable': True,
                'plugins': {}
            }
            
            # 转换插件配置
            for plugin_name, plugin_config in plugins_config.items():
                config_data['plugins'][plugin_name] = plugin_config
            
            # 写入YAML文件
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"创建临时配置文件: {config_path}")
            
        except Exception as e:
            logger.error(f"创建配置文件失败: {str(e)}")
            raise
    
    async def search_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """文本搜索"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 使用MMExtractor处理文本
            mm_data = MMData(text=TextItem(text=query))
            result = await self.mm_extractor.forward(mm_data)
            
            # 构建搜索输入
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
            
            # 执行搜索
            search_result = self.search_engine.search(search_input)
            
            # 转换结果格式
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),  # 生成临时ID
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"文本搜索失败: {str(e)}")
            raise
    
    async def search_image(self, image_url: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """图像搜索"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 使用MMExtractor处理图像
            mm_data = MMData(image=ImageItem(image=image_url))
            result = await self.mm_extractor.forward(mm_data)
            
            # 构建搜索输入
            embeddings = []
            if result.image and result.image.image_embedding:
                embeddings.append(EmbeddingInfo(
                    label='image_embedding',
                    embedding=result.image.image_embedding
                ))
            
            search_input = SearchInput(
                text='',
                embeddings=embeddings,
                topk=top_k
            )
            
            # 执行搜索
            search_result = self.search_engine.search(search_input)
            
            # 转换结果格式
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"图像搜索失败: {error_msg}")
            
            # 转换插件错误为自定义异常
            if "image format is illegal" in error_msg or "cannot be opened" in error_msg:
                raise InvalidMediaFormatException("图像", image_url, error_msg)
            elif "download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("图像", image_url, error_msg)
            elif "QwenIEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"图像处理失败: {error_msg}")
            else:
                raise ServiceException(f"图像搜索服务异常: {error_msg}")
    
    async def search_video(self, video_url: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """视频搜索"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 使用MMExtractor处理视频
            mm_data = MMData(video=VideoItem(video=video_url))
            result = await self.mm_extractor.forward(mm_data)
            
            # 构建搜索输入
            embeddings = []
            if result.video and result.video.video_embedding:
                embeddings.append(EmbeddingInfo(
                    label='video_embedding',
                    embedding=result.video.video_embedding
                ))
            
            search_input = SearchInput(
                text='',
                embeddings=embeddings,
                topk=top_k
            )
            
            # 执行搜索
            search_result = self.search_engine.search(search_input)
            
            # 转换结果格式
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"视频搜索失败: {error_msg}")
            
            # 转换插件错误为自定义异常
            if "Video URL download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("视频", video_url, error_msg)
            elif "QwenVEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"视频处理失败: {error_msg}")
            else:
                raise ServiceException(f"视频搜索服务异常: {error_msg}")
    
    async def search_multimodal(self, text: Optional[str] = None, 
                               image_url: Optional[str] = None,
                               video_url: Optional[str] = None,
                               top_k: int = 10) -> List[Dict[str, Any]]:
        """多模态搜索"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 构建多模态输入
            mm_data = MMData(
                text=TextItem(text=text or '') if text else None,
                image=ImageItem(image=image_url or '') if image_url else None,
                video=VideoItem(video=video_url or '') if video_url else None
            )
            
            # 使用MMExtractor处理多模态数据
            result = await self.mm_extractor.forward(mm_data)
            
            # 构建搜索输入
            embeddings = []
            search_text = text or ''
            
            # 添加所有可用的embedding
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
            
            # 执行搜索
            search_result = self.search_engine.search(search_input)
            
            # 转换结果格式
            results = []
            for item in search_result.items:
                results.append({
                    'id': str(uuid.uuid4()),
                    'text': item.text,
                    'image': item.image,
                    'video': item.video,
                    'score': item.score
                })
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"多模态搜索失败: {error_msg}")
            
            # 转换插件错误为自定义异常
            if "image format is illegal" in error_msg or "cannot be opened" in error_msg:
                raise InvalidMediaFormatException("图像", image_url or "", error_msg)
            elif "Video URL download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("视频", video_url or "", error_msg)
            elif "QwenIEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"图像处理失败: {error_msg}")
            elif "QwenVEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"视频处理失败: {error_msg}")
            else:
                raise ServiceException(f"多模态搜索服务异常: {error_msg}")
    
    async def insert_data(self, text: str = '', image_url: str = '', video_url: str = ''):
        """插入单条数据"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # 构建输入数据
            mm_data = MMData(
                text=TextItem(text=text) if text else None,
                image=ImageItem(image=image_url) if image_url else None,
                video=VideoItem(video=video_url) if video_url else None
            )
            
            # 使用MMExtractor处理数据
            result = await self.mm_extractor.forward(mm_data)
            logger.info(f"mm_extractor result: {result}")
            
            # 构建插入数据
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
                image_text = result.image.image_text
            
            if result.video and result.video.video_embedding:
                embeddings.append(EmbeddingInfo(
                    label='video_embedding',
                    embedding=result.video.video_embedding
                ))
                video_text = result.video.video_text
            insert_data = InsertData(
                text=text,
                image=image_url,
                video=video_url,
                embeddings=embeddings,
                image_text=image_text,
                video_text=video_text
            )
            
            # 执行插入
            self.search_engine.insert(insert_data)
            
            logger.info("数据插入成功")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"数据插入失败: {error_msg}")
            
            # 转换插件错误为自定义异常
            if "image format is illegal" in error_msg or "cannot be opened" in error_msg:
                raise InvalidMediaFormatException("图像", image_url, error_msg)
            elif "Video URL download error" in error_msg or "inaccessible" in error_msg:
                raise MediaDownloadException("视频", video_url, error_msg)
            elif "QwenIEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"图像处理失败: {error_msg}")
            elif "QwenVEmbedPlugin forward failed" in error_msg:
                raise MediaProcessingException(f"视频处理失败: {error_msg}")
            else:
                raise ServiceException(f"数据插入服务异常: {error_msg}")
    
    async def batch_insert_data(self, data_list: List[InsertDataRequest]) -> int:
        """批量插入数据"""
        if not self.initialized:
            await self.initialize()
        
        try:
            insert_data_list = []
            
            for data_request in data_list:
                # 构建输入数据
                mm_data = MMData(
                    text=TextItem(text=data_request.text) if data_request.text else None,
                    image=ImageItem(image=data_request.image_url) if data_request.image_url else None,
                    video=VideoItem(video=data_request.video_url) if data_request.video_url else None
                )
                
                # 使用MMExtractor处理数据
                result = await self.mm_extractor.forward(mm_data)
                
                # 构建插入数据
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
                    image_text = result.image.image_text
                if result.video and result.video.video_embedding:
                    embeddings.append(EmbeddingInfo(
                        label='video_embedding',
                        embedding=result.video.video_embedding
                    ))
                    video_text = result.video.video_text
                insert_data = InsertData(
                    text=data_request.text,
                    image=data_request.image_url,
                    video=data_request.video_url,
                    embeddings=embeddings,
                    image_text=image_text,
                    video_text=video_text
                )
                
                insert_data_list.append(insert_data)
            
            # 执行批量插入
            self.search_engine.batch_insert(insert_data_list)
            
            logger.info(f"批量插入完成，共 {len(insert_data_list)} 条数据")
            return len(insert_data_list)
            
        except Exception as e:
            logger.error(f"批量插入失败: {str(e)}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        try:
            status = {
                'initialized': self.initialized,
                'mm_extractor': self.mm_extractor is not None,
                'search_engine': self.search_engine is not None
            }
            
            # 检查搜索引擎连接状态
            if self.search_engine:
                try:
                    # 尝试执行一个简单的搜索来检查连接
                    test_search = SearchInput(text='test', embeddings=[], topk=1)
                    self.search_engine.search(test_search)
                    status['search_engine_connected'] = True
                except Exception as e:
                    status['search_engine_connected'] = False
                    status['search_engine_error'] = str(e)
            
            return status
            
        except Exception as e:
            logger.error(f"获取状态失败: {str(e)}")
            raise 