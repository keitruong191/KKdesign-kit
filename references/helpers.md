# Invoke bundled helpers

Both provider adapters use these same entrypoints and `kkdesign_run.py` dispatcher.
`SKILL_DIR` is the host-supplied absolute directory containing the activated
SKILL.md; it is never inferred from product CWD or project metadata. Paths and
arguments containing spaces must remain individual quoted arguments.

On macOS/GNU Linux:

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_core validate --design "$PROJECT/design"
```

On native Windows, run in the authorized Windows PowerShell 5.1 host (if the
executor uses another shell, launch the system PowerShell host as in Setup):

```powershell
& "$SKILL_DIR\scripts\kkdesign_setup_windows.ps1" -PackageRoot "$SKILL_DIR" -Helper kkdesign_core -HelperArguments @('validate', '--design', "$PROJECT\design")
```

Use the same OS form for every helper command in the workflow guides. On Windows
translate the documented POSIX prefix into this PowerShell form and pass the
helper arguments as an array. Do not add policy bypass flags or ask users to
configure a terminal. `HELPER` must be one of `kkdesign_core`, `kkdesign_project`,
`kkdesign_sources`, `kkdesign_task`, `kkdesign_review`, `kkdesign_learn`,
`kkdesign_install`, or `materialize_example`; executable paths are rejected.
The packaging helper does not authorize standalone plugin installation/lifecycle.

Helper mode never downloads, provisions, repairs caches or edits plugin bytes.
It checks the pinned bootstrap artifact and full inventory before executing
Python, then verifies the requirements-matched runtime and receipt before
starting the requested helper. Missing bootstrap/runtime means choose Setup;
changed requirements or ownership/receipt errors mean preserve the cache and
inspect it with its owner before repair. Never substitute PATH Python, a
remembered Setup executable path or a project-provided runtime/marker.

The private user cache is the trust boundary, not protection against compromise
of the user's own account. Helpers may write explicitly selected project data
as part of their requested workflow; dispatch itself does not provision or write
plugin/project state. Validation proves contract checks only, not live tools,
human approval or native provider discovery. Historical standalone maintainer
scripts retain their original Python prerequisites and are not plugin entrypoints.
