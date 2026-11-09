# WWA-03 — Setup consent and readiness verification

Implementation is code-ready for integration. External acceptance is pending;
the owner will arrange native provider/OS/account and usability resources
separately. This report does not establish platform support or human consent.

## Coding and changed-path evidence

Final checks on macOS ARM64 with Python 3.9.6 in a temporary development venv
populated from `requirements.txt`:

| Check | Result | Actual scope |
|---|---|---|
| `python -m unittest discover -s tests -v` | PASS, 138 tests, 17.518 seconds | Existing core regressions plus consent refusal without writes/execution, real cached-helper reuse, integrity/requirements/missing-interpreter rejection, symlink and unsafe permission rejection, failed provisioning cleanup, failed actual helper validation and both relocated plugin layouts. |
| `python -B scripts/smoke_agent_setup.py` | PASS | Real venv/pip dependency provisioning after explicit test consent, then repeated Setup and actual materialize/validate helpers for Claude and Codex marketplace artifacts in arbitrary temporary paths with spaces and unrelated product CWD. |
| `git diff --check` | PASS | Whitespace/error check only. |

The smoke creates a temporary HOME, extracts actual deterministic marketplace
artifacts, first requests Setup without consent and observes no cache creation,
then provisions and runs real dependency-backed validation. The second adapter
reuses the same requirements-matched cache without new consent/download. Both
repeat Setup and run the existing helper dispatcher. Plugin files and the
synthetic project sentinel remain unchanged. Inherited pip target/prefix/user
settings are deliberately pointed outside the cache; no redirected files are
created. Dependency installation is real pip, which may reuse download caches;
no Python interpreter acquisition is claimed.

Failure regressions inject network/provisioning, permission and timeout errors
at the process boundary to verify cleanup and error state; they do not claim
real corporate firewall or native security-policy acceptance. Cached-runtime
regressions use a real venv with the suite's installed dependencies and execute
actual helpers, without network. Real dependency installation is the separate
smoke above. Package integrity verifies resource hashes, not publisher identity.

## Acceptance criteria

| WWA-03 criterion | Implementation verdict | Evidence and external boundary |
|---|---|---|
| Explicit Setup discoverable; install/menu do not provision | Implemented | Shared menu and Setup guide; provider descriptors have no install hook. Native post-install agent interaction still needs acceptance. |
| Explain purpose, storage, network/permissions and obtain consent before new-runtime download/execution; refusal stops | Implemented | No-consent returns disclosure and `consent-required` before venv/download/write. Agent must observe a real yes before using `--consent`; test consent/flag is not evidence of human permission. |
| Show phases/results; verify and reuse valid runtime without another download prompt | Implemented | Streamed checking, consent, preparation, helper verification and completion/failure events; actual Setup smoke and repeated reuse for both layouts. |
| Runtime/helpers ready only after real checks; separate plugin/tool/approval states | Implemented | Synthetic materialization plus dependency-backed validation required for ready; receipt/requirements/interpreter and cache ownership checked before reuse. External tools remain unverified and no approval is inferred. |
| Actionable missing-executor, policy, network and write failures, without hanging or fallback | Implemented | Agent preflight and next-action guidance for unavailable executor/policy; structured failure result and bounded subprocesses; rollback of only a newly created incomplete runtime. Native host denial and non-dev interpretation still need acceptance. |

## Remaining integration and merge safety

- WWA-04/05/06 own Python-free OS bootstrap/acquisition, pinned artifact trust
  and missing/unsuitable Python or missing venv/ensurepip recovery. Their
  entrypoints must honor the same consent, explicit package-root, private-cache
  and actual helper-verification boundary. This item implements real Setup with
  available Python, not a preview/no-op substitute.
- WWA-07 owns Python-free helper startup, full caller migration and its full
  trust matrix. This change removes the blanket plugin refusal from the one
  existing Python dispatcher so a successful Setup is usable now. A descriptor
  at either skill root or enclosing plugin root takes precedence over a
  standalone-shaped directory; standalone behavior remains covered by tests.
- WWA-08/09 own native update/lifecycle compatibility and legacy migration.
  Existing caches without this Setup verification receipt are preserved and
  reported for inspection, never silently executed or overwritten.
- Pending external acceptance: real authenticated native agent menu → consent
  → Setup interaction, native policy/local-executor failures, other OS/CPU
  combinations, live external tools and non-dev usability. None is inferred
  from tests, schema checks or extracted-package smoke.

No CI workflow, credentials, provider configuration, hooks, public installer,
shared project schemas or project-data lifecycle changed. No new integration
framework or alternate dispatcher was introduced. Existing validation CI can
run the unit suite; the network provisioning smoke is a maintainer command.
The code is suitable for coordinator review/integration with the documented
Python and later-item boundaries; public release still requires integrated
native acceptance. Memory recall/impact were attempted before implementation;
the connected graph had no matching symbols, so callers were traced directly.
Reflection found no additional durable memory beyond the committed contracts.
