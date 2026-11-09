# Trusted helper runtime verification

WWA-07 implements Python-free helper startup for both provider packages using
`kkdesign_setup_posix.sh --package-root ABSOLUTE_SKILL_DIR --helper NAME ...`
or the native PowerShell equivalent in [helper invocation](../../references/helpers.md).
These are internal execution modes, not another distribution/installer lifecycle.
Both delegate to the existing `kkdesign_run.py` allowlist and runtime resolver.

The native entrypoint verifies the bootstrap's pinned archive, complete inventory
and user ownership before executing Python. The dispatcher receives the explicit
package root, verifies its resources and ownership of the dispatcher path, then
checks the private requirements-matched runtime, marker and full receipt before
executing the helper with isolated imports. It ignores project runtime paths and
never uses PATH Python or invokes provisioning in helper mode. A lost bootstrap
or runtime requires explicit Setup; changed/unowned state is preserved for review
before repair. Cache verification locks are temporary user-cache writes; plugin
and project files are not changed by dispatch.

Regression coverage includes relocated packages from both builders, real
materialization/contract validation, arbitrary roots without provider markers,
missing/forged/tampered runtimes, startup-file injection, executable helper names,
unsafe permissions, bootstrap refusal and unchanged retained state. Legacy
standalone maintainer probes remain historical tooling with existing Python
prerequisites; they do not establish marketplace acceptance.

Coding checks and changed-path smoke results are recorded with the PR. The smoke
runs both relocated provider payloads with no Python/Node on PATH, real acquired
CPython/venv/dependencies, materialization, validation, task integrity and feedback
capture. It also verifies runtime-receipt/bootstrap-library rejection and checks
that plugin bytes and unrelated project data remain unchanged.

This proves only the host architecture and artifact/helper execution actually
observed. Native provider install/discovery/agent workflow in authenticated Codex
and Claude Code sessions, native Linux/Windows/Intel execution, live design tools
and human consent/usability remain external acceptance pending owner resources.
No unobserved platform is advertised as supported. WWA-08 owns update/cache
compatibility and native lifecycle integration; WWA-09 owns standalone conflicts
and consented migration; WWA-10 owns published onboarding and support evidence.

Observed coding checks on macOS ARM64:

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` (Python 3.9.6 development environment with requirements installed) | 159 tests run; OK, 9 native Windows tests skipped |
| `python -B scripts/smoke_posix_setup.py` | Pass on Darwin ARM64 for both relocated adapter packages; PATH Python/Node unavailable, real pinned CPython acquisition and requirements provisioning, reuse, validation/task/feedback workflows, receipt/library rejection and preservation |
| `git diff --check` | Pass |

The first suite run exposed a new fixture cleanup error (an already-existing
runtime parent); it was corrected and the full required suite rerun successfully.
No provider workflow or other native platform result is inferred from these checks.

Per WWA-07 acceptance criterion:

| Criterion | Implementation verdict and evidence | External acceptance |
|---|---|---|
| Used helpers execute from arbitrary installed caches without system Python/activation/CWD dependence | Implemented; both relocated payloads execute real workflows through OS helper mode with PATH unavailable | Authenticated native provider sessions and remaining OS/CPUs pending |
| Both adapters share dispatch/resolution and migrated callers/contracts | Implemented; one canonical dispatcher, both builders ship the same resources, active instructions and smoke callers use explicit roots | Native provider interaction pending; historical standalone probes are not plugin callers |
| Lost/incompatible/unowned runtime requires Setup/repair, no PATH fallback | Implemented; missing/forged/changed requirements/interpreter/receipt and permission regressions reject before requested effects | Native policy/account observation on remaining OSes pending |
| Project executables/forged markers cannot redirect execution; preserve plugin bytes | Implemented; allowlisted names, explicit validated package owner, private-cache verification, startup injection rejection and hash/preservation checks | Same-user account compromise remains outside the private-cache trust boundary |
| Consumer-visible regression coverage and both-provider real workflow smoke | Implemented; suite and macOS relocated adapter materialization/validation/task/learning smoke pass | Native marketplace → authenticated agent workflow acceptance for both providers pending |

Code-ready integration is distinct from completion of external acceptance and
release gates. The owner-arranged resource policy permits implementation review
without treating missing native provider/account/OS resources as a code failure.
