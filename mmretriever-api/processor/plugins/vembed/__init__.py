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

# Redefine from_dict method after decorator
def _vembed_from_dict(cls, config: dict) -> 'VEmbedPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # Process nested param field
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'qwen':
            instance.param = QwenVEmbedParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown VEmbedPlugin implementation: {instance.impl}')
    
    return instance

# Override dataclass_json's from_dict method
VEmbedPluginParam.from_dict = classmethod(_vembed_from_dict)

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
