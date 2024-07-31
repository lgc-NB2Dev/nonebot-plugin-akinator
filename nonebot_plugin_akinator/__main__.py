from enum import Enum, auto
from typing import Dict, Tuple, Union

from cooaki import Answer
from nonebot import on_command

from . import render as render


class OtherAction(str, Enum):
    PREVIOUS = auto()
    EXIT = auto()


ACTION_DICT: Dict[Union[Answer, OtherAction], Tuple[str, ...]] = {
    Answer.YES: ("1", "y", "yes", "是", "s", "真", "true"),
    Answer.NO: ("2", "n", "no", "否", "f", "不是", "bs", "假", "false"),
    Answer.I_DONT_KNOW: ("3", "i", "idk", "i dont know", "i don't know", "不知道", "bzd", "不清楚", "bqc"),
    Answer.PROBABLY: ("4", "p", "probably", "或许是", "hxx", "可能是", "kns"),
    Answer.PROBABLY_NOT: ("5", "pn", "probably not", "或许不是", "hxbs", "可能不是", "knbs"),
    OtherAction.PREVIOUS: ("b", "back", "prev", "previous", "上一问", "syw", "上一题", "syt", "上一个", "syg"),
    OtherAction.EXIT: ("e", "exit", "退出", "tc", "不玩了", "bwl"),
}  # fmt: skip


cmd_aki = on_command("akinator", aliases={"aki"})
