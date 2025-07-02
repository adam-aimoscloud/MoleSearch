from ..core import Pipeline, PipelineParam, DataIO, MMData
from ..plugins import *


class MMExactor(Pipeline):
    def __init__(self, param: PipelineParam) -> None:
        super().__init__(param)
        self.asr = ASRPlugin(param.get_plugin_param(ASRPluginParam.__class__.__name__))
        self.tembed = TEmbedPlugin(param.get_plugin_param(TEmbedPluginParam.__class__.__name__))
        self.vembed = VEmbedPlugin(param.get_plugin_param(VEmbedPluginParam.__class__.__name__))
        self.vlm = VLMPlugin(param.get_plugin_param(VLMPluginParam.__class__.__name__))

    def forward(self, input: MMData) -> MMData:
        output = MMData()
        if input.text.text is not None:
            data_io = DataIO(
                text=input.text.text,
            )
            data_io = self.asr.forward(data_io)
            output.text.text_embeddings = data_io.embeddings
        if input.image.image is not None:
            data_io = DataIO(
                image=input.image.image,
            )
            data_io = self.iembed.forward(data_io)
            output.image.image_embeddings = data_io.embeddings
            data_io = self.vlm.forward(data_io)
            data_io = self.tembed.forward(data_io)
            output.image.text = data_io.text
            output.image.text_embeddings = data_io.embeddings
        if input.video.video is not None:
            data_io = DataIO(
                video=input.video.video,
            )
            data_io = self.vembed.forward(data_io)
            output.video.image_embeddings = data_io.embeddings
            data_io = self.asr.forward(data_io)
            data_io = self.tembed.forward(data_io)
            output.video.text_embeddings = data_io.embeddings
            output.video.text = data_io.text
        return output
    
MMExactor.register_self()