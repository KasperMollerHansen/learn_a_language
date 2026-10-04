#!/usr/bin/env bash
# The CI gate, locally, in fix mode. POSIX twin of syntax.ps1; keep the two in step.
set -euo pipefail

step() {
    echo
    echo "=== $1 ==="
    shift
    "$@"
}

step "poetry check --lock" poetry check --lock

# Fix mode, unlike CI's --check. Running the formatters is the point of this script.
step "isort" poetry run isort .
step "black" poetry run black .

step "mypy" poetry run mypy .
step "flake8" poetry run flake8
step "pytest" poetry run pytest

echo
echo "All checks passed."
