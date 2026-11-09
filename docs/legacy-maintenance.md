# Historical standalone maintenance

For maintainers of existing standalone copies only. This is not a current
installation channel, plugin lifecycle or Setup fallback. New users follow
[marketplace onboarding](installation.md). Prefer Setup's
[consented migration](../references/setup.md#standalone-conflicts-and-migration)
when moving an intact managed copy to a native plugin; preserve modified or
unmanaged copies for owner inspection. The commands below require Python 3.9+
and the historical source/installed maintenance script.

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

The historical target is `<BASE>/.agents/skills/kkdesign-kit` for Codex or
`<BASE>/.claude/skills/kkdesign-kit` for Claude Code. Installer
ownership and lifecycle state are kept outside that discovery directory under
`<BASE>/.kkdesign-kit/installations/<harness>/`, including `state.json` and
`previous/`. Runtime bytes and creation markers live separately in the private
user cache `~/.kkdesign-kit/runtimes/`, never in project installation state.
Project-scope writes therefore include that user cache as well as the selected
project's skill and ledger; personal scope uses the user base for both.

SHA-256 covers the installed skill tree and the transport checksum covers the
ZIP. They detect corruption or modification but are not publisher signatures
and do not establish authenticity. Acquire from a trusted source.

