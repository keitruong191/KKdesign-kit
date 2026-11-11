# Fixture Atlas — internal request capture

Synthetic product and interaction brief for an interactive prototype exercise. This is input to a future project-init/demo task, not a feature implementation or a claim about a real product.

## Product context

Fictional Atlas is an internal workspace used by fictional product and operations teammates. The scenario is an internal teammate recording an idea/request with a short title and description so it can be reviewed and receive a clear outcome. Use only local fixture state. No account, customer, network service, business API, or production integration exists in this scenario.

## Objective and user

- **Objective:** communicate how a teammate drafts, reviews, submits, and understands the outcome of an internal request.
- **User:** an internal teammate with a request to record; no role/permission system is in scope.
- **Content:** deterministic sample title `Reduce duplicate weekly reports` and description `Let workspace owners combine recurring reports into one weekly digest.` These are synthetic and are the initial form values only where a scenario explicitly says so.

## Entry, flow, and ending

- **Entry:** the Fixture Atlas Requests list in its initial empty state.
- **Main path:** choose **New request** → enter/edit title and description → choose **Review request** → inspect the exact draft values → choose **Submit request** → show one explicit simulated success result with a stable local reference `REQ-1042`.
- **End:** success result with request summary and controls **Create another request** and **Back to requests**.
- **Alternative path:** from review choose **Edit request** to return to the form with the same values; from the form choose **Cancel** to return to the list and discard the current draft. Reopen **New request** starts with empty fields.
- **Validation:** both title and description are required before review; show a clear inline message for each missing field. Do not invent character limits or server validation.
- **Back/cancel:** form-to-review back action is **Edit request** and preserves values. Form cancel discards that draft. Review-to-form preserves values. Navigation to the initial list from a completed result retains the completed list item for the current session.
- **Reset:** a dedicated fixture reset returns to the initial empty list and clears drafts, submitted items, feedback, and pending simulated work. It may clear only demo state; never use persistent product storage.

## Deterministic feedback scenarios

The prototype may expose explicit scenario choices labeled **Simulate success**, **Simulate recoverable error**, and **Simulate loading**. These are visibly simulation controls, not claims of real network behavior.

- **Success:** submission creates exactly one local item and shows its stable summary/reference. Repeated submit while pending or after completion must not create duplicates.
- **Recoverable error:** show a fixed explanatory message that the simulated submission did not complete; retain title and description; **Retry** returns to the same deterministic success path. Do not add a real request or random error.
- **Loading:** show an explicit simulated pending state with a fixed, documented delay of 800 ms before the selected outcome. Reset, cancel, or navigation out of the pending scenario cancels that pending transition. After reset, waiting longer than the delay cannot change the screen or repopulate state. No timing is inferred from source metadata/config.

The default submit path is deterministic success. Scenario controls may change the selected simulated outcome, but not the entered content. A reset restores default success selection and initial state.

## Labels and actionable scope

In-scope actions: **New request**, **Review request**, **Edit request**, **Cancel**, **Submit request**, **Retry**, **Create another request**, **Back to requests**, and **Reset demo**. All visible in-scope actions must work and follow the transitions above. Shell navigation outside Requests may be shown for context but must be visibly marked as illustrative/non-interactive; it must not create dead ends that look like supported workflows.

## DS and reference use

Use the local synthetic DS source `atlas-demo` and asset IDs declared in `ds/ds.json`: `button.primary`, `textfield.default`, and `card.default`, with `theme.light` and its declared tokens. The registered DS source contains token/spec/reference data only. A separate optional authored React fixture is available in `code-ds/`; it is not declared as importable DS code in the source registry. If an implementation uses only the token/spec source, record recreated components as recreated rather than native/reused. Do not invent token values or treat this brief as permission to substitute another design system.

- Web comparison viewport: **1280×800 CSS px**.
- iOS profile/browser-approximation viewport: **390×844 CSS px**. Keep the iOS profile/platform/lesson; a browser view is not native iOS evidence.
- Reference: `reference-shell.html` is a visual shell/form reference only. Compare typography, color, spacing, layout, and the listed component IDs. No pixel-diff threshold or native/pixel-parity claim is specified.

## Verification states to observe in a future interactive demo

| Area | Required state/action | Expected observation |
|---|---|---|
| Requests shell/list | Initial, after success, then reset | Initial is empty; success adds exactly one request; reset restores the empty entry. |
| Form | Empty; populated; Edit request from review; Cancel then reopen | Empty title is blocked with inline feedback; edit preserves both values; cancel discards; reopened form is empty. |
| Review | Initial review and review after editing | Displayed values match the current form values without overflow for the sample content. |
| Feedback | Simulated loading, error, retry, success | State and simulation label are explicit; retry follows deterministic success; no duplicate item. |
| Reset | Reset from success, error, and loading; wait after pending reset | Return to initial fixture state; pending work cannot mutate state later. |
| iOS approximation | Same scenario at 390×844 | Compare with compact synthetic reference; document browser/native limitations, do not claim native fidelity. |

Capture each future screenshot with task/scenario/state, viewport, and reference source. A screenshot does not replace interaction walkthrough; code inspection does not replace visual inspection. All observations and images belong in the selected disposable project, not this fixture package.
