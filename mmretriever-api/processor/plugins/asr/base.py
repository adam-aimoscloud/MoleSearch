from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam


@dataclass_json
@dataclass
class BaseASRPluginParam(BasePluginParam):
    pass


@dataclass_json
@dataclass
class BaseASRPlugin(BasePlugin):
    def __init__(self, param: BaseASRPluginParam) -> None:
        super().__init__(param)
        self.param = param