from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseTEmbed, BaseTEmbedParam
from ...core import DataIO


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
        rsp = dashscope.TextEmbedding.call(
            model=self.param.model,
            input=input.text,
            api_key=self.param.api_key,
        )
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'QwenTEmbedPlugin forward failed: {error_msg}')
        return DataIO(
            embeddings=[item['embedding'] for item in rsp.output['embeddings']],
        )
