# Windows runtime implementation and acceptance

WWA-06 adds the canonical internal `scripts/kkdesign_setup_windows.ps1` to both
provider packages. It performs Setup only; provider installation, update and
uninstall remain native. The shared Python Setup still provisions requirements,
runs real synthetic materialization/validation and records readiness.

## Implemented matrix and trust boundary

Implemented acquisition targets are Windows x64 and ARM64, using native Windows
PowerShell **5.1**, .NET HTTPS/SHA-256/NTFS ACL APIs and the Windows system tar
executable (Windows 10 1803+). The agent invokes the system Windows PowerShell
host explicitly, including from PowerShell 7. Unsupported hosts/CPUs or missing
tar stop before acquisition. No OS/CPU/provider combination is advertised as
verified until native smoke and provider acceptance have run.

System Python, Node, WSL and Git Bash are unnecessary. Setup never asks for
admin, changes execution policy, unblocks scripts, edits PATH/profiles or installs
packages into system Python. If the host blocks entrypoint execution before
JSON can be emitted, the agent reports the host denial and requests an authorized
session; it must not bypass policy or choose an alternate installer.

CPython 3.12.12 from Astral python-build-standalone release **20251014** is pinned:

| Target | SHA-256 |
|---|---|
| x86_64-pc-windows-msvc | `2d670beb3b930d30e3a13cc909923a001dbdfcb5537692d5da40b6b41643ce1c` |
| aarch64-pc-windows-msvc | `d708734581e8cb03f4cf95f39f17ea331bc4761dfdad99b6b738a245444c9c54` |

Source: [upstream pinned release](https://github.com/astral-sh/python-build-standalone/releases/tag/20251014).
The exact HTTPS URL and SHA-256 are bundled; redirects must remain HTTPS and
bytes are checked before extraction/execution. Hashes establish integrity,
not independent publisher identity. The provider package must be trusted.
This historical pin is not a claim about the latest security patch.

Without explicit consent, a missing bootstrap returns consent-required and
explains source, purpose, storage, network/write/execution permissions without
creating KKdesign cache data or starting a downloaded executable. The native
PowerShell host can maintain its own AppData module-analysis cache; this is not
KKdesign runtime provisioning. After agent-observed
consent, `-Consent` authorizes acquisition. A test flag never proves human consent.

Executable storage is under the user's profile, outside plugin and project:
`.kkdesign-kit/bootstrap/cpython-3.12.12-20251014-<target>-pc-windows-msvc/`
and requirements-matched `.kkdesign-kit/runtimes/`. New private directories are
created atomically with protected inheritable DACLs. Existing data is never
re-ACLed or silently repaired. The shared security helper checks ownership by the current user, SYSTEM or Administrators and rejects write grants to principals other than that user, SYSTEM
and Administrators (including OWNER RIGHTS grants to that already verified
owner), null DACLs and reparse points, including cache ancestry.
Windows can assign Administrators ownership to newly created files for an
elevated account; this is the same privileged authority allowed write access,
not trust in another ordinary user. The child PowerShell process selects only
its native built-in modules so a PowerShell 7 executor cannot redirect 5.1
autoloading to incompatible modules. No system module/PATH setting changes.
OWNER RIGHTS denotes the verified object owner, as defined by
[Microsoft well-known SID structures](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/81d92bba-d22b-4a8c-908a-554ab29148ab).
Tree walking rejects junctions before traversal. Python Setup/readiness uses the
same checks for managed runtimes, including files and metadata, before execution.
A compromised same-user account or trusted administrator remains outside this
private user-cache boundary.

An exclusive lock protects bootstrap transactions; interrupted locks are preserved
for inspection. New acquisition stages are removed on failure, existing caches
are preserved. Cached archive digest and full directory/file inventory are checked
before executing acquired Python. Corrupt/unowned/incomplete caches never cause
fallback to PATH Python or readiness. Bounded download/provisioning failures stop
with diagnostics and approved next actions. The existing shared transaction records
ready only after requirements and real helpers pass. Returned absolute interpreter
paths support the existing dispatcher for this session without activation.

## Verification and native handoff

The available development host is macOS ARM64; there is no Windows machine,
VM or authenticated Windows provider session available. Portable integrity,
parser and coding results below establish only their stated scope. Native
acquisition/helper Setup, account/policy observation and provider behavior
remain external acceptance. Existing Windows CI can test individual ACL and
transaction boundaries; its results are reported separately in PR checks;
missing resources do not block code-ready integration under the owner decision.

The required coding suite is `python -m unittest discover -s tests -v` using a
Python 3.9+ development environment with requirements.txt. Native Windows tests
in `tests/test_windows_setup.py` exercise no-consent preservation with no PATH
interpreters, corrupt artifact rejection, writable ACL rejection/preservation,
actual write denial, junction rejection, interrupted lock preservation and explicit
package roots.
They are skipped on other OSes; a skip is not native proof.

| Coding/available check | Result | Evidence boundary |
|---|---|---|
| `python -m unittest discover -s tests -v` | PASS: 154 tests, 8 native Windows skips, Python 3.9.6 with requirements.txt | Shared regressions pass; Windows skips are pending, not native evidence |
| `python -B scripts/smoke_windows_setup.py --inspect-artifacts` | PASS, x64 and ARM64 | Real upstream downloads, pinned SHA-256 and archive contents; no Windows execution |
| PowerShell AST parse of both shipped scripts | PASS, development PowerShell 7.6.9 on macOS ARM64 | Syntax only; not Windows PowerShell 5.1 execution |
| Actual unsupported-host entrypoint invocation | PASS: error JSON, nonzero exit, no ready | PowerShell 7 on macOS is rejected; not native Windows evidence |
| `git diff --check` | PASS | Whitespace only |

The development-only PowerShell parser was acquired outside the repository
from Microsoft's release with its published asset digest checked; no binary is
shipped or committed. Existing Foundation contracts CI already runs the suite
on Windows, macOS and Ubuntu; no workflow edits, credentials or permission
changes are needed. CI unit checks are not the missing-Python acquisition smoke.

Portable changed-artifact inspection:

```sh
python -B scripts/smoke_windows_setup.py --inspect-artifacts
```

This downloads both pinned real archives, verifies SHA-256, checks Windows PE
signature and venv/ensurepip/library contents without executing Windows bytes.

On each native Windows target, run:

```powershell
python -B scripts/smoke_windows_setup.py
```

The maintainer harness needs a development Python and requirements.txt; the
launched Setup receives no Python/Node on PATH. It builds and relocates both
real provider payloads, uses paths with spaces and an unrelated product CWD,
then exercises no-consent, real acquisition/provisioning, actual helpers, repeat
reuse, plugin/project preservation and tampered-library rejection. It does not
prove native marketplace discovery, observed human consent or tool authentication.
Also observe native agent Setup on both providers, actual policy denial and
write denial in an authorized test account, and retain synthetic evidence only.
Never relax policy or acquire credentials to construct acceptance.

## Per-criterion verdict and remaining integration

| WWA-06 criterion | Implementation verdict | External acceptance |
|---|---|---|
| Missing Python/Node, native consented Setup and helpers | Implemented in PowerShell with complete pinned CPython and shared verification | Native Windows x64/ARM64 and both providers pending |
| Spaces, native separators, product CWD differs from plugin root | Explicit absolute package root, argument arrays and managed interpreter; relocated native harness supplied | Native path/CWD execution pending |
| No admin, system changes or policy bypass | Implemented; host execution denial is surfaced by agent, subprocess errors stop | Actual Windows policy/account observation pending |
| Integrity/permission failures, valid reuse, unowned cache rejection | Archive/inventory checks, protected DACLs, shared ACL/reparse verification, exclusive locks and preserved errors | Native ACL, denial and reuse smoke pending |
| Real Windows smoke for each advertised combination | Native harness and acceptance handoff supplied; no Windows combination advertised as verified | Pending owner-arranged Windows/provider resources |

WWA-07 now supplies [verified helper invocation](../../references/helpers.md)
through the same OS entrypoint and dispatcher, without system Python.
[WWA-08 lifecycle compatibility](native-lifecycle.md) is implemented; its macOS
native evidence does not establish Windows acceptance. WWA-09 owns standalone migration. WWA-10
and release gates own published support instructions, provider/OS and non-dev
acceptance. Provider owns plugin bytes/lifecycle; runtime retention does not
imply external-tool authentication or human approval.
