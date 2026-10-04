# Development environment

What a fresh machine needs before it can run this repo's gate or deploy the Claude Code framework.
Each step ends with the command that proves it worked. Windows first, WSL where it differs.

## 1. Git

Install Git for Windows: https://git-scm.com/install/windows. On WSL, `sudo apt-get install -y git`.

```powershell
git --version
```

Set your identity once per machine:

```powershell
git config --global user.name "<name>"
git config --global user.email "<email>"
```

**Line endings.** Repos that carry shell scripts pin them to LF in `.gitattributes`, because bash
fails on CRLF with `\r: command not found`. Do not override that with a global `core.autocrlf`
setting; let the repo decide.

## 2. Python

Install Python 3.12 from https://www.python.org/downloads/ with the **py launcher** option ticked.
The launcher lets several versions coexist and is how Poetry gets pointed at the right one below.

```powershell
py -0          # lists installed versions; 3.12 must be among them
py -3.12 -c "import sys; print(sys.executable)"
```

On WSL, `sudo apt-get install -y python3.12 python3.12-venv`.

## 3. Poetry

Install with the official installer: https://python-poetry.org/docs/#installation. Do not install
it into a project's own virtual environment.

```powershell
poetry --version
poetry config virtualenvs.in-project true
```

`in-project` puts the environment at `<repo>/.venv`, where the editor finds it and `.gitignore`
already hides it.

**Two traps, both silent:**

- **Poetry cannot find `python3.12` by name on Windows.** `poetry env use 3.12` fails with
  *Could not find the python executable python3.12*. Give it the path instead:

  ```powershell
  poetry env use (py -3.12 -c "import sys; print(sys.executable)")
  ```

- **An active `VIRTUAL_ENV` wins over the repo you are standing in.** With a shell that has another
  project's environment activated, `poetry install` installs this repo's dependencies into that
  other environment, reports success, and can downgrade its packages. Before installing, clear it
  and check where Poetry is pointing:

  ```powershell
  $env:VIRTUAL_ENV = $null
  poetry env info --path      # must name the repo you are standing in
  ```

Then, in a clone of this repo:

```powershell
poetry install --with dev
.\syntax.ps1                 # every step green
```

## 4. PowerShell 7

Windows ships PowerShell 5.1. Install PowerShell 7 (`pwsh`) as well:
https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows.

```powershell
pwsh -Command '$PSVersionTable.PSVersion'
```

It is required rather than nice-to-have if you deploy Claude Code hooks written for `pwsh`: on a
5.1-only machine they never fire and nothing says so.

## 5. Claude Code

Install the CLI, not the desktop app: https://code.claude.com/docs/en/quickstart. On WSL, install
the Linux build inside WSL; the Windows install does not serve WSL sessions.

```powershell
claude --version
```

WSL keeps its own configuration tree at `/home/<user>/.claude`, separate from Windows'
`%USERPROFILE%\.claude`. Anything deployed into one is invisible to the other.

## 6. WSL extras

If the framework's hooks run under WSL they parse their input with `jq`:

```bash
sudo apt-get install -y jq
jq --version
```

Continue with [agentic-template.md](agentic-template.md) to deploy the framework.
