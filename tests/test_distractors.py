from collections import defaultdict
from typing import Any

import pytest

from wordbank import MODE_PAIRS, PAIRS, level_word_ids, load_wordbank


BANK = load_wordbank()


def answers_by_prompt(source: str, target: str) -> defaultdict[str, set[str]]:
    """Mirror answersByPrompt in src/index.html: normalised prompt to every target text."""
    answers: defaultdict[str, set[str]] = defaultdict(set)
    for entry in BANK["words"].values():
        answers[entry[source].strip().lower()].add(entry[target])
    return answers


ANSWERS = {pair: answers_by_prompt(*pair) for pair in PAIRS}


def accepted_answers(word: dict[str, Any], source: str, target: str) -> set[str]:
    """Mirror acceptedAnswers() in src/index.html: every target valid for this word's prompt."""
    alternatives = set(word.get(f"{target}Alternatives", []))
    return ANSWERS[(source, target)][word[source].strip().lower()] | alternatives


def article_answer(word_id: str, form: str, case: str) -> str:
    word = BANK["words"][word_id]
    noun = BANK["grammar"]["genitiveNouns"][word_id] if case == "genitive" else word["german"]
    return f"{BANK['grammar']['articles'][form][case][word['gender']]} {noun}"


@pytest.mark.parametrize(
    ("level", "source", "target"),
    [
        pytest.param(level, source, target, id=f"{level['id']}-{source}-{target}")
        for level in BANK["levels"]
        if level["mode"] in {"word", "article"}
        for source, target in MODE_PAIRS[level["mode"]]
    ],
)
def test_every_word_has_two_unambiguous_distractors(
    level: dict[str, Any], source: str, target: str
) -> None:
    pool = level_word_ids(BANK, level)
    targets = {word_id: BANK["words"][word_id][target] for word_id in pool}
    if level["mode"] == "word":
        distinct = set(targets.values())
        for word_id in pool:
            accepted = accepted_answers(BANK["words"][word_id], source, target)
            assert len(distinct - accepted) >= 2, word_id
        return
    forms = [
        (form, case, {other: article_answer(other, form, case) for other in pool})
        for form in ("definite", "indefinite")
        for case in BANK["grammar"]["cases"]
    ]
    for word_id in pool:
        accepted = accepted_answers(BANK["words"][word_id], source, target)
        eligible = [other for other in pool if targets[other] not in accepted]
        for form, case, answers_by_word in forms:
            answers = {answers_by_word[other] for other in eligible} - {answers_by_word[word_id]}
            assert len(answers) >= 2, (word_id, form, case)
