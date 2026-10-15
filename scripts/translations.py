"""Export the wordbank to translations.csv for review in Excel, and apply corrections back."""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CSV_PATH = ROOT / "translations.csv"

TEXT_FIELDS = [
    "danish",
    "german",
    "english",
    "spanish",
    "french",
    "gender",
    "danishDefinite",
    "danishIndefinite",
]
# Sentence-builder chunks list their gate options per target language.
OPTION_FIELDS = [
    "danishOptions",
    "germanOptions",
    "englishOptions",
    "spanishOptions",
    "frenchOptions",
]
# Extra accepted answers per target language, joined like the options.
ALTERNATIVE_FIELDS = [
    "danishAlternatives",
    "germanAlternatives",
    "englishAlternatives",
    "spanishAlternatives",
    "frenchAlternatives",
]
LIST_FIELDS = [*OPTION_FIELDS, *ALTERNATIVE_FIELDS]
COLUMNS = ["id", "levels", *TEXT_FIELDS, *LIST_FIELDS, "checked", "comment"]
OPTIONS_SEP = " | "
DELIMITER = ";"


def read_json(path: Path) -> Any:
    """Parse a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    """Write JSON in the repo's wordbank format."""
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def word_files(src: Path) -> list[Path]:
    """Return the wordbank files in index order."""
    names = read_json(src / "wordbank" / "index.json")["words"]
    return [src / "wordbank" / name for name in names]


def level_ids_by_word(src: Path) -> dict[str, list[str]]:
    """Map each word id to the ids of the levels whose pool includes it."""
    words = {
        word_id: entry for path in word_files(src) for word_id, entry in read_json(path).items()
    }
    result: dict[str, list[str]] = {}
    for name in read_json(src / "levels" / "index.json")["files"]:
        for level in read_json(src / "levels" / name):
            tiers = level.get("tiers")
            for word_id, entry in words.items():
                if word_id.split(".")[0] in level["categories"] and (
                    tiers is None or entry["tier"] in tiers
                ):
                    result.setdefault(word_id, []).append(level["id"])
    return result


def entry_to_row(word_id: str, entry: dict[str, Any], levels: list[str]) -> dict[str, str]:
    """Flatten one wordbank entry into a CSV row (without checked/comment)."""
    row = {"id": word_id, "levels": ",".join(levels)}
    for field in TEXT_FIELDS:
        row[field] = str(entry.get(field, ""))
    for field in LIST_FIELDS:
        row[field] = OPTIONS_SEP.join(entry.get(field, []))
    return row


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    """Read translations.csv as dicts."""
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=DELIMITER))


def export(src: Path, csv_path: Path) -> int:
    """Write the wordbank to csv_path, keeping any checked/comment values already there."""
    kept = {row["id"]: row for row in read_rows(csv_path)} if csv_path.exists() else {}
    levels = level_ids_by_word(src)
    rows = []
    for path in word_files(src):
        for word_id, entry in read_json(path).items():
            row = entry_to_row(word_id, entry, levels.get(word_id, []))
            old = kept.get(word_id, {})
            row["checked"] = old.get("checked", "")
            row["comment"] = old.get("comment", "")
            rows.append(row)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, delimiter=DELIMITER)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def apply(src: Path, csv_path: Path) -> list[str]:
    """Write csv_path edits into the wordbank files; return the ids that changed.

    An emptied cell for a field that has a value is refused (nothing is written), so a
    blank left by accident can never delete data.
    """
    rows = {row["id"]: row for row in read_rows(csv_path)}
    files = {path: read_json(path) for path in word_files(src)}
    known = {word_id for data in files.values() for word_id in data}
    unknown = sorted(set(rows) - known)
    if unknown:
        raise ValueError(f"unknown ids in {csv_path.name}: {', '.join(unknown)}")
    changed: list[str] = []
    cleared: list[str] = []
    for data in files.values():
        for word_id, entry in data.items():
            row = rows.get(word_id)
            if row is None:
                continue
            new_values: dict[str, Any] = {f: row.get(f, "") for f in TEXT_FIELDS}
            for field in LIST_FIELDS:
                if field in row:
                    new_values[field] = row[field].split(OPTIONS_SEP) if row[field] else ""
            touched = False
            for field, value in new_values.items():
                if value == "":
                    if field in entry:
                        cleared.append(f"{word_id}.{field}")
                elif entry.get(field) != value:
                    entry[field] = value
                    touched = True
            if touched:
                changed.append(word_id)
    if cleared:
        raise ValueError(f"refusing to clear existing fields: {', '.join(cleared)}")
    for path, data in files.items():
        if any(word_id in changed for word_id in data):
            write_json(path, data)
    return changed


def main(argv: list[str] | None = None) -> int:
    """Run the export or apply subcommand."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["export", "apply"])
    args = parser.parse_args(argv)
    if args.command == "export":
        sys.stdout.write(f"wrote {export(SRC, CSV_PATH)} rows to {CSV_PATH.name}\n")
        return 0
    try:
        changed = apply(SRC, CSV_PATH)
    except ValueError as error:
        sys.stderr.write(f"error: {error}\n")
        return 1
    sys.stdout.write(f"changed {len(changed)} ids\n")
    sys.stdout.writelines(f"  {word_id}\n" for word_id in changed)
    if changed:
        sys.stdout.write("now re-run: python scripts/translations.py export\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
