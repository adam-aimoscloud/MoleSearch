from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam


@dataclass_json
@dataclass
class BaseIEmbedPluginParam(BasePluginParam):
    pass


@dataclass_json
@dataclass
class BaseIEmbedPlugin(BasePlugin):
    def __init__(self, param: BaseIEmbedPluginParam) -> None:
        super().__init__(param)
        self.param = param