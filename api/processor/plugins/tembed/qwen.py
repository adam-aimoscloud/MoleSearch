from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from http import HTTPStatus
from .base import BaseTEmbed, BaseTEmbedParam
from ...core import DataIO
from ...utils.async_dashscope import AsyncDashScope


@dataclass_json
@dataclass
class QwenTEmbedParam(BaseTEmbedParam):
    api_key: str = field(default='')
    model: str = field(default='text-embedding-v4')


@dataclass_json
@dataclass
class QwenTEmbed(BaseTEmbed):
    def __init__(self, param: QwenTEmbedParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        """异步文本嵌入"""
        output = await AsyncDashScope.text_embedding(
            model=self.param.model,
            input_text=input.text,
            api_key=self.param.api_key,
        )
        
        return DataIO(
            embeddings=[item['embedding'] for item in output['embeddings']],
        )
