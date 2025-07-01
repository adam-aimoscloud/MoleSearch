from .qwen import QwenIEmbed, QwenIEmbedParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class IEmbedPluginParam(BasePluginParam):
    param: QwenIEmbedParam = field(default=None)

_iembed_impls_ = {
    ImplType.QWEN: QwenIEmbed,
}

_iembed_impl_params_ = {
    ImplType.QWEN: QwenIEmbedParam,
}

@dataclass_json
@dataclass
class IEmbedPlugin(BasePlugin):
    def __init__(self, param: IEmbedPluginParam) -> None:
        super().__init__(param)
        self._impl = _iembed_impls_[param.impl.lower()](_iembed_impl_params_[param.impl.lower()]().from_dict(param.param))

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


IEmbedPlugin.register_self()
IEmbedPluginParam.register_self()