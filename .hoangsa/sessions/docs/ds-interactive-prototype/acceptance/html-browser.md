# proto-12 HTML browser acceptance — `html-demo`

**E2E behavior: PASS. Browser screenshot/reference inspection: PASS with explicit layout deviations. Handoff: `design_verified_review_pending` (human review pending). Task helper check and foundation validation: PASS.**

A disposable token/spec-only synthetic Atlas web project was initialized using the extracted canonical skill. Planning, profile `product-web`, lesson, flows, required fields, states, viewport, reference, source decisions, and component/token mappings were recorded before app files were added. `kkdesign_task begin` succeeded for `html-demo` before authoring the dependency-free HTML app. Main identified an evidence-placement defect in the first project; that project is preserved unchanged under location key `htmlPrevious`. Its raw JSON had been written under task `captures/`, where the foundation validator treated it as an invalid evidence record. The replacement below places the raw observation payload only in the artifact root and records it through the evidence helper.

Project-relative paths are recorded in `.kkdesign-kit/planning/ds-interactive-prototype/acceptance-locations.json` under `html`:
- Task ID: `html-demo`
- Artifact root: `design/prototypes/html-demo`
- Entry: `design/prototypes/html-demo/index.html`
- README: `design/prototypes/html-demo/README.md`
- Raw observation payload: `design/prototypes/html-demo/browser-observation.json`
- Task record: `design/tasks/html-demo/task.json`
- Evidence: `design/tasks/html-demo/evidence-0001.json`; screenshots in `design/tasks/html-demo/captures/`

## Real browser behavior

Dedicated headless Chrome CDP session `127.0.0.1:9241`; viewport was explicitly set and verified as 1280×800 CSS px before every retained screenshot. HTTP entry was `http://127.0.0.1:8123/`. The static reference and actual `file://` app entry were opened on the same exclusive endpoint. Screenshots were regenerated, opened, and matched to the state/file names.

| Scenario | Observed outcome |
|---|---|
| Initial Requests | Empty list, New request, Reset demo. `captures/01-initial-1280x800.png`. |
| Required title and description | Empty submission showed both field errors and blocked review. `captures/02-form-empty-1280x800.png`, `03-required-errors-1280x800.png`. |
| Review and edit | Review showed entered values; Edit request retained them in the form. `04-review-1280x800.png`, `05-edit-retained-1280x800.png`. |
| Cancel and reopen | Cancel to list then New request reopened with blank title and description. `06-cancel-reopen-empty-1280x800.png`. |
| Simulated error and retry | Recoverable error shown; values retained; Retry reached deterministic local success `REQ-1042`. `07-simulated-error-1280x800.png`, `08-success-1280x800.png`. |
| Submitted list and success reset | One `REQ-1042` item; Reset restored empty list. `09-list-after-success-1280x800.png`, `10-reset-after-success-1280x800.png`. |
| Loading, reset, stale timer | Loading shown for the documented 800 ms; Reset returned to empty; after 1000 ms still empty. `11-loading-1280x800.png`, `12-reset-from-loading-1280x800.png`. |
| Double submit | Double-click Submit yielded one request; list count was one. `13-double-submit-single-item-1280x800.png`. |
| Direct file mode | Actual file entry opened; New request → filled values → Review worked. `14-file-entry-review-1280x800.png`. |
| Reset from error | Reset from visible simulated error returned to empty; second reset stayed empty. `17-reset-from-error-1280x800.png`. |
| Storage and diagnostics | localStorage/sessionStorage keys remained empty. Console and page errors empty. HTTP document GET returned 200 (subsequent reloads 304); file entry/reference documents opened successfully. No business API, external runtime assets, or network fetch/XHR were observed. |

Reference screenshot: `captures/16-reference-shell-1280x800.png`. Full browser observations are in `design/prototypes/html-demo/browser-observation.json`; helper-wrapped evidence references all captures, app/README, and reference in `design/tasks/html-demo/evidence-0001.json`. Task directory contains task/evidence wrappers, task-local feature brief required by foundation validation, and image captures; raw observation JSON remains under the artifact root.

## Static reference and design-system comparison

The source registry identifies `atlas-demo` as local token/spec/reference data only; it provides no importable components. The task maps `button.primary`, `textfield.default`, `card.default`, and `theme.light` as **recreated**, not reused/native. App and reference computed values match Arial, canvas `rgb(245,247,250)`, brand `rgb(36,87,166)`, 64px topbar, and 224px navigation rail. Captures show the app's input/card/primary-action treatment using the declared palette and semantic tokens.

Measured at 1280×800: reference form card x=280, y=238.6, w=594.2, h=445.3; companion guidance card x=898.2, y=238.6, w=325.8, h=253.3. Demo form card x=372, y=266, w=760, h=548; document height is 883px. The demo presents only the in-scope Requests navigation rather than reference Overview/Reports rows and omits the static companion guidance card. Its form is wider/taller than the reference and extends below the initial viewport, although key actions are visible. This is an observed composition gap—not pixel parity or native-fidelity evidence—and is listed for reviewer disposition in the task handoff.

## Handoff and integrity

- README documents HTTP server launch, direct-file launch, and walkthrough; HTTP and direct-file entry were both opened, with file-mode interaction observed.
- Final `kkdesign_task check --project "$PROJECT" --task-id html-demo` exited 0: `checked`, 2 evidence records. Offline schema/path/reference integrity only; not browser or design approval.
- `kkdesign_core validate --design "$PROJECT/design"` exited 0: `pass`, no errors or warnings. The initialized task's feature-brief reference was missing at the task-relative path, so the actual project brief is also retained as `design/tasks/html-demo/feature-brief.md`; validated references now resolve without relocating the raw observation payload into the task directory.
- Evidence-linked artifact handoff is `design_verified_review_pending`; measured composition differences remain explicitly for human review.
- Actual task/artifact paths are retained in the selected replacement project; the location index provides its machine-specific root to Main. The prior failed project remains intact under `htmlPrevious` for traceability.
- No Node/Figma, installs, business API, upload, or deployment. The owned tab and local HTTP server were closed; the CDP service is Main-owned and was left running.

## Final criterion traceability audit

Main assigned `FLOW-01`–`FLOW-05` and `DEMO-01`–`DEMO-08` to the already recorded flow/criterion content, without changing demo behavior. IDs were finalized during integration, not retroactively claimed to exist before the initial browser run. README checkpoints and handoff mappings now use those IDs and cite the original browser snapshot. New `evidence-0002.json` is an actual metadata/offline-integrity audit, not a second browser or approval claim. Entry bytes and the lesson review/hash were unchanged; final task check and foundation validation passed with the exact delivery kit.
