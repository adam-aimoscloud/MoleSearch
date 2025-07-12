from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Any, Dict


_impls_ = {}


class SearchEngineType:
    ABSTRACT = 'abstract'
    ES = 'es'

@dataclass_json
@dataclass
class SearchEngineParam:
    type: SearchEngineType = field(default=SearchEngineType.ES)
    param: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class EmbeddingInfo:
    label: str = field(default='')
    embedding: List[float] = field(default_factory=list)


@dataclass_json
@dataclass
class SearchInput:
    text: str = field(default='')
    embeddings: List[EmbeddingInfo] = field(default_factory=list)
    topk: int = field(default=10)


@dataclass_json
@dataclass
class SearchOutputItem:
    text: str = field(default='')
    image: str = field(default='')
    video: str = field(default='')
    image_text: str = field(default='')
    video_text: str = field(default='')
    score: float = field(default=0.0)


@dataclass_json
@dataclass
class SearchOutput:
    items: List[SearchOutputItem] = field(default_factory=list)


@dataclass_json
@dataclass
class InsertData:
    text: str = field(default='')
    image: str = field(default='')
    video: str = field(default='')
    embeddings: List[EmbeddingInfo] = field(default_factory=list)
    image_text: str = field(default='')
    video_text: str = field(default='')


@dataclass_json
@dataclass
class ListDataOutput:
    total: int = field(default=0)
    items: List[SearchOutputItem] = field(default_factory=list)


class BaseSearchEngine(object):
    type = SearchEngineType.ABSTRACT
    def __init__(self, param: Dict[str, Any]) -> None:
        self.param = param

    async def search(self, input: SearchInput) -> SearchOutput:
        pass

    async def insert(self, data: InsertData) -> None:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement insert method')
    
    async def batch_insert(self, data_list: List[InsertData]) -> None:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement batch_insert method')
    
    async def list_data(self, page: int = 1, page_size: int = 20) -> ListDataOutput:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement list_data method')
    
    async def close(self) -> None:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement close method')
    
    @classmethod
    def register_self(cls) -> None:
        _impls_[cls.type] = cls


class SearchEngineFactory(object):
    def __init__(self, param: SearchEngineParam) -> None:
        self.param = param

    def get_search_engine(self) -> BaseSearchEngine:
        return _impls_[self.param.type](self.param.param)
