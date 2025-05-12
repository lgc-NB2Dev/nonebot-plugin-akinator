import mimetypes
from collections.abc import Awaitable
from contextlib import suppress
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    cast,
)
from typing_extensions import Concatenate, ParamSpec

import anyio
import fleep
import jinja2 as jj
from cookit.pw import RouterGroup, make_real_path_router, screenshot_html
from cookit.pw.loguru import log_router_err
from nonebot_plugin_htmlrender import get_new_page

from .config import debug
from .const import DATA_ADDITIONAL_CSS_PATH, DATA_AKITUDE_DIR, RES_DIR

if TYPE_CHECKING:
    from cooaki import BaseAkinator
    from playwright.async_api import Route
    from yarl import URL


P = ParamSpec("P")

jj_env = jj.Environment(
    loader=jj.FileSystemLoader(Path(__file__).parent / "res" / "templates"),
    autoescape=True,
    enable_async=True,
)

ROUTE_BASE_URL = "https://akinator.nonebot"
router_group = RouterGroup()


@router_group.router(f"{ROUTE_BASE_URL}/res/**/*")
@log_router_err()
@make_real_path_router
async def _(url: "URL", **_):
    return RES_DIR.joinpath(*url.parts[2:])


def add_akitude_router(group: RouterGroup, aki: "BaseAkinator"):
    @group.router(f"{ROUTE_BASE_URL}/akitude/*")
    @log_router_err()
    async def _(url: "URL", route: "Route", **_):
        filename = url.parts[2]
        file_path = DATA_AKITUDE_DIR / filename
        if file_path.exists():
            data = await anyio.Path(file_path).read_bytes()
        else:
            data = await aki.get_akitude_image(filename)
            await anyio.Path(file_path).write_bytes(data)
        await route.fulfill(
            body=data,
            content_type=mimetypes.guess_type(filename)[0] or "image/png",
        )


def renderer(
    func: Callable[
        Concatenate[RouterGroup, P],
        Awaitable[tuple[str, dict[str, Any], Optional[str]]],
    ],
):
    async def wrapper(aki: "BaseAkinator", *args: P.args, **kwargs: P.kwargs) -> bytes:
        new_router_group = router_group.copy()

        add_akitude_router(new_router_group, aki)

        template_name, render_kwargs, selector = await func(
            new_router_group,
            *args,
            **kwargs,
        )
        template = jj_env.get_template(template_name)
        additional_css = DATA_ADDITIONAL_CSS_PATH.read_text("u8")

        html = await template.render_async(
            additional_style=f"<style>\n{additional_css}\n</style>",
            **render_kwargs,
        )
        if debug.enabled:
            debug.write(html, "{time}.html")

        @new_router_group.router(f"{ROUTE_BASE_URL}/")
        @log_router_err()
        async def _(route: "Route", **_):
            await route.fulfill(body=html, content_type="text/html")

        async with get_new_page() as page:
            await new_router_group.apply(page)
            await page.goto(f"{ROUTE_BASE_URL}/")
            return await screenshot_html(page, html, selector)

    return wrapper


@renderer
async def render_question_image(
    _: RouterGroup,
    akitude: str,
    index: int,
    question: str,
):
    return (
        "question.html.jinja",
        {"akitude": akitude, "index": index, "question": question},
        "main",
    )


@renderer
async def render_answer_image(
    router_group: RouterGroup,
    name: str,
    description: Optional[str] = None,
    photo: Optional[bytes] = None,
    pseudo: Optional[str] = None,
):
    if photo:
        photo_mime = "image"
        with suppress(IndexError):
            photo_mime = cast("list[str]", fleep.get(photo[:128]).mime)[0]

        @router_group.router(f"{ROUTE_BASE_URL}/answer_photo")
        @log_router_err()
        async def _(route: "Route", **_):
            await route.fulfill(body=photo, content_type=photo_mime)

    return (
        "answer.html.jinja",
        {
            "akitude": "confiant.png",
            "name": name,
            "description": description,
            "has_photo": bool(photo),
            "pseudo": pseudo,
        },
        "main",
    )
