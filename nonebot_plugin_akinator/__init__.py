# ruff: noqa: E402

from nonebot import logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_waiter")
require("nonebot_plugin_alconna")

from .const import HTML_RENDER_AVAILABLE

if HTML_RENDER_AVAILABLE:
    require("nonebot_plugin_htmlrender")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel, config  # noqa: E402

__version__ = "1.0.3"
__plugin_meta__ = PluginMetadata(
    name="Akinator",
    description="网络天才",
    usage="使用 `akinator` 指令开始让我猜人物吧！",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-akinator",
    type="application",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_waiter",
        "nonebot_plugin_alconna",
    ),
    extra={"License": "MIT", "Author": "LgCookie"},
)


if config.akinator_client_type == "playwright":
    if not HTML_RENDER_AVAILABLE:
        logger.warning(
            "Client type set to playwright, but required dependencies not installed. "
            "Consider install them by `pip install nonebot-plugin-akinator[image]`. "
            "Will automatically fallback to httpx client.\n"
            "P.S.: If you want to use patchright, "
            "run `pip install nonebot-plugin-akinator[patchright]` instead. "
            "Then run `nb akinator-patch-import` to let it take effect.",
        )
    else:
        from nonebot import get_driver
        from nonebot_plugin_htmlrender import init

        driver = get_driver()
        driver._lifespan._startup_funcs.remove(init)  # noqa: SLF001

        @driver.on_startup
        async def new_init():
            await init(headless=False)  # type: ignore
