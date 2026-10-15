import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

from wordbank import SRC, load_wordbank


ROOT = Path(__file__).resolve().parents[1]


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "translations_script", ROOT / "scripts" / "translations.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load_script()


def test_csv_is_in_sync_with_wordbank() -> None:
    rows = script.read_rows(ROOT / "translations.csv")
    ids = [row["id"] for row in rows]
    words = load_wordbank()["words"]
    assert ids == list(words), "translations.csv is stale: run scripts/translations.py export"
    for row in rows:
        expected = script.entry_to_row(row["id"], words[row["id"]], [])
        for column in [*script.TEXT_FIELDS, *script.OPTION_FIELDS]:
            assert row[column] == expected[column], f"{row['id']}.{column}"


def test_apply_round_trip(tmp_path: Path) -> None:
    src = tmp_path / "src"
    shutil.copytree(SRC, src)
    csv_path = tmp_path / "translations.csv"
    script.export(src, csv_path)
    text = csv_path.read_text(encoding="utf-8-sig").replace(";Mutter;", ";Mama;", 1)
    csv_path.write_text(text, encoding="utf-8-sig", newline="")

    assert script.apply(src, csv_path) == ["people.mother"]

    words = script.read_json(src / "wordbank" / "people.json")
    assert words["people.mother"]["german"] == "Mama"
    assert script.apply(src, csv_path) == []
