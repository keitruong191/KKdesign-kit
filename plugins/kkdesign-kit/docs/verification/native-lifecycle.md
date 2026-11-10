# WWA-08 native lifecycle verification

Implementation and coding verification are assessed separately from authenticated
agent/native usability acceptance, under the owner's clarified acceptance policy.
This item keeps lifecycle in the provider; it adds no update/rollback/uninstall
CLI, hook, local MCP, credentials or alternate distribution channel.

Native compatibility uses the exact requirements digest plus the canonical
`RUNTIME_CONTRACT` in `scripts/kkdesign_setup.py`. Bump this integer when
interpreter, provisioning or receipt requirements become incompatible; package
versions alone must not force runtime replacement. Both providers use the same
resolver. New namespaces preserve older caches and require Setup consent;
matching caches still require full trust verification and real helper checks.
The first contract namespace intentionally does not execute older dependency-only
native caches; those remain preserved for their existing consumers.

## Reproduction

Use an external Python 3.9+ development venv with requirements.txt installed:

```text
python -m unittest discover -s tests -v
python -B scripts/smoke_native_lifecycle.py --output <new-outside-repo-directory>
```

The opt-in probe requires both provider CLIs and native macOS/GNU/Linux local
execution with approved GitHub/package-index access. It creates a disposable
home and two synthetic Git marketplaces served through real Git smart HTTP on
loopback. It neither reads/copies provider authentication nor calls a model. Its
consent flags authorize synthetic smoke provisioning only and do not establish
human approval in an agent. It leaves private raw logs in the chosen output.

The probe installs both native consumers into one home, provisions through the
POSIX bootstrap without PATH Python, verifies shared reuse and real helpers,
uses Claude native disable/enable and Codex's native configuration API, then updates both providers to synthetic
versions with unchanged and changed requirements. A changed requirement must
request consent before provisioning a separate cache. It verifies the still-active older Claude consumer while Codex is updated and
a new runtime is provisioned, removes each provider in turn, checks the other consumer and
project/runtime preservation, then reinstalls and verifies reuse. Synthetic
version changes exist only in the disposable marketplace source.

## Observed results

Code-ready for integration review; external acceptance remains pending.
Native probe: **pass** on macOS ARM64, Codex CLI **0.167.0**, Claude Code
**2.1.308**. Both native profiles shared one isolated home and two private
runtimes; no provider credentials were copied. PATH was `/nonexistent` for
Setup/helper execution. CPython bootstrap download, real venv/pip provisioning
and dependency-backed helper validation succeeded.

| Acceptance criterion | Implementation and measured result |
| --- | --- |
| Native update preserves compatible runtime and gates changed requirements | Both providers natively updated from synthetic 0.5.0a1 to 0.5.0a2 and reused the same verified runtime. Codex updated to 0.5.0a3 with changed jsonschema requirements: no-consent Setup returned consent-required; explicit smoke consent created a separate runtime. Claude's older active consumer still ran before and after that provisioning. Claude then updated and reused the newly verified shared runtime. Contract-version changes have regression coverage for non-execution and old-cache preservation. |
| Enable/disable does not provision, create standalone copies or mutate project | Claude native disable/enable exit 0. Codex app-server config/value/write changed its native plugin enabled setting, and new plugin list processes observed false/true. Project sentinels and runtime fingerprint stayed unchanged. No standalone skill was created. |
| Native uninstall preserves data and shared runtime | Both native remove/uninstall commands exit 0. After Codex removal the still-installed Claude consumer runs the real verified helper. Design, lesson and task-history sentinels plus the original runtime fingerprint remain unchanged after both removals. Provider cache retention/deletion remains provider-owned. |
| Reinstall reevaluates and reuses verified caches | Both native reinstall commands exit 0 and Setup returns ready/reused without acquisition consent. Existing regression tests reject missing/changed interpreters, receipts, requirements, unsafe ownership and injected startup code before execution. |
| Real two-consumer lifecycle evidence | Actual native Git marketplace registration/install, unchanged/changed updates, enable/disable, uninstall and reinstall ran with real shared runtimes and helpers. This is measured native lifecycle plus direct agent-entrypoint execution; authenticated model/menu interaction and human approval were not exercised. |

Coding check: `python -m unittest discover -s tests -v` in the external
Python 3.9 development venv: **161 tests run, OK, 9 skipped**. Skips are
platform-specific native Windows/PowerShell cases on this macOS host.
`git diff --check` passed. The changed-path probe was:
`python -B scripts/smoke_native_lifecycle.py --output <new-outside-repo-directory>`.
Raw outputs remain outside the repository. The final passing probe recorded all
native lifecycle commands with exit 0; earlier probe defects were fixed before
this result. No unavailable-authentication scenario was retried.

Claude adds host-owned `.orphaned_at` metadata to retired cache versions;
Codex removes obsolete cached versions. The probe therefore tests an older
consumer while it is actively installed, rather than treating retired cached
bytes as an installed consumer or weakening strict package integrity checks.
Neither cache-directory retention nor a schema check implies native readiness.

## External acceptance and later contracts

Authenticated native menus, human consent interaction and non-developer usability
remain pending; previously observed missing authentication is not retried.
Interactive native UI controls and broader OS/CPU/provider combinations require
separate acceptance. CLI/native lifecycle results cannot establish those passes,
public marketplace publication, external-tool connection or human approval.
WWA-09 owns standalone conflict detection and consented migration; WWA-10 owns
final onboarding/support-matrix consolidation. The coordinator reviews/merges
only into the integration feature branch; this worker does not merge or publish.
