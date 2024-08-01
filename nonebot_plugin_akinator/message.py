from typing import Optional

from cooaki import Akinator, WinResp
from nonebot_plugin_alconna.uniseg import UniMessage

from .config import config
from .render import render_answer_image, render_question_image


async def get_answer_photo(aki: Akinator, data: WinResp) -> Optional[bytes]:
    if not data.photo:
        return None
    async with aki.create_client() as cli:
        return (await cli.get(data.photo)).raise_for_status().content


async def build_answer_msg_text(aki: Akinator, data: WinResp) -> UniMessage:
    msg = UniMessage()
    msg += f"我猜：\n{data.name_proposition}"
    if data.description_proposition:
        msg += f"\n{data.description_proposition}"

    photo = await get_answer_photo(aki, data)
    if photo:
        msg += "\n"
        msg += UniMessage.image(raw=photo)
        if data.pseudo:
            msg += f"From: {data.pseudo}"

    msg += "\n猜错了？继续游戏 (C)"
    return msg


async def build_answer_msg_img(aki: Akinator, data: WinResp) -> UniMessage:
    img = await render_answer_image(
        data.name_proposition,
        data.description_proposition,
        await get_answer_photo(aki, data),
        data.pseudo,
    )
    return UniMessage.image(raw=img)


async def build_answer_msg(aki: Akinator, data: WinResp) -> UniMessage:
    return await (
        build_answer_msg_text(aki, data)
        if config.akinator_text_mode
        else build_answer_msg_img(aki, data)
    )


async def build_question_msg_text(aki: Akinator) -> UniMessage:
    state = aki.state
    return UniMessage.text(
        f"问题 {state.step + 1}：\n"
        f"{state.question}\n"
        f"\n"
        f"1. 是 (Y) | 2. 否 (N) | 3. 不知道 (IDK)\n"
        f"4. 或许是 (P) | 5. 或许不是 (PN)\n"
        f"{'' if state.step == 0 else '上一问 (B) | '}退出 (E)",
    )


async def build_question_msg_img(aki: Akinator) -> UniMessage:
    state = aki.state
    img = await render_question_image(state.akitude, state.step + 1, state.question)
    return UniMessage.image(raw=img)


async def build_question_msg(aki: Akinator) -> UniMessage:
    return await (
        build_question_msg_text(aki)
        if config.akinator_text_mode
        else build_question_msg_img(aki)
    )
