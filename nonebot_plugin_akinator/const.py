from pathlib import Path

RES_DIR = Path(__file__).parent / "res"

DATA_DIR = Path.cwd() / "data" / "akinator"
DATA_AKITUDE_DIR = DATA_DIR / "akitude"

for _p in (DATA_DIR, DATA_AKITUDE_DIR):
    _p.mkdir(parents=True, exist_ok=True)

DATA_ADDITIONAL_CSS_PATH = DATA_DIR / "additional.css"
if not DATA_ADDITIONAL_CSS_PATH.exists():
    DATA_ADDITIONAL_CSS_PATH.write_text("")
