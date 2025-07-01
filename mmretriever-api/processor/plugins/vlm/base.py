from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam


@dataclass_json
@dataclass
class BaseVLMParam(BasePluginParam):
    pass


@dataclass_json
@dataclass
class BaseVLM(BasePlugin):
    def __init__(self, param: BaseVLMParam) -> None:
        super().__init__(param)
        self.param = param