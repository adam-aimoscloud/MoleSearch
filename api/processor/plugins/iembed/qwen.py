from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseIEmbed, BaseIEmbedParam
from ...core import DataIO


@dataclass_json
@dataclass
class QwenIEmbedParam(BaseIEmbedParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')


@dataclass_json
@dataclass
class QwenIEmbed(BaseIEmbed):
    def __init__(self, param: QwenIEmbedParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        rsp = dashscope.MultiModalEmbedding.call(
            model=self.param.model,
            input=[{'image': input.image}],
            api_key=self.param.api_key,
        )
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'QwenIEmbedPlugin forward failed: {error_msg}')
        return DataIO(
            embeddings=[item['embedding'] for item in rsp.output['embeddings']],
        )
