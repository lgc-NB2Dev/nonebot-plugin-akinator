from io import BytesIO
from pathlib import Path

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


class Akinator(BaseAkinator):
    old_progression: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, proxy=config.proxy, **kwargs)

    async def start_game(self, *args, **kwargs) -> str:
        return await super().start_game(
            *args,
            language=config.akinator_language,
            child_mode=config.akinator_child_mode,
            **kwargs,
        )

    async def answer(self, ans: str) -> str:
        self.old_progression = self.progression
        return await super().answer(ans)

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

    async def draw_question_img(self) -> BytesIO:
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
                ("1. 是  |  2. 否  |  3. 不知道\n4. 或许是  |  5. 或许不是\n上一题 (P)  |  退出 (E)"),
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
