import asyncio
import time
from contextlib import asynccontextmanager
from enum import Enum, auto
from typing import Dict, Set, Tuple, Union

from cooaki import Akinator, Answer, CanNotGoBackError, GameEndedError, WinResp
from cookit.nonebot.alconna import RecallContext
from httpx import HTTPError
from nonebot import logger, on_command
from nonebot.adapters import Event as BaseEvent
from nonebot.exception import NoneBotException
from nonebot.matcher import Matcher
from nonebot.params import EventPlainText
from nonebot_plugin_alconna.uniseg import UniMessage
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
    except NoneBotException:
        raise
    except Exception:
        logger.exception("Unexpected error during game")
        await UniMessage.text("出现意外错误，结束游戏").send(at_sender=True)
    finally:
        active_sessions.discard(session_id)
    return


async def action_waiter_handler(
    msg: str = EventPlainText(),
) -> Union[Answer, OtherAction, None]:
    msg = msg.strip().lower()
    return next((k for k, v in ACTION_DICT.items() if msg in v), None)


def make_action_waiter(**kwargs):
    return waiter(waits=["message"], keep_session=True, **kwargs)(action_waiter_handler)


async def continue_waiter_handler(msg: str = EventPlainText()) -> bool:
    return msg.strip().lower() in CONTINUE_ACTION


def make_continue_waiter(**kwargs):
    return waiter(waits=["message"], keep_session=True, **kwargs)(
        continue_waiter_handler,
    )


async def wait_and_handle_action(aki: Akinator, recall: RecallContext) -> bool:
    """return should end game"""

    wait_time_end = time.time() + config.akinator_operation_timeout
    while True:
        action = await make_action_waiter().wait(
            before=None,
            timeout=wait_time_end - time.time(),
        )
        if action is None:
            await UniMessage.text("等待超时，退出游戏").send(at_sender=True)
            return True

        if action is OtherAction.EXIT:
            await UniMessage.text("已退出游戏").send(at_sender=True)
            return True

        try:
            if action is OtherAction.PREVIOUS:
                resp = await aki.back()
            else:
                resp = await aki.answer(action)
        except HTTPError:
            logger.exception("Request error occurred")
            await recall.send("请求失败，请重试", at_sender=True)
            continue
        except CanNotGoBackError:
            await recall.send("无法返回上一问，请重试", at_sender=True)
            continue
        except GameEndedError:
            await UniMessage.text("我想不出来更多问题了，游戏结束").send(at_sender=True)
            return True

        if isinstance(resp, WinResp):
            asyncio.create_task(recall.recall())
            await (await build_answer_msg(aki, resp)).send(at_sender=True)

            if not (await make_continue_waiter().wait()):
                return True

            for _ in range(3):
                try:
                    await aki.continue_answer()
                except HTTPError:
                    logger.exception("Request failed when continuing")
                    continue
                break
            else:
                await UniMessage.text("请求失败，结束游戏").send(at_sender=True)

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
            timeout=config.akinator_request_timeout,
        )
        try:
            await aki.start()
        except Exception:
            logger.exception("Failed to start game")
            await m.finish("初始化游戏失败，请检查后台输出")

        while not aki.state.ended:
            async with RecallContext() as recall:
                await recall.send(await build_question_msg(aki), at_sender=True)
                if await wait_and_handle_action(aki, recall):
                    break
