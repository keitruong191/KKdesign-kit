# WWA-10 onboarding verification and acceptance handoff

Implementation/docs can be integrated after coding review. Publication, native
platform/account acceptance and observed non-dev usability are separate and
remain pending under the owner's acceptance decision. This document grants no
permission to release, tag, submit a listing or merge main.

## Publication observation

WWA-11 supersedes the historical WWA-10 no-source observation: author-operated
review/prerelease sources now exist in the public repository for both providers,
at version `0.5.0a1`. See [source provenance](../marketplace-sources.md) and
[remote native evidence](marketplace-sources.md) for exact commands, immutable
snapshots and measured pin limitations. The default branch is not the built
marketplace. Review-channel availability does not establish production release
approval, authenticated menu/Setup or observed non-dev usability.

A repo marketplace, OpenAI public directory, Anthropic Directory and
claude-plugins-official are separate publication/review states. No release,
tag, legacy release-workflow dispatch or official submission was performed.

## Available maintainer entrypoints

Run these from a reviewed checkout with an external Python 3.9+ development
environment containing `requirements.txt`. The `python` below means that
interpreter. Choose a new output directory outside the checkout; placeholders
are review locations, not published endpoints. These are contributor commands,
not runtime terminal instructions for users.

```sh
python -m unittest discover -s tests -v
python -B scripts/build_claude_marketplace.py --output '<new-outside-source>/claude.zip'
python -B scripts/build_codex_marketplace.py --output '<new-outside-source>/codex.zip'
python -m zipfile -e '<new-outside-source>/claude.zip' '<new-outside-source>/claude'
python -m zipfile -e '<new-outside-source>/codex.zip' '<new-outside-source>/codex'
```

Verify the extracted resources with the development interpreter (integrity only):

```sh
python -I -B '<new-outside-source>/claude/kkdesign-marketplace/plugins/kkdesign-kit/scripts/kkdesign_install.py' verify --source '<new-outside-source>/claude/kkdesign-marketplace/plugins/kkdesign-kit'
python -I -B '<new-outside-source>/codex/kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit/scripts/kkdesign_install.py' verify --source '<new-outside-source>/codex/kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit'
```

Actual installed-package execution probes:

| Entry point | Expected outcome and scope |
| --- | --- |
| `python -B scripts/smoke_posix_setup.py` | On native macOS/GNU Linux: builds/extracts both provider layouts, consent-required with no writes, real pinned acquisition/provisioning with no PATH Python/Node, reuse, materialize/validate/task/learning and package/extracted verification, tamper rejection and data preservation. No model or native marketplace discovery. |
| `python -B scripts/smoke_posix_setup.py --incomplete-python '<absolute-Linux-interpreter>'` | Same native Linux smoke after independently confirming this actual system Python lacks venv or ensurepip. Do not fake the interpreter or remove system modules. |
| `python -B scripts/smoke_windows_setup.py --inspect-artifacts` | Downloads and checks both pinned Windows archives and contents without executing Windows bytes; portable integrity only. |
| `python -B scripts/smoke_windows_setup.py` | On each native Windows CPU: actual Windows PowerShell acquisition/helpers/reuse, spaces/CWD, trust rejection/preservation. Skips or syntax parsing on another OS are not Windows acceptance. |
| `python -B scripts/smoke_native_lifecycle.py --output '<new-outside-source>/lifecycle'` | On native macOS/GNU Linux with both provider CLIs: isolated Git smart-HTTP marketplaces, native install/update/enable/disable/remove/reinstall, real shared runtimes and surviving consumers/project data. No model credentials or human interaction. |
| `python -B scripts/smoke_standalone_migration.py` | POSIX relocated plugin Setup: actual synthetic managed migration, retained ledgers/backups/project data, both provider layouts. Historical copies are test fixtures, not fallback installation. |

For a direct project-start check after consented Setup in a disposable test home,
set `SKILL_DIR` to either extracted skill directory above and `PROJECT_ROOT` to
a separate synthetic project with a valid local `sources.json` (see
[source formats](../source-adapters.md)). Run from an unrelated CWD:

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project init --project "$PROJECT_ROOT" --sources "$PROJECT_ROOT/sources.json"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project plan --project "$PROJECT_ROOT" --plan "$PLAN_ID"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project apply --project "$PROJECT_ROOT" --plan "$PLAN_ID"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project validate --project "$PROJECT_ROOT"
```

Use the actual `id` returned by init as `PLAN_ID`; inspect changes before
explicitly authorizing apply in the synthetic probe. Windows maintainers use
the native PowerShell helper argument-array form in [helper invocation](../../references/helpers.md)
with the same helper/arguments. A direct helper run verifies project behavior;
it does not prove an agent selected or explained these steps to a person.

The acquisition probes grant consent for their own disposable synthetic test
only, download real runtime/dependencies, and need approved network access and
writable user storage. They do not establish user permission. Keep raw logs
outside the repository. Never copy credentials, relax policy or buy resources
for a probe. The provider guides include exact native registration, install,
invocation and lifecycle commands; the lifecycle probe supplies working disposable
transport when testing cache relocation. Do not use old standalone live-model
harnesses as the marketplace acceptance path.

## Owner-arranged native and human cases

Use a clean authorized test profile, a synthetic product project, unrelated CWD
and package/project paths containing spaces. Record OS version, CPU, provider
surface/version, catalog revision and plugin version. Supply authentication only
through the provider's authorized sign-in flow; never copy primary credentials.
Do not repeat the previously known unauthenticated menu failure as evidence.

| Required case | Exact exercise | Expected observation |
| --- | --- | --- |
| Both provider agent journeys on macOS ARM64 | Native install from approved review source; restart; open `$kkdesign-kit:kkdesign-kit` or `/kkdesign-kit:kkdesign-kit`; choose the same invocation with `Setup`, then `init` | Correct version/namespaced discovery; menu readable without Python or download; runtime consent before acquisition; helper-ready and external-tools state separate; init stages a plan, apply requires authorization, validation succeeds |
| macOS Intel | Native POSIX smoke then both provider agent journeys on x86_64 | Same outcomes measured on actual Intel hardware; ARM64 results do not count |
| GNU/Linux x86_64 and ARM64 | For each recorded GNU libc 2.28+ distro/CPU, native smoke with no Python/Node and genuine missing-venv/ensurepip case, then both provider journeys | Pinned private runtime/helpers work without system repair; repeated Setup reuses; record distro rather than claiming all Linux |
| Windows x64 and ARM64 | Each CPU's native smoke and both authorized provider surfaces, native separators/spaces, actual ACL/write and execution-policy denial | Native Windows PowerShell 5.1, no WSL/Git Bash or policy change; denial reports error and no ready; prior data preserved |
| Consent refusal and constrained access | Decline runtime download; separately test authorized network/write/policy denial | No acquisition/execution after refusal; plain-language cause/next step; no sudo, bypass or alternate installer |
| Existing and broken cache | Repeat Setup, remove only a disposable owned test runtime, tamper a disposable receipt/library, change test requirements | Valid reuse; missing/incompatible runtime needs Setup/consent; changed/unowned cache rejected and retained, no arbitrary interpreter |
| Duplicate copies and migration | Synthetic intact managed, modified and unmanaged user/project/ancestor copies; decline then separately authorize migration of every eligible copy | Exact versions/locations disclosed; separate migration consent; modified/unmanaged copies preserved; fresh-session discovery reflects completed moves |
| Shared native lifecycle | Run lifecycle probe, then observe provider update/uninstall in agent | Same contract reuses; changed requirements need consent; enable/disable never provisions; other consumer, project data and private caches survive removal |
| Non-dev usability — at least one participant | Ask someone unfamiliar with dev environments to follow README → native install → menu → Setup on an authorized measured surface, using the recorded review source and exact version | Observer records completion, prompts, assistance, misunderstandings and failure point; no runtime terminal homework; do not infer success from automated tests |
| Live design tools | Authorize the specific external connection in a synthetic workspace, run the requested design/review operation | Read back saved structure and inspect render/playback as appropriate; runtime/schema checks alone do not establish live results or human design approval |

Until these cases are observed, the [matrix](../compatibility.md) keeps the
relevant combinations pending. Production onboarding still waits for owner approval; the persistent review
sources are now available for owner-arranged observation. A maintainer review observation may be
recorded earlier but must name that limited source scope. No participant has
been observed for WWA-10 yet; no improvement or usability pass is claimed.

## Feedback record

Submit a redacted record to the owner/reviewer through the agreed review channel;
this kit sends no automatic telemetry. Copy this synthetic template and replace
only with non-private facts:

```text
Case: native-agent / usability / acquisition / lifecycle / migration
Date: YYYY-MM-DD
Plugin version: 0.5.0a1 (example; record actual)
Catalog: approved public source + immutable revision, or "isolated review source"
Provider: name, version, surface; user/project scope
Platform: OS version, CPU; Linux distro/libc when applicable
Step: install / discovery / menu / consent / Setup / init / apply / workflow / removal
Observed: pass / failed / blocked / not run; expected and actual outcome
Diagnostic: error code + redacted short message (no personal paths or private IDs)
States: plugin loaded? runtime/helpers ready? external tools tested separately?
Consent: declined / explicitly granted / not requested; migration consent separate
Preservation: project data, other consumer, private cache unchanged?
Usability: non-dev participant pseudonym; completed? assistance? confusing prompt?
Evidence scope: automated helper / native command / authenticated agent / human observation
```

Keep account names, tokens, customer/source registries, private design IDs,
local machine paths, full environment dumps and raw provider logs out of commits
and PR attachments. Private raw evidence may stay with the authorized observer;
share a sanitized summary and synthetic reproduction only. A pass must identify
what was actually observed and never imply publishing or design approval.

## WWA-10 criterion verdict

| Criterion | Implementation/docs verdict | External acceptance |
| --- | --- | --- |
| Published source/version, provider-specific install/Setup/workflow | Native maintainer flows and exact discovered invocations documented; no invented public commands | Review sources published and native installation recorded by WWA-11; production approval pending |
| Truthful native matrix and separated channels/execution/tools | Consolidated measured macOS ARM64 evidence, implementation-only targets and channel boundaries | Other OS/CPU/surfaces and authenticated journeys pending |
| Missing Python goes to agent Setup, no terminal or standalone fallback | README/install flow uses agent Setup and init; historical maintenance separated | Human observation pending |
| Actionable consent/network/policy/write/runtime/duplicate errors | Recovery table and shared Setup/migration/lifecycle guides document real current behavior | Native denial/account observations on pending platforms remain pending |
| Non-dev completes menu and Setup with sanitized observation | Practical observation and feedback protocol supplied; no fabricated participant result | At least one owner-arranged participant still required |

No remaining integration API is delegated to a later backlog item: WWA-01–09
supply packaging, runtime, trusted helpers, lifecycle and migration. Remaining
work is owner production review and external acceptance, plus fixing any real
defect those observations uncover. Code readiness is not release readiness.
