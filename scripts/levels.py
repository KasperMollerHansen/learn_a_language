"""Generate src/levels/: one chapter per word tier, each with the same level structure.

Edit THEMES or CHAPTERS below, then run `python scripts/levels.py` to rewrite the level files.
"""

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# A theme gets a level in a chapter only when that chapter's tier has at least this many words.
MIN_POOL = 15
# At most this many levels per chapter; themes past the cap (in THEMES order) are left out.
MAX_LEVELS = 15
WORD_PROMPT = "Find the {target} word for"
# (name, mode, prompt, categories), in the order the word levels appear in every chapter.
# Order is priority too: when a chapter has more themes than MAX_LEVELS allows, the last go.
THEMES: list[tuple[str, str, str, list[str]]] = [
    ("People and feelings", "word", WORD_PROMPT, ["people", "emotions", "personality", "life"]),
    ("People with articles", "article", "Choose the {target} form", ["people"]),
    ("Describing words", "word", WORD_PROMPT, ["adjectives", "colors", "adverbs"]),
    (
        "Small words, numbers and time",
        "word",
        WORD_PROMPT,
        ["prepositions", "function", "numbers", "time"],
    ),
    ("Verbs", "word", WORD_PROMPT, ["verbs"]),
    ("Food and drink", "word", WORD_PROMPT, ["food", "drinks", "restaurant"]),
    (
        "Home and everyday things",
        "word",
        WORD_PROMPT,
        ["home", "kitchen", "everyday", "tools", "materials", "office"],
    ),
    ("Body, health and clothes", "word", WORD_PROMPT, ["body", "health", "clothing"]),
    (
        "Animals, nature and weather",
        "word",
        WORD_PROMPT,
        ["animals", "nature", "garden", "weather"],
    ),
    (
        "Town, travel and shopping",
        "word",
        WORD_PROMPT,
        ["city", "travel", "transport", "shopping", "countries"],
    ),
    ("Sport, music and hobbies", "word", WORD_PROMPT, ["sport", "music", "hobbies"]),
    (
        "Work, school and society",
        "word",
        WORD_PROMPT,
        [
            "work",
            "learning",
            "technology",
            "money",
            "media",
            "communication",
            "society",
            "science",
            "culture",
        ],
    ),
    ("Words that look alike", "word", "Translate the {source} word into {target}", ["spelling"]),
]
SENTENCES = (
    "Sentences",
    "word",
    "Translate the {source} sentence into {target}",
    ["modals", "sentences"],
)
BUILDER = (
    "Sentence builder",
    "sentence",
    "Build the {target} sentence one chunk at a time",
    ["sentence-builder"],
)
# Chapter N uses tier N words.
CHAPTERS = [
    "Chapter 1 · Basics",
    "Chapter 2 · Everyday",
    "Chapter 3 · Confident",
    "Chapter 4 · Fluent",
    "Chapter 5 · Advanced",
]


def read_json(path: Path) -> Any:
    """Parse a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    """Write JSON in the repo's data format."""
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def load_words(src: Path) -> dict[str, Any]:
    """Return every wordbank entry by id, in index order."""
    words: dict[str, Any] = {}
    for name in read_json(src / "wordbank" / "index.json")["words"]:
        words.update(read_json(src / "wordbank" / name))
    return words


def pool_size(words: dict[str, Any], categories: list[str], tiers: list[int]) -> int:
    """Count the words a level with these categories and tiers would draw from."""
    return sum(
        word_id.split(".")[0] in categories and word["tier"] in tiers
        for word_id, word in words.items()
    )


def level(spec: tuple[str, str, str, list[str]], tiers: list[int]) -> dict[str, Any]:
    """Build one level entry (without id and chapter)."""
    name, mode, prompt, categories = spec
    return {"name": name, "mode": mode, "prompt": prompt, "categories": categories, "tiers": tiers}


def build_chapters(src: Path) -> dict[str, list[dict[str, Any]]]:
    """Return each chapter file name mapped to its levels.

    Each chapter: theme word levels, then sentences, a mixed review of this tier and all earlier
    ones, and the sentence builder.
    """
    words = load_words(src)
    categories = list(dict.fromkeys(word_id.split(".")[0] for word_id in words))
    review = [c for c in categories if c not in SENTENCES[3] + BUILDER[3]]
    chapters: dict[str, list[dict[str, Any]]] = {}
    for tier, chapter in enumerate(CHAPTERS, start=1):
        levels = [
            level(theme, [tier])
            for theme in THEMES
            if pool_size(words, theme[3], [tier]) >= MIN_POOL
        ][: MAX_LEVELS - 3]
        levels.append(level(SENTENCES, [tier]))
        levels.append(level(("Review", "word", WORD_PROMPT, review), list(range(1, tier + 1))))
        levels.append(level(BUILDER, [tier]))
        chapters[f"chapter-{tier}.json"] = [
            {"id": f"{tier}-{index}", "chapter": chapter, **entry}
            for index, entry in enumerate(levels, start=1)
        ]
    return chapters


def write_chapters(src: Path) -> int:
    """Rewrite the chapter files and levels/index.json; return the number of levels."""
    chapters = build_chapters(src)
    for stale in (src / "levels").glob("chapter-*.json"):
        if stale.name not in chapters:
            stale.unlink()
    for name, levels in chapters.items():
        write_json(src / "levels" / name, levels)
    write_json(src / "levels" / "index.json", {"files": list(chapters)})
    return sum(len(levels) for levels in chapters.values())


def main() -> int:
    """Regenerate the level files."""
    sys.stdout.write(f"wrote {write_chapters(SRC)} levels\n")
    sys.stdout.write(
        "also update APP_FILES in src/service-worker.js if the chapter files changed\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
