from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .config import ConfigModel

__version__ = "0.1.2"
__plugin_meta__ = PluginMetadata(
    name="Akinator",
    description="网络天才",
    usage="使用 `akinator` 指令开始让我猜人物吧！",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-akinator",
    type="application",
    config=ConfigModel,
    supported_adapters=["~onebot.v11"],
    extra={"License": "MIT", "Author": "student_2333"},
)
