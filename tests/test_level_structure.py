from typing import Any, cast

from wordbank import level_word_ids, load_wordbank


def test_chapters_are_tiers_ending_with_review_then_sentence_builder() -> None:
    bank = load_wordbank()
    chapters: dict[int, list[dict[str, Any]]] = {}
    for level in bank["levels"]:
        chapters.setdefault(int(level["id"].split("-")[0]), []).append(level)

    assert list(chapters) == [1, 2, 3]
    for number, levels in chapters.items():
        assert [level["id"] for level in levels] == [
            f"{number}-{index}" for index in range(1, len(levels) + 1)
        ]
        assert len({level["chapter"] for level in levels}) == 1
        *words, sentences, review, builder = levels
        assert sentences["name"] == "Modal verbs"
        assert review["name"] == "Review"
        assert builder["mode"] == "sentence"
        assert all(level["mode"] in {"word", "article"} for level in words)
        assert review["tiers"] == list(range(1, number + 1))
        assert all(level["tiers"] == [number] for level in [*words, sentences, builder])


def test_every_category_is_in_a_theme_level_and_pools_are_playable() -> None:
    bank = load_wordbank()
    themes = [level for level in bank["levels"] if level["name"] != "Review"]
    categories = {word_id.split(".")[0] for word_id in bank["words"]}

    assert categories == {category for level in themes for category in level["categories"]}
    assert all(len(level_word_ids(bank, level)) >= 9 for level in bank["levels"])
    modal_ids = [
        word_id
        for level in bank["levels"]
        if level["name"] == "Modal verbs"
        for word_id in level_word_ids(bank, level)
    ]
    assert {word_id.split(".")[1] for word_id in modal_ids} == {
        "koennen",
        "muessen",
        "wollen",
        "duerfen",
        "sollen",
        "moegen",
    }
    for level in bank["levels"]:
        if level["mode"] != "article":
            continue
        for word_id in level_word_ids(bank, level):
            assert word_id in bank["grammar"]["genitiveNouns"], word_id
            assert bank["words"][word_id].get("gender") in {"der", "die", "das"}, word_id


def test_every_word_has_a_tier() -> None:
    bank = load_wordbank()

    assert all(word.get("tier") in {1, 2, 3} for word in bank["words"].values())


def test_every_word_has_danish_german_and_english_translations() -> None:
    bank = load_wordbank()

    for word_id, word in bank["words"].items():
        for language in ("danish", "german", "english"):
            translation = word.get(language)
            assert isinstance(translation, str), word_id
            assert translation.strip(), word_id
            assert translation == translation.strip(), word_id


def test_reference_translations_match_expected_pairs() -> None:
    bank = load_wordbank()
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
    bank = load_wordbank()
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
    assert bank["grammar"]["caseLabels"] == {
        "nominative": "Nominative",
        "accusative": "Accusative",
        "dative": "Dative",
        "genitive": "Genitive",
    }


def test_sentence_builder_chunks_have_ordered_answers_and_distractors() -> None:
    bank = load_wordbank()
    word_ids = [word_id for word_id in bank["words"] if word_id.startswith("sentence-builder.")]
    chunks = [bank["words"][word_id] for word_id in word_ids]
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
        "sentence-builder.soster.subject": (
            "Min søster",
            "Meine Schwester",
            "Min søster arbejder i Berlin.",
        ),
        "sentence-builder.soster.verb": ("arbejder", "arbeitet", "Min søster arbejder i Berlin."),
        "sentence-builder.soster.place": (
            "i Berlin",
            "in Berlin.",
            "Min søster arbejder i Berlin.",
        ),
    }
    sentences: dict[str, list[dict[str, object]]] = {}
    for word_id, chunk in zip(word_ids, chunks):
        assert (chunk["danish"], chunk["german"], chunk["sentence"]) == expected[word_id]
        sentences.setdefault(cast(str, chunk["sentenceId"]), []).append(chunk)
        options = chunk["options"]
        assert len(options) == 3
        assert len(set(options)) == 3
        assert chunk["german"] in options

    assert len(chunks) == 30
    assert len(sentences) == 10
    assert all(
        sorted(cast(int, chunk["step"]) for chunk in parts) == [1, 2, 3]
        for parts in sentences.values()
    )
    assert all(len({chunk["sentence"] for chunk in parts}) == 1 for parts in sentences.values())
    assert all(len({chunk["tier"] for chunk in parts}) == 1 for parts in sentences.values())
    assert set(bank["words"]["sentence-builder.mand.subject"]["options"]) == {
        "Der Mann",
        "Den Mann",
        "Dem Mann",
    }
