# WWA-09 standalone migration verification

Implementation review and coding checks are separate from provider/account/OS
and human acceptance. Migration belongs to explicit native Setup, with no new
standalone lifecycle, hook, alias or installer fallback.

Setup scans user locations and the explicit selected project plus all ancestors
for both harnesses, including legacy Codex skill and Claude command locations.
Exact supported ledgers and intact inventories establish managed ownership;
modified, unmanaged, unsafe or ambiguous copies remain conflicts. Discovery is
read-only. Migration consent identifies every disclosed location independently
of runtime acquisition consent. Only an intact bundled plugin with matching
native descriptor and successful real helper validation can deactivate copies.

Deactivation moves each entire verified tree and ledger into a retained archive
under its historical owner's state, outside native skill discovery. It preserves
rollback backups, project design data/lessons/profiles/history, credentials and
all shared runtime caches. Locks and revalidation reject stale/new conflicts;
caught partial move failures restore active trees and ledgers. Crash/power-loss
recovery is explicit owner inspection of locks/archives, never silent deletion.
A fresh native session is required to discard a running host's cached discovery.

## Reproduction and evidence

Use an external Python 3.9+ development venv with requirements.txt installed:

```text
python -m unittest discover -s tests -v
python -B scripts/smoke_standalone_migration.py
```

The opt-in POSIX probe obtains pinned CPython and provisions real dependencies
with explicit synthetic consent, in a disposable private home. Both relocated
marketplace artifacts exercise user/ancestor discovery, refused migration,
complete managed deactivation, modified-copy conflict preservation, real helper
validation and project/plugin/runtime preservation from unrelated CWD. It does
not read/copy provider credentials or authenticate a model. It does not prove
native provider registration, native Windows behavior or observed human consent.

Regression tests cover explicit project scope, both harnesses, all scopes and
legacy locations; full/partial/refused consent; modified/unmanaged/invalid
ledger/symlink conflicts; verified relocated plugins and actual helpers;
helper failure and missing descriptor preservation; new conflicts during
verification; transaction rollback; and separate runtime acquisition consent.

Observed on macOS ARM64 with Python 3.9.6:

- `python -m unittest discover -s tests -v`: **171 tests, OK, 9 skipped**
  (native Windows PowerShell/ACL cases unavailable on this host).
- `python -B scripts/smoke_standalone_migration.py`: **pass** for both
  relocated Claude and Codex packages. Actual POSIX pinned-Python acquisition,
  venv/pip provisioning and real dependency-backed helper checks passed.
  Claude created the runtime and Codex reused it. Both passed refused-consent,
  clean migration and modified-conflict preservation, retaining plugin bytes,
  project sentinels and the shared runtime.
- `git diff --check`: **pass**.

These are isolated filesystem/Setup measurements, not native discovery or
human approval. Native
agent/menu/consent/usability observation and Windows migration acceptance remain
external acceptance pending resources. Existing provider lifecycle evidence is
recorded separately in [native lifecycle verification](native-lifecycle.md).
WWA-10 still owns the published onboarding/support matrix; final publication
requires the combined native journey and provider-specific directory decisions.
