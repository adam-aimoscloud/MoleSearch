from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseVEmbed, BaseVEmbedParam
from ...core import DataIO


@dataclass_json
@dataclass
class QwenVEmbedParam(BaseVEmbedParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')


@dataclass_json
@dataclass
class QwenVEmbed(BaseVEmbed):
    def __init__(self, param: QwenVEmbedParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        try:
            rsp = dashscope.MultiModalEmbedding.call(
                model=self.param.model,
                input=[{'video': input.video}],
                api_key=self.param.api_key,
            )
            if rsp.status_code != HTTPStatus.OK:
                error_msg = getattr(rsp, 'message', str(rsp))
                raise Exception(f'QwenVEmbedPlugin forward failed: {error_msg}')
            return DataIO(
                embeddings=[item['embedding'] for item in rsp.output['embeddings']],
            )
        except Exception as e:
            # 改善错误消息，提供更多上下文
            if "download" in str(e).lower():
                raise Exception(f'QwenVEmbedPlugin forward failed: Video URL download error - {input.video} may be inaccessible')
            else:
                raise Exception(f'QwenVEmbedPlugin forward failed: {str(e)}')
    
