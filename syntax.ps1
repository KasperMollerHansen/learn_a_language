# The CI gate, locally, in fix mode: the same tools over the same paths as
# .github/workflows/ci.yml, so this cannot pass where CI fails. Exclusions live in .flake8 and
# pyproject.toml, never here. Exits non-zero on the first failing step.

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Step
    )
    Write-Output ""
    Write-Output "=== $Name ==="
    & $Step
    if ($LASTEXITCODE -ne 0) {
        Write-Output ""
        Write-Output "FAILED: $Name (exit $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
}

Invoke-Step "poetry check --lock" { poetry check --lock }

# Fix mode, unlike CI's --check. Running the formatters is the point of this script.
Invoke-Step "isort" { poetry run isort . }
Invoke-Step "black" { poetry run black . }

Invoke-Step "mypy" { poetry run mypy . }
Invoke-Step "flake8" { poetry run flake8 }
Invoke-Step "pytest" { poetry run pytest }

Write-Output ""
Write-Output "All checks passed."
