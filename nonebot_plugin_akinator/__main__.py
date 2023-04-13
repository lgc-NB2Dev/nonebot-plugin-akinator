from typing import Dict, Literal, Union

from aiohttp import ClientSession
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config
from .game import Akinator

RUNNING_GAMES: Dict[int, Dict[int, Union[Akinator, Literal[True]]]] = {}

cmd_start = on_command("akinator", aliases={"aki"})


@cmd_start.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0

    group_games = RUNNING_GAMES.get(group_id)
    if not group_games:
        group_games = {}
        RUNNING_GAMES[group_id] = group_games

    current_game = group_games.get(event.user_id)
    ans = arg.extract_plain_text().strip().lower()

    # 即将开始 True占位
    if current_game is True:
        await matcher.finish("你先别急，游戏正在开始~")

    # 游戏已开始，但是没带参数
    if current_game and (not ans):
        await matcher.finish("要重新开始，请使用 [aki q] 命令退出该局游戏")

    # 还没有开始
    if not current_game:
        # 带了参数
        if ans:
            await matcher.finish("要开始一局新游戏，直接发送命令即可，不要带参数")

        # 没带参数，开始游戏
        group_games[event.user_id] = True
        current_game = Akinator()

        try:
            await current_game.start_game()
        except:
            await current_game.close()
            del group_games[event.user_id]
            logger.exception("开始游戏失败")
            await matcher.finish("开始游戏失败，请重试")

        group_games[event.user_id] = current_game

    # 游戏开始，带了参数
    if ans:
        if ans == "e":
            await current_game.close()
            await matcher.finish("已退出游戏")

        if ans == "p":
            try:
                await current_game.back()
            except:
                await current_game.close()
                del group_games[event.user_id]
                logger.exception("切换上一题出错")
                await matcher.finish("切换上一题失败，结束游戏")

        elif ans in ("1", "2", "3", "4", "5", "y", "n", "idk", "p", "pn"):
            # 1 开始 转 0 开始
            if ans.isdigit():
                ans = str(int(ans) - 1)

            try:
                await current_game.answer(ans)
            except:
                await current_game.close()
                del group_games[event.user_id]
                logger.exception("回答出错")
                await matcher.finish("回答出错，结束游戏")

        else:
            await matcher.finish("参数错误")

        if current_game.progression >= 95:
            guess = None
            try:
                guess = await current_game.win()
                async with ClientSession() as s:
                    async with s.get(
                        guess["absolute_picture_path"],
                        proxy=config.proxy,
                    ) as r:
                        pic = await r.read()
            except:
                logger.exception("获取游戏结果失败")
                await matcher.finish("获取游戏结果失败")
            finally:
                await current_game.close()
                del group_games[event.user_id]

            await matcher.finish(
                f"游戏结束，我猜的答案是 {guess['name']}" + MessageSegment.image(pic),
            )

    try:
        pic = await current_game.draw_question_img()
    except:
        await current_game.close()
        del group_games[event.user_id]
        logger.exception("绘制问题图片出错")
        await matcher.finish("绘制问题图片出错，结束游戏")
    await matcher.finish(MessageSegment.image(pic))
