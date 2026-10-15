# Wortlauf

Wortlauf is a small Danish-to-German vocabulary runner, built as an installable progressive web app
(PWA). It runs in a modern browser and does not need a JavaScript build step.

## Play locally

With Python installed, run this from the repository root:

```powershell
python -m http.server 8000 --directory src
```

Open <http://localhost:8000>. The game also caches its files for offline use after the first visit.

## Install on a phone

Publish the repository's static files to an HTTPS host, then open its URL on the phone. In Android
Chrome, use **Install app** or **Add to Home screen**. On iPhone, open the URL in Safari, tap Share,
then **Add to Home Screen**. The game must be served from HTTPS (or localhost) for installation
and offline caching to work; opening `index.html` directly is only suitable for a quick look.

## Levels

There are five chapters, one per word tier, following the CEFR steps: **1 · Basics** (A1),
**2 · Everyday** (A2), **3 · Confident** (B1), **4 · Fluent** (B2) and **5 · Advanced** (C1). A
chapter uses only words of its own tier, except the review. Every chapter has the same shape:

1. **Word levels**, one per theme: People, People with articles (German definite and indefinite
   forms in all four cases), Describing words, Small words, Verbs, Food and drink, Home, Body and
   clothes, Nature, Town and travel, Free time, Work and school, and Words that look alike. A
   theme gets a level in a chapter only when that tier has at least 15 words.
2. **Sentences:** short Danish sentences to translate, including the modal verbs *können, müssen,
   wollen, dürfen, sollen* and *mögen*.
3. **Review:** mixed words from every theme, this chapter's tier and all earlier ones.
4. **Sentence builder:** build a German sentence one chunk at a time.

The level files are generated: edit `THEMES` or `CHAPTERS` in [`scripts/levels.py`](scripts/levels.py)
and run `python scripts/levels.py`. A test fails if the level files drift from the generator.

Levels are cleared from the top: a level opens once every level above it is cleared, and the menu
starts on the first level not yet cleared.

- Catch all 30 words before the clock runs out. The Danish prompt sits ahead of the stationary
  gates, and the runner advances toward them for each timed choice. A correct pass speeds up the
  next approach; a miss bounces the runner back, slows the next approach, and retries the same word.
  The first approach takes 4.2 seconds. Only one gate is ever a correct answer: a German word that also translates the Danish prompt (for
  example *unterhalb* for "under") is never shown as a wrong gate. Tap a gate on a phone, or use
  the arrow keys and number keys on a keyboard.

## Easy and Hard

Pick the difficulty with the **Easy / Hard** toggle above the level list. New players start on Easy.

| | Round length | Approach speed-up per correct pass | Slow-down per miss |
|---|---|---|---|
| Easy | 2½ minutes (150 s) | ÷ 1.085 | × 1.2 |
| Hard | 2 minutes (120 s) | ÷ 1.1 | × 1.3 |

Each difficulty keeps its own cleared levels (marked ✓). Clearing a level on Easy counts only for
Easy; clearing it on Hard counts for both Hard and Easy. The chaptered levels replaced the old level
list, so progress from an earlier version keeps only its difficulty and answer counters.

## Game data

Vocabulary lives in [`src/wordbank/`](src/wordbank) (one file per category plus `grammar.json`) and level lists in [`src/levels/`](src/levels) (one file per chapter), separate from the game code. Each folder has an `index.json` listing its files.
Every entry carries an `english` gloss as well as the Danish and German, and every word a difficulty `tier` from 1 to 5 (CEFR A1, A2, B1, B2, C1). A level does not list words:
it names `categories` (the word ID prefix, e.g. `people`) and optionally `tiers`, and its pool is
every matching word. A run deals 30 questions from that pool, reshuffling when the pool is smaller,
so growing the word bank grows the levels without editing them. Entries may be words or practice
sentences. Noun entries contain German gender and Danish
article forms. The word bank also stores German article declensions and genitive noun forms.
Pacing and scoring live in
[`config.json`](src/config.json), so you can tune the round duration, speed multiplier, penalties, and
transitions without changing JavaScript. The per-difficulty values (round duration and the two gate
speed multipliers) sit under `difficulties.easy` and `difficulties.hard`. A word entry may list
`germanAlternatives`: other German answers that are also correct for its Danish prompt, which are
then never offered as wrong gates.

## Reviewing translations

1. `poetry run python scripts/translations.py export` writes `translations.csv` (`;`-separated, UTF-8 with BOM, opens in Excel with æøå/ß intact). Re-running it keeps your `checked` and `comment` columns.
2. Review in Excel and correct danish, german, gender, danishDefinite, danishIndefinite or options (separate options with ` | `). Use `checked` and `comment` for your own notes. Save as CSV (semicolon-delimited), keeping the same file name.
3. `poetry run python scripts/translations.py apply` writes the changed cells back into `src/wordbank/*.json` and lists the changed ids. It refuses unknown ids and refuses to blank a field that has a value.
4. Re-run `export` afterwards so the CSV matches the wordbank; a test fails if they drift.

## Publish and install on a phone

The GitHub Actions workflow deploys the static app to GitHub Pages whenever changes reach `main`.
In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.
After the workflow succeeds, open <https://kaspermollerhansen.github.io/learn_a_language/> on a
phone and use the browser's **Add to Home Screen** or **Install app** option. Progress is stored
locally in that browser; it does not sync between devices.

## Python quality gate

Runs locally in fix mode with `.\syntax.ps1` (or `./syntax.sh`), and in check mode on every push
and pull request through GitHub Actions:

```
poetry check --lock, isort, black, mypy, flake8, pytest
```

## Setup guides

| Guide | What it covers |
|---|---|
| [docs/setup/development-environment.md](docs/setup/development-environment.md) | Git, Python, Poetry, PowerShell 7 and Claude Code on a fresh machine, with the traps hit on the way |
| [docs/setup/agentic-template.md](docs/setup/agentic-template.md) | Deploying a shared Claude Code framework (agents, skills, commands, hooks, settings) from a git clone by symlink, on Windows and WSL |

## Layout

```
src/                the static app
  index.html          the game and level flow
  config.json         pacing and scoring settings
  wordbank/           Danish-German vocabulary, one file per category, plus grammar
  levels/             level lists, one file per chapter
  service-worker.js   offline app and data cache
tests/              pytest
docs/setup/         the guides above
```
