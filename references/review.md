# Review UX and visual design
> Selectively adapted and modified by KKdesign-kit from Impeccable 4.8.0. See [attribution and license](../docs/review-attribution.md).

Review provides evidence-backed recommendations. It is a read-only assessment: a request to review does not authorize changing source files, canvas objects, assets, or prototypes. Make edits or prototypes only after a separate, explicit request and scope. No Impeccable launcher, detector, browser overlay, Hoangsa service, or network access is needed. Attribution, source/version, adaptations, and the complete upstream license are recorded in [review attribution](../docs/review-attribution.md).

## Establish scope and authority

1. Identify the specific surface, user goal, principal task, platform(s), viewport/device, themes/modes, and flows/states requested. Mark unknowns instead of inventing them. Choose mode per surface (Operate, Read, Persuade, Experience), not per product.
2. Read applicable product context, design-system sources, and only the scoped canonical lessons/task evidence. Treat product refs as product behavior/voice constraints; treat declared DS sources as visual/component authority; treat scoped lessons as prior evidence and constraints, not universal law. A conflict or stale reference is a finding to resolve, not permission to silently choose one.
3. Inspect the actual target and evidence. For Figma, identify the exact file/page/frame/component and capture the relevant canvas view and selection. For shipped UI, identify the running build, route, environment and viewport. Source code, a design canvas, screenshots, and a live runtime are different evidence types; never infer one from another.
4. State what was not accessible, exercised, or in scope. Do not claim native rendering, behavior, accessibility, performance, implementation parity, or approval without direct evidence for it.

## Review dimensions

Assess the user journey and visual communication together:

- **Purpose and specificity:** Can the target's intended audience and task be recognized? Are decisions grounded in this product rather than category convention alone? Respect the brief; do not replace intentional identity with reviewer taste.
- **Hierarchy and composition:** Is the primary action/content obvious? Do grouping, alignment, scale, whitespace, density, and emphasis express priority? Is the information architecture comprehensible at first use and on return?
- **Cognitive load:** Count decision points and visible competing choices. Check whether the user must remember information across steps, interpret ambiguous labels, or infer relationships. Reduce unnecessary choice and recall without hiding essential options.
- **Typography and consistency:** Verify legibility, hierarchy, text styles, token bindings, spacing/color/radius conventions, component anatomy, and behavior across instances and variants. A copied value that looks right is not proof that a design-system binding remains intact.
- **Copy and comprehension:** Check labels, instructions, empty/loading/success/error copy, tone, factual claims, and recovery guidance. Prefer specific, actionable language over jargon or generic error states.
- **Accessibility and inclusion:** Inspect contrast, type size/zoom, focus and keyboard path where applicable, target size, non-color cues, labels/semantics, motion, reading order, localization expansion, and assistive-technology behavior. A canvas-only check cannot prove runtime semantics.
- **States and recovery:** Cover initial, populated, loading, empty, validation, success, partial failure, destructive confirmation, offline/permission-denied, and retry/undo paths relevant to the task. Explain what happened, preserve user work, and offer a safe next step.
- **Content and resilience:** Inspect long text, translated strings, large numbers, missing/slow assets, narrow/wide layouts, scrolling, clipping, truncation, wrapping, and dynamic content. Verify scroll containment and reachability of actions.
- **Emotional journey:** Identify high-stakes moments, uncertainty, friction, reassurance and the last interaction. Ensure confidence is earned, not promised.

Use [review lenses](review/lenses.md) for evidence questions, [platform review](review/platforms.md) for independent platform-specific checks, and the [report template](review/report-template.md) for output structure.

## Evidence and findings

Each finding MUST include:

- `location`: exact page/frame/component/layer, screen/route/state, or source location; include a stable identifier when available.
- `severity`: P0–P3, defined by user harm and reach, not aesthetic preference.
- `userImpact`: the concrete task or user group affected and the consequence.
- `evidence`: what was actually observed, including artifact kind, version/build, viewport/platform, state, and a screenshot/record pointer where available. Separate direct observation from inference.
- `recommendation`: specific change to consider, without applying it during review.
- `verification`: a repeatable check and expected result, plus the evidence source that would establish it.
- `verificationStatus`: `evidence-only`, `not-verified`, `blocked`, or `verified`
  for the exact exercised criterion; identify which evidence establishes that status.

Prioritize findings by severity, frequency, task criticality and confidence. Report strengths and limits alongside defects. Avoid duplicate findings: combine causes when one systemic issue appears in several screens and enumerate affected locations. A disagreement between the product brief, DS, lesson, source and observed result should name both authorities and their revisions.

### Severity

- **P0 — blocker / serious harm:** prevents a critical task, exposes sensitive information, or creates a credible serious accessibility/safety risk.
- **P1 — major:** blocks or materially derails a common or important task, with no reasonable workaround.
- **P2 — moderate:** causes significant friction, confusion, or inconsistency, but a workable path remains.
- **P3 — minor:** polish, low-frequency friction, or a small inconsistency with limited user consequence.

Do not promote aesthetic disagreement to a higher severity without a demonstrated user consequence.

## Scoring

If a numeric heuristic score is useful, score only criteria that are applicable **and actually assessed**. Use 0–4 with a short evidence note per criterion; report `n/a` for inapplicable and `not assessed` for missing evidence. Report total as points / (4 × count of applicable assessed criteria); never include n/a or unassessed criteria in the denominator. Do not let a score imply overall approval or compensate for a P0/P1. If numeric scoring adds no value, omit it.

## Evidence boundaries and stop conditions

- **Figma/canvas:** canvas evidence can support statements about visible frames, layer structure, component/variant/instance configuration and explicit token bindings when inspected. A static export may show appearance, but not necessarily its source, bindings, interactions, or runtime behavior. A source-code detector or HTML scan does not establish anything about Figma unless that exact connection was observed.
- **Source:** code inspection establishes implementation intent/state in that source revision, not that the target is deployed or rendered as designed.
- **Runtime:** only an exercised build/environment establishes observed runtime behavior for the tested path and conditions. A screenshot alone does not establish performance, all device behavior, or accessibility-tree semantics.
- **Native:** review macOS, iOS, and Android independently when each is in scope. Do not treat iOS/Android patterns as macOS authority (or vice versa), and do not claim a native/runtime pass from web markup, mockups, or a schema validation.
- **Fixture:** fixture findings demonstrate the review format and expected ability to notice seeded defects. They are synthetic and never evidence about a real product or actual Figma file.

When evidence is insufficient, keep the finding provisional, record the gap, and specify what capture, inspection, or exercise would resolve it. No approval/pass language without evidence covering the named target, platforms, states and criteria.

## Bundled synthetic example

[Flawed design fixture](../examples/review/flawed-design.json) contains deliberately seeded defects and evidence limits. Its [expected findings](../examples/review/expected-findings.json) show how to report the defects without falsely asserting live/native approval. It is an offline training fixture, not a Figma export or test of any real interface.
For deterministic readback of structured, observed records:

```sh
python "<SKILL_DIR>/scripts/kkdesign_review.py" "<PATH_TO_REVIEW_RECORD.json>"
```

The input is a `design-review-record` JSON object with `schemaVersion`,
`scope`, and `records` fields; supported record categories are `references`,
`instances`, `textStyles`, `contentBounds`, and `contrast`. The helper compares
only explicit fields in those records; see the bundled fixture for examples.
Output is always `assessment: evidence-only` and `approval: not-assessed`.
Missing platform metadata is reported as unassessed, not as a mismatch; empty
findings mean no supported recorded mismatch, not a pass. It does not inspect
canvases, source files, rendered pixels, native apps, or user behavior. Its
output is not a substitute for the human review above. The fixture's seeded
evidence is synthetic and does not establish a Figma/native/runtime pass.
Regression tests are in `tests/test_review.py`.