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

# Redefine from_dict method after decorator
def _pipeline_from_dict(cls, config: Dict[str, Any]) -> 'PipelineParam':
    instance = cls()
    instance.name = config['name']
    instance.type = config['type']
    instance.enable = config.get('enable', False)
    instance.plugins = {}
    
    for name, param in config['plugins'].items():
        plugin_param_class = get_registered_plugin_params()[name]
        plugin_param_instance = plugin_param_class.from_dict(param)
        instance.plugins[name] = plugin_param_instance
    return instance

# Override dataclass_json's from_dict method
PipelineParam.from_dict = classmethod(_pipeline_from_dict)

    
def get_plugin_param(self, name: str) -> BasePluginParam:
    return self.plugins[name]

# Add get_plugin_param method to PipelineParam class
PipelineParam.get_plugin_param = get_plugin_param


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
    