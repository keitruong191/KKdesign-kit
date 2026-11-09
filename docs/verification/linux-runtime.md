# Linux runtime implementation and acceptance

This is an item-specific historical verification record. For current integrated
behavior and remaining external acceptance, use the [support matrix](../compatibility.md)
and [onboarding handoff](onboarding.md); earlier implementation gaps below are
not current capability limits when superseded by later items.

WWA-05 extends the internal marketplace Setup to Linux through the canonical
`scripts/kkdesign_setup_posix.sh`. Both provider packages ship this same source;
there is no standalone distribution, second dispatcher or installer lifecycle.

## Implementation matrix and trust

The implemented acquisition targets are GNU/Linux x86_64 and aarch64, GNU libc
2.28 or newer, with `/bin/sh`, host curl, GNU tar/gzip and coreutils/findutils
in `/bin` and `/usr/bin`. This conservative libc floor is intentional. musl,
other CPUs and missing tools are rejected before download. No Linux distribution
or native provider combination is advertised as verified until its smoke runs.

The bootstrap always selects its own complete CPython, ignoring system Python
and Node. Thus an existing Python missing venv or ensurepip does not become a
provisioning prerequisite. No sudo, system pip, activation, shell profile or
system PATH mutation is involved. Only tar's subprocess receives a fixed host
tool PATH to find gzip; no PATH interpreter is discovered or executed.

CPython 3.12.12 from Astral python-build-standalone release **20251014** is pinned:

| Target | SHA-256 |
|---|---|
| aarch64-unknown-linux-gnu | `d32487b853d6f5709019a471770be5e5d3e6bd2ac507e5629e2d6825565d3e71` |
| x86_64-unknown-linux-gnu | `1ab2b6594d1c3d76cbebea09d6bc3e6ba68d8eb3b6322080375c4cc3dd188f34` |

The entrypoint pins exact HTTPS URLs and verifies bytes before extraction or
execution. Pins are checked against upstream release asset digest metadata and
`SHA256SUMS`. Sources: [pinned release](https://github.com/astral-sh/python-build-standalone/releases/tag/20251014)
and [upstream distribution/runtime documentation](https://gregoryszorc.com/docs/python-build-standalone/main/running.html).
Hashes establish artifact integrity, not independent publisher identity. Changes
to these pins require review and new smoke; this historical pin is not a claim
about the latest security patch.

Consent precedes acquisition. Before consent, the entrypoint discloses source,
purpose, permissions and storage without creating state. Acquired Python and
archive stay in `~/.kkdesign-kit/bootstrap/cpython-3.12.12-20251014-<target>/`;
requirements-matched workflow runtimes remain in `~/.kkdesign-kit/runtimes/`.
Neither location belongs to a project or the provider's plugin cache.

Full file/link/directory inventory, retained archive digest, cache ownership,
permissions and ancestry are checked before executing cached Python. Linux uses
GNU stat/find/sha256sum with a sorted inventory; macOS retains its original
inventory format and cache identity. Same-account compromise is outside this
user-cache trust boundary. Unowned, modified or incomplete caches are preserved
and rejected, without fallback to an arbitrary executable. Download/staging
failures never publish ready; the shared Python Setup publishes its readiness
receipt only after real dependencies and materialize/validate helper checks.
Execution policy is respected. Network/write/policy errors stop with diagnostics
and an authorized next action, without retries or alternate installation routes.

## Coding and changed-path checks

The available development host is macOS ARM64; no Linux host, container runtime
or VM executable was found. The shared POSIX changed-path smoke passed there,
including actual pinned acquisition, dependency provisioning, both relocated
provider payloads, repeat reuse, real helpers and tampered-library rejection.
That result verifies the shared/macOS path only, never Linux native execution.
Linux native acceptance is pending resources, separately from code readiness.

| Coding check | Result | Scope |
|---|---|---|
| `python -m unittest discover -s tests -v` | PASS, 146 tests, Python 3.9 development venv with requirements.txt | Core regressions including consent, corruption/executable rejection, lock preservation, real network refusal and write denial; native Linux branch awaits Linux execution |
| `python -B scripts/smoke_posix_setup.py` | PASS, Darwin ARM64 | Actual shared/macOS acquisition, real requirements and helpers, relocated Claude/Codex payloads, spaces/CWD, reuse, plugin/project preservation and tamper rejection |
| Upstream `SHA256SUMS` and GitHub asset digest comparison | PASS, both Linux targets | Pin metadata matches upstream; does not prove Linux runtime execution |
| `git diff --check` | PASS | Whitespace only |

No workflow edits or credential changes are needed. Existing Foundation contracts
CI already executes the coding suite on Ubuntu, macOS and Windows; its existing
legacy bootstrap smoke does not exercise Linux acquisition and is not counted
as that evidence.

The shared changed-path harness is:

```sh
python -B scripts/smoke_posix_setup.py
```

On each Linux target also run it in a fresh temporary home with an actual
installed system interpreter missing venv or ensurepip:

```sh
python -B scripts/smoke_posix_setup.py --incomplete-python /usr/bin/python3
```

The development interpreter running this harness needs requirements.txt; the
incomplete interpreter supplied to the second command must actually fail an
isolated `import venv, ensurepip`. The harness checks that fact before Setup,
places only that interpreter on its PATH, then downloads the separate pinned
runtime and runs real helpers. It never removes modules or modifies system
packages to construct the condition. The default case supplies no PATH
Python/Node. Both cases use relocated real provider artifacts, unrelated product
CWD, spaces, real provisioning, reuse, plugin/project preservation and rejection
of a modified acquired standard-library file. These are shell/runtime checks,
not authenticated agent consent, native marketplace or usability evidence.

## Per-criterion verdict and remaining integration

| WWA-05 criterion | Implementation verdict | External acceptance |
|---|---|---|
| No usable Python/Node → consented runtime → actual helper validation | Implemented via pinned acquisition and canonical Setup | Native Linux x86_64/ARM64 and provider-agent observation pending |
| System Python lacks venv/ensurepip; no package repair/sudo | Implemented by using complete private CPython; smoke verifies a genuinely incomplete supplied interpreter | Run incomplete-system-Python smoke on Linux pending |
| User cache outside plugin/project; no activation/PATH edits | Implemented; use successful Setup's absolute interpreter with existing helper dispatcher | Linux native observation pending |
| Integrity/write/policy/network failures never ready or trust foreign executables | Implemented with pre-execution verification, private transaction, clear refusal and preservation | Real organization policy/firewall acceptance pending |
| Repeat Setup, arbitrary CWD and spaces preserve valid runtime/project | Implemented and covered by relocated harness | Linux native repeat smoke pending |

WWA-07 now supplies [verified helper invocation](../../references/helpers.md)
through the same OS entrypoint and dispatcher, without system Python.
[WWA-08 lifecycle compatibility](native-lifecycle.md) is implemented with macOS
native evidence; WWA-09 owns standalone migration. Linux provider lifecycle, authentication,
human consent and non-dev usability remain separate integrated acceptance.
