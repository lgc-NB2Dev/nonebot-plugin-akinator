from pathlib import Path
from typing import Literal, Optional

from cookit import DebugFileWriter
from nonebot import get_plugin_config
from pydantic import BaseModel


class ConfigModel(BaseModel):
    proxy: Optional[str] = None

    akinator_child_mode: bool = False
    akinator_language: str = "cn"
    akinator_text_mode: bool = False
    akinator_operation_timeout: int = 120
    akinator_request_timeout: float = 15
    akinator_client_type: Literal["httpx", "playwright"] = "httpx"
    akinator_base_url_template: str = "https://{}.akinator.com"


config = get_plugin_config(ConfigModel)

debug = DebugFileWriter(Path.cwd() / "debug", "akinator")
