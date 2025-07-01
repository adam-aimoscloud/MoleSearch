from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseIEmbedPlugin, BaseIEmbedPluginParam
from ...core import DataIO


@dataclass_json
@dataclass
class QwenIEmbedPluginParam(BaseIEmbedPluginParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')


@dataclass_json
@dataclass
class QwenIEmbedPlugin(BaseIEmbedPlugin):
    def __init__(self, param: QwenIEmbedPluginParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        rsp = dashscope.MultiModalEmbedding.call(
            model=self.param.model,
            input=input.image,
            api_key=self.param.api_key,
        )
        if rsp.status_code != HTTPStatus.OK:
            raise Exception(f'QwenIEmbedPlugin forward failed: {rsp.text}')
        return DataIO(
            embeddings=rsp.output.embeddings,
        )
    
QwenIEmbedPlugin.register_self()
QwenIEmbedPluginParam.register_self()
