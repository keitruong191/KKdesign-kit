# PROTO-01 — integration and acceptance

## Disposition

**Implementation and local browser verification are complete. Full native acceptance is not complete.** Core/package contracts, authored HTML/React demos, token-only recreation, and the iOS-profile browser approximation have current evidence. Native browser/Figma prerequisites and observed native-agent scope failures remain explicitly separate; none is reported as passed.

During implementation verification, no source commit, branch change, publish, deployment, or dependency provisioning was performed. The later, explicitly requested source PR is recorded below. The approved product scope remains a DS-first PM/PO feature-flow demonstration, not backend integration or production architecture.

## Verification performed

| Surface | Current result | Evidence |
|---|---|---|
| Python compatibility | Python 3.9.6 compiled syntax for 25 modules | [local-integrity.md](local-integrity.md) |
| Integrated regression | 165 unittest cases passed, 18.021 seconds | [local-integrity.md](local-integrity.md) |
| Package/extraction | Version 0.5.0a1; 63 files / 42 required resources verified in a relocated path with spaces | [local-integrity.md](local-integrity.md) |
| Actual CLI lifecycle | Refresh → inspect → apply → task check → foundation passed with a delivered React artifact and dependency symlink; relocated launcher also exercised | [local-integrity.md](local-integrity.md) |
| HTML | Required fields, review/edit, cancel, error/retry, success/list, double submit, reset/timer, HTTP and actual file entry observed at 1280×800 | [html-browser.md](html-browser.md) |
| React / code reuse | Actual project Button/TextField/Card/theme rendered; full scoped flow, loading cancellation, repeatability and reload observed at 1280×800 | [react-browser.md](react-browser.md) |
| React / token-only / iOS profile | Recreated components, preserved product-ios profile/platform, full scoped flow and reference captures at 390×844 | [ds-platform.md](ds-platform.md) |
| Missing DS / hostile data | Controlled source-inspection probe blocked rendering, retained in_progress, created no generic artifact, and did not execute source instructions | [ds-platform.md](ds-platform.md) |
| Native Codex / Claude | Target/routing and selected helper/artifact/build steps observed; full native browser/handoff not passed; scope deviations disclosed | [native-harness-figma.md](native-harness-figma.md) |
| Native Figma / native iOS | PENDING; no authorized native tool/context or native behavior proof | [native-harness-figma.md](native-harness-figma.md), [ds-platform.md](ds-platform.md) |

The implementation-stage package SHA-256 is `9248dd765cfdb684515cb1fae65fe66f91c00801bb28e3e1a0af4e0625835ae5`. The table above records that stage, before integration with newer marketplace/Setup work. Syntax checks are not a claim that unconfigured linters/type checkers ran. Model tests/builds and schema checks are not browser or human approval.

## Source PR integration

The owner subsequently requested a separate branch, commit, and PR. Integration
uses `origin/main` at `dbd692a`, preserving the newer marketplace distributions,
verified helper entrypoints, Setup contracts, and measured-support documentation.
The original checkout's unrelated contributor/configuration edits are excluded.

- Current-main unittest run: **212 cases; 203 passed, 9 skipped**, 35.735 seconds,
  exit 0. Skips require native Windows PowerShell and ACLs.
- Relocated package verification: **85 files, 51 required resources**, exit 0.
  SHA-256: `943139ee0d2ee83cca6819d0b7080d15feac7fae18117606cedcb906b44a079f`.
- Actual relocated `refresh` → `plan` → `apply` → task check → foundation
  validation passed again for the delivered React/dependency-symlink fixture.
- The fixture README now invokes the current verified OS helper entrypoint;
  it no longer prescribes Python-on-PATH startup for installed plugins.
- The documented verified OS helper completed disposable-fixture `init` → `plan`
  → `apply` → `validate` using an intact existing private cache, without
  provisioning. Earlier probes rejected a symlink-aliased home and a changed
  cached Python tree; the cache was preserved, not repaired or counted as ready.
- A current-main review caught a dropped `references/learn.md` completeness
  requirement. An unbundled source missing the guide packaged before repair;
  restoring the requirement makes the same missing-guide source fail before
  creating an archive. The review finding is closed.

These additional checks do not replace or upgrade the historical browser/native
observations below. Native browser/Figma acceptance and reported scope deviations
remain unresolved.

## CI follow-up — isolated runtime fixture

The owner requested a separate repair sub-session, `fix/pr21-ci-runtime`, after
PR #21 failed. The original [push run](https://github.com/keitruong191/KKdesign-kit/actions/runs/42984341249)
and [PR run](https://github.com/keitruong191/KKdesign-kit/actions/runs/42984411186)
each failed all six OS/Python validation variants with the same eleven handoff
failures. Bootstrap smoke passed. Existing logs were used as failure evidence;
the old runs were not rerun merely to confirm the report.

The source checkout contains plugin metadata, so its real dispatcher requires a
verified private Setup runtime. The handoff fixture inherited the developer HOME
and accidentally borrowed its existing cache locally. Fresh CI homes had no
matching runtime and correctly refused before task execution. One negative test
also passed for that wrong refusal reason. This was a test precondition/isolation
defect, not authorization to weaken production startup.

The fixture now reuses `test_setup`'s owned, no-download runtime and receipt
setup, including native Windows ACL handling. Every launcher subprocess receives
the fixture HOME and USERPROFILE; interpreter-injection variables are cleared.
Actual dispatcher/task/evidence/handoff paths and meaningful negative assertions
are retained. The incomplete-artifact test distinguishes its artifact rejection
from missing Setup; an incidental scope-wording assertion was removed.
Production scripts, dependency requirements and CI policy are unchanged.

Post-fix local checks used an empty, physically resolved contributor HOME and
USERPROFILE, not the developer cache:

- Focused handoff suite: **12 passed**, 7.796 seconds.
- Full suite: **212 cases; 203 passed, 9 native-Windows skips**, 31.680 seconds.
- Independent real-dispatcher smoke: unconfigured HOME refused without task/cache
  mutation; isolated verified HOME completed begin/evidence/artifact-only
  delivery/check/foundation; deleting the delivered entry then failed both
  integrity gates while preserving task bytes.
- The workflow's downstream materialize → foundation validate → package steps
  passed. Relocated package verification passed with **85 files / 51 required
  resources** and the unchanged payload SHA-256 recorded above.

Remote matrix completion must be observed on the repair commit's PR checks,
not inferred from these local results. Native browser/Figma and human design
acceptance remain separate.

## Current-state audit, not only worker reports

Main read the canonical reports, actual README instructions, task/evidence metadata, and rendered reference/form/result captures. Main independently reopened the current React app from its README, observed entered content in review, reached local success `REQ-1042`, saw one list item, and reset to the empty entry. Main also replayed success/reset on the accepted compact prototype and on the replacement HTML artifact through its actual `file://` entry.

Using the final relocated kit, Main ran both task check and foundation validation against all accepted projects:

| Location-index key | Accepted task | Task check | Foundation |
|---|---|---|---|
| html | html-demo | checked; 2 evidence records | pass; no errors/warnings |
| react | react-demo | checked; 4 evidence records | pass; no errors/warnings |
| platform | ios-token-demo-acceptance | checked; 4 evidence records | pass; no errors/warnings |
| gapProbe | ds-gap-probe | checked; 1 evidence record | pass; no errors/warnings; intentionally in_progress without an artifact |

Machine-bound project roots and the extracted kit are recorded only in ignored `.kkdesign-kit/planning/ds-interactive-prototype/acceptance-locations.json`. App sources, README files, screenshot captures, raw transcripts, and helper evidence remain in those selected projects, not public examples. Temporary capture/replay servers and browsers were shut down after use.

The already recorded flow/criterion descriptions were normalized to stable IDs during final integration, and README checkpoints/handoff mappings now use the same IDs. That normalization is explicitly not a claim that the IDs existed before the initial browser run. New helper-wrapped audits record actual metadata and offline checks; genuine browser evidence was retained unchanged. App entry bytes and lesson review/hash were unchanged, so these audits do not fabricate a new browser or approval result.

## Requirement / backlog accounting

| Requirement / acceptance | Local implementation and evidence | Remaining boundary |
|---|---|---|
| REQ-01 / AC-01 | One explicit prototype route with Figma/HTML/React; native target question and design/review no-interaction probes observed; HTML/React browser outputs exercised | Full native target surfaces and Figma remain separate |
| REQ-02 / AC-02 | Valid planning/lesson/profile gates before begin; actual init-generated profile identity supported; accepted tasks planned before artifact creation | Earlier invalid-order/fixture attempts are preserved and excluded, not retroactively approved |
| REQ-03 / AC-03 | HTML and token-only React are recorded as recreated; React code fixture is actually imported/rendered; real source IDs/hashes and code references recorded | Missing warning token remains a scoped source gap; no invented DS value |
| REQ-04 / AC-04 | Browser captures and computed values compared with synthetic references; Atlas identity, declared palette/type/control treatment observed | Documented shell/card/helper-content differences remain for human design review; no pixel/native parity claim |
| REQ-05 / AC-05 | Real local-state main/alternative flows, validation, error/retry/success and single-item outcomes observed | No business API/backend/auth fidelity is claimed |
| REQ-06 / AC-06 | Back/edit retains draft, cancel clears it, reset clears demo state and cancels pending 800ms work; repeated-submit/storage observations recorded | Scope is the deterministic fixture, not arbitrary product behavior |
| REQ-07 / AC-07 | Actual browser/state/render captures and helper evidence; task/foundation integrity checked independently | Native CLI browser proof and human approval remain pending |
| REQ-08 / AC-08 | Exact artifact root, project-relative entry/README/cwd, task-relative evidence, artifact-only handoff and immutable rejection behavior implemented/tested; README reopen exercised | Launch metadata itself grants no execution/publication permission |
| REQ-09 / AC-09 | Local ownership/path boundaries and no business integration; unsafe paths reject, single-winner begin tested, partial work retained; hostile source probe ignored instructions | Native CLI scratch writes outside selected projects are recorded FAIL side effects, not accepted permission behavior |
| REQ-10 / AC-10 | Shared routing/resources for both harnesses; capability-specific prerequisites, relocated package, non-web regressions and refresh compatibility verified | Claude restricted-mode slash discovery and native browser/Figma limitations remain disclosed |

## Error / edge-case evidence

| Cases | Exercised evidence or explicit limit |
|---|---|
| EC-01, E-01 | Actual native unresolved-target question; design/review stayed non-prototype; absent Figma context remains pending rather than target fallback |
| EC-02, E-02 | Preflight regression covers stale lesson/index, missing/malformed profile, platform mismatch, missing/invalid destination, and no mutation; actual init→begin→foundation path passed |
| EC-03–04, E-03 | Token-only browser output; absent warning alias recorded; separate missing-core-DS/hostile-note probe kept task in progress and produced no generic UI or source-command side effect |
| EC-05, E-04–05 | Initial unavailable screenshot evidence was not called pass; capture backend was recovered and acceptance re-exercised. Native generated apps remain in progress without native browser proof |
| EC-06, E-06 | Real double-click/single-item, reset during pending work and wait beyond delay, back/edit/cancel/retry/reset/reload observations |
| EC-07, E-08 | Actual core/schema/helper tests for absolute/URL/traversal, symlinks, missing/type errors, invalid cwd/argv, file/root modes, and preserved prior task bytes |
| EC-08, E-07–08 | Missing artifacts/checks/citations/mapping cannot bypass delivery; deleted entry/README detected; repaired handoff uses candidate rather than stale persisted paths |
| EC-09, E-09 | Two actual child processes positively reached a resolved-path barrier; exactly one begin won. Duplicate begin preserved task/artifact bytes. No post-begin multiwriter safety or adversarial filesystem guarantee is claimed |
| EC-10–11, E-08–09 | After-begin partial entry retained; incomplete delivery rejected; blocked in-progress handoff accepted; later completion works; temp-open/replace failures preserve saved task state |
| EC-12, E-10 | Missing resources are rejected by installation regression; native missing-runtime limits disclosed; forced occupied-port React launch exited 1 with strictPort and no fallback port |
| EC-13 | Existing Figma/non-web destination, template, source/profile/lesson/history and evidence regressions passed; no historical fixture restamping or global Node/Figma dependency |

These observations do not turn the skill into a filesystem sandbox. In particular, the native scratch-scope failures are counter-evidence to a blanket claim that every external agent honors the instructions.

## Review repairs and scope refinements

Read-only agreement reviews found and rechecked fixes for schema/non-web isolation, retained manifest resources, file-mode cwd and project-root cwd, actual delivery statuses, scope-safe launch wording, code-vs-token fixture separation, required description, init/profile identity, stale-artifact repair, and React refresh compatibility. No supported blocking finding remains open in the reviewed new implementation; this is not a claim that all pre-existing behavior is defect-free.

Two compatibility refinements extend the original file list:

- `scripts/kkdesign_project.py` and `tests/test_project.py`: exclude user-owned prototype runtime trees from broad contract scans/copies, while checking real declared artifacts and projected references. A delivered React refresh/apply regression with node_modules symlinks passes; deleting its entry still blocks apply. A throwaway old-traversal mutation made that regression fail.
- `scripts/smoke_workflow_harness.py`: include `design/prototypes` in the no-interaction artifact boundary. The legacy credential/provisioning smoke runner itself was not run; direct native route-boundary observations are reported separately.

Current-state audits caught two acceptance-fixture defects after worker task checks: raw observation JSON under tasks, and a lesson citation using the wrong relative base. The guide now explicitly requires raw JSON outside tasks plus both task/foundation checks. The rejected HTML project's evidence remains intact under `htmlPrevious`; its replacement was initialized/begun and exercised afresh. The active React citation was corrected without changing the lesson hash or pending claim.

Browser-device issues were also kept out of product claims: initial target/screenshot failures and shared-CDP cross-page interference were discarded as proof. Final captures use separate browser endpoints, explicit viewport setup, verified target URLs, and actual saved screenshots.

## Native follow-through and human review

1. Provide authorized interactive browser capability inside each native CLI, then repeat the native-generated app's full scenario/render/evidence/handoff sequence. Parent-browser proof does not substitute for that native surface.
2. For Claude, use a mode where the installed slash skill is actually discovered; a restricted-mode manual guide read is not a slash-route pass. Use the already available compatible Python runtime rather than treating system Python dependency absence as feature completion.
3. Recheck exact allowed write scopes. The disclosed native scratch-path writes must not be accepted as compliant behavior; those outside files were not read, moved, or deleted by the coordinator.
4. Provide an authorized synthetic Figma file/project and Plugin API/tool context for graph mutation/readback/preview. Native iOS behavior also needs a real native surface; the browser approximation does not establish it.
5. A human reviewer should disposition the measured reference composition differences and any real-project DS coverage gaps. No human design approval has been inferred.

All sixteen plan tasks have implementation/verification or capability-disposition records. This completes local implementation and reporting, not full native or product-design acceptance.
