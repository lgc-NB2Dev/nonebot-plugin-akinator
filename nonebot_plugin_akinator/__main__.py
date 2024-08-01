from contextlib import asynccontextmanager
from enum import Enum, auto
from typing import Dict, Set, Tuple, Union

from cooaki import Akinator, Answer, CanNotGoBackError, GameEndedError, WinResp
from cookit.nonebot.alconna import RecallContext
from httpx import HTTPError
from nonebot import logger, on_command
from nonebot.adapters import Event as BaseEvent
from nonebot.matcher import Matcher, current_matcher
from nonebot.params import EventPlainText
from nonebot_plugin_waiter import waiter

from .config import config
from .message import build_answer_msg, build_question_msg


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
    OtherAction.EXIT: ("e", "exit", "退出", "q", "quit", "tc", "不玩了", "bwl"),
}  # fmt: skip
CONTINUE_ACTION = ("c", "continue", "继续")


active_sessions: Set[str] = set()


@asynccontextmanager
async def with_active_session(session_id: str):
    active_sessions.add(session_id)
    try:
        yield
    except Exception:
        await current_matcher.get().send("出现意外错误，结束游戏")
    finally:
        active_sessions.discard(session_id)
    return


@waiter(waits=["message"], keep_session=True)
async def action_waiter(
    msg: str = EventPlainText(),
) -> Union[Answer, OtherAction, None]:
    msg = msg.strip().lower()
    return next((k for k, v in ACTION_DICT.items() if msg in v), None)


@waiter(waits=["message"], keep_session=True)
async def continue_waiter(msg: str = EventPlainText()) -> bool:
    return msg.strip().lower() in CONTINUE_ACTION


async def wait_and_handle_action(aki: Akinator, recall: RecallContext) -> bool:
    """return should end game"""

    m = current_matcher.get()

    while True:
        action = await action_waiter.wait(
            before=None,
            timeout=config.akinator_operation_timeout,
        )
        if not action:
            await m.send("等待超时，退出游戏")
            return True

        if action is OtherAction.EXIT:
            await m.send("已退出游戏")
            return True

        try:
            if action is OtherAction.PREVIOUS:
                resp = await aki.back()
            else:
                resp = await aki.answer(action)
        except HTTPError:
            await recall.send("请求失败，请重试")
            continue
        except CanNotGoBackError:
            await recall.send("无法返回上一问，请重试")
            continue
        except GameEndedError:
            await m.send("我想不出来更多问题了，游戏结束")
            return True

        if isinstance(resp, WinResp):
            await (await build_answer_msg(aki, resp)).send()
            if not (await continue_waiter.wait()):
                return True
        return False


cmd_aki = on_command("akinator", aliases={"aki"})


@cmd_aki.handle()
async def _(m: Matcher, ev: BaseEvent):
    session_id = ev.get_session_id()
    if session_id in active_sessions:
        await m.finish("当前对话有游戏正在进行中，请先退出")

    async with with_active_session(session_id):
        aki = Akinator(
            lang=config.akinator_language,
            child_mode=config.akinator_child_mode,
            proxy=config.proxy,
        )
        try:
            await aki.start()
        except Exception:
            logger.exception("Failed to start game")
            await m.finish("初始化游戏失败，请检查后台输出")

        while not aki.state.ended:
            async with RecallContext() as recall:
                await recall.send(await build_question_msg(aki))
                if await wait_and_handle_action(aki, recall):
                    break
