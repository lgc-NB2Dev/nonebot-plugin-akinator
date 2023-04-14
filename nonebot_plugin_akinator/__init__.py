from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .config import ConfigModel

__version__ = "0.1.0.post2"
__plugin_meta__ = PluginMetadata(
    "Akinator",
    "网络天才",
    "使用 `akinator` 指令开始让我猜人物吧！",
    ConfigModel,
    {"License": "MIT", "Author": "student_2333"},
)
