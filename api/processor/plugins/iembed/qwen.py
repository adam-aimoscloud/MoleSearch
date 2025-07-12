from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from http import HTTPStatus
from .base import BaseIEmbed, BaseIEmbedParam
from ...core import DataIO
from ...utils.async_dashscope import AsyncDashScope


@dataclass_json
@dataclass
class QwenIEmbedParam(BaseIEmbedParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')
    dimension: int = field(default=1024)


@dataclass_json
@dataclass
class QwenIEmbed(BaseIEmbed):
    def __init__(self, param: QwenIEmbedParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        """异步图像嵌入"""
        output = await AsyncDashScope.multimodal_embedding(
            model=self.param.model,
            input_data=[{'image': input.image}],
            api_key=self.param.api_key,
            dimension=self.param.dimension,
        )
        
        return DataIO(
            embeddings=[item['embedding'] for item in output['embeddings']],
        )
