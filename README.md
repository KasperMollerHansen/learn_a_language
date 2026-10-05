# Wortlauf

Wortlauf is a small Danish-to-German vocabulary runner, built as an installable progressive web app
(PWA). It runs in a modern browser and does not need a JavaScript build step.

## Play locally

With Python installed, run this from the repository root:

```powershell
python -m http.server 8000
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
- **1-2 Adjective:** 30 words for a first pass at descriptive vocabulary.
- **1-3 Tilægsord:** 30 Danish/German adjective pairs to reinforce the same pattern.
- **1-4 People with articles:** 30 people nouns practiced with German definite and indefinite forms.
- **1-5 Sentences:** 30 words chosen one at a time to build sentence rhythm and recall.

### Chapter 2 - More advanced
- **2-1 More advanced:** a next-step set for broader vocabulary and faster recall.

- Catch all 30 words within two minutes. The Danish prompt sits ahead of the stationary gates, and
  the runner advances toward them for each timed choice. A correct pass speeds up the next run by
  1.1; a miss bounces the runner back, slows the next approach, and retries the same word. The first
  approach takes 3.5 seconds. Tap a gate on a phone, or use the arrow keys and number keys on a
  keyboard.

## Game data

Vocabulary and level lists live in [`wordbank.json`](wordbank.json), separate from the game code.
Each level references 30 word IDs; entries contain Danish forms, German nouns, and gender. The word
bank also stores article declensions and genitive noun forms. Pacing and scoring live in
[`config.json`](config.json), so you can tune the round duration, speed multiplier, penalties, and
transitions without changing JavaScript.

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
index.html          the game and level flow
config.json         pacing and scoring settings
wordbank.json       levels and Danish-German vocabulary
service-worker.js   offline app and data cache
src/init_repo/      the package
tests/              pytest
docs/setup/         the guides above
```
