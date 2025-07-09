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
        messages = []
        
        if prompt:
            messages.append({
                'role': Role.SYSTEM,
                'content': [{'text': prompt}]
            })
        
        messages.append({
            'role': Role.USER,
            'content': [{'image': image_url}]
        })
        
        return messages
