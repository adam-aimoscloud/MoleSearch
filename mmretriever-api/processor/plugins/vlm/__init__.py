from .qwen import QwenVLM, QwenVLMParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO
from typing import Union

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class VLMPluginParam(BasePluginParam):
    param: Union[QwenVLMParam, None] = field(default=None)

_vlm_impls_ = {
    ImplType.QWEN: QwenVLM,
}

_vlm_impl_params_ = {
    ImplType.QWEN: QwenVLMParam,
}

@dataclass_json
@dataclass
class VLMPlugin(BasePlugin):
    def __init__(self, param: VLMPluginParam) -> None:
        super().__init__(param)
        self._impl = _vlm_impls_[param.impl.lower()](_vlm_impl_params_[param.impl.lower()]().from_dict(param.param))

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


VLMPlugin.register_self()
VLMPluginParam.register_self()
