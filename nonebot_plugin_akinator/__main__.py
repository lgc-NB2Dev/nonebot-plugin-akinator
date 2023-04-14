from typing import Dict, Tuple

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from .akinator.akinator.exceptions import AkiNoQuestions, CantGoBackAnyFurther
from .game import Akinator

cmd_start = on_command("akinator", aliases={"aki"})


def get_group_id_and_user_id(event: MessageEvent) -> tuple[int, int]:
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    user_id = event.user_id
    return group_id, user_id


@cmd_start.handle()
async def _(matcher: Matcher, event: MessageEvent):
    group_id, user_id = get_group_id_and_user_id(event)

    game = Akinator.get(group_id, user_id)
    if game:
        await matcher.finish("已有游戏正在进行中，如果想结束，请先发送「E」结束游戏", at_sender=True)

    game = Akinator(group_id, user_id)
    try:
        await game.start_game()
        pic = game.draw_question_img()
    except:
        await game.close()
        logger.exception("启动游戏失败")
        await matcher.finish("启动游戏失败，请检查后台输出")

    await matcher.finish(MessageSegment.image(pic), at_sender=True)


ARG_DICT: Dict[str, Tuple[str, ...]] = {
    "0": ("1", "y", "yes", "是", "s", "真"),
    "1": ("2", "n", "no", "否", "f", "不是", "假"),
    "2": ("3", "i", "idk", "i dont know", "i don't know", "bzd", "不知道", "不清楚"),
    "3": ("4", "p", "probably", "或许是", "hxx", "可能是", "有可能"),
    "4": ("5", "pn", "probably not", "或许不是", "hxbs", "可能不是"),
    "q": ("q", "prev", "previous", "上一题", "syt", "上一个"),
    "e": ("e", "exit", "退出", "tc", "不玩了"),
}


async def handle_game_rule(event: MessageEvent, state: T_State) -> bool:
    group_id, user_id = get_group_id_and_user_id(event)
    game = Akinator.get(group_id, user_id)

    if game:
        arg = event.message.extract_plain_text().strip().lower()

        for k, v in ARG_DICT.items():
            if arg in v:
                state["game"] = game
                state["answer"] = k
                return True

    return False


answer_handler = on_message(rule=handle_game_rule)


@answer_handler.handle()
async def _(matcher: Matcher, state: T_State):
    game: Akinator = state["game"]
    ans: str = state["answer"]

    if game.operating:
        await matcher.finish("你先别急，游戏正在执行中~", at_sender=True)

    if ans == "e":
        await game.close()
        await matcher.finish("已退出游戏", at_sender=True)

    win = False
    try:
        if ans == "q":
            await game.back()

        else:
            await game.answer(ans)

            if game.progression >= 95:
                win = True
                await game.win()

        pic = await game.draw_win_img() if win else game.draw_question_img()

    except Exception as e:
        if isinstance(e, CantGoBackAnyFurther):
            await matcher.finish("没有上一题了", at_sender=True)

        # 其他情况结束游戏并记录
        logger.exception("游戏出错")
        await game.close()

        if isinstance(e, AkiNoQuestions):
            await matcher.finish("我想不出来更多问题了，游戏结束……", at_sender=True)

        await matcher.finish("遇到错误，结束游戏……", at_sender=True)

    if win:
        await matcher.pause(
            MessageSegment.image(pic) + "如果结果不对，你可以发送「C」继续答题",
            at_sender=True,
        )

    await matcher.finish(MessageSegment.image(pic), at_sender=True)


CONTINUE_WORDS = ("c", "continue", "继续")


@answer_handler.handle()
async def _(matcher: Matcher, event: MessageEvent, state: T_State):
    game: Akinator = state["game"]
    msg = event.message.extract_plain_text().strip().lower()

    if msg not in CONTINUE_WORDS:
        # logger.debug("结束游戏")
        await game.close()
        return

    # logger.debug("继续游戏")
    try:
        pic = game.draw_question_img()
    except:
        logger.exception("游戏出错")
        await game.close()
        await matcher.finish("遇到错误，结束游戏……", at_sender=True)

    await matcher.finish(MessageSegment.image(pic), at_sender=True)
