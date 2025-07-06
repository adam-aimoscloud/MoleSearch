from .aliyun import AliyunASR, AliyunASRParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO
from typing import Union

class ImplType:
    ALIYUN = 'Aliyun'.lower()


@dataclass_json
@dataclass
class ASRPluginParam(BasePluginParam):
    param: Union[AliyunASRParam, None] = field(default=None)

# 在装饰器之后重新定义from_dict方法
def _asr_from_dict(cls, config: dict) -> 'ASRPluginParam':
    instance = cls()
    instance.name = config.get('name', '')
    instance.type = config.get('type', '')
    instance.impl = config.get('impl', '')
    
    # 处理嵌套的param字段
    if 'param' in config:
        param_config = config['param']
        impl_type = instance.impl.lower()
        if impl_type == 'aliyun':
            instance.param = AliyunASRParam.from_dict(param_config)
        else:
            raise ValueError(f'Unknown ASR implementation: {instance.impl}')
    
    return instance

# 覆盖dataclass_json的from_dict方法
ASRPluginParam.from_dict = classmethod(_asr_from_dict)

_asr_impls_ = {
    ImplType.ALIYUN: AliyunASR,
}

_asr_impl_params_ = {
    ImplType.ALIYUN: AliyunASRParam,
}

@dataclass_json
@dataclass
class ASRPlugin(BasePlugin):
    def __init__(self, param: ASRPluginParam) -> None:
        super().__init__(param)
        self._impl = _asr_impls_[param.impl.lower()](param.param)

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


ASRPlugin.register_self()
ASRPluginParam.register_self()
