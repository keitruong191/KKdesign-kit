# Project contracts

The project owns `DESIGN.md` and `design/`; the skill orchestrates their use.
DS snapshots can retain provider-specific schemas. Foundation records use the
four schemas in this repository.

## Canonical lessons

Each lesson in `design/LESSON.md` has an explicit anchor, a heading and exactly one JSON metadata comment:

```md
<a id="DL-001"></a>
### DL-001 · Inspect the designated reference

<!-- kkdesign-lesson {"id":"DL-001","status":"active","platforms":["any"],"tags":["reference"],"appliesWhen":"When reusing an incumbent component.","evidence":["../PRODUCT.md"],"originTask":null} -->

Read the relevant instance as well as its main component.

**Verification:** Record properties and rendered evidence for the target.
```

Keep IDs stable. `platforms` is `any`, `web`, `macos`, `ios`, `android` or `windows`. `status` is `active`, `superseded` or `retired`. The prose is authoritative; the index contains metadata, anchors and hashes, not a second editable copy of advice.

After editing:

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_core lessons-index --design path/to/project/design
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_core validate --design path/to/project/design
```

## Task lifecycle

Copy `task-template.json`; change kind to `design-task`, supply `taskId`, objective, platform and a known `productProfileId`. New tasks start with `lessonReview.status=pending`.

For each selected lesson record `decision` (`apply` or `not-applicable`), a reason, verification status and evidence paths relative to the task folder. `pass` requires evidence; an artifact link alone does not establish that the underlying behavior was tested. Recheck the claims against the artifact when executing a real task.

Use `retrospective` only when mapping pre-existing evidence after the task; it cannot declare new `pass` results or prove the agent read lessons before execution. `not-applicable` requires a reason. Pin the lesson source hash when completing the review. Template files remain pending and empty.

When `learn` changes canonical lessons it first preserves the old Markdown and
generated index in `design/lesson-history/<sourceHash>/`. Historical tasks retain
their original source hash, decisions and verification claims byte-for-byte.
Validation accepts an old hash only with an intact matching source snapshot and
exact regenerated index, and evaluates applicability against that historical
metadata. This proves the pinned source's integrity, not prior reading or a new
test pass. Missing or corrupt snapshots still fail stale-source validation.

`learn` stores direct feedback separately in `design/feedback.json`. Authored
lessons may carry `kind` (`direct-feedback` or `inferred`) and `originFeedback`;
their prose remains canonical in `LESSON.md`. See [learn](../references/learn.md)
for stable IDs, deduplication, evidence and explicit supersession.

## Evidence wrappers

Task evidence has `$schema`, `schemaVersion`, `kind=task-evidence`, and `record`. Keep the original payload at its original keys. `record.payloadSha256` hashes the payload excluding those four wrapper fields, serialized as UTF-8 JSON with `sort_keys=True`, `ensure_ascii=False`, `separators=(',', ':')`. Metadata identifies task, evidence type, historical status, description and references. A wrapper migration must compare the original and migrated payloads.

Reference paths are relative to the record's documented base, stay inside the project, and must exist. Remote evidence is HTTPS and is recorded without network verification.

## Prototype delivery

Prototype work is explicit and separate from design/review. The existing Figma
delivery is `figma_design`; web tasks select `html_prototype` or
`react_prototype` explicitly. If the requested output is unresolved, ask rather
than choosing a target or creating multiple outputs. The product `platform` and
profile remain the product's, even when a web browser is used to present a demo.
`productProfileId` is the selected profile document's declared `id`, not its filename.
Web prototypes reuse the existing `design-task` lifecycle and evidence wrappers;
they do not define a second schema family or change historical records or the
shared pending template. Web task records declare an explicit web `delivery` and
the exact project-relative `target.destination` `design/prototypes/<taskId>`.
The source decisions record important design system mappings and provenance
(`surface`, real project `sourceId`, `assetIds`, `revisionOrHash`,
`implementation` as `reuse-code` or `recreated`, optional `codeReference`, and
notes). Missing provenance is recorded as a scoped exception, not fabricated
identity or proof of conformance.

Web handoffs retain the common fields `frameLinks`, `createdNodeIds`,
`modifiedNodeIds`, `checks`, `remainingGaps`, and `requirementStateMapping`.
Canvas-only arrays may be empty for web; do not invent links or node IDs. A
delivered web handoff additionally requires nonempty `handoff.artifacts`:
project-relative `entry` and `instructions` files under the target artifact
root, plus launch metadata (`file` or `command`; React uses `command`). Command
launch metadata includes a nonempty string `argv` and project-relative `cwd`.
Artifact paths and `cwd` are project-root-relative; evidence references retain
their task-directory base. Artifact files must exist, remain within the project,
and not traverse symlinks. Path metadata is never permission to execute it.

Project refresh treats `design/prototypes` as user-owned runtime output, not as
managed design contracts or a dependency tree to scan/copy. Asset impact review
uses the task's recorded source decisions. Candidate validation still checks
artifact metadata against the actual project and materializes only declared
artifact/evidence references; missing or unsafe artifacts continue to block it.

Offline check/foundation validation establishes schema and artifact integrity
only. It does not establish that a browser ran, interactions work, a design
system conforms, or a human approved the result. Delivered web tasks need
evidence-cited checks and requirement/state mappings; `blockedDisposition` does
not replace those requirements. Incomplete or unverified work remains
`in_progress`. Figma keeps its existing graph workflow and non-web delivery gate.
