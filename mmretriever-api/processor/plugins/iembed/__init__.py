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

# 在装饰器之后重新定义from_dict方法
def _iembed_from_dict(cls, config: dict) -> 'IEmbedPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # 处理嵌套的param字段
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'qwen':
            instance.param = QwenIEmbedParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown IEmbedPlugin implementation: {instance.impl}')
    
    return instance

# 覆盖dataclass_json的from_dict方法
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