from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import BasePlugin, BasePluginParam


@dataclass_json
@dataclass
class BaseTEmbedPluginParam(BasePluginParam):
    pass


@dataclass_json
@dataclass
class BaseTEmbedPlugin(BasePlugin):
    def __init__(self, param: BaseTEmbedPluginParam) -> None:
        super().__init__(param)
        self.param = param