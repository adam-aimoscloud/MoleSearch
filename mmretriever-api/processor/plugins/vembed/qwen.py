from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseVEmbedPlugin, BaseVEmbedPluginParam
from ...core import DataIO


@dataclass_json
@dataclass
class QwenVEmbedPluginParam(BaseVEmbedPluginParam):
    api_key: str = field(default='')
    model: str = field(default='multimodal-embedding-v1')


@dataclass_json
@dataclass
class QwenVEmbedPlugin(BaseVEmbedPlugin):
    def __init__(self, param: QwenVEmbedPluginParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        rsp = dashscope.MultiModalEmbedding.call(
            model=self.param.model,
            input=input.video,
            api_key=self.param.api_key,
        )
        if rsp.status_code != HTTPStatus.OK:
                raise Exception(f'QwenVEmbedPlugin forward failed: {rsp.text}')
        return DataIO(
            embeddings=rsp.output.embeddings,
        )
    
QwenVEmbedPlugin.register_self()
QwenVEmbedPluginParam.register_self()
