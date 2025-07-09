from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import DataIO


@dataclass_json
@dataclass
class BaseVEmbedParam:
    pass


@dataclass_json
@dataclass
class BaseVEmbed:
    def __init__(self, param: BaseVEmbedParam) -> None:
        self.param = param

    def forward(self, input: DataIO) -> DataIO:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement forward method')