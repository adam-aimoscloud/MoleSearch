from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict, Any, List
from elasticsearch import Elasticsearch
from ..base import BaseSearchEngine, SearchEngineParam, SearchEngineType, SearchInput, SearchOutput, InsertData, SearchOutputItem, EmbeddingInfo, ListDataOutput
import uuid
import json


@dataclass_json
@dataclass
class ESParam:
    host: str = field(default='localhost')
    port: int = field(default=9200)
    index: str = field(default='mmretriever')
    username: str = field(default='')
    password: str = field(default='')
    scheme: str = field(default='http')


class ESSearchEngine(BaseSearchEngine):
    type = SearchEngineType.ES

    def __init__(self, param: Dict[str, Any]) -> None:
        self.param = ESParam().from_dict(param)
        
        # 构建ES连接
        es_config = {
            'hosts': [f"{self.param.scheme}://{self.param.host}:{self.param.port}"]
        }
        
        if self.param.username and self.param.password:
            es_config['basic_auth'] = (self.param.username, self.param.password)
        
        self.es = Elasticsearch(**es_config)
        self.index_name = self.param.index
        
        # 从参数中获取向量维度配置
        self.vector_dimensions = param.get('vector_dimensions', {
            'text_embedding': 1024,
            'image_embedding': 1024,
            'video_embedding': 1024,
            'image_text_embedding': 1024,
            'video_text_embedding': 1024
        })
        
        # 确保索引存在并配置mapping
        self._ensure_index()

    def _ensure_index(self):
        """确保索引存在并配置正确的mapping"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "image": {
                            "type": "keyword"
                        },
                        "video": {
                            "type": "keyword"
                        },
                        "image_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "video_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "text_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.get('text_embedding', 1024),
                            "index": True,
                            "similarity": "cosine"
                        },
                        "image_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.get('image_embedding', 1024),
                            "index": True,
                            "similarity": "cosine"
                        },
                        "video_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.get('video_embedding', 1024),
                            "index": True,
                            "similarity": "cosine"
                        },
                        "image_text_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.get('image_text_embedding', 1024),
                            "index": True,
                            "similarity": "cosine"
                        },
                        "video_text_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.get('video_text_embedding', 1024),
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, **mapping)

    def search(self, input: SearchInput) -> SearchOutput:
        """执行搜索，支持文本检索和向量检索混合召回，统一排序"""
        should_queries = []
        
        # 构建multi_match文本检索（支持text/image_text/video_text）
        if input.text:
            should_queries.append({
                "multi_match": {
                    "query": input.text,
                    "fields": [
                        "text^2",  # 主文本权重更高
                        "image_text",
                        "video_text"
                    ],
                    "type": "best_fields"
                }
            })
        
        # 构建向量检索（支持多embedding字段）
        for embedding_info in input.embeddings:
            if embedding_info.label and embedding_info.embedding:
                field_name = self._get_embedding_field(embedding_info.label)
                if field_name:
                    should_queries.append({
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": f"cosineSimilarity(params.query_vector, '{field_name}') + 1.0",
                                "params": {
                                    "query_vector": embedding_info.embedding
                                }
                            }
                        }
                    })
        
        # 构建最终查询
        if not should_queries:
            query = {"match_all": {}}
        elif len(should_queries) == 1:
            query = should_queries[0]
        else:
            query = {
                "bool": {
                    "should": should_queries,
                    "minimum_should_match": 1
                }
            }
        
        # 执行搜索
        try:
            search_body = {
                "query": query,
                "size": input.topk,
                "_source": True
            }
            
            response = self.es.search(
                index=self.index_name,
                **search_body
            )
            
            # 解析结果
            items = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                item = SearchOutputItem(
                    text=source.get('text', ''),
                    image=source.get('image', ''),
                    video=source.get('video', ''),
                    image_text=source.get('image_text', ''),
                    video_text=source.get('video_text', ''),
                    score=hit['_score']
                )
                items.append(item)
            
            return SearchOutput(items=items)
            
        except Exception as e:
            print(f"ES搜索错误: {e}")
            return SearchOutput(items=[])

    def insert(self, data: InsertData) -> None:
        """插入数据到ES"""
        try:
            # 构建文档
            doc = {
                "text": data.text,
                "image": data.image,
                "video": data.video,
                "image_text": data.image_text,
                "video_text": data.video_text
            }
            
            # 添加embedding数据
            for embedding_info in data.embeddings:
                if embedding_info.label and embedding_info.embedding:
                    field_name = self._get_embedding_field(embedding_info.label)
                    if field_name:
                        doc[field_name] = embedding_info.embedding
            
            # 生成文档ID
            doc_id = str(uuid.uuid4())
            
            # 插入文档
            self.es.index(
                index=self.index_name,
                id=doc_id,
                document=doc
            )
            
            # 刷新索引以确保数据可搜索
            self.es.indices.refresh(index=self.index_name)
            
        except Exception as e:
            print(f"ES插入错误: {e}")
            raise

    def _get_embedding_field(self, label: str) -> str:
        """根据embedding标签获取对应的字段名"""
        label_lower = label.lower()
        if 'text' in label_lower or 'tembed' in label_lower:
            return 'text_embedding'
        elif 'image' in label_lower or 'img' in label_lower or 'iembed' in label_lower:
            return 'image_embedding'
        elif 'video' in label_lower or 'vid' in label_lower or 'vembed' in label_lower:
            return 'video_embedding'
        elif 'image_text' in label_lower or 'img_text' in label_lower:
            return 'image_text_embedding'
        elif 'video_text' in label_lower or 'vid_text' in label_lower:
            return 'video_text_embedding'
        else:
            # 默认返回文本embedding字段
            return 'text_embedding'

    def batch_insert(self, data_list: List[InsertData]) -> None:
        """批量插入数据"""
        try:
            actions = []
            for data in data_list:
                doc = {
                    "text": data.text,
                    "image": data.image,
                    "video": data.video,
                    "image_text": data.image_text,
                    "video_text": data.video_text
                }
                
                # 添加embedding数据
                for embedding_info in data.embeddings:
                    if embedding_info.label and embedding_info.embedding:
                        field_name = self._get_embedding_field(embedding_info.label)
                        if field_name:
                            doc[field_name] = embedding_info.embedding
                
                action = {
                    "_index": self.index_name,
                    "_id": str(uuid.uuid4()),
                    "_source": doc
                }
                actions.append(action)
            
            # 批量插入
            from elasticsearch.helpers import bulk
            bulk(self.es, actions)
            
            # 刷新索引
            self.es.indices.refresh(index=self.index_name)
            
        except Exception as e:
            print(f"ES批量插入错误: {e}")
            raise

    def delete_all(self) -> None:
        """删除索引中的所有数据"""
        try:
            self.es.delete_by_query(
                index=self.index_name,
                query={"match_all": {}}
            )
            self.es.indices.refresh(index=self.index_name)
        except Exception as e:
            print(f"ES删除数据错误: {e}")
            raise

    def list_data(self, page: int = 1, page_size: int = 20) -> ListDataOutput:
        """分页查询全量数据"""
        try:
            # 计算分页参数
            from_index = (page - 1) * page_size
            
            # 构建查询
            search_body = {
                "query": {"match_all": {}},
                "from": from_index,
                "size": page_size,
                "_source": True,
                "sort": [{"_id": {"order": "desc"}}]  # 按ID倒序，最新数据在前
            }
            
            # 执行搜索
            response = self.es.search(
                index=self.index_name,
                **search_body
            )
            
            # 获取总数
            total = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
            
            # 解析结果
            items = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                item = SearchOutputItem(
                    text=source.get('text', ''),
                    image=source.get('image', ''),
                    video=source.get('video', ''),
                    image_text=source.get('image_text', ''),
                    video_text=source.get('video_text', ''),
                    score=hit['_score']
                )
                items.append(item)
            
            return ListDataOutput(total=total, items=items)
            
        except Exception as e:
            print(f"ES查询数据错误: {e}")
            return ListDataOutput(total=0, items=[])


ESSearchEngine.register_self()