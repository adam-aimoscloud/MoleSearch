from .qwen import QwenTEmbed, QwenTEmbedParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class TEmbedPluginParam(BasePluginParam):
    param: QwenTEmbedParam = field(default=None)

_tembed_impls_ = {
    ImplType.QWEN: QwenTEmbed,
}

_tembed_impl_params_ = {
    ImplType.QWEN: QwenTEmbedParam,
}

@dataclass_json
@dataclass
class TEmbedPlugin(BasePlugin):
    def __init__(self, param: TEmbedPluginParam) -> None:
        super().__init__(param)
        self._impl = _tembed_impls_[param.impl.lower()](_tembed_impl_params_[param.impl.lower()]().from_dict(param.param))

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


TEmbedPlugin.register_self()
TEmbedPluginParam.register_self()
