from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseTEmbedPlugin, BaseTEmbedPluginParam
from ...core import DataIO


@dataclass_json
@dataclass
class QwenTEmbedPluginParam(BaseTEmbedPluginParam):
    api_key: str = field(default='')
    model: str = field(default='text-embedding-v4')


@dataclass_json
@dataclass
class QwenTEmbedPlugin(BaseTEmbedPlugin):
    def __init__(self, param: QwenTEmbedPluginParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        rsp = dashscope.TextEmbedding.call(
            model=self.param.model,
            input=input.text,
            api_key=self.param.api_key,
        )
        if rsp.status_code != HTTPStatus.OK:
            raise Exception(f'QwenTEmbedPlugin forward failed: {rsp.text}')
        return DataIO(
            embeddings=rsp.output.embeddings,
        )
    
QwenTEmbedPlugin.register_self()
QwenTEmbedPluginParam.register_self()
