# Install and maintain KKdesign-kit

For the new Claude Code adapter, see [marketplace packaging preview](claude-marketplace.md).
It uses native plugin lifecycle and `/kkdesign-kit:kkdesign-kit`; its menu and
Setup instructions do not require Python. Runtime Setup is still required and
not implemented by this preview. Do not use standalone commands below to set
up or manage a plugin. The remainder documents the legacy standalone lifecycle.

Requires Python 3.9+ on macOS, Linux or Windows and a separately installed,
authenticated Codex CLI or Claude Code. Bootstrap and installer use only the
Python standard library; the workflow runtime installs `requirements.txt`
dependencies into an environment outside the skill. Runtime provisioning needs
working `venv`/`ensurepip` and network/package-index access. Nothing installs
Hoangsa, Impeccable, hooks or MCP configuration. See
[compatibility](compatibility.md) for verification limits.

## Bootstrap and manual installation

The one-command bootstrap and public release are pending PR approval and
release. No public URL is ready, so do not use a guessed `curl` command. Once
the versioned ZIP and `.sha256` are actually published, add the exact pinned
command here only after smoke-testing that exact command against the public
artifact. The upcoming version is `0.5.0a1`; that does not mean it is available.

For source acquisition into a new path:

```sh
git clone https://github.com/keitruong191/KKdesign-kit.git "$HOME/KKdesign-kit-source"
cd "$HOME/KKdesign-kit-source"
```

Use the reviewed revision containing this installer change (PR reviewers: check
out the PR branch). Never overwrite an existing checkout. The source directory
contains the installer; `--project` selects only the destination, not where to
find `scripts/` or `requirements.txt`.

For a usable local-source route from the checkout root (or manual route after
acquiring and extracting the trusted portable ZIP), install with the standard
library installer:

```sh
python3 -I -B scripts/kkdesign_install.py install --harness codex --scope project --project "/path/to/project with spaces" --runtime
python3 -I -B scripts/kkdesign_install.py inspect --harness codex --scope project --project "/path/to/project with spaces"
```

To acquire manually after release, obtain the versioned portable
`kkdesign-kit-0.5.0a1.zip` and matching `.sha256` from a trusted release. Verify
the ZIP checksum, extract it, then `cd` into its `kkdesign-kit/` directory and
run the same installer commands. Quote paths containing spaces. On Windows use
`py -3 -I -B scripts\kkdesign_install.py ...` with quoted native paths. Python
3.9+ is required; if `python` points at Python 2 or is unavailable, use
`python3` (macOS/Linux) or `py -3` (Windows). `curl` and network access are
needed for bootstrap artifact retrieval; manual acquisition can use a browser.

Select one harness and scope explicitly. Use `--harness claude-code` for Claude
Code, or `--scope user` for a personal installation. The shell bootstrap takes
`--harness`, `--scope`, and `--project`; its default is project scope at the
current working directory. Run there, or pass an explicit quoted `--project`.
The bootstrap performs an install; use the installer lifecycle commands below to update existing
installations.
`--runtime` provisions dependencies in the user's private cache at
`~/.kkdesign-kit/runtimes/<requirements-sha256>/`, outside the destination
repository and hash-managed skill. Both scopes need a writable user home.
Bootstrap always enables this option; the stdlib manual installer keeps it
optional. Without a recorded runtime, the launcher uses its current Python
interpreter, which must already have `requirements.txt` installed. This also
applies after updating a manual installation from `0.4.0a1`. No activation is
needed. An explicitly recorded but mismatched/missing runtime is an error,
never a reason to silently fall back to another interpreter.

| Harness | User scope | Project scope | Invoke after restarting harness |
|---|---|---|---|
| Codex | `~/.agents/skills/kkdesign-kit` | `<project>/.agents/skills/kkdesign-kit` | `$kkdesign-kit` |
| Claude Code | `~/.claude/skills/kkdesign-kit` | `<project>/.claude/skills/kkdesign-kit` | `/kkdesign-kit` |

Restart the agent in the intended product project after installation. Bare
invocation displays the command menu; use `$kkdesign-kit init` or
`/kkdesign-kit init` to invoke a route. Menu availability is not a guarantee
that the harness discovered the skill or that live design tools are ready.
Codex gets display metadata from `agents/openai.yaml`; Claude Code uses the
canonical frontmatter and native slash invocation. No plugin, settings merge or
hook adapter is enabled.

The installed `kkdesign_run.py` launcher resolves helpers relative to the
absolute installed `SKILL_DIR`, never product CWD. Invoke it as
`python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" HELPER args...`, with helper
name without `.py`; no activation is needed.

## Inspect, update, rollback, uninstall

Use the same `--harness`, `--scope`, `--project` (and `--home` if overridden)
for lifecycle operations:

```sh
python3 -I -B scripts/kkdesign_install.py inspect --harness codex --scope project --project "/path/to/project with spaces"
python3 -I -B scripts/kkdesign_install.py update --harness codex --scope project --project "/path/to/project with spaces" --source "/path/to/new extracted/kkdesign-kit"
python3 -I -B scripts/kkdesign_install.py rollback --harness codex --scope project --project "/path/to/project with spaces"
python3 -I -B scripts/kkdesign_install.py uninstall --harness codex --scope project --project "/path/to/project with spaces"
```

Identical payload bytes are unchanged; a different payload uses `update`.
Updates retain one previous version. Rollback swaps current and previous, so it
can be undone. Managed runtime environments live only in the user's private
cache, shared across harnesses/projects with the same requirements. Project
markers and project-supplied executable paths are not trusted as provenance.
State records the corresponding trusted runtime; runtime-enabled updates and
rollback reuse or provision it under a shared cache lock before commit.
Uninstall removes owned skill/state records but deliberately retains the shared
user cache. Remove a retained runtime manually only after confirming no other
installation needs it. Project DESIGN.md, lessons, profiles, task
history, unrelated settings and credentials are not managed.

The uninstall result reports `runtimeReady: false` and, when a cache exists,
`retainedRuntimeRoot` to identify the preserved directory. The installer does
not erase the external environment; manual removal is safe only after confirming
it is no longer shared or needed.

The managed target is the harness skill directory in the table above. Installer
ownership and lifecycle state are kept outside that discovery directory under
`<BASE>/.kkdesign-kit/installations/<harness>/`, including `state.json` and
`previous/`. Runtime bytes and creation markers live separately in the private
user cache `~/.kkdesign-kit/runtimes/`, never in project installation state.
Project-scope writes therefore include that user cache as well as the selected
project's skill and ledger; personal scope uses the user base for both.

SHA-256 covers the installed skill tree and the transport checksum covers the
ZIP. They detect corruption or modification but are not publisher signatures
and do not establish authenticity. Acquire from a trusted source.

## Conflicts and troubleshooting

- `inspect` reports absent, managed, modified or unmanaged conflict and same-name
  user/ancestor-project installs. Inspect conflicts before install/update/rollback;
  admin-managed paths and external harness search roots may require checking in
  the harness discovery UI.
- No force-overwrite: move an unmanaged conflict safely or preserve local edits
  outside the managed skill. A modified backup blocks lifecycle mutations.
- If invoked from the wrong CWD, use the absolute installed `SKILL_DIR` and the
  launcher; never construct `../scripts/...` paths from the product directory.
- On Linux, the Python installation must include working `venv` and `ensurepip`
  support (some distributions package these separately). If environment
  activation fails, do not cascade through guessed activation paths: the
  installed launcher uses the recorded runtime without activation. Resolve
  missing provisioning prerequisites directly; never use `sudo` for a
  user/project install.
- If Python is missing or resolves to Python 2, use `python3` on macOS/Linux or
  `py -3` on Windows. Runtime provisioning can fail if `venv`/`ensurepip` or
  network/package-index access is unavailable; resolve that prerequisite rather
  than activating arbitrary environments or suppressing the failure.
- A path using `../` may require write permission on its parent directory.
  Choose a project path you own or request the needed permission; do not retry
  with `sudo`, which can create root-owned state and bypass normal user scope.
- Symlinked installation ancestors or payload files are rejected. Choose a real
  directory rather than a linked home/project path.
- A managed runtime from an older, unreleased bootstrap under project
  installation state is not trusted or reused. Preserve that directory for
  inspection; do not redirect the launcher to it or copy its marker into the
  user cache. Project-scope managed runtime provisioning refuses a destination
  containing the private user-cache path; select a separate project instead.
- Locking prevents concurrent mutations. After interruption preserve and inspect
  target, `state.json`, `previous/`, staging and lock before recovery. Remove a
  stale lock only after confirming no installer is running; staging can contain
  recoverable previous data.
- Skill not found: restart, check the native path, inspect conflicts, and check
  workspace trust/managed policy. Installer success alone does not prove
  discovery. Cloud harnesses and Desktop syncing are outside this CLI.
- Missing external design tools are not installation failures. See
  [project-kit lifecycle](project-kits.md); source reads do not certify live
  rendering, accessibility, performance or human approval.
