from collections import defaultdict
from typing import Any

import pytest

from wordbank import load_wordbank


BANK = load_wordbank()
GERMAN_BY_DANISH: defaultdict[str, set[str]] = defaultdict(set)
for _entry in BANK["words"].values():
    GERMAN_BY_DANISH[_entry["danish"].strip().lower()].add(_entry["german"])


def accepted_german(word: dict[str, Any]) -> set[str]:
    """Mirror acceptedGerman() in src/index.html: every German valid for this Danish prompt."""
    alternatives = set(word.get("germanAlternatives", []))
    return GERMAN_BY_DANISH[word["danish"].strip().lower()] | alternatives


def article_answer(word_id: str, form: str, case: str) -> str:
    word = BANK["words"][word_id]
    noun = BANK["grammar"]["genitiveNouns"][word_id] if case == "genitive" else word["german"]
    return f"{BANK['grammar']['articles'][form][case][word['gender']]} {noun}"


@pytest.mark.parametrize(
    "level",
    [level for level in BANK["levels"] if level["mode"] in {"word", "article"}],
    ids=lambda level: level["id"],
)
def test_every_word_has_two_unambiguous_distractors(level: dict[str, Any]) -> None:
    for word_id in level["wordIds"]:
        accepted = accepted_german(BANK["words"][word_id])
        eligible = [
            other for other in level["wordIds"] if BANK["words"][other]["german"] not in accepted
        ]
        if level["mode"] == "word":
            assert len({BANK["words"][other]["german"] for other in eligible}) >= 2, word_id
            continue
        for form in ("definite", "indefinite"):
            for case in BANK["grammar"]["cases"]:
                correct = article_answer(word_id, form, case)
                answers = {article_answer(other, form, case) for other in eligible} - {correct}
                assert len(answers) >= 2, (word_id, form, case)
