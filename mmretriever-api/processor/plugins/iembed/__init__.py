from typing import Union
from .qwen import QwenIEmbed, QwenIEmbedParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class IEmbedPluginParam(BasePluginParam):
    param: Union[QwenIEmbedParam, None] = field(default=None)

# Redefine from_dict method after decorator
def _iembed_from_dict(cls, config: dict) -> 'IEmbedPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # Process nested param field
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'qwen':
            instance.param = QwenIEmbedParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown IEmbedPlugin implementation: {instance.impl}')
    
    return instance

# Override dataclass_json's from_dict method
IEmbedPluginParam.from_dict = classmethod(_iembed_from_dict)

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