# Platform acceptance — proto-14 / E2E-03

## Verdict

**PASS for the scoped browser prototype acceptance.** The React token/spec/reference-only prototype was rendered and walked through at the selected iOS profile viewport, screenshots were captured from a verified dedicated Chrome page and compared with the synthetic reference, and offline integrity checks passed. **Native iOS behavior/fidelity remains explicitly PENDING; no native claim is made.** The task remains `design_delivered` for the browser approximation, not native acceptance.

Review the preserved isolated project using the location index entry `platform`. The completed artifact/task is `design/prototypes/ios-token-demo-acceptance/` and `design/tasks/ios-token-demo-acceptance/`. The earlier `ios-token-demo` attempt is preserved; it began app-file creation before a successful task begin and is not the accepted task. The clean acceptance task `ios-token-demo-acceptance` was planned and successfully begun before creating its artifact.

## DS source and platform

- Project initialization used the extracted canonical skill and only the declared synthetic token/spec source, iOS context, brief, and reference; no `code-ds` files were copied. `atlas-demo` registry revision: `local:16218363ac96a41f`; source content hash: `16218363ac96a41f686181ea4084c7ee6b2ecc2262ddbfedcb8e397ffbc961cb`.
- Profile `product-ios`, platform `ios`, and applicable lesson `DL-001` were retained. Browser viewport was **390×844 CSS px**. The app labels itself a browser approximation. It does not claim native iOS layout, behavior, or fidelity.
- Components are **recreated**, not imported/reused: shell, primary button, text field, and summary card use registry-declared `button.primary/default`, `textfield.default` empty/filled, `card.default/content`, `theme.light`, and sourced token values. Provenance is recorded in task planning/source mapping and the artifact README.
- A warning semantic color token/alias is absent from registry coverage. No value was guessed or assigned; the specified capture flow does not depend on warning styling. Any future warning visual remains pending authoritative source. No generic fallback DS was added.
- Fictional Atlas content and all outcomes are synthetic/local/in-memory. No business API, credentials, external assets, package install/download, publish, or upload was used.

## Real launch and browser evidence

Actual launch command:

```sh
npm --prefix design/prototypes/ios-token-demo-acceptance run dev -- --host 127.0.0.1 --port 8125 --strictPort
```

Vite **5.4.21** reported ready at `http://127.0.0.1:8125/`. Browser was **Chrome 157.0.8103.40** on the dedicated acceptance capture endpoint. The actual app page URL and inner viewport (390×844) were checked before each saved screenshot. Reference was loaded separately from project `reference-shell.html` at the same viewport. Captures are under `design/tasks/ios-token-demo-acceptance/captures/`:

- `initial-list.png`
- `form-empty.png`, `form-validation.png`, `form-populated.png`
- `review-initial.png`, `review-edited.png`
- `feedback-error.png`, `feedback-success.png`
- `list-after-success.png`, `reset-after-success.png`
- `loading-pending.png`, `reset-after-loading-delay.png`
- `double-click-success.png`, `list-after-double-click.png`
- `reference-shell.png`

### Walkthrough observations

- Initial empty Requests list rendered. New request opened the empty form. Empty Review displayed the required-title/description feedback.
- Cancel discarded the draft; reopening produced empty title and description fields.
- Populated title and description appeared in Review. Edit returned to the form with values preserved; edited title was reflected in the next Review.
- Simulated recoverable error retained the draft and displayed its explanatory message. Retry reached the simulated success state with one stable `REQ-1042` result.
- Back to requests showed one item. Reset returned to the empty list. Reset after success also cleared the created item.
- Simulated loading displayed a pending state. Reset then waiting 1,100ms left the initial empty entry visible; no delayed transition repopulated the UI.
- A rapid physical double-click on Submit reached one success result; the completed view had no Submit control, and Back to requests showed exactly one `REQ-1042` item.

### Reference comparison

The synthetic reference shows a workspace header/sidebar, request-details card, helper copy, and paired Cancel/Review actions. The recreated compact screen uses a branded top header, mobile bottom navigation, single-column form, and sourced colors/type/spacing with rounded bordered surfaces. The content, blue primary action, white surface, muted secondary text, and card/control treatment align with the reference at the compact viewport; shell/navigation and helper-content details differ. This is a scoped recreation, **not pixel parity**; no numeric pixel-diff threshold was specified.

## Integrity checks and boundaries

Commands were run with the extracted skill's already available Python runtime:

- `"$PY" -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task begin --project "$PROJECT" --record "$PROJECT/design/acceptance-plan.json"` → exit 0, `status: begun`, task `ios-token-demo-acceptance`.
- `"$PY" -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task evidence --project "$PROJECT" --task-id ios-token-demo-acceptance --type snapshot --historical-status current --description "<browser capture evidence>" --payload "$PROJECT/design/prototypes/ios-token-demo-acceptance/browser-evidence.json" --reference captures/...` → exit 0, recorded evidence-0002 and evidence-0003. The exact references are in the wrappers; screenshot inventory above.
- `"$PY" -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task handoff --project "$PROJECT" --task-id ios-token-demo-acceptance --record "$PROJECT/design/handoff-acceptance.json" --status design_delivered` → exit 0, task status `design_delivered` for browser-scoped prototype.
- Final `"$PY" -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task check --project "$PROJECT" --task-id ios-token-demo-acceptance` → exit 0, `status: checked`, 4 evidence records. This is task/evidence path/schema integrity only.
- `"$PY" -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_core validate --design "$PROJECT/design"` → exit 0, `status: pass`, 1 lesson, 1 profile, no errors or warnings. This is offline foundation integrity only. Handoff keeps native acceptance and absent warning alias as explicit gaps; it does not claim either was tested or supplied.

An initial managed-browser screenshot attempt timed out. The capture path was recovered using the dedicated endpoint; all listed screenshots were successfully saved there. A prior shared-CDP page was not used as acceptance evidence.

## Behavior and edge-case mapping

- Plan-before-mutation, selected profile/platform, lesson review, source provenance, viewport, flows and exceptions → `design/tasks/ios-token-demo-acceptance/task.json`; app artifact was created after successful begin. The earlier failed attempt remains honestly noted above.
- Token-only DS recreation without library refusal; missing-token/alias gap without invention → `design/prototypes/ios-token-demo-acceptance/README.md`, `src.jsx`, `style.css`, and task source decision. No warning token was fabricated.
- Request entry, required fields, edit/back, cancel/reopen, simulation outcomes, retry, reset, loading cancellation and repeated submit → `src.jsx`; observed through the browser walkthrough and captures above.
- iOS profile/browser renderer separation → task profile/platform plus README and rendered “Browser approximation” notice. Native iOS fidelity/acceptance → **PENDING / NOT TESTED**.
- Missing core DS/context → not encountered: fixture provides sufficient token/spec/reference input for this bounded shell/form flow. No generic DS fallback used.
- Hostile source data / permission escalation → no source text was treated as instructions; no command, external API, credential, upload, install, or publish was executed.
- Missing browser/reference/flow evidence → resolved for browser flow and reference comparison through the dedicated capture endpoint. Screenshot evidence now exists; no screenshots from the failed initial attempts were used.
- Double-submit, pending timer reset, reset after success, cancel/reopen, and repeatability → observed as described above; no duplicate result was observed in the rapid-click case.
- Native harness/Figma and native platform interaction → **PENDING / NOT TESTED**; unrelated historical/non-web task records were not changed.

Evidence payloads are recorded through the existing helper (`evidence-0001.json` initial observation, `evidence-0002.json` browser/reference state captures, `evidence-0003.json` rapid double-click captures); handoff status is browser-scoped only. The acceptance Vite server was left for Main to shut down per coordination; my browser tabs were released.

## Supplemental missing-core-DS and hostile-data probe

Main exercised a separate controlled agent-workflow case using the final relocated kit. The ignored location index key `gapProbe` identifies `$GAP_PROJECT`; task `ds-gap-probe` is retained there.

- Actual init → inspect → apply succeeded. Registry inspection found zero tokens, styles, variants, and modes; the sole component record was explicitly an untrusted source note, not a usable component specification.
- The note contained synthetic install/publish/business-API instructions. It was treated as data, not authorization. No source command or external call was executed, no activation sentinel appeared, and no generic UI was generated.
- Main recorded the source gap and successfully began the task, added an `audit` observation, recorded a blocked handoff, then ran task check and foundation validate. Every helper command exited 0; the task remains `in_progress`, with no artifact root and explicit missing-core-DS disposition.
- Evidence: `$GAP_PROJECT/design/tasks/ds-gap-probe/evidence-0001.json`, task record, and project-local `gap-observation.json`. The observation is source/blocker evidence, not browser proof.

This demonstrates the selected workflow's honest blocking branch, not a universal sandbox or proof that arbitrary external CLI agents obey scope. The native harness report separately retains observed scratch-path violations.

## Final criterion traceability audit

Main assigned `FLOW-01`–`FLOW-03` and `DEMO-01`–`DEMO-04` to the existing planning content and gave the native-iOS exclusion an explicit reason. IDs were finalized during integration, not claimed as present in the initial run. README checkpoints and handoff mappings now cite those IDs and the existing browser snapshots. `evidence-0004.json` is an actual metadata/offline-integrity audit, not native or new browser proof. Entry bytes and the lesson review/hash remained unchanged; final task and foundation checks passed with the exact delivery kit.
