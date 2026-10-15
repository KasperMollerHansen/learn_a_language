# Multi-language: "I speak X, I learn Y"

Status: proposal. Covers Danish, German and English in any of the 6 ordered pairs
(`da-de`, `da-en`, `de-da`, `de-en`, `en-da`, `en-de`). Today the app is `da-de` only.

Every word entry already carries `danish`, `german` and `english` (a test enforces it), so word
mode needs no new data for any pair. The work is mostly in `src/index.html`, which hardcodes
`danish` as the prompt and `german` as the answer.

## 1. Choosing the pair

- **First launch** (no saved progress): a pair screen replaces the menu until a pair is picked.
- **Existing players** (v2 progress found) skip it and land on `da-de`.
- **Later**: the header label `Danish / German` becomes a button showing the current pair; it
  opens the same screen. Switching pair switches the level list and progress track.

```
I speak    [ Dansk ]  [ Deutsch ]  [ English ]
I learn    [ Deutsch ]  [ English ]        (the spoken language is not offered)
           [ Start ]
```

Language buttons use each language's own name so a reader finds theirs. The rest of the UI stays
English; translating the UI is out of scope.

## 2. Question logic per pair

One module owns the pair: `pair = { source: "danish", target: "german" }`. All question code
reads `word[pair.source]` for the prompt and `word[pair.target]` for the answer.

- `danishKey` / `germanByDanish` / `acceptedGerman` become `answersByPrompt` (built when the pair
  is set: normalised source text to the set of target texts) and `acceptedAnswers(word)` =
  `answersByPrompt[word[source]]` plus `word[target + "Alternatives"]`. So `germanAlternatives`
  keeps its meaning, and `danishAlternatives` / `englishAlternatives` are added where needed.
  Alternatives belong to the target word, not the pair: *unterhalb* is a correct German answer for
  "under" whether the prompt is Danish or English.
- **Word mode** works for all 6 pairs. Modal sentences (`modals.*`) are word-mode entries with full
  sentences in all three fields, so they work too.
- **Article mode** only applies when the target is German. Prompt by source: Danish shows
  `danishDefinite` / `danishIndefinite` as today; English shows the bare `english` noun (the label
  already says definite/indefinite). Levels in this mode are hidden for `da-en`, `de-da`, `de-en`
  and `en-da`. A Danish en/et mode is a separate later mode, not a variant of this one.
- **Sentence mode** stays `da-de` only. A chunk's `sentence`, its step order and its `options` are
  written for a Danish sentence built in German word order; other pairs need their own sentences.
  Hidden for the other 5 pairs.
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

German as the source is ambiguous (*sie/Sie*, noun and verb sharing a word once lowercased, *Uhr*).
`answersByPrompt` handles it: every entry with the same normalised prompt counts as correct, so
none of them is shown as a wrong gate.

Adjectives and prepositions no longer carry placeholder noun fields (`gender`, `danishDefinite`,
`danishIndefinite`); those fields now exist only on nouns, so `gender` marks a noun.

Tiers stay one per entry. They describe how common the concept is, which is close enough across
the three languages.

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
2. **Pair screen and word mode for all 6 pairs.** Add alternatives where the tests below fail;
   enable only pairs whose tests pass. Article mode also for `en-de`.
3. **Later, if wanted:** a Danish en/et mode (after the noun-field cleanup) and sentence sets for
   other pairs.

Test changes, in `tests/`:

- `wordbank.py`: a `PAIRS` list and the mode-to-pairs table, mirroring `index.html`.
- `test_distractors.py`: `accepted_german` becomes `accepted_answers(word, source, target)`;
  parametrize over every (level, pair) the level's mode supports.
- `test_level_structure.py`: level prompts contain no literal `Danish` / `German` / `English`, and
  only the `{source}` / `{target}` placeholders; `<language>Alternatives` keys name one of the three
  languages.
- `scripts/translations.py` and `test_translations.py`: export and apply the new alternatives
  columns.
