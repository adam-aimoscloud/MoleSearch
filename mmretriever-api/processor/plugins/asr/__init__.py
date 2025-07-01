from .aliyun import AliyunASR, AliyunASRParam
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam, DataIO

class ImplType:
    ALIYUN = 'Aliyun'.lower()


@dataclass_json
@dataclass
class ASRPluginParam(BasePluginParam):
    param: AliyunASRParam = field(default=None)

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
        self._impl = _asr_impls_[param.impl.lower()](_asr_impl_params_[param.impl.lower()]().from_dict(param.param))

    def forward(self, input: DataIO) -> DataIO:
        return self._impl.forward(input)


ASRPlugin.register_self()
ASRPluginParam.register_self()
