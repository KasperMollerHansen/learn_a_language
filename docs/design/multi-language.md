# Multi-language: "I speak X, I learn Y"

Status: implemented (rollout steps 1 and 2). Covers Danish, German, English, Spanish and French in any of the 20 ordered pairs
(`da-de`, `da-en`, `da-es`, `da-fr`, `de-da`, ... `fr-es`).

Every word entry carries `danish`, `german`, `english`, `spanish` and `french` (a test enforces it), so word
mode needs no new data for any pair. The work is mostly in `src/index.html`, which hardcodes
`danish` as the prompt and `german` as the answer.

## 1. Choosing the pair

- **First launch** (no saved progress): a pair screen replaces the menu until a pair is picked.
- **Existing players** (v2 progress found) skip it and land on `da-de`.
- **Later**: the header label `Danish / German` becomes a button showing the current pair; it
  opens the same screen. Switching pair switches the level list and progress track.

```
I speak    [ Danish ]  [ German ]  [ English ]  [ Spanish ]  [ French ]
I learn    the same list without the spoken language
           [ Start ]
```

Language buttons use the English name of each language, like the rest of the UI; translating the UI is out of scope.

## 2. Question logic per pair

One module owns the pair: `pair = { source: "danish", target: "german" }`. All question code
reads `word[pair.source]` for the prompt and `word[pair.target]` for the answer.

- `danishKey` / `germanByDanish` / `acceptedGerman` become `answersByPrompt` (built when the pair
  is set: normalised source text to the set of target texts) and `acceptedAnswers(word)` =
  `answersByPrompt[word[source]]` plus `word[target + "Alternatives"]`. So `germanAlternatives`
  keeps its meaning, and `danishAlternatives` / `englishAlternatives` are added where needed.
  Alternatives belong to the target word, not the pair: *unterhalb* is a correct German answer for
  "under" whether the prompt is Danish or English.
- **Word mode** works for all 20 pairs. Modal sentences (`modals.*`) are word-mode entries with full
  sentences in all three fields, so they work too.
- **Article mode** only applies when the target is German and the source is Danish or English: Spanish and French nouns carry their own article, which would contradict the definite/indefinite hint. Prompt by source: Danish shows
  `danishDefinite` / `danishIndefinite` as today; English shows the bare `english` noun (the label
  already says definite/indefinite). Levels in this mode are hidden for every other pair. A Danish en/et mode is a separate later mode, not a variant of this one.
- **Sentence mode** works for all 20 pairs. Each chunk is one meaning slot holding its text in all
  five languages, in the same step order, and `<language>Options` with the wrong gates for that
  target. The prompt sentence is the source chunks joined by spaces, except after an apostrophe
  (French elision: "J'" + "ai"), so each language's final chunk carries the full stop.
- The code holds one table of which pairs each mode supports; the menu lists only playable levels.
- **Prompt texts**: a level's `prompt` uses placeholders, e.g. `Find the {target} word for`,
  `Translate the {source} sentence into {target}`. The other hardcoded copy ("German chunk",
  "Choose the German form", the overlay texts in `selectLevel`, the intro text, "Sehr gut!") gets the
  same treatment.

## 3. Wordbank needs

| Target | Needs |
|---|---|
| German (`da-de`, `en-de`) | Nothing. |
| English (`da-en`, `de-en`) | `englishAlternatives` where the distractor test finds ambiguity. |
| Danish (`de-da`, `en-da`) | `danishAlternatives` likewise. Gender for a future en/et mode comes from the `danishIndefinite` prefix, no new field. |
| Spanish, French | `spanish` / `french` on every entry; nouns (entries with `gender`, except `countries.`) carry the definite article (*el perro*, *le chien*, *l'eau*). `spanishAlternatives` / `frenchAlternatives` where the distractor test finds ambiguity. |

German as the source is ambiguous (*sie/Sie*, noun and verb sharing a word once lowercased, *Uhr*).
`answersByPrompt` handles it: every entry with the same normalised prompt counts as correct, so
none of them is shown as a wrong gate.

Adjectives and prepositions no longer carry placeholder noun fields (`gender`, `danishDefinite`,
`danishIndefinite`); those fields now exist only on nouns, so `gender` marks a noun.

Tiers stay one per entry. They describe how common the concept is, which is close enough across
the five languages.

## 4. Progress

New key `wortlauf-progress-v4` (v3 is the chaptered single-pair format); difficulty is global, everything else is per pair:

```json
{ "version": 4, "pair": "da-de", "difficulty": "easy", "lastPlayedAt": "...",
  "pairs": { "da-de": { "tracks": { "easy": {}, "hard": {} },
                        "correctAnswers": 0, "wrongAnswers": 0, "completedRuns": 0 } } }
```

`loadProgress` reads v4, else migrates v3 into `pairs["da-de"]` with `pair: "da-de"`. Old keys
stay untouched. No saved progress means no `pair`, which shows the pair screen. Unlocking is
already by level id (a level opens when every level above it is cleared), so a pair whose
filtered list hides some levels only needs the "above it" check to run over its own list.

## 5. Levels

Levels stay pair-agnostic: `categories` and `tiers` pick the pool, `mode` decides which pairs can
play it, `prompt` uses placeholders. The level redesign only has to follow three rules:

- no language name in level data outside `{source}` / `{target}`;
- each chapter needs word-mode levels, or it is empty for pairs without German as target;
- unlock by level id rather than index, since hiding levels per pair already makes indexes differ.

## 6. Rollout and tests

1. **Pair seam, no visible change.** Introduce `pair`, `answersByPrompt`, prompt placeholders and
   v3 progress with `da-de` fixed. Verify by hand: seed a v2 entry in localStorage, reload, and
   check levels, ticks and counters are unchanged.
2. **Pair screen and word mode for all 20 pairs.** Add alternatives where the tests below fail;
   enable only pairs whose tests pass (now all 20). Article mode also for `en-de`.
3. **Later, if wanted:** a Danish en/et mode (after the noun-field cleanup).

Test changes, in `tests/`:

- `wordbank.py`: a `PAIRS` list and the mode-to-pairs table, mirroring `index.html`.
- `test_distractors.py`: `accepted_german` becomes `accepted_answers(word, source, target)`;
  parametrize over every (level, pair) the level's mode supports.
- `test_distractors.py` checks linearly: every word has at least two distractors that no accepted
  answer matches, per (level, pair), rather than comparing all pairs of words.
- `test_level_structure.py`: the Spanish and French article test requires each noun to start with
  its definite article, except the ids listed in `BARE_NOUNS` (months, midnight, Christmas,
  Easter, Pentecost, Halloween). The sentence-builder test joins chunks the way the page does
  (no space after an apostrophe) and checks each sentence starts upper-case and ends with a full stop.
- `test_level_structure.py`: level prompts contain no literal `Danish` / `German` / `English`, and
  only the `{source}` / `{target}` placeholders; `<language>Alternatives` keys name one of the five
  languages.
- `scripts/translations.py` and `test_translations.py`: export and apply the new alternatives
  columns.
