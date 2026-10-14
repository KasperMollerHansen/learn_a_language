"""Assemble the split game data in src/ into the in-memory {levels, grammar, words} dict."""

import json
from pathlib import Path
from typing import Any


SRC = Path(__file__).resolve().parents[1] / "src"
WORDBANK_DIR = SRC / "wordbank"
LEVELS_DIR = SRC / "levels"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_wordbank() -> dict[str, Any]:
    word_index = read_json(WORDBANK_DIR / "index.json")
    levels: list[dict[str, Any]] = []
    for name in read_json(LEVELS_DIR / "index.json")["files"]:
        levels.extend(read_json(LEVELS_DIR / name))
    words: dict[str, Any] = {}
    for name in word_index["words"]:
        words.update(read_json(WORDBANK_DIR / name))
    return {
        "levels": levels,
        "grammar": read_json(WORDBANK_DIR / word_index["grammar"]),
        "words": words,
    }
