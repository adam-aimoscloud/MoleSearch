from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict, Any, List
from elasticsearch import AsyncElasticsearch
from ..base import BaseSearchEngine, SearchEngineParam, SearchEngineType, SearchInput, SearchOutput, InsertData, SearchOutputItem, EmbeddingInfo, ListDataOutput
import uuid
import json


@dataclass_json
@dataclass
class VectorDimensions:
    text_embedding: int = field(default=1024)
    image_embedding: int = field(default=1024)
    video_embedding: int = field(default=1024)

@dataclass_json
@dataclass
class ESParam:
    host: str = field(default='localhost')
    port: int = field(default=9200)
    index: str = field(default='mmretriever')
    username: str = field(default='')
    password: str = field(default='')
    scheme: str = field(default='http')
    timeout: int = field(default=30)
    max_retries: int = field(default=3)
    vector_dimensions: VectorDimensions = field(default_factory=VectorDimensions)
    batch_size: int = field(default=100)
    refresh_policy: str = field(default='wait_for')


class ESSearchEngine(BaseSearchEngine):
    type = SearchEngineType.ES

    def __init__(self, param: Dict[str, Any]) -> None:
        self.param = ESParam().from_dict(param)
        
        # Build ES connection
        es_config = {
            'hosts': [f"{self.param.scheme}://{self.param.host}:{self.param.port}"]
        }
        
        if self.param.username and self.param.password:
            es_config['basic_auth'] = (self.param.username, self.param.password)
        
        self.es = AsyncElasticsearch(**es_config)
        self.index_name = self.param.index
        
        # Get vector dimension configuration from parameters
        self.vector_dimensions = self.param.vector_dimensions

    async def _ensure_index(self):
        """Ensure index exists and configure correct mapping"""
        if not await self.es.indices.exists(index=self.index_name):
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
                            "dims": self.vector_dimensions.text_embedding,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "image_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.image_embedding,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "video_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.video_embedding,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "image_text_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.text_embedding,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "video_text_embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimensions.text_embedding,
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            }
            
            await self.es.indices.create(index=self.index_name, **mapping)

    async def search(self, input: SearchInput) -> SearchOutput:
        """Execute search, support text retrieval and vector retrieval mixed retrieval, unified sorting"""
        await self._ensure_index()
        
        should_queries = []
        
        # Build multi_match text retrieval (support text/image_text/video_text)
        if input.text:
            should_queries.append({
                "multi_match": {
                    "query": input.text,
                    "fields": [
                        "text^2",  # Main text weight higher
                        "image_text",
                        "video_text"
                    ],
                    "type": "best_fields"
                }
            })
        
        # Build vector retrieval (support multiple embedding fields)
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
        
        # Build final query
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
        
        # Execute search
        try:
            search_body = {
                "query": query,
                "size": input.topk,
                "_source": True
            }
            
            response = await self.es.search(
                index=self.index_name,
                **search_body
            )
            
            # Parse result
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
            print(f"ES search error: {e}")
            return SearchOutput(items=[])

    async def insert(self, data: InsertData) -> None:
        """Insert data into ES"""
        await self._ensure_index()
        
        try:
            # Build document
            doc = {
                "text": data.text,
                "image": data.image,
                "video": data.video,
                "image_text": data.image_text,
                "video_text": data.video_text
            }
            
            # Add embedding data
            for embedding_info in data.embeddings:
                if embedding_info.label and embedding_info.embedding:
                    field_name = self._get_embedding_field(embedding_info.label)
                    if field_name:
                        doc[field_name] = embedding_info.embedding
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Insert document
            await self.es.index(
                index=self.index_name,
                id=doc_id,
                document=doc
            )
            
            # Refresh index to ensure data is searchable
            await self.es.indices.refresh(index=self.index_name)
            
        except Exception as e:
            print(f"ES insert error: {e}")
            raise

    def _get_embedding_field(self, label: str) -> str:
        """Get corresponding field name based on embedding label"""
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
            # Default return text embedding field
            return 'text_embedding'

    async def batch_insert(self, data_list: List[InsertData]) -> None:
        """Batch insert data with configurable batch size"""
        await self._ensure_index()
        
        try:
            # Process data in batches according to batch_size
            for i in range(0, len(data_list), self.param.batch_size):
                batch_data = data_list[i:i + self.param.batch_size]
                actions = []
                
                for data in batch_data:
                    doc = {
                        "text": data.text,
                        "image": data.image,
                        "video": data.video,
                        "image_text": data.image_text,
                        "video_text": data.video_text
                    }
                    
                    # Add embedding data
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
                
                # Batch insert current batch
                from elasticsearch.helpers import async_bulk
                await async_bulk(
                    self.es, 
                    actions,
                    chunk_size=self.param.batch_size,
                    refresh=self.param.refresh_policy
                )
            
            # Final refresh if not using wait_for policy
            if self.param.refresh_policy != 'wait_for':
                await self.es.indices.refresh(index=self.index_name)
            
        except Exception as e:
            print(f"ES batch insert error: {e}")
            raise

    async def delete_all(self) -> None:
        """Delete all data in the index"""
        try:
            await self.es.delete_by_query(
                index=self.index_name,
                query={"match_all": {}}
            )
            await self.es.indices.refresh(index=self.index_name)
        except Exception as e:
            print(f"ES delete data error: {e}")
            raise

    async def list_data(self, page: int = 1, page_size: int = 20) -> ListDataOutput:
        """Query all data with paging"""
        await self._ensure_index()
        
        try:
            # Calculate paging parameters
            from_index = (page - 1) * page_size
            
            # Build query
            search_body = {
                "query": {"match_all": {}},
                "from": from_index,
                "size": page_size,
                "_source": True,
                "sort": [{"_id": {"order": "desc"}}]  # Sort by ID in descending order, latest data first
            }
            
            # Execute search
            response = await self.es.search(
                index=self.index_name,
                **search_body
            )
            
            # Get total
            total = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
            
            # Parse result
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
            print(f"ES query data error: {e}")
            return ListDataOutput(total=0, items=[])

    async def close(self):
        """Close the ES connection"""
        await self.es.close()


ESSearchEngine.register_self() 