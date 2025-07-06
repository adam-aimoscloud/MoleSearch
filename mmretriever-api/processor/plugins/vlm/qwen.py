from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import dashscope
from http import HTTPStatus
from .base import BaseVLM, BaseVLMParam
from ...core import DataIO
from ...utils.message_builder import MessageBuilder


@dataclass_json
@dataclass
class QwenVLMParam(BaseVLMParam):
    api_key: str = field(default='')
    model: str = field(default='qwen-vl-max-latest')
    prompt_path: str = field(default='qwen_vlm_prompt.txt')


@dataclass_json
@dataclass
class QwenVLM(BaseVLM):
    def __init__(self, param: QwenVLMParam) -> None:
        super().__init__(param)

    def load_prompt(self) -> str:
        with open(self.param.prompt_path, 'r') as f:
            return f.read()

    async def forward(self, input: DataIO) -> DataIO:
        prompt = self.load_prompt()
        messages = MessageBuilder.build_dashscope_vlm_message(
            image_url=input.image,
            prompt=prompt,
        )
        rsp = dashscope.MultiModalConversation.call(
            api_key=self.param.api_key,
            model=self.param.model,
            messages=messages,
            stream=False,
        )
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'QwenVLM forward failed: {error_msg}')
        return DataIO(
            text=rsp.output['choices'][0]['message']['content'][0]['text'],
        )
