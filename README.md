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

## First levels

### Chapter 1 - The basic
- **1-1 People:** 30 words about family, friends, and everyday people.
- **1-2 Tilægsord:** 30 adjectives for describing people and things.
- **1-3 Forholdsord:** 30 common prepositions and place relationships.
- **1-4 People with articles:** 30 people nouns practiced with German definite and indefinite forms.
- **1-5 Animals:** 30 familiar animal names.
- **1-6 Words that look alike:** Danish-German cognates and near-cognates, with attention to spelling changes.

### Chapter 2 - Verbs and sentences
- **2-1 Modalverber:** sentence patterns for *können, müssen, wollen, dürfen, sollen,* and *mögen* across five subjects.
- **2-2 Common verbs:** 30 useful infinitives that can follow modal verbs.
- **2-3 Everyday things:** household, meal, and technology vocabulary.

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

Each difficulty keeps its own unlocked levels and cleared levels (marked ✓). Clearing a level on
Easy counts only for Easy; clearing it on Hard counts for both Hard and Easy. Progress saved by an
earlier version is copied into both difficulties the first time the new version loads.

## Game data

Vocabulary lives in [`src/wordbank/`](src/wordbank) (one file per category plus `grammar.json`) and level lists in [`src/levels/`](src/levels) (one file per chapter), separate from the game code. Each folder has an `index.json` listing its files.
Each lesson curates 30 stable, category-prefixed word IDs from the shared vocabulary map; entries
may be words or practice sentences. This keeps a large vocabulary inventory reusable across short,
focused lessons instead of duplicating translations. Noun entries contain German gender and Danish
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
