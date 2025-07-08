from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from http import HTTPStatus
from .base import BaseASR, BaseASRParam
from ...core import DataIO
from ...utils.audio_extractor import AudioExtractor
from dashscope.audio.asr import Recognition


@dataclass_json
@dataclass
class AliyunASRParam(BaseASRParam):
    oss_access_key_id: str = field(default='')
    oss_access_key_secret: str = field(default='')
    oss_endpoint: str = field(default='')
    oss_bucket_name: str = field(default='')
    model: str = field(default='')
    api_key: str = field(default='paraformer-realtime-v2')
    audio_prefix: str = field(default='audio_')


@dataclass_json
@dataclass
class AliyunASR(BaseASR):
    def __init__(self, param: AliyunASRParam) -> None:
        super().__init__(param)

    async def forward(self, input: DataIO) -> DataIO:
        try:
            audio_url = AudioExtractor(
                oss_access_key_id=self.param.oss_access_key_id,
                oss_access_key_secret=self.param.oss_access_key_secret,
                oss_endpoint=self.param.oss_endpoint,
                oss_bucket_name=self.param.oss_bucket_name,
            ).extract_audio(
                video_url=input.video,
                audio_prefix=self.param.audio_prefix,
            )
            recognition = Recognition(model=self.param.model,
                              format='wav',
                              sample_rate=16000,
                              # "language_hints" only support paraformer-realtime-v2 model
                              language_hints=['zh', 'en'],
                              callback=None)
            result = recognition.call(audio_url)
            if result.status_code != HTTPStatus.OK:
                print(f'Warning: ASR failed but continuing: {result.text}')
                return DataIO(text='')  # Return empty text instead of throwing an exception
            return DataIO(
                text=result.output.text if hasattr(result.output, 'text') else '',
            )
        except Exception as e:
            # Return empty text when ASR fails, without interrupting the entire process
            print(f'Warning: ASR processing failed, returning empty text: {e}')
            return DataIO(text='')
