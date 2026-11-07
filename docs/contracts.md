# Stage-A contracts

The project owns `DESIGN.md` and `design/`; the skill will orchestrate their use in Stage B. DS snapshots can retain their provider-specific schemas. Foundation records use the four schemas in this repository.

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
python scripts/kkdesign_core.py lessons-index --design path/to/project/design
python scripts/kkdesign_core.py validate --design path/to/project/design
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
