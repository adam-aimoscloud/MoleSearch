from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from ...core import DataIO


@dataclass_json
@dataclass
class BaseTEmbedParam:
    pass


@dataclass_json
@dataclass
class BaseTEmbed:
    def __init__(self, param: BaseTEmbedParam) -> None:
        self.param = param

    def forward(self, input: DataIO) -> DataIO:
        raise NotImplementedError(f'{self.__class__.__name__} does not implement forward method')