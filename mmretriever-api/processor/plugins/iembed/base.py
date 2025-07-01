from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import DataIO


@dataclass_json
@dataclass
class BaseIEmbedParam:
    pass


@dataclass_json
@dataclass
class BaseIEmbed:
    def __init__(self, param: BaseIEmbedParam) -> None:
        self.param = param

    def forward(self, input: DataIO) -> DataIO:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement forward method')