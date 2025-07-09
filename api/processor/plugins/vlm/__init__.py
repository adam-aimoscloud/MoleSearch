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

# Redefine from_dict method after decorator
def _vlm_from_dict(cls, config: dict) -> 'VLMPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # Process nested param field
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'qwen':
            instance.param = QwenVLMParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown VLMPlugin implementation: {instance.impl}')
    
    return instance

# Override dataclass_json's from_dict method
VLMPluginParam.from_dict = classmethod(_vlm_from_dict)

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
