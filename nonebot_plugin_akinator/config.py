from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    proxy: Optional[str] = None

    akinator_child_mode: bool = False
    akinator_language: str = "cn"


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
