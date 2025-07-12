from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from http import HTTPStatus
from .base import BaseVLM, BaseVLMParam
from ...core import DataIO
from ...utils.message_builder import MessageBuilder
from ...utils.async_dashscope import AsyncDashScope


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
        """异步视觉语言模型"""
        prompt = self.load_prompt()
        messages = MessageBuilder.build_dashscope_vlm_message(
            image_url=input.image,
            prompt=prompt,
        )
        
        output = await AsyncDashScope.multimodal_conversation(
            api_key=self.param.api_key,
            model=self.param.model,
            messages=messages,
            stream=False,
        )
        
        return DataIO(
            text=output['choices'][0]['message']['content'][0]['text'],
        )
