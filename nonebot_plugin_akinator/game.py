from contextlib import suppress
from io import BytesIO
from pathlib import Path
from typing import Awaitable, Callable, List, Optional

from aiohttp import ClientSession
from nonebot import logger
from pil_utils import BuildImage, Text2Image

from .akinator.akinator.async_aki import Akinator as BaseAkinator
from .config import config

RES_PATH = Path(__file__).parent / "res"
IMG_BG = BuildImage.open(RES_PATH / "bg.jpg")
IMG_CONCENTRATION_INTENSE = BuildImage.open(RES_PATH / "concentration_intense.webp")
IMG_CONFIANT = BuildImage.open(RES_PATH / "confiant.webp")
IMG_ETONNEMENT = BuildImage.open(RES_PATH / "etonnement.webp")
IMG_INSPIRATION_FORTE = BuildImage.open(RES_PATH / "inspiration_forte.webp")
IMG_INSPIRATION_LEGERE = BuildImage.open(RES_PATH / "inspiration_legere.webp")
IMG_LEGER_DECOURAGEMENT = BuildImage.open(RES_PATH / "leger_decouragement.webp")
IMG_MOBILE = BuildImage.open(RES_PATH / "mobile.webp")
IMG_SEREIN = BuildImage.open(RES_PATH / "serein.webp")
IMG_SURPRISE = BuildImage.open(RES_PATH / "surprise.webp")
IMG_TENSION = BuildImage.open(RES_PATH / "tension.webp")
IMG_VRAI_DECOURAGEMENT = BuildImage.open(RES_PATH / "vrai_decouragement.webp")

RUNNING_GAMES: List["Akinator"] = []


class OperatingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Game already in operation", *args)


def change_operating(async_func: Callable[..., Awaitable]):
    async def wrapper(self: "Akinator", *args, **kwargs):
        if self.operating:
            raise OperatingError

        self.operating = True
        try:
            return await async_func(self, *args, **kwargs)
        finally:
            self.operating = False

    return wrapper


class Akinator(BaseAkinator):
    group_id: int
    user_id: int

    old_progression: float = 0.0
    operating: bool = False

    def __init__(self, group_id: int, user_id: int, *args, **kwargs):
        if self.get(group_id, user_id):
            raise ValueError("Game already created")

        self.group_id = group_id
        self.user_id = user_id
        RUNNING_GAMES.append(self)
        super().__init__(*args, proxy=config.proxy, **kwargs)

    @staticmethod
    def get(group_id: int, user_id: int) -> Optional["Akinator"]:
        li = [
            x for x in RUNNING_GAMES if x.group_id == group_id and x.user_id == user_id
        ]
        return li[0] if li else None

    @change_operating
    async def start_game(self, *args, **kwargs) -> str:
        return await super().start_game(
            *args,
            language=config.akinator_language,
            child_mode=config.akinator_child_mode,
            **kwargs,
        )

    @change_operating
    async def answer(self, ans: str) -> str:
        self.first_guess = None
        self.guesses = None
        return await super().answer(ans)

    @change_operating
    async def back(self) -> str:
        return await super().back()

    @change_operating
    async def win(self) -> dict:
        return await super().win()

    async def close(self):
        with suppress(ValueError):
            RUNNING_GAMES.remove(self)

        return await super().close()

    def get_akitude(self) -> BuildImage:
        progression = self.progression
        old_progression = self.old_progression
        step = self.step

        target_progress = step * 4
        weighted_progress = (
            (step * progression + (10 - step) * target_progress) / 10
            if step <= 10
            else 0.0
        )

        if progression >= 80:
            return IMG_MOBILE
        if old_progression < 50 and progression >= 50:
            return IMG_INSPIRATION_FORTE
        if progression >= 50:
            return IMG_CONFIANT
        if old_progression - progression > 16:
            return IMG_SURPRISE
        if old_progression - progression > 8:
            return IMG_ETONNEMENT
        if weighted_progress >= target_progress:
            return IMG_INSPIRATION_LEGERE
        if weighted_progress >= target_progress * 0.8:
            return IMG_SEREIN
        if weighted_progress >= target_progress * 0.6:
            return IMG_CONCENTRATION_INTENSE
        if weighted_progress >= target_progress * 0.4:
            return IMG_LEGER_DECOURAGEMENT
        if weighted_progress >= target_progress * 0.2:
            return IMG_TENSION
        return IMG_VRAI_DECOURAGEMENT

    def draw_question_img(self) -> BytesIO:
        padding = 50
        text_color = (21, 61, 79)

        aki = self.get_akitude()
        aki_height = aki.height
        img_width = aki.width

        text_width = img_width - padding * 2
        question_text = (
            Text2Image.from_text(
                f"Question {self.step + 1}\n{self.question}",
                40,
                align="center",
                weight="bold",
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        question_height = question_text.height
        question_width = question_text.width

        answer_text = (
            Text2Image.from_text(
                ("1. 是  |  2. 否  |  3. 不知道\n4. 或许是  |  5. 或许不是\n上一题 (Q)  |  退出 (E)"),
                40,
                align="center",
                weight="bold",
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        answer_height = answer_text.height
        answer_width = answer_text.width

        img_height = aki_height + question_height + answer_height + padding * 5
        mask_height = img_height - aki_height - padding * 2
        img = (
            IMG_BG.copy()
            .resize((img_width, img_height))
            .paste(
                BuildImage.new("RGBA", (img_width, mask_height), (255, 255, 255, 120)),
                (0, aki_height + padding * 2),
                alpha=True,
            )
        )

        img.paste(aki, (0, padding), alpha=True)
        img.paste(
            question_text,
            (int((img_width - question_width) / 2), aki_height + padding * 3),
            alpha=True,
        )
        img.paste(
            answer_text,
            (
                int((img_width - answer_width) / 2),
                aki_height + question_height + padding * 4,
            ),
            alpha=True,
        )

        return img.save_jpg()

    async def draw_win_img(self) -> BytesIO:
        data = self.first_guess
        if not data:
            raise ValueError("No guess")

        name: str = data["name"]
        desc: str = data["description"]
        uploder: str = data["pseudo"]
        target_pic: Optional[bytes] = None
        try:
            async with ClientSession() as s:
                async with s.get(data["absolute_picture_path"]) as r:
                    target_pic = await r.read()
        except:
            logger.exception("获取猜想对象图片失败")

        # draw
        padding = 50
        text_color = (21, 61, 79)

        aki = IMG_CONFIANT
        aki_height = aki.height
        aki_width = 380
        aki_width_offset = 145

        text_width = int(aki_width * 1.5)
        img_width = aki_width + text_width + padding * 4

        title_text = (
            Text2Image.from_text(
                "我想",
                40,
                weight="bold",
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        title_height = title_text.height

        target_title = (
            Text2Image.from_text(
                f"{name}",
                40,
                weight="bold",
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        target_title_height = target_title.height

        target_desc = (
            Text2Image.from_text(
                f"{desc}",
                30,
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        target_desc_height = target_desc.height

        target_image = (
            (BuildImage.open(BytesIO(target_pic)).resize_width(text_width))
            if target_pic
            else None
        )
        target_image_height = padding + target_image.height if target_image else 0

        uploader_text = (
            Text2Image.from_text(
                f"提交人：{uploder}",
                30,
                fill=text_color,
            )
            .wrap(text_width)
            .to_image()
        )
        uploader_height = uploader_text.height

        min_height = aki_height + padding * 2
        img_height = (
            padding * 4
            + title_height
            + target_title_height
            + target_desc_height
            + target_image_height
            + uploader_height
        )
        img_height = max(img_height, min_height)

        mask_height = img_height
        mask_width = img_width - aki_width - padding

        right_half_pos = aki_width + padding * 2
        right_half_start = right_half_pos + padding
        img = (
            IMG_BG.copy()
            .resize((img_width, img_height))
            .paste(
                BuildImage.new("RGBA", (mask_width, mask_height), (255, 255, 255, 120)),
                (right_half_pos, 0),
                alpha=True,
            )
            .paste(
                aki,
                ((-aki_width_offset + padding), int((img_height - aki_height) / 2)),
                alpha=True,
            )
            .paste(title_text, (right_half_start, padding), alpha=True)
            .paste(
                target_title,
                (right_half_start, padding * 2 + title_height),
                alpha=True,
            )
            .paste(
                target_desc,
                (right_half_start, padding * 2 + title_height + target_title_height),
                alpha=True,
            )
        )

        if target_image:
            img.paste(
                target_image,
                (
                    right_half_start,
                    padding * 3
                    + title_height
                    + target_title_height
                    + target_desc_height,
                ),
                alpha=True,
            )

        img.paste(
            uploader_text,
            (
                right_half_start,
                padding * 3
                + title_height
                + target_title_height
                + target_desc_height
                + target_image_height,
            ),
            alpha=True,
        )

        return img.save_jpg()
