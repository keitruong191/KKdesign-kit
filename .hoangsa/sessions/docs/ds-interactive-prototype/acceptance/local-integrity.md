# Local integrity — execution evidence

Status: **PASS — local integrity**. Native/browser acceptance is separate.

## Runtime

System Python 3.9.6 does not have `jsonschema`. Checks use an existing isolated Python 3.12.12 environment with the repository requirement installed; no dependency was downloaded or installed for this task. This portable CPython requires its base-library directory in `DYLD_LIBRARY_PATH` for nested-venv runtime tests. `$PYTHON_ENV/bin` is first in `PATH`; `$PYTHON_BASE/lib` is the dynamic-library path. Machine-specific paths are intentionally not part of this portable report.

## Core regression

```sh
PATH="$PYTHON_ENV/bin:$PATH" DYLD_LIBRARY_PATH="$PYTHON_BASE/lib" \
  python3 -B -m unittest discover -s tests -v
```

- Implementation-stage final run: **165 tests passed**, 18.021 seconds, exit 0. This includes foundation, installation, runtime, source/project lifecycle, historical Figma, and the new web preflight/path/handoff suites. The subsequent current-main PR run is recorded in [INTEGRATION.md](INTEGRATION.md#source-pr-integration).
- Earlier failing runs exposed and led to repairs for a non-web schema regression, missing manifest resource requirements, invalid new-test setup, file-mode/project-root launch metadata, stale-artifact re-handoff, and initialized-project profile identity. No old test expectation was weakened to hide a production regression.
- The concurrent-begin regression now resolves macOS path aliases and positively observes both child processes reaching its barrier. A redundant stale React fixture test was removed; the stronger command-mode lifecycle case covers package isolation and nonexecution with an absolute sentinel.

## Actual package relocation smoke

```sh
python3 -I -B scripts/kkdesign_install.py package --output "$OUT/kit.zip"
python3 -m zipfile -e "$OUT/kit.zip" "$OUT/extracted"
python3 -I -B "$OUT/extracted/kkdesign-kit/scripts/kkdesign_install.py" \
  verify --source "$OUT/extracted/kkdesign-kit"
```

All three commands exited 0 in a temporary physical path containing spaces. Implementation-stage package version: `0.5.0a1`; extracted verification: **63 files, 42 required resources**. SHA-256: `9248dd765cfdb684515cb1fae65fe66f91c00801bb28e3e1a0af4e0625835ae5`. Current-main PR integration has a larger resource inventory and is recorded separately in the integration report.

The first output attempt used macOS's logical `/var` temp prefix and was correctly refused as a symlink conflict. Resolving the temporary root to its physical path allowed packaging; installer behavior was not changed.

Package verification proves resource completeness and SHA-256 integrity only. It does not establish browser behavior, native harness invocation, Figma behavior, publisher authenticity, or human approval.

## Static and actual lifecycle smoke

- System Python 3.9.6 successfully compiled the syntax of all 25 Python script/test modules without writing bytecode. No unconfigured linter or type checker was added.
- Actual launcher commands `kkdesign_project refresh`, `plan`, `apply`, `kkdesign_task check`, and `kkdesign_core validate` all exited 0 against a delivered React fixture with a dependency-command symlink under `node_modules/.bin`. The same commands passed from the relocated final package with the subprocess working directory set to the selected project.
- Project refresh no longer traverses or copies user-owned `design/prototypes` runtime trees. It still validates real artifact references and candidate integrity. The regression preserves task/artifact/dependency bytes, lists task-record DS references, and rejects a missing entry before apply.
- A throwaway mutation restoring the old unpruned traversal made that regression fail on the dependency symlink; the unmodified implementation passed. The mutation did not edit repository source.
- A malformed profile JSON root was reproduced as an `AttributeError` before repair; the current preflight reports `ValueError` before task/artifact mutation, with permanent regression coverage.

Current-state browser-project audits also exposed raw observation JSON placed
under `design/tasks` and a lesson citation with the wrong relative base. The
guide now requires unwrapped payload JSON outside tasks and both task/foundation
checks. The accepted HTML rerun preserves the rejected project's history rather
than rewriting evidence wrappers; active React citation metadata was corrected
without changing the pinned lesson hash or verification claims.

## Evidence-driven scope refinements

`scripts/kkdesign_project.py` and `tests/test_project.py` were added to the implementation scope after actual review reproduction showed that the approved React output layout broke existing refresh/candidate validation. This is compatibility repair, not a new provisioning or lifecycle feature. `scripts/smoke_workflow_harness.py` now includes the web artifact root in its no-interaction boundary check; its legacy credential/provisioning runner remains distinct from directly observed native routing checks.

During this implementation-verification stage, no commits, branch changes, dependency downloads, publishing, deployments, or business API calls were performed. A subsequent owner request explicitly authorized a separate source branch, commit, and PR; that integration does not imply deployment or native acceptance.
