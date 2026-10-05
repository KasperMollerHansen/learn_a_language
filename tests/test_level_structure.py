import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_level_structure_matches_plan() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    level_ids = [level["id"] for level in bank["levels"]]
    level_names = [level["name"] for level in bank["levels"]]

    assert level_ids == ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "2-1", "2-2", "2-3", "2-4"]
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
        "Sentence builder",
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


def test_every_word_has_danish_and_german_translations() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))

    for word_id, word in bank["words"].items():
        for language in ("danish", "german"):
            translation = word.get(language)
            assert isinstance(translation, str), word_id
            assert translation.strip(), word_id
            assert translation == translation.strip(), word_id


def test_reference_translations_match_expected_pairs() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    expected = {
        "people.mother": ("mor", "Mutter"),
        "adjectives.happy": ("glad", "glücklich"),
        "prepositions.in": ("i", "in"),
        "animals.dog": ("hund", "Hund"),
        "verbs.be": ("at være", "sein"),
        "modals.koennen.ich": ("Jeg kan svømme.", "Ich kann schwimmen."),
        "everyday.breakfast": ("morgenmad", "Frühstück"),
    }

    for word_id, translations in expected.items():
        word = bank["words"][word_id]
        assert (word["danish"], word["german"]) == translations


def test_german_article_declensions_match_expected_forms() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    expected = {
        "definite": {
            "nominative": {"der": "der", "die": "die", "das": "das"},
            "accusative": {"der": "den", "die": "die", "das": "das"},
            "dative": {"der": "dem", "die": "der", "das": "dem"},
            "genitive": {"der": "des", "die": "der", "das": "des"},
        },
        "indefinite": {
            "nominative": {"der": "ein", "die": "eine", "das": "ein"},
            "accusative": {"der": "einen", "die": "eine", "das": "ein"},
            "dative": {"der": "einem", "die": "einer", "das": "einem"},
            "genitive": {"der": "eines", "die": "einer", "das": "eines"},
        },
    }

    assert bank["grammar"]["articles"] == expected


def test_sentence_builder_chunks_have_ordered_answers_and_distractors() -> None:
    bank = json.loads((ROOT / "wordbank.json").read_text(encoding="utf-8"))
    level = next(level for level in bank["levels"] if level["mode"] == "sentence")
    chunks = [bank["words"][word_id] for word_id in level["wordIds"]]
    expected = {
        "sentence-builder.mand.subject": ("Manden", "Der Mann", "Manden er stor."),
        "sentence-builder.mand.verb": ("er", "ist", "Manden er stor."),
        "sentence-builder.mand.adjective": ("stor", "groß.", "Manden er stor."),
        "sentence-builder.kvinde.subject": ("Kvinden", "Die Frau", "Kvinden er glad."),
        "sentence-builder.kvinde.verb": ("er", "ist", "Kvinden er glad."),
        "sentence-builder.kvinde.adjective": ("glad", "glücklich.", "Kvinden er glad."),
        "sentence-builder.barn.subject": ("Barnet", "Das Kind", "Barnet er lille."),
        "sentence-builder.barn.verb": ("er", "ist", "Barnet er lille."),
        "sentence-builder.barn.adjective": ("lille", "klein.", "Barnet er lille."),
        "sentence-builder.hund.subject": ("Jeg", "Ich", "Jeg ser hunden."),
        "sentence-builder.hund.verb": ("ser", "sehe", "Jeg ser hunden."),
        "sentence-builder.hund.object": ("hunden", "den Hund.", "Jeg ser hunden."),
        "sentence-builder.pige.subject": ("Pigen", "Das Mädchen", "Pigen drikker vand."),
        "sentence-builder.pige.verb": ("drikker", "trinkt", "Pigen drikker vand."),
        "sentence-builder.pige.object": ("vand", "Wasser.", "Pigen drikker vand."),
        "sentence-builder.bror.subject": ("Min bror", "Mein Bruder", "Min bror læser en bog."),
        "sentence-builder.bror.verb": ("læser", "liest", "Min bror læser en bog."),
        "sentence-builder.bror.object": ("en bog", "ein Buch.", "Min bror læser en bog."),
        "sentence-builder.vi.subject": ("Vi", "Wir", "Vi køber æbler."),
        "sentence-builder.vi.verb": ("køber", "kaufen", "Vi køber æbler."),
        "sentence-builder.vi.object": ("æbler", "Äpfel.", "Vi køber æbler."),
        "sentence-builder.hun.subject": ("Hun", "Sie", "Hun taler langsomt."),
        "sentence-builder.hun.verb": ("taler", "spricht", "Hun taler langsomt."),
        "sentence-builder.hun.adverb": ("langsomt", "langsam.", "Hun taler langsomt."),
        "sentence-builder.laerer.subject": ("Læreren", "Der Lehrer", "Læreren åbner døren."),
        "sentence-builder.laerer.verb": ("åbner", "öffnet", "Læreren åbner døren."),
        "sentence-builder.laerer.object": ("døren", "die Tür.", "Læreren åbner døren."),
        "sentence-builder.soster.subject": ("Min søster", "Meine Schwester", "Min søster arbejder i Berlin."),
        "sentence-builder.soster.verb": ("arbejder", "arbeitet", "Min søster arbejder i Berlin."),
        "sentence-builder.soster.place": ("i Berlin", "in Berlin.", "Min søster arbejder i Berlin."),
    }
    sentences: dict[str, list[dict[str, object]]] = {}
    for word_id, chunk in zip(level["wordIds"], chunks):
        assert (chunk["danish"], chunk["german"], chunk["sentence"]) == expected[word_id]
        sentences.setdefault(chunk["sentenceId"], []).append(chunk)
        options = chunk["options"]
        assert len(options) == 3
        assert len(set(options)) == 3
        assert chunk["german"] in options

    assert len(chunks) == 30
    assert len(sentences) == 10
    assert all(sorted(chunk["step"] for chunk in parts) == [1, 2, 3] for parts in sentences.values())
    assert all(len({chunk["sentence"] for chunk in parts}) == 1 for parts in sentences.values())
    assert set(bank["words"]["sentence-builder.mand.subject"]["options"]) == {
        "Der Mann",
        "Den Mann",
        "Dem Mann",
    }
