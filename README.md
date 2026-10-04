# __init__

A general-purpose starter: a Python project skeleton with its quality gate, and setup guides for a
development machine. Public tools only, nothing organisation-specific.

## Starting a project from it

```powershell
poetry install --with dev
poetry run pytest
```

Then rename `src/init_repo` and the `name` field in `pyproject.toml` together.

## The gate

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
src/init_repo/      the package
tests/              pytest
docs/setup/         the guides above
```
