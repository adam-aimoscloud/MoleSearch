from .qwen import QwenVEmbed, QwenVEmbedParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO
from typing import Union

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class VEmbedPluginParam(BasePluginParam):
    param: Union[QwenVEmbedParam, None] = field(default=None)

_vembed_impls_ = {
    ImplType.QWEN: QwenVEmbed,
}

_vembed_impl_params_ = {
    ImplType.QWEN: QwenVEmbedParam,
}

@dataclass_json
@dataclass
class VEmbedPlugin(BasePlugin):
    def __init__(self, param: VEmbedPluginParam) -> None:
        super().__init__(param)
        self._impl = _vembed_impls_[param.impl.lower()](_vembed_impl_params_[param.impl.lower()]().from_dict(param.param))

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


VEmbedPlugin.register_self()
VEmbedPluginParam.register_self()
