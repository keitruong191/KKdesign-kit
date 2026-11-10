# Design workflow

The design command is an agent-orchestrated workflow. The helper records a plan and
real evidence; it does not connect to Figma, inspect a canvas, draw, mutate nodes,
run a visual check, or publish. Resolve the request with the user and use the
user-authorized design tool manually. The design task record is the pre-mutation
contract; do not begin canvas changes until it is complete and stored.

Resolve `SKILL_DIR` to the absolute installed directory containing `SKILL.md`,
never from the current directory. Invoke the helper as
`/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_task ...` (helper name
without `.py`). The launcher verifies the private runtime prepared by Setup. For native Windows
use the equivalent PowerShell form in [helper invocation](helpers.md). `PROJECT` is the user's selected
project kit. The generic synthetic example is `"$SKILL_DIR/examples/minimal"`;
never copy private data into this public package.

## 1. Resolve and record before mutation

1. Read the request and identify its brief/source, outcome, users, flows, target
   platform, delivery destination (file/page/frame or equivalent), reference
   instances/assets, target viewport/modes, required and explicitly inapplicable
   states, constraints, content, and acceptance criteria. Mark unknowns as open
   questions; do not invent product requirements.
2. Inspect existing destination frames and actual reference instances/assets in
   the live design tool. Record identifiers/links and observed properties,
   variants, bindings, and editability. A component definition alone does not
   establish its instance behavior. If the tool is unavailable, record the
   specific blocked inspection as a gap; do not claim the destination was read.
3. Resolve the installed project's design profile and active lessons. Review
   every active lesson applicable to the platform and record `apply` or
   `not-applicable` plus a reason. Keep verification pending until there is
   task evidence. Resolve current sourceHash from `design/lessons-index.json`.
4. Make design decisions before editing: reuse an instance where suitable;
   bind semantic variables/styles instead of hard-coded values when supported;
   prefer Auto Layout/native responsive constraints where suitable. Record a
   reason for each override, local exception, or scoped fallback, plus its
   exact affected surface and scope. Do not detach or replace components merely
   for convenience.
5. Build a complete task JSON from the task template/contract. It must have
   `kind: design-task`, `status: in_progress`, a unique `taskId`, objective,
   platform, `productProfileId`, resolved nonempty `target`, planned `designPlan`,
   and current reviewed `lessonReview` (nonempty entries). Preserve remaining
   task fields and contract schema. For example, from an initialized project's
   `design/` directory, copy `task-template.json` to a temporary file, fill it
   using the provided request and observations, and pass that file to:

   ```sh
   /bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_task begin \
     --project "$PROJECT" --record /path/to/complete-task.json
   ```

   `begin` rejects stale/incomplete lesson review, invalid profiles/platforms,
   unresolved destination/planning, invalid contracts, and existing task IDs. It
   creates only `design/tasks/<taskId>/task.json`; it never replaces task data.
   If it rejects the record, resolve the reported preflight item before invoking
   `begin` again. Starting a task is not authorization to mutate; the user's
   request/tool policy supplies that authorization.

## 2. Execute and verify the design

1. Follow the agreed scope. Reuse existing components/assets, retain semantic
   bindings, use appropriate Auto Layout/responsive behavior, and implement all
   required states. Keep decisions and exceptions scoped to the exact instance
   or surface. Design/review work MUST NOT create or alter prototype graph
   interactions; see [prototype.md](prototype.md) for the separately requested
   prototype route.
2. After each meaningful change, read back persisted destination properties,
   not merely the intended values: geometry/constraints, component and variant,
   semantic variable/style bindings, typography, modes, editability, and link.
   Capture a genuine screenshot/render or tool readback. Check actual visual
   output against the brief, viewport, reference, acceptance criteria, and every
   required state. Fix only defects confirmed in readback and repeat the check.
3. Preserve evidence as received. Make a JSON payload file describing actual
   observation records, captured images, or tool results; do not generate a
   pass-result payload from this helper. Example:

   ```sh
   /bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_task evidence \
     --project "$PROJECT" --task-id "$TASK_ID" --type snapshot \
     --description "Actual saved settings frame readback and viewport capture" \
     --payload /path/to/real-readback.json --historical-status current \
     --reference captures/settings.png
   ```

   Each evidence record is wrapped in the existing task-evidence contract and
   gets a hash of its payload. Payload should say how, where, and when it was
   captured and distinguish a fixture or simulation from live evidence. Local
   references must exist under the project; remote references must be
   credential-free HTTPS URLs. Evidence files append as `evidence-NNNN.json`
   beside `task.json`; unrelated records are never overwritten. The default
   `historicalStatus` is `historical`; select `current` only when the supplied
   payload genuinely records current task evidence. The helper does not determine
   recency, truth, pass/fail, or fresh/live status from JSON validity.

   Run the offline integrity check before handoff:

   ```sh
   /bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_task check \
     --project "$PROJECT" --task-id "$TASK_ID"
   ```

   It verifies task/evidence schemas, payload hashes, local references, and
   evidence citations. Its `checked` status is not a design or visual pass.

4. Record complete handoff JSON with direct frame/state links, created/modified
   node IDs, requirement-to-state mapping, decisions, evidence-linked checks,
   and remaining gaps/questions. Each `checks` item must cite an existing
   evidence filename in its `evidence` array. Example:

   ```sh
   /bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_task handoff \
     --project "$PROJECT" --task-id "$TASK_ID" \
     --record /path/to/evidence-linked-handoff.json --status design_delivered
   ```
   A handoff record has the standard task `handoff` fields plus
   `requirementStateMapping`, for example:

   ```json
   {
     "frameLinks": ["https://www.figma.com/file/example?node-id=10%3A20"],
     "createdNodeIds": ["10:20"],
     "modifiedNodeIds": [],
     "requirementStateMapping": [
       {"requirement": "brief-1", "state": "empty", "evidence": ["evidence-0001.json"]}
     ],
     "checks": [
       {"check": "Persisted empty-state geometry and semantic bindings",
        "evidence": ["evidence-0001.json"]}
     ],
     "remainingGaps": []
   }
   ```

   These sample IDs and URLs are placeholders, not evidence. For unavailable
   tools, keep status `in_progress` and add a specific `blockedDisposition` to
   the handoff; do not manufacture links, checks, or a delivered status.

   `design_delivered` requires at least one recorded evidence record; no check
   result is generated. Keep status `in_progress` while the handoff is partial.
   A handoff with remaining gaps can still be delivered only when those gaps are
   stated explicitly; do not present them as verified behavior. Do not publish
   or externally share project content.

The task evidence wrapper validates offline shape and payload hash only. The
project's core validator checks file references and contract integrity; neither
one proves live design-tool behavior, visual quality, owner approval, or a test
pass. Report unavailable tools as scoped blocked evidence, clearly naming the
uninspected destination, unverified requirements/states, and resulting questions.
