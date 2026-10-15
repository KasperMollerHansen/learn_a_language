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


def level_word_ids(bank: dict[str, Any], level: dict[str, Any]) -> list[str]:
    """Mirror the level pool in src/index.html: words in the level's categories and tiers."""
    tiers = level.get("tiers")
    return [
        word_id
        for word_id, word in bank["words"].items()
        if word_id.split(".")[0] in level["categories"]
        and (tiers is None or word["tier"] in tiers)
    ]


LANGUAGES = ["danish", "german", "english", "spanish", "french"]
# (source, target) pairs; mirrors modePlayable in src/index.html.
PAIRS = [(source, target) for source in LANGUAGES for target in LANGUAGES if source != target]
MODE_PAIRS = {
    "word": PAIRS,
    "article": [
        pair for pair in PAIRS if pair[1] == "german" and pair[0] in {"danish", "english"}
    ],
    "sentence": PAIRS,
}
