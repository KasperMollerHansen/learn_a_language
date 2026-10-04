# Deploying a shared Claude Code framework

How to put a team's Claude Code framework, kept in a git repository, onto a machine so that a
`git pull` updates it everywhere. The repository this guide assumes is laid out as the
"AgenticTemplate" pattern:

```
<clone>/
└── claude_setup/
    ├── repos_root/
    │   ├── CLAUDE.md                 engineering principles, loaded by every session under the repos root
    │   └── .claude/
    │       ├── agents/               specialist subagents, one .md each
    │       ├── skills/               reusable skills, one <name>/SKILL.md each
    │       ├── commands/             slash commands, one .md each
    │       ├── hooks/                guardrail and refresh hooks, each as .ps1 plus a .sh port
    │       ├── settings.json         permission baseline plus the Windows hook wiring
    │       └── settings.wsl.json     the same baseline, hooks wired to bash and the .sh ports
    └── setup/
        ├── setup-symlinks.ps1        deploy or undo, Windows
        └── setup-wsl-symlinks.sh     deploy or undo, WSL
```

Prerequisites are in [development-environment.md](development-environment.md). Any step your own
template adds beyond these, such as registering an MCP server or cloning a companion repo, is
documented in that template's README, not here.

## How it works

Claude Code finds agents, skills, commands and `settings.json` in exactly two places: the session's
own `<cwd>/.claude/` and the user scope `~/.claude/`. It does not walk up the directory tree for
them, so a framework placed at a workspace root is invisible to sessions started in a sub-repo.
`CLAUDE.md` is the exception: Claude Code does walk up the tree for it.

The deployment therefore links the framework at user scope and `CLAUDE.md` at the workspace root:

| Source in the clone | Destination | Method |
|---|---|---|
| `repos_root/CLAUDE.md` | `<ReposRoot>/CLAUDE.md` | file symlink |
| `repos_root/.claude/agents/` | `~/.claude/agents/` | directory symlink |
| `repos_root/.claude/skills/` | `~/.claude/skills/` | directory symlink |
| `repos_root/.claude/commands/` | `~/.claude/commands/` | directory symlink |
| `repos_root/.claude/hooks/` | `~/.claude/hooks/` | directory symlink |
| `repos_root/.claude/settings.json` | `~/.claude/settings.json` | file symlink |

`<ReposRoot>` is the parent directory of the clone by default. The setup scripts detect it as two
levels above `claude_setup/` and accept an override (`-ReposRoot` on Windows, `--repos-root` on
WSL) when the clone lives somewhere else.

Because the directories are linked whole, a new agent, skill or command dropped into the clone is
live immediately and needs no re-run. Only a new single-file target, such as a second settings
file, needs an entry added to the script and one re-run.

Two things the deployment deliberately leaves alone: personal preferences (`~/.claude.json`,
managed by `/config`) and Claude Code's per-repo memory. Neither is shared through the template.

## Install on Windows

1. Clone the template repository into the folder that will be your repos root, so the clone is a
   direct child of it. Sibling repos under that root inherit the linked `CLAUDE.md`.
2. Open PowerShell 7 as Administrator, or enable Windows Developer Mode, which allows symlinks
   without elevation. The script checks for one of the two before it starts.
3. Run the deploy script:

   ```powershell
   cd <clone>\claude_setup\setup
   .\setup-symlinks.ps1
   ```

   If it is refused as not digitally signed:

   ```powershell
   pwsh -ExecutionPolicy Bypass -File .\setup-symlinks.ps1
   ```

4. Verify. Every entry should report `SymbolicLink` and a target inside the clone:

   ```powershell
   Get-Item ~\.claude\agents, ~\.claude\skills, ~\.claude\commands, ~\.claude\hooks, ~\.claude\settings.json |
       Select-Object Name, LinkType, Target
   Get-Item <ReposRoot>\CLAUDE.md | Select-Object LinkType, Target
   ```

   Then start a Claude Code session anywhere under the repos root and type one of the template's
   slash commands. Tab completion listing it is the proof it loaded.

The script is idempotent: an existing correct link is skipped, and a real file already sitting at a
destination is backed up with a timestamp suffix rather than overwritten. `.\setup-symlinks.ps1 -Undo`
removes every link the script created and refuses to delete anything that is not a symlink.

## Install on WSL

WSL has its own `~/.claude`, so deploy there separately if you run Claude Code inside it. The bash
script wires `settings.wsl.json` in place of `settings.json`, so the hooks run under bash and the
`.sh` ports.

It also deploys every target as a **bind mount** rather than a symlink. Windows Explorer cannot
follow Linux symlinks over `\\wsl.localhost` and shows them as unreadable 0-byte files. A bind
mount exposes the real files, stays live with the clone, and is persisted across WSL restarts in a
managed block in `/etc/fstab`. That needs `sudo` once. Without `sudo` the script falls back to
symlinks, which work for Claude Code but not for Explorer.

1. Install `git` and `jq` inside WSL. `jq` is a hard requirement: the guard hooks parse their
   payload with it and the script refuses to deploy without it, because a hook that cannot parse
   its input fails open.
2. Clone the template into your WSL repos root, for example `~/src/`.
3. Run the deploy script and enter your password at the `sudo` prompt:

   ```bash
   bash ~/src/<clone>/claude_setup/setup/setup-wsl-symlinks.sh
   ```

4. Verify:

   ```bash
   for d in agents skills commands hooks; do mountpoint ~/.claude/$d; done
   mountpoint ~/.claude/settings.json
   mountpoint <ReposRoot>/CLAUDE.md
   head -1 <ReposRoot>/CLAUDE.md
   ```

   Every `mountpoint` line says `is a mountpoint`, and `head` prints the first line of the real
   file. In Windows Explorer, `\\wsl.localhost\<distro>\home\<user>\.claude\agents` opens as an
   ordinary folder.

`setup-wsl-symlinks.sh --undo` unmounts everything, removes the emptied mount points and strips
the `/etc/fstab` block.

**Caveat on bind mounts.** A symlink always resolves; a bind mount is re-applied at each WSL boot
from `/etc/fstab`, which needs WSL's `automount.mountFsTab` left at its default of on. If the clone
is moved or deleted, or that setting is turned off, the targets come up empty: a blank `CLAUDE.md`,
no agents or skills, and hooks that fail loudly. Re-running the script repairs it.

## Alternative: copy once, no sync

To restore a framework once without git: copy `agents/`, `skills/`, `commands/`, `hooks/` and
`settings.json` from `repos_root/.claude/` into `~/.claude/`, and `repos_root/CLAUDE.md` to
`<ReposRoot>/CLAUDE.md`. `hooks/` is not optional: `settings.json` references hooks by path, and a
missing directory makes every tool call fail noisily. Nothing refreshes afterwards, and any step
the deploy script performs beyond linking, such as setting environment variables the refresh hooks
read, is not done.

## Everyday workflow once deployed

1. Edit or add an agent, skill, command or hook in the clone. The user-scope directories are the
   same files on disk, so the change is live in the next session.
2. Commit and push in the template repository.
3. On every other machine, `git pull`. Nothing else.

Conventions that keep the two platforms in step:

- New skills go in as `skills/<name>/SKILL.md`, commands as `commands/<name>.md`.
- A hook is written twice, `hooks/<name>.ps1` and `hooks/<name>.sh`, and wired in both
  `settings.json` and `settings.wsl.json`. A behavioural difference between the two ports is a bug.
- The two settings files match except for their hooks block. Check with:

  ```bash
  diff <(jq -S 'del(.hooks)' settings.json) <(jq -S 'del(.hooks)' settings.wsl.json)
  ```

  No output means they agree.
- `*.sh` is pinned to LF in `.gitattributes`. Bash fails on a CRLF script committed from Windows.

Re-run the deploy script only for a new machine, a broken link, or a new single-file target.

## Review is the security boundary

A merge to the template's default branch becomes live configuration on every deployed machine at
its next session start. That is the point of sharing it, and it means review on that repository
protects every teammate's machine. Protect its default branch and require review on it.
