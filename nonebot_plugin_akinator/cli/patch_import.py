import shutil
from pathlib import Path

from nonebot import logger

RES_PATH = Path(__file__).parent / "res"

PATCH_KEYWORD = "scripts.patch_pw_import"
PATCH_STATEMENT = """
import scripts.patch_pw_import

scripts.patch_pw_import.patch()
""".strip()


def main():
    cwd = Path.cwd()

    scripts_p = cwd / "scripts"
    scripts_p.mkdir(exist_ok=True)

    shutil.copy(RES_PATH / "patch_pw_import.py", scripts_p)
    logger.success("Copied patch_pw_import.py")

    bot_py_path = cwd / "bot.py"
    if not bot_py_path.exists():
        shutil.copy(RES_PATH / "bot.py", cwd)
        logger.success("Copied bot.py")
    else:
        logger.info("Skipped copying bot.py")

    bot_py_content = bot_py_path.read_text("u8")
    if PATCH_KEYWORD in bot_py_content:
        logger.info("Skipped patching bot.py")
        return

    lines = bot_py_content.splitlines()
    index = 0
    while lines[index].startswith("#"):
        index += 1
    lines.insert(index, PATCH_STATEMENT)
    bot_py_path.write_text("\n".join(lines), "u8")
    logger.success("Patched bot.py")


if __name__ == "__main__":
    main()
