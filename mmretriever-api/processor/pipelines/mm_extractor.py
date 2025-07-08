from ..core import Pipeline, PipelineParam, DataIO, MMData, TextItem, ImageItem, VideoItem
from ..plugins import *


class MMExtractor(Pipeline):
    def __init__(self, param: PipelineParam) -> None:
        super().__init__(param)
        self.asr = ASRPlugin(param.get_plugin_param(ASRPluginParam.__name__))
        self.tembed = TEmbedPlugin(param.get_plugin_param(TEmbedPluginParam.__name__))
        self.iembed = IEmbedPlugin(param.get_plugin_param(IEmbedPluginParam.__name__))
        self.vembed = VEmbedPlugin(param.get_plugin_param(VEmbedPluginParam.__name__))
        self.vlm = VLMPlugin(param.get_plugin_param(VLMPluginParam.__name__))

    async def forward(self, input: MMData) -> MMData:
        output = MMData()
        output.text = TextItem() if output.text is None else output.text
        output.image = ImageItem() if output.image is None else output.image
        output.video = VideoItem() if output.video is None else output.video
        
        if input.text and input.text.text is not None:
            data_io = DataIO(
                text=input.text.text,
            )
            # For text input, directly use text embedding plugin
            embed_result = await self.tembed.forward(data_io)
            output.text.text_embeddings = embed_result.embeddings
        if input.image and input.image.image is not None:
            # Image embedding
            data_io = DataIO(
                image=input.image.image,
            )
            embed_result = await self.iembed.forward(data_io)
            output.image.image_embedding = embed_result.embeddings[0] if embed_result.embeddings else None
            
            # VLM generate text description
            vlm_result = await self.vlm.forward(data_io)
            output.image.text = vlm_result.text
            
            # Text embedding
            text_data_io = DataIO(text=vlm_result.text)
            text_embed_result = await self.tembed.forward(text_data_io)
            output.image.text_embeddings = text_embed_result.embeddings
        if input.video and input.video.video is not None:
            # Video embedding
            data_io = DataIO(
                video=input.video.video,
            )
            embed_result = await self.vembed.forward(data_io)
            output.video.video_embedding = embed_result.embeddings[0] if embed_result.embeddings else None
            
            # ASR extract audio text
            asr_result = await self.asr.forward(data_io)
            output.video.text = asr_result.text
            
            # Text embedding
            text_data_io = DataIO(text=asr_result.text)
            text_embed_result = await self.tembed.forward(text_data_io)
            output.video.text_embeddings = text_embed_result.embeddings
        return output
    
MMExtractor.register_self()