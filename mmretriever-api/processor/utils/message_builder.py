from typing import List, Union, Dict, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


class Role:
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


class OpenAIContentType:
    TEXT = 'text'
    IMAGE_URL = 'image_url'


@dataclass_json
@dataclass
class DashscopeMessageContent:
    text: str = field(default=None)
    image: str = field(default=None)


@dataclass_json
@dataclass
class OpenAIImageURL:
    url: str = field(default=None)


@dataclass_json
@dataclass
class OpenAIMessageContent:
    type: OpenAIContentType = field(default=OpenAIContentType.TEXT)
    text: str = field(default=None)
    image: OpenAIImageURL = field(default=None)


@dataclass_json
@dataclass
class Message:
    role: str = field(default='')
    content: List[Union[OpenAIMessageContent, DashscopeMessageContent]] = field(default_factory=list)


class MessageBuilder:

    @classmethod
    def build_dashscope_vlm_message(cls, image_url: str, prompt: str = None) -> List[Dict[str, Any]]:
        system_msg = Message(
            role=Role.SYSTEM,
            content=DashscopeMessageContent(
                text=prompt,
            ),
        ).to_dict() if prompt else None
        user_msg = Message(
            role=Role.USER,
            content=DashscopeMessageContent(
                image=image_url,
            ),
        ).to_dict()
        return [system_msg, user_msg] if system_msg else [user_msg]
