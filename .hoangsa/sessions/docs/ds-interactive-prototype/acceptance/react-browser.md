# proto-13 React browser acceptance

**Result: PASS for exercised E2E-02 behavior; integrity check PASS.** The demo ran from the selected isolated React project, not the package checkout. Project location is resolved by `acceptance-locations.json` (`react`); below, `$PROJECT` means that selected location and paths are project-relative. The artifact and evidence remain there for review.

## Setup and runtime

- Initialized the separate Fictional Atlas web project using the extracted kit launcher: `kkdesign_project init` produced plan `1d28c9167b704d149d78163e1a78e3e7`; inspected/applied that plan before task planning.
- Before app files, began `react-demo` with the explicit `product-web` profile. The task destination is `design/prototypes/react-demo`.
- Explicitly copied the optional authored `examples/prototype/code-ds` fixture into `$PROJECT/ds/code-ds`. This is synthetic project code, not an upstream library. The app imports the actual `Button`, `TextField`, and `Card` exports and the authored theme stylesheet.
- Provenance in `design/tasks/react-demo/task.json`: source `atlas-demo`; assets `button.primary`, `textfield.default`, `card.default`, `theme.light`; revision/hash fields use SHA-256 of the actual copied authored source; `codeReference` points to the matching source file/export. Hashes: components `fd3b7fcff3857458a18ac5e869528a441d024055b87fe83c270a4bc505c88c56`; theme `b309f0988be131f4ec57e5ae4da3810225f40d5007b640998a9731ca8455b731`.
- The standalone fixture uses Vite with cache at `design/prototypes/react-demo/.vite-cache`, a read-only symlink to the already-present React/Vite dependencies, and no dependency install/download. Launched with `npm run dev -- --strictPort` from `design/prototypes/react-demo`; Vite reported ready at loopback `http://127.0.0.1:8124/` (Vite 5.4.21). The server was stopped after acceptance and the browser tab closed.
- Browser: dedicated HeadlessChrome 157.0.0.0; viewport 1280×800 CSS px. URL and viewport were checked before app captures. No production API/backend/auth/storage was used.

## Behavior contract

1. Initial Requests entry → observed empty list; capture `captures/01-entry.png`.
2. Empty submit/review → observed separate required-field messages for title and description; capture `captures/02-empty-form.png`.
3. Populate title/description → observed both values on form; capture `captures/03-form-filled.png`.
4. Review and edit/back → review showed exact entered values and edit preserved both; capture `captures/04-review.png`.
5. Cancel/reopen → cancel discarded the draft and opening New request again yielded empty fields.
6. Recoverable error → simulated pending then fixed error; values remained available; captured `captures/05-loading.png` and `captures/06-error.png`.
7. Retry/success → retry produced the deterministic local success `REQ-1042`; success explicitly says no request was sent; capture `captures/07-success.png`.
8. Return to list → one item with `REQ-1042` appeared; capture `captures/08-list-success.png`.
9. Double-click submit → loading then one success result; returning to list showed exactly one item; capture `captures/09-double-submit-result.png`.
10. Reset from completed success → observed the populated success result, then reset returned to the empty list; captures `captures/15-success-reset-source.png` and `captures/16-reset-success-entry.png`.
11. Reset from error → observed error then reset returned to the empty entry; capture `captures/10-error-reset-source.png` documents the source error state; outcome verified in the browser walkthrough.
12. Reset while loading → reset returned immediately to initial empty entry; after waiting 1000ms (beyond the fixed 800ms simulation delay), screen remained empty and no item reappeared. Captures: `captures/11-loading-reset-before.png`, `captures/12-reset-immediate.png`, `captures/13-reset-after-delay.png`.
13. Storage/reload → `localStorage` and `sessionStorage` remained empty. Reload reopened the empty initial state; capture `captures/14-reload-entry.png`.
14. Network boundary → observed localhost app/Vite/DS module requests only; no business API calls.

## DS/reference observation

Actual rendered DOM included the authored DS classes for Button, TextField, and Card—not merely imports. At 1280×800 computed values included canvas `rgb(245, 247, 250)`, brand button `rgb(36, 87, 166)`, Arial/sans-serif, field minimum height `44px`, border `rgb(215, 222, 232)`, and card radius `12px`. These match the synthetic source theme/spec.

The reference was rendered and captured separately at the same viewport as `captures/00-reference-shell.png`, then visually compared with the app captures. The palette, typography, and component treatment align. The reference has a top announcement/header and two-card form composition that the scoped list/review flow shell does not reproduce; this is recorded as a layout difference, not pixel parity. Raw captures remain in the selected project; ignored local review copies are under `.kkdesign-kit/planning/ds-interactive-prototype/evidence/proto-13/browser-captures/`.

## Evidence and handoff

- README: `$PROJECT/design/prototypes/react-demo/README.md` documents runtime, exact launch command/cwd, viewport, demo script, reset/retry, simulations, and limitations.
- Task status is `design_delivered`; helper handoff contains a real `react_prototype` artifact (`src/main.jsx`), README, command/cwd, requirement-state mapping, evidence-linked checks, and the disclosed reference-layout gap. No frame links or node IDs were invented.
- Evidence records: `evidence-0001.json` (initial browser record), `evidence-0002.json` (full flow/captures), `evidence-0003.json` (success reset), and `evidence-0004.json` (integration metadata/integrity audit). Final `kkdesign_task check --project "$PROJECT" --task-id react-demo` exited 0: `checked`, 4 records. The check is offline integrity, not human approval.
- Main's current-state audit also ran foundation validation with the final relocated kit: `pass`, no errors or warnings. It first caught an active lesson citation using `feature-brief.md` as though it were project-relative; that citation was corrected to task-relative `../../../feature-brief.md`. The pinned lesson hash, `pending` verification claim, and immutable evidence wrappers were not restamped.

## Edge cases

- Repeated submit/double-click → one request item; verified in browser.
- Reset while the 800ms timer is pending, then wait past the delay → remains empty; verified and captured.
- Reset from success and error → empty entry; verified and captured.
- Cancel and reopen → draft discarded; verified in browser.
- Unrelated browser storage → untouched/empty before and after; verified.
- Reload/reopen → returns to empty session fixture; verified.
- No external integrations or dependency installation → observed launch/runtime and network; none used.

## Scope note

The interaction/browser portion of E2E-02 passed. The visual comparison records a known structural difference from the static reference; no pixel-parity or native-fidelity claim is made. A previous screenshot attempt on a shared browser target timed out; it was discarded. The final captures above were made using the dedicated browser endpoint and inspected.

## Controlled runtime-limit probe

Main deliberately occupied loopback port 9261 with a separate fixture server, then ran the actual app command `npm --prefix "$PROJECT/design/prototypes/react-demo" run dev -- --port 9261`. Vite retained `--strictPort`, exited 1, and reported `Port 9261 is already in use`; it did not silently select a fallback port. The fixture server was stopped immediately afterward. This is an observed launch-resource failure, not a browser-flow failure or permission to change renderer/install dependencies.

## Final criterion traceability audit

Main assigned `FLOW-01`–`FLOW-05` and `DEMO-01`–`DEMO-08` to the existing planned scenario content. These identifiers were finalized during integration; no new behavior or pre-mutation ID history is claimed. README checkpoints and handoff mapping now use the same IDs and cite genuine browser records. `evidence-0004.json` records actual metadata and offline checks only. Entry bytes and the lesson review/hash remained unchanged; final task and foundation checks passed with the exact delivery kit.