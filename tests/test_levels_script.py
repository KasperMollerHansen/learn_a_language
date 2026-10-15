import importlib.util
from pathlib import Path
from types import ModuleType

from wordbank import LEVELS_DIR, SRC, read_json


ROOT = Path(__file__).resolve().parents[1]


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("levels_script", ROOT / "scripts" / "levels.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load_script()


def test_level_files_match_the_generator() -> None:
    chapters = script.build_chapters(SRC)

    assert read_json(LEVELS_DIR / "index.json") == {"files": list(chapters)}
    for name, levels in chapters.items():
        assert read_json(LEVELS_DIR / name) == levels, "stale levels: run scripts/levels.py"
