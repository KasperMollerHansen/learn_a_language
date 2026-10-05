import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_level_structure_matches_plan() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    level_ids = [level["id"] for level in bank["levels"]]
    level_names = [level["name"] for level in bank["levels"]]

    assert level_ids == ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "2-1", "2-2", "2-3"]
    assert level_names == [
        "People",
        "Tilægsord",
        "Forholdsord",
        "People with articles",
        "Animals",
        "Words that look alike",
        "Modalverber",
        "Common verbs",
        "Everyday things",
    ]
    assert all(len(level["wordIds"]) == 30 for level in bank["levels"])
    assert all(word_id in bank["words"] for level in bank["levels"] for word_id in level["wordIds"])
    modal_level = next(level for level in bank["levels"] if level["id"] == "2-1")
    assert all(word_id.startswith("modals.") for word_id in modal_level["wordIds"])
    assert {word_id.split(".")[1] for word_id in modal_level["wordIds"]} == {
        "koennen",
        "muessen",
        "wollen",
        "duerfen",
        "sollen",
        "moegen",
    }
    article_level = next(level for level in bank["levels"] if level["mode"] == "article")
    assert all(word_id in bank["grammar"]["genitiveNouns"] for word_id in article_level["wordIds"])
    assert all(bank["words"][word_id].get("gender") in {"der", "die", "das"} for word_id in article_level["wordIds"])
