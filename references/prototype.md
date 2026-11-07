# Explicit prototype workflow

Prototype work is separate from design and review. Do not add, remove, or change
prototype graph edges during design/review. Start this route only when the user
explicitly asks for a prototype or prototype changes. A prototype request does
not authorize publishing or sharing outside the selected design file.

## Resolve the graph before editing

Before any graph mutation, record a `design-task` with the requested brief,
platform, destination file/page, source/target frame IDs, direct links, reference
instances, all relevant entry points, and current existing reactions. Specify
required and excluded states, every edge, trigger, navigation method, transition,
back/cancel behavior, and validation scenarios. Resolve ambiguous behavior with
the user or mark it as an open question and block the affected edge. Review the
applicable lessons before beginning the mutation (see [design.md](design.md)).
The task CLI's `begin` command refuses an unresolved destination, planning record,
or incomplete/stale lesson review.

For Figma `NAVIGATE`, inspect parent/page identity before mutation: destinations
must be different top-level frames on the same page. A state nested under a
layout board is not a valid navigation destination. If the requested frames are
nested, record the limitation and resolve their placement before applying edges.
For authorized acceptance copies, promoting the existing frames to the page
while preserving absolute geometry and resolved modes avoids creating duplicate
prototype screens. Never silently reparent a product frame or redirect an edge
to a wrapper; record the placement decision in the task first.

A concrete transfer-flow graph should name its page and entry point, cover normal
and invalid paths, and separate design-tool simulation from application logic:

```json
{
  "entryPoints": [{"pageId": "PageID", "frameId": "Home", "name": "Transfer"}],
  "edges": [
    {"from":"Home", "to":"Form", "trigger":{"type":"ON_CLICK"}, "navigation":"NAVIGATE",
     "transition":{"type":"DISSOLVE", "duration":0.2, "easing":{"type":"EASE_IN_AND_OUT"}}},
    {"from":"Form", "to":"Invalid", "trigger":{"type":"ON_CLICK"}, "navigation":"NAVIGATE",
     "transition":{"type":"DISSOLVE", "duration":0.2, "easing":{"type":"EASE_IN_AND_OUT"}}},
    {"from":"Invalid", "to":"Form", "trigger":{"type":"ON_CLICK"}, "navigation":"NAVIGATE",
     "transition":null},
    {"from":"Form", "to":"Complete", "trigger":{"type":"ON_CLICK"}, "navigation":"NAVIGATE",
     "transition":null},
    {"from":"Form", "action":"BACK", "trigger":{"type":"ON_CLICK"}},
    {"from":"Form", "to":"Home", "trigger":{"type":"ON_CLICK"}, "navigation":"NAVIGATE",
     "transition":null}
  ]
}
```

Names are illustrative placeholders, not live node IDs. The Form-to-Invalid
click is an intentionally simulated invalid branch: a simple frame reaction
does not evaluate input or implement validation logic. In a real flow, clearly
label the control that enters the invalid state, the edit/retry route back to
Form, the valid Submit path to Complete, and Cancel back to Home. If true
conditional behavior is required, model and verify it with the appropriate
Plugin API variables/conditional actions; this helper deliberately does not
pretend to implement it. Record each validation scenario and its simulated
behavior separately from real application validation.

Before adding edges, inspect the existing page's entry points and reactions.
The Figma Plugin API exposes `PageNode.flowStartingPoints` and
`PageNode.prototypeStartNode` as read-only. The helper never chooses an
entrypoint implicitly or modifies it. `entryPoints` in the example is
preflight/handoff planning data only; it is not passed as a mutation request.
`applyPrototypeGraph` consumes the `edges` array and leaves page flow-starting-
point configuration untouched. With explicit user authorization, select the
top-level frame in the Figma UI, open the right-side **Prototype** tab, then
choose **+** in **Flow starting point**. Creating the first connection on a page
may also create an entry point automatically; inspect the page before and after
connecting. Read back
`page.flowStartingPoints` and `page.prototypeStartNode?.id` in the Plugin API
context and capture the entry point name/ID. Do not publish or copy a share
link outside the selected project. Figma's
[flow-management guide](https://help.figma.com/hc/en-us/articles/360039823894-Create-and-manage-prototype-flows)
documents manual creation, entrypoint inspection, and previewing.

Test scenarios should enumerate entry, every principal path, invalid input,
retry/edit, cancel/back, and disabled/inapplicable actions. For the example:

- Start preview from Home; activate Transfer and confirm Form appears.
- Activate invalid Submit; confirm the Invalid state appears (prototype branch
  simulation, not input validation).
- Activate Edit/Retry; confirm return to Form and retained/reset field values
  match the request.
- Activate Cancel and confirm Home; separately exercise the back-history action.
- Exercise valid Submit and confirm Complete; record actual behavior in the
  preview rather than inferring it from the edge list.

## Optional Figma Plugin API graph helper

`scripts/figma_prototype.js` exports `applyPrototypeGraph(figma, graph, authorized)`
for use inside an existing Figma plugin context. It requires the caller to pass
`authorized === true`; a script import or inspection alone does not change a
file. The function validates all edges and node IDs before writing, supports
`ON_CLICK`, `ON_HOVER`, `ON_PRESS`, `ON_DRAG`, and `AFTER_TIMEOUT` triggers,
`NODE` navigation actions (`NAVIGATE`, `OVERLAY`, `SWAP`, `SCROLL_TO`,
`CHANGE_TO`), plus explicit `BACK` and `CLOSE` actions. Each edge is appended to
existing reactions rather than replacing them. It writes via Plugin API
`setReactionsAsync`, reads reactions back, verifies the requested trigger (including
`AFTER_TIMEOUT.timeout` in milliseconds) and requested transition/navigation while
tolerating serialized duration rounding, and checks existing reactions remain
unchanged. It attempts to restore changed nodes if a write or readback fails.
It refuses unknown destinations, unsupported triggers/actions, duplicate edges in
the requested graph and semantically matching edges already persisted on a source.
Native serialization defaults such as `resetVideoPosition: false` do not permit a
duplicate to bypass that check; rejection happens before any graph write.

The supported enum values follow the
[Figma Plugin API Trigger](https://developers.figma.com/docs/plugins/api/Trigger/),
[Action](https://developers.figma.com/docs/plugins/api/Action/),
[Transition](https://developers.figma.com/docs/plugins/api/Transition/), and
[Reaction](https://developers.figma.com/docs/plugins/api/Reaction/) contracts.

The helper does not create or delete frames, infer interactions, simulate
behavior, or capture evidence. Use an existing authorized Plugin API project that
can include this module; this package does not provide a plugin manifest or claim
the module can be run as a standalone shell script. Plugin API write/readback is
not equivalent to a preview test. If a usable plugin context is unavailable,
record that as blocked evidence and do not claim graph changes.

## Verify and hand off

After a requested graph change, inspect persisted reactions on every affected
node and verify source and destination IDs, triggers, navigation, and transitions.
Then run the prototype in the design tool's preview and exercise every specified
path, including back/cancel and invalid/error paths. Record actual persisted
readback separately from actual simulated/preview behavior; label fixture-only
or simulated evidence explicitly. Fix only observed defects, then repeat the
applicable preview paths and readback. Capture direct entry-point and state
links, edge-to-requirement mapping, decisions, evidence, and remaining
questions in the task handoff. The CLI only stores supplied records; it never
creates graph edges, passes tests, approves work, or publishes anything.
