from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict
from .data import DataIO


__plugins__ = {}
__plugin_params__ = {}


@dataclass_json
@dataclass
class BasePluginParam:
    name: str = field(default='')
    type: str = field(default='')
    impl: str = field(default='')

    @classmethod
    def register_self(cls) -> None:
        if cls.__name__ in __plugin_params__:
            raise ValueError(f'{cls.__name__} already exists')
        __plugin_params__[cls.__name__] = cls
    

class BasePlugin(object):
    def __init__(self, param: BasePluginParam) -> None:
        self.param = param

    async def forward(self, input: DataIO) -> DataIO:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement forward method')
    
    @classmethod
    def register_self(cls) -> None:
        if cls.__name__ in __plugins__:
            raise ValueError(f'{cls.__name__} already exists')
        __plugins__[cls.__name__] = cls
    
def get_registered_plugins() -> Dict[str, BasePlugin]:
    return __plugins__

def get_registered_plugin_params() -> Dict[str, BasePluginParam]:
    return __plugin_params__
