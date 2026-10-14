import re

from wordbank import LEVELS_DIR, SRC, WORDBANK_DIR, read_json


def test_wordbank_index_matches_folder() -> None:
    index = read_json(WORDBANK_DIR / "index.json")
    on_disk = {p.name for p in WORDBANK_DIR.glob("*.json")} - {"index.json"}
    assert {index["grammar"], *index["words"]} == on_disk


def test_levels_index_matches_folder() -> None:
    index = read_json(LEVELS_DIR / "index.json")
    on_disk = {p.name for p in LEVELS_DIR.glob("*.json")} - {"index.json"}
    assert set(index["files"]) == on_disk


def test_no_duplicate_word_id_across_files() -> None:
    seen: dict[str, str] = {}
    for path in WORDBANK_DIR.glob("*.json"):
        if path.name in {"index.json", "grammar.json"}:
            continue
        for word_id in read_json(path):
            assert word_id not in seen, f"{word_id} in {seen[word_id]} and {path.name}"
            seen[word_id] = path.name


def test_word_ids_are_prefixed_by_their_file() -> None:
    for path in WORDBANK_DIR.glob("*.json"):
        if path.name in {"index.json", "grammar.json"}:
            continue
        assert all(word_id.startswith(f"{path.stem}.") for word_id in read_json(path))


def test_service_worker_caches_every_data_file() -> None:
    app_files = set(
        re.findall(r'"\./([^"]+)"', (SRC / "service-worker.js").read_text(encoding="utf-8"))
    )
    expected = {"wordbank/index.json", "levels/index.json"}
    expected |= {f"wordbank/{p.name}" for p in WORDBANK_DIR.glob("*.json")}
    expected |= {f"levels/{p.name}" for p in LEVELS_DIR.glob("*.json")}
    assert expected <= app_files
