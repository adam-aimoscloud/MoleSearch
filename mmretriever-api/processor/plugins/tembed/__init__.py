from .qwen import QwenTEmbed, QwenTEmbedParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO
from typing import Union

class ImplType:
    QWEN = 'Qwen'.lower()


@dataclass_json
@dataclass
class TEmbedPluginParam(BasePluginParam):
    param: Union[QwenTEmbedParam, None] = field(default=None)

# Redefine from_dict method after decorator
def _tembed_from_dict(cls, config: dict) -> 'TEmbedPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # Process nested param field
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'qwen':
            instance.param = QwenTEmbedParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown TEmbedPlugin implementation: {instance.impl}')
    
    return instance

# Override dataclass_json's from_dict method
TEmbedPluginParam.from_dict = classmethod(_tembed_from_dict)

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
