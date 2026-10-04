# __init__

**A general-purpose starter repository.** It carries a Python project skeleton with its quality
gate, and setup guides for a development machine. Nothing in it is specific to any organisation,
codebase or domain, and nothing here may become so: every dependency comes from public PyPI, every
CI action from public GitHub, every guide names only public tools.

This file is the project's own instructions. Instruction files loaded from a parent directory
belong to whatever workspace this clone happens to sit in, not to this repo, and do not apply here.

## What this is for

- Starting a new Python project: copy the repo, rename the package, keep the gate.
- Setting up a machine: the guides under `docs/setup/` walk through the tools and the Claude Code
  framework deployment, step by step, with a verification at the end of each.

## Toolchain

- Python `~3.12`, managed by Poetry with a committed `poetry.lock`.
- The gate is `poetry check --lock`, `isort`, `black`, `mypy`, `flake8`, `pytest`, in that order.
  `syntax.ps1` (Windows) and `syntax.sh` (POSIX) run it locally in fix mode; the GitHub Actions
  workflow in `.github/workflows/ci.yml` runs the same tools over the same paths in check mode.
  The two must not drift: a step added to one is added to the other in the same change.
- Line length is 99 everywhere. `mypy` runs strict. Exclusions live in `.flake8` and
  `pyproject.toml`, never on a command line.
- A test that needs an external service is marked `integration`. The gate deselects those; run
  them by hand with `poetry run pytest -m integration`.

## Layout

```
src/init_repo/      the package; rename it together with `name` in pyproject.toml
tests/              pytest, mirrors src/
docs/setup/         machine and framework setup guides
```

## How to work here

- Change only what the request requires, and match the conventions already in the file.
- Write the minimum that solves the problem. No speculative abstractions or error handling.
- A guide states each step's command and how to verify it worked. A step that cannot be verified
  is not finished.
- Never invent a flag, a URL or a command. Check it, or say it is unchecked.
- Log failures in `MISTAKES.md`: what happened, root cause, consequence, and the one rule that
  prevents a repeat. Newest first. Promote a rule into this file once it has repeated.
