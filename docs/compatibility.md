# Compatibility and observed evidence

B3 (`0.4.0a1`) retains one canonical `SKILL.md`, technical identifier `kkdesign-kit`
and Codex display name **KKdesign-kit**. Claude Code uses the same frontmatter
and native skill/slash-command handling. See [installation](installation.md).

The discovery paths were checked against the official
[Codex skills documentation](https://learn.chatgpt.com/docs/build-skills) and
[Claude Code skills documentation](https://code.claude.com/docs/en/skills).
Compatibility below is limited to the versions actually run, not all later or
earlier releases. Desktop sync, cloud sessions and managed enterprise policies
are unverified.

## B3 workflow evidence

- Python 3.9.6 on macOS 26.5 arm64: **104 regression tests passed**, including
  foundation, installer, source adapters, project lifecycle, lesson history,
  evidence integrity and prototype timeout/transition mismatch rollback.
  The final ship-stage CLI smoke additionally verified earlier/superseded lesson
  replay without mutation and rejection of history-root/hash-directory symlinks
  without copying private snapshots into synthetic public docs. These later
  corrections were not rerun through the pinned Codex/Claude or native Figma
  captures below; their historical local ZIP remains unchanged.
- Codex CLI **0.167.0**, project-installed extracted package in a fresh isolated
  home: actual `design` preflight/check, bundled review findings, feedback capture,
  inferred lesson authoring/deduplication, subsequent task lesson decision,
  packaging, extracted verification and foundation validation passed.
  Source extraction was removed; no Impeccable, Hoangsa, MCP, user skills or hooks
  were installed. The task remained `in_progress` with honest unavailable-canvas
  gaps. No prototype artifact was created by design/review.
- Claude Code **2.1.308**: after user reauthentication, the isolated B3 installed
  workflow probe passed. Actual task begin/check/handoff, all five fixture review
  findings, feedback/lesson deduplication, subsequent task lesson selection,
  package/extracted verification and foundation validation were reviewed against
  tool output and independent postconditions. Existing task hashes and installed
  skill bytes remained unchanged; no prototype artifact was created. The prior
  HTTP 401/OAuth-revoked attempt remains recorded as a historical failure.
  The tested ZIP matched the existing `0.4.0a1` archive exactly; that archive and
  checksum are not overwritten by this later checkout-evidence update.
- The controlled flawed fixture produced findings for wrong-platform reference,
  instance override, lost typography binding, long-content overflow and contrast.
  Output remains `assessment: evidence-only`, `approval: not-assessed`.
- A separate authenticated Figma design run created four editable 768×544
  macOS transfer-state copies in an isolated authorized review board. Each state
  retained 637 layers, 107 instances and 173 text layers. Separate persisted
  readback found no instance/property, typography, style/variable binding,
  editability or reaction mismatch. Two vector Y-coordinate differences per
  frame were approximately 0.0001221 px; retained as a scoped serialization
  exception, not concealed as exact geometry equality.
- All four genuine PNG exports were directly inspected: uploading, offline,
  complete and long-content states remained distinct; long filenames were
  intentionally ellipsized without overlapping adjacent content. This proves
  those rendered artifact states, not API calculations or native accessibility.
  During design/review capture all source and copied subtrees had zero reactions.
  Native snapshots, images, direct links and requirement/state mapping stay in
  the authorized private workspace, outside this public distribution.
- The separate, explicit prototype request persisted the requested five-edge
  graph through the installed helper. A first attempt correctly failed on nested
  `NAVIGATE` destinations; the existing acceptance copies were then promoted to
  page-level frames with absolute geometry and all 15 resolved modes preserved.
  No duplicate screens or original-product edits were introduced. Separate
  readback verified triggers, destinations, back action and the simulated
  1200 ms timeout / 0.2 s dissolve. Figma automatically added the entry flow.
  Structural error/retry, completion/back and long-content/cancel traversals
  passed; **interactive preview remains untested because the browser requires
  Figma login**. These are not API, text-validation, native or timing passes.
- Recorded native reaction defaults exposed a duplicate-edge comparison defect:
  `resetVideoPosition: false` made a serialized edge look different. A
  failing-before/passing-after smoke and permanent regression now verify
  semantic duplicate rejection before writes.
- Clean extracted public resources validated with 57 payload files, 32 required
  resources and 48 resolvable bundled Markdown links. Identical inputs produced
  identical ZIP bytes; modified extraction verification failed as intended.
  Private project paths and known private Figma identities were absent.

The source-only, opt-in runner uses the actual installed helpers and preserves
raw transcripts outside the checkout:

```sh
python scripts/smoke_workflow_harness.py --harness codex --credential "/private/auth/auth.json" --output "/private/results/b3-codex"
python scripts/smoke_workflow_harness.py --harness claude-code --credential "/private/auth/claude.json" --output "/private/results/b3-claude"
```

Use the dependency-equipped interpreter. Review transcript commands as well as
postconditions; model success text alone is insufficient. Failed authentication
or incomplete runs are retained as failures, never converted to passes.
See [B3 evidence](evidence/b3-verification.json) for current outcomes and gates.

## B2 project workflow evidence

| Environment / path | Observed scope |
|---|---|
| Codex CLI 0.167.0, macOS 26.5 arm64 | Project-installed package: real init, inspected/applicable plans, apply, changed refresh, validation and unchanged refresh |
| Claude Code 2.1.308, macOS 26.5 arm64 | Same project workflow through native skill activation |
| Python 3.9.6, committed Git source | CLI init, revision diff, authorized refresh, missing access, migration, replacement, recovery, rollback and relocated-kit validation |
| Authenticated Figma Plugin API capture | Real private-source read, bounded native export, adapter init/apply/validate and unchanged refresh |
| Direct Figma REST with a personal access token | HTTP behavior covered by synthetic fixtures; live PAT transport unverified |
| B2 user-scope harness execution, Linux/Windows live execution, other harness versions | Unverified; B1 user-scope discovery evidence is historical, not a B2 execution claim |

[B2 verification](evidence/b2-verification.json) records reviewed outcomes and
private-transcript hashes. [Before/after sample](evidence/b2-init-refresh-sample.json)
uses only a synthetic committed Git source. Failed attempts are not passes.

Figma evidence is not a unit fixture: the bundled read-only exporter ran through
an authenticated Figma connector, and its complete private result was ingested
by the Figma adapter. The scoped capture contains two selected roots, seventeen
nodes and two components. Styles are two of 732; variables are two of 917. There
were 68 unavailable property reads, no missing selected nodes and no truncated
values. Those limits remain explicit `partial` coverage, not a claim that the
entire DS was scanned. The Plugin API did not expose a REST revision/time; the
adapter records `unknown` revision and a content hash. No Figma node/prototype
mutations, live imports, render verification or external publication occurred.
Private file/node IDs, DS values and captures are not bundled in this repository.

The B2 runner is source-only, opt-in and separate from the B1 discovery probe:

```sh
python scripts/smoke_project_harness.py --harness codex --codex-auth-file "/private/auth/auth.json" --output "/private/results/b2-codex"
python scripts/smoke_project_harness.py --harness claude-code --claude-credentials-file "/private/auth/claude-credentials.json" --output "/private/results/b2-claude"
```

Run it with the dependency-equipped Python environment; `--python` can select
another interpreter without resolving away its virtual-environment symlink.
It installs an extracted package in an isolated project/home, removes the source
extraction, asks the actual harness to execute the installed CLI, then independently
checks preserved PRODUCT.md, changed token value and generated-kit validation.
Read the raw transcript as well: model success text alone is insufficient.
Recovery checks additionally kill a real writer process after its registry swap
and verify restoration of the prior valid kit. Windows uses a process-handle
liveness query, never `os.kill(pid, 0)`; its live behavior remains unverified here.

## Historical B1 installation evidence

The following table and `b1-harness-smoke.json` describe release `0.2.0a1`;
they do not establish B2 init/refresh behavior.

| Layer / environment | User scope | Project scope |
|---|---|---|
| Codex CLI 0.167.0, macOS 26.5 arm64 | Discovery, menu, actual bundled read: PASS | Discovery, menu, actual bundled read: PASS |
| Claude Code 2.1.308, macOS 26.5 arm64 | Discovery, menu, actual bundled read: PASS | Discovery, menu, actual bundled read: PASS |
| Installer, Python 3.9.6, macOS | Lifecycle / conflicts / integrity: PASS | Lifecycle / conflicts / integrity: PASS |
| Linux / Windows installer, Python 3.9 and 3.12 | CI matrix configured; remote result not observed here | Same |
| Linux / Windows live harness | Unverified | Unverified |
| Other harness versions / Figma / design tools | Unverified, outside B1 | Unverified, outside B1 |

[Reviewed smoke evidence](evidence/b1-harness-smoke.json) records harness versions,
normalized tool calls, final menu responses and SHA-256 of the private raw
transcripts. Paths use `<ISOLATED_ROOT>`; no account metadata, credentials,
session identifiers or customer data are published. This is a reviewed summary,
not a substitute for rerunning the probes in your target environment.

Each probe installed an extracted portable package in a fresh home and synthetic
project with spaces in its path, removed the source extraction, and launched the
actual CLI. Only authentication was reused. No user settings, Hoangsa,
Impeccable, optional hooks or MCP servers were installed. Harness-bundled system
skills/plugins remain present. Codex read SKILL.md and commands.md through its
shell; Claude's native skill activation supplied SKILL.md, and its Read tool
opened commands.md. All four responses rendered the full menu and correctly
reported `init` unavailable. Claude initially failed with revoked OAuth; after
reauthentication both scopes passed. Failed attempts are not counted as passes.

## Reproduce offline checks

From the source checkout:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/materialize_example.py --output .demo
.venv/bin/python scripts/kkdesign_core.py validate --design .demo/design
.venv/bin/python scripts/kkdesign_install.py package --output ../kkdesign-kit-0.4.0a1.zip
```

On Windows use `.venv\Scripts\python.exe`. The suite includes Stage-A regressions,
installer lifecycle/integrity/conflicts, source-adapter parsing and error cases,
and project plan/apply/migration/recovery. See the B2 evidence below for actually
observed results. No offline result claims successful model or Figma behavior.

## Reproduce live CLI probes

The source checkout's `scripts/smoke_harness.py` is an opt-in acceptance runner;
it is not automatically run by the installer, package or CI. It uses your
existing executable and its default model, so ordinary account access is needed.
It copies only the explicitly supplied authentication file into a temporary
private home, removes it at exit and never prints credential contents. It does
not change the real user's configuration. macOS Claude keychain auth may need
exporting to a temporary private credentials file; never commit that file.

```sh
python scripts/smoke_harness.py --harness codex --scope project --codex-auth-file "/private/auth/auth.json" --output "/private/results/codex-project"
python scripts/smoke_harness.py --harness codex --scope user --codex-auth-file "/private/auth/auth.json" --output "/private/results/codex-user"
python scripts/smoke_harness.py --harness claude-code --scope project --claude-credentials-file "/private/auth/claude-credentials.json" --output "/private/results/claude-project"
python scripts/smoke_harness.py --harness claude-code --scope user --claude-credentials-file "/private/auth/claude-credentials.json" --output "/private/results/claude-user"
```

Choose new output directories outside the checkout. Credentials remain external
to the artifact; use short-lived private files and remove any supplied exports
after testing. The runner captures raw local logs: review/redact them before
sharing. Exit zero still requires transcript review: confirm discovery from the
installed path, a real successful resource read, the seven-command menu and
honest unavailable-command status. Model self-report alone is insufficient.

Hooks remain opt-in future integration; installation does not add or enable
hooks at either scope. B1 probes cover discovery only. B2 init/refresh requires
the separate live project workflow. B3 live design/prototype evidence is distinct
from the offline record/fixture/learn/package checks above.
