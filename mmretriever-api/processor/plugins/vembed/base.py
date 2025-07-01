from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam


@dataclass_json
@dataclass
class BaseVEmbedPluginParam(BasePluginParam):
    pass


@dataclass_json
@dataclass
class BaseVEmbedPlugin(BasePlugin):
    def __init__(self, param: BaseVEmbedPluginParam) -> None:
        super().__init__(param)
        self.param = param