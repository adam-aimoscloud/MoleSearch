from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


Embedding = List[float]


@dataclass_json
@dataclass
class TextItem:
    text: str = field(default='')
    text_embeddings: List[Embedding] = field(default_factory=list)


@dataclass_json
@dataclass
class ImageItem:
    image: str = field(default='')
    image_embedding: Embedding = field(default=None)
    text: str = field(default='')
    text_embeddings: List[Embedding] = field(default_factory=list)


@dataclass_json
@dataclass
class VideoItem:
    video: str = field(default='')
    video_embedding: Embedding = field(default=None)
    text: str = field(default='')
    text_embeddings: List[Embedding] = field(default_factory=list)


@dataclass_json
@dataclass
class MMData:
    text: TextItem = field(default=None)
    image: ImageItem = field(default=None)
    video: VideoItem = field(default=None)


@dataclass_json
@dataclass
class DataIO:
    text: str = field(default='')
    image: str = field(default='')
    video: str = field(default='')
    embeddings: List[Embedding] = field(default_factory=list)
