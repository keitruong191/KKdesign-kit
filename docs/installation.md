# Install and maintain KKdesign-kit

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
`--runtime` provisions the dependency-equipped environment outside the
installed skill, under the installation state area. The skill itself stays in
the harness discovery directory and its integrity hash tree; runtime bytes are
not included in that tree. Do not activate the runtime in a shell. Installer
operations use the standard library; project workflow commands use that
separately provisioned runtime. Source/manual helper commands require
dependencies in the current Python environment.

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
can be undone. Runtime environments are stored outside the hash-protected skill
tree under the installation state area; state records the runtime corresponding
to the active skill. Runtime-enabled updates and rollback reuse or provision
the matching environment before commit. Uninstall removes owned skill/state
records but deliberately retains external runtime directories; remove a
retained runtime manually only after uninstall and only when you have confirmed
it is no longer shared or needed. Project DESIGN.md, lessons, profiles, task
history, unrelated settings and credentials are not managed.

The uninstall result reports `runtimeReady: false` and, when a cache exists,
`retainedRuntimeRoot` to identify the preserved directory. The installer does
not erase the external environment; manual removal is safe only after confirming
it is no longer shared or needed.

The managed target is the harness skill directory in the table above. Installer
ownership and lifecycle state are kept outside that discovery directory under
`<BASE>/.kkdesign-kit/installations/<harness>/`, including `state.json`,
`previous/` and `runtimes/`. Project-scope files are limited to the selected
project's skill and this installation state; user scope uses the user base.

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
