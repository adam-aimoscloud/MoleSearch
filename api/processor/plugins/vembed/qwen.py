from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from http import HTTPStatus
from .base import BaseVEmbed, BaseVEmbedParam
from ...core import DataIO
from ...utils.async_dashscope import AsyncDashScope


@dataclass_json
@dataclass
class QwenVEmbedParam(BaseVEmbedParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')
    dimension: int = field(default=1024)


@dataclass_json
@dataclass
class QwenVEmbed(BaseVEmbed):
    def __init__(self, param: QwenVEmbedParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        """异步视频嵌入"""
        try:
            output = await AsyncDashScope.multimodal_embedding(
                model=self.param.model,
                input_data=[{'video': input.video}],
                api_key=self.param.api_key,
                dimension=self.param.dimension,
            )
            
            return DataIO(
                embeddings=[item['embedding'] for item in output['embeddings']],
            )
        except Exception as e:
            # Improve error message, provide more context
            if "download" in str(e).lower():
                raise Exception(f'QwenVEmbedPlugin forward failed: Video URL download error - {input.video} may be inaccessible')
            else:
                raise Exception(f'QwenVEmbedPlugin forward failed: {str(e)}')
    
