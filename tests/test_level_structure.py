from typing import Any, cast

from wordbank import LANGUAGES, level_word_ids, load_wordbank


MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)

# Nouns that correctly take no definite article, by id and the languages where that holds.
BARE_NOUNS: dict[str, set[str]] = {
    **{f"time.{month}": {"spanish", "french"} for month in MONTHS},
    "time.midnight": {"french"},
    "time.christmas": {"french"},
    "time.easter": {"french"},
    "culture.pentecost": {"spanish"},
    "culture.halloween": {"spanish", "french"},
}


def test_chapters_are_tiers_ending_with_review_then_sentence_builder() -> None:
    bank = load_wordbank()
    chapters: dict[int, list[dict[str, Any]]] = {}
    for level in bank["levels"]:
        chapters.setdefault(int(level["id"].split("-")[0]), []).append(level)

    assert list(chapters) == [1, 2, 3, 4, 5]
    for number, levels in chapters.items():
        assert [level["id"] for level in levels] == [
            f"{number}-{index}" for index in range(1, len(levels) + 1)
        ]
        assert len({level["chapter"] for level in levels}) == 1
        *words, sentences, review, builder = levels
        assert sentences["name"] == "Sentences"
        assert review["name"] == "Review"
        assert builder["mode"] == "sentence"
        assert all(level["mode"] in {"word", "article"} for level in words)
        assert review["tiers"] == list(range(1, number + 1))
        assert all(level["tiers"] == [number] for level in [*words, sentences, builder])


def test_every_category_is_in_a_level_and_pools_are_playable() -> None:
    bank = load_wordbank()
    categories = {word_id.split(".")[0] for word_id in bank["words"]}

    assert categories == {category for level in bank["levels"] for category in level["categories"]}
    assert all(
        sum(level["id"].startswith(f"{chapter}-") for level in bank["levels"]) <= 15
        for chapter in range(1, 6)
    )
    assert all(len(level_word_ids(bank, level)) >= 9 for level in bank["levels"])
    modal_ids = [
        word_id
        for level in bank["levels"]
        if level["name"] == "Sentences"
        for word_id in level_word_ids(bank, level)
        if word_id.startswith("modals.")
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


def test_level_prompts_name_languages_only_through_placeholders() -> None:
    bank = load_wordbank()
    language_names = {language.capitalize() for language in LANGUAGES}

    for level in bank["levels"]:
        prompt = level["prompt"].replace("{source}", "").replace("{target}", "")
        assert "{" not in prompt and "}" not in prompt, level["id"]
        assert not language_names & set(prompt.split()), level["id"]


def test_every_word_has_a_tier() -> None:
    bank = load_wordbank()

    assert all(word.get("tier") in {1, 2, 3, 4, 5} for word in bank["words"].values())


def test_every_word_has_a_translation_in_every_language() -> None:
    bank = load_wordbank()

    for word_id, word in bank["words"].items():
        for language in LANGUAGES:
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


def test_reference_spanish_and_french_translations_match_expected_pairs() -> None:
    bank = load_wordbank()
    expected = {
        "people.mother": ("la madre", "la mère"),
        "animals.dog": ("el perro", "le chien"),
        "adjectives.happy": ("feliz", "heureux"),
    }

    for word_id, translations in expected.items():
        word = bank["words"][word_id]
        assert (word["spanish"], word["french"]) == translations


def test_spanish_and_french_nouns_carry_their_definite_article() -> None:
    bank = load_wordbank()
    spanish = ("el ", "la ", "los ", "las ")
    french = ("le ", "la ", "les ", "l'")

    for word_id, word in bank["words"].items():
        if "gender" not in word or word_id.startswith("countries."):
            continue
        bare = BARE_NOUNS.get(word_id, set())
        assert "spanish" in bare or word["spanish"].startswith(spanish), word_id
        assert "french" in bare or word["french"].startswith(french), word_id


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
        "sentence-builder.mand.subject": ("Manden", "Der Mann"),
        "sentence-builder.mand.verb": ("er", "ist"),
        "sentence-builder.mand.adjective": ("stor.", "groß."),
        "sentence-builder.kvinde.subject": ("Kvinden", "Die Frau"),
        "sentence-builder.kvinde.verb": ("er", "ist"),
        "sentence-builder.kvinde.adjective": ("glad.", "glücklich."),
        "sentence-builder.barn.subject": ("Barnet", "Das Kind"),
        "sentence-builder.barn.verb": ("er", "ist"),
        "sentence-builder.barn.adjective": ("lille.", "klein."),
        "sentence-builder.hund.subject": ("Jeg", "Ich"),
        "sentence-builder.hund.verb": ("ser", "sehe"),
        "sentence-builder.hund.object": ("hunden.", "den Hund."),
        "sentence-builder.pige.subject": ("Pigen", "Das Mädchen"),
        "sentence-builder.pige.verb": ("drikker", "trinkt"),
        "sentence-builder.pige.object": ("vand.", "Wasser."),
        "sentence-builder.bror.subject": ("Min bror", "Mein Bruder"),
        "sentence-builder.bror.verb": ("læser", "liest"),
        "sentence-builder.bror.object": ("en bog.", "ein Buch."),
        "sentence-builder.vi.subject": ("Vi", "Wir"),
        "sentence-builder.vi.verb": ("køber", "kaufen"),
        "sentence-builder.vi.object": ("æbler.", "Äpfel."),
        "sentence-builder.hun.subject": ("Hun", "Sie"),
        "sentence-builder.hun.verb": ("taler", "spricht"),
        "sentence-builder.hun.adverb": ("langsomt.", "langsam."),
        "sentence-builder.laerer.subject": ("Læreren", "Der Lehrer"),
        "sentence-builder.laerer.verb": ("åbner", "öffnet"),
        "sentence-builder.laerer.object": ("døren.", "die Tür."),
        "sentence-builder.soster.subject": ("Min søster", "Meine Schwester"),
        "sentence-builder.soster.verb": ("arbejder", "arbeitet"),
        "sentence-builder.soster.place": ("i Berlin.", "in Berlin."),
    }
    sentences: dict[str, list[dict[str, object]]] = {}
    for word_id, chunk in zip(word_ids, chunks):
        if word_id in expected:
            assert (chunk["danish"], chunk["german"]) == expected[word_id]
        sentences.setdefault(cast(str, chunk["sentenceId"]), []).append(chunk)
        assert "sentence" not in chunk and "options" not in chunk, word_id
        # Every option in a sentence's final chunk ends it; no other chunk does.
        last = chunk["step"] == chunk["steps"]
        for language in LANGUAGES:
            options = cast(list[str], chunk[f"{language}Options"])
            assert len(options) == 3, (word_id, language)
            assert len(set(options)) == 3, (word_id, language)
            assert chunk[language] in options, (word_id, language)
            assert all(option.endswith(".") == last for option in options), (word_id, language)
            if chunk[language].endswith(("'", "’")):
                assert all(option.endswith(("'", "’")) for option in options), (word_id, language)

    for parts in sentences.values():
        ordered = sorted(parts, key=lambda chunk: cast(int, chunk["step"]))
        for language in LANGUAGES:
            text = ""
            for chunk in ordered:
                gap = "" if text.endswith(("'", "’")) else " "
                text += (gap if text else "") + cast(str, chunk[language])
            assert text[0].isupper() and text.endswith("."), (parts[0]["sentenceId"], language)

    sentences_per_tier: dict[int, int] = {}
    for parts in sentences.values():
        tier = cast(int, parts[0]["tier"])
        sentences_per_tier[tier] = sentences_per_tier.get(tier, 0) + 1
    assert set(sentences_per_tier) == {1, 2, 3, 4, 5}
    assert min(sentences_per_tier.values()) >= 10
    assert all(
        sorted(cast(int, chunk["step"]) for chunk in parts) == [1, 2, 3]
        for parts in sentences.values()
    )
    assert all(len({chunk["tier"] for chunk in parts}) == 1 for parts in sentences.values())
    assert set(bank["words"]["sentence-builder.mand.subject"]["germanOptions"]) == {
        "Der Mann",
        "Den Mann",
        "Dem Mann",
    }
