from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .config import ConfigModel

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    "Akinator",
    "网络天才",
    "插件用法",
    ConfigModel,
    {"License": "MIT", "Author": "student_2333"},
)
