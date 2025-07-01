from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict, Any
from .plugin import BasePluginParam, BasePlugin, get_registered_plugin_params, get_registered_plugins
from .data import MMData


__pipelines__ = {}


@dataclass_json
@dataclass
class PipelineParam:
    name: str = field(default='')
    type: str = field(default='')
    enable: bool = field(default=False)
    plugins: Dict[str, BasePluginParam] = field(default_factory=dict)

    @classmethod
    def from_dict(self, config: Dict[str, Any]) -> 'PipelineParam':
        self.name = config['name']
        self.type = config['type']
        self.enable = config.get('enable', False)
        self.plugins = {}
        for name, param in config['plugins'].items():
            self.plugins[name] = get_registered_plugin_params()[name]().from_dict(param)
        return self
    
    def get_plugin_param(self, name: str) -> BasePluginParam:
        return self.plugins[name]


class Pipeline(object):
    def __init__(self, param: PipelineParam) -> None:
        self.param = param

    def forward(self, input: MMData) -> MMData:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement forward method')
    
    @classmethod
    def register_self(cls) -> None:
        if cls.__name__ in __pipelines__:
            raise ValueError(f'{cls.__name__} already exists')
        __pipelines__[cls.__name__] = cls

    
def get_registered_pipelines() -> Dict[str, Pipeline]:
    return __pipelines__
    