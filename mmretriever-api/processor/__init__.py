from .pipelines import MMExtractor
from .core import PipelineParam, MMData

# 导入插件模块以触发注册
from .plugins import asr, tembed, iembed, vembed, vlm
