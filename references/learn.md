# Learn workflow

`kkdesign_learn.py` records direct feedback separately from inferred lessons. It
never calls Figma, a test harness, or an agent, and it does not verify a design.
Feedback and lessons must cite existing project-local evidence. Remote-only URLs
are not accepted for these authoring operations; preserve native evidence first
as a project-local record where policy permits.
Resolve `SKILL_DIR` to the absolute installed directory containing `SKILL.md`,
never the project working directory. Invoke helpers as
`python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_learn ...` (helper
name without `.py`). Installed helpers use the external runtime recorded by
installation; source/manual use needs Python 3.9+ and packages from
`requirements.txt` in the current environment. Quote absolute project paths.

## Capture direct feedback

```sh
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_learn feedback \
  --design "/path/to/project/design" \
  --content "The selected control is hard to distinguish." \
  --evidence ../evidence/review-notes.json \
  --scope web \
  --origin "design-review"
```

This appends one record to `design/feedback.json`, including scope, origin,
evidence, and a content-derived fingerprint. An exact repeat returns its
existing `FB-NNN` ID without writing again. Feedback is not itself a lesson,
proof of task execution, or an approval.

## Author an inferred lesson

Review the direct feedback and its evidence. Author a generalizable practice
only if supported; distinguish observation from inference in its prose and
retain its evidence and origin. Canonical authored advice lives only in
`design/LESSON.md`; `lessons-index.json` is derived and regenerated from it.

```sh
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_learn author \
  --title "Keep control states distinguishable" \
  --body "When documenting a control, explain how its relevant states differ. This is an inferred practice, not a claim that a live implementation was tested." \
  --verification "On a later task, inspect the specified states and record task-specific evidence before claiming verification." \
  --evidence ../evidence/review-notes.json \
  --scope web \
  --tag controls \
  --applies-when "When a task includes stateful controls." \
  --origin-task review-2026-01 \
  --feedback-id FB-001
```

The CLI allocates the next stable `DL-NNN`, labels the entry `kind=inferred`,
records `originTask` and optional `originFeedback`, and regenerates
`lessons-index.json` from canonical Markdown. All evidence references must
resolve inside the project. Inputs and the generated index are checked before
mutation; concurrent CLI writers are serialized and conflicting file changes
abort. A lock left by a terminated process must be removed only after verifying
that no learn process is still active.

An exact authoring replay returns the original ID without rewriting files,
including after other lessons were added or IDs were exhausted. Replaying a
superseded or retired lesson does not reactivate it; lifecycle changes remain
explicit.
LF and CRLF line endings compare as the same advice; a duplicate replay still
preserves the exact stored canonical bytes and their existing source hash.

Before the canonical source changes, the CLI writes the old source and a freshly
generated matching index to
`design/lesson-history/<old-source-sha256>/{LESSON.md,lessons-index.json}`.
These immutable snapshots allow historical tasks to keep their original
`lessonReview.sourceHash`. They do not prove that lessons were read, add a task
review result, or upgrade any verification claim. The CLI never edits task JSON.
Learning writes reject symlinks in destination paths and must stay inside the
selected design directory, including history hash directories. These checks
protect against pre-existing redirected paths; they are not a filesystem-race
guarantee against a concurrent process changing directory entries.

## Supersede explicitly

Author the replacement first, then explicitly mark the prior lesson:

```sh
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_learn supersede \
  --design "/path/to/project/design" --id DL-001 --by DL-002
```

Both IDs must exist. Supersession updates the old lesson's canonical metadata
and regenerates the index; it does not delete or rewrite historical lesson
records or task reviews. Repeating the same operation is idempotent. A different
replacement cannot silently overwrite an existing supersession. Retain old
lesson IDs so historical task decisions remain resolvable.

## Smoke recipe: trace a subsequent task

1. Capture a synthetic feedback record with an existing project-local evidence
   file and note its returned `FB-NNN`.
2. Author an inferred lesson linked to that ID, then confirm its stable `DL-NNN`
   entry appears in `LESSON.md` and its index is generated from that source.
3. Follow [design.md](design.md) to prepare a new task from the template. Read the
   current canonical lessons and record reasoned decisions before `begin`, with
   applied lesson verification still pending. Only the task's real execution may
   establish a verification result; creating a record never does.
4. After a completed review, record its source hash and evidence using the
   existing task process. Add another lesson and confirm the earlier task JSON
   is byte-for-byte unchanged and its original hash snapshot remains at
   `design/lesson-history/<hash>/`.
5. Run the foundation validator. It should accept the old task hash only when
   the snapshot is valid and should continue to check its historical lesson
   decisions against the lesson metadata captured at that hash. No review is
   re-stamped and no previous reading or pass is inferred.

All examples are generic and synthetic; they are instructions, not product
findings or evidence of live design-system, Figma, runtime, or harness behavior.
