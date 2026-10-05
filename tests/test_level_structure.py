import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_level_structure_matches_plan() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    level_ids = [level["id"] for level in bank["levels"]]
    level_names = [level["name"] for level in bank["levels"]]

    assert level_ids[:5] == ["1-1", "1-2", "1-3", "1-4", "1-5"]
    assert level_names[:5] == [
        "People",
        "Adjective",
        "Tilægsord",
        "People with articles",
        "Sentences",
    ]
    assert level_ids[-1] == "2-1"
    assert level_names[-1] == "More advanced"
    assert all(len(level["wordIds"]) == 30 for level in bank["levels"])
