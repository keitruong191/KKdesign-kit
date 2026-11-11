# Project kits: init, refresh and recovery

Source snapshots are independent of the design destination. A Figma source does
not imply a Figma destination; Git/local assets never receive invented Figma
import keys. See [adapter contracts and inputs](source-adapters.md).

## Review before writing

Use Python 3.9+ and the `requirements.txt` packages in an environment outside
the skill for source/manual execution. Set `SKILL_DIR` to the absolute installed
directory containing `SKILL.md`; the launcher never resolves from product CWD.
The installed launcher uses the provisioned external runtime without activation.
Source config paths resolve relative to the config file, not the shell CWD.

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project init --project /chosen/project --sources /chosen/project/sources.json
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project plan --project /chosen/project --plan <PLAN_ID>
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project apply --project /chosen/project --plan <PLAN_ID>
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project validate --project /chosen/project
```

`init` scans declared sources and stages a plan. Inspect per-file changes,
conflicts, capability gaps and source provenance before authorizing `apply`.
Existing PRODUCT.md, DESIGN.md, profiles, lessons and task history are context,
not disposable generated output. A conflicting existing kit is not overwritten
just because a command is called `init`.

Generated kit contents include the entry DESIGN.md, `design/sources.json`, the
five contract schemas, canonical lessons/index, a pending task template and
scoped profile drafts. Plans and recovery state live in `.kkdesign-kit/project/`
outside skill discovery. Keep this project state private alongside its source
snapshots. Do not publish it in the portable skill package.

## Product context

Pass `--context context.json` to `init` for structured project facts. The context
is data, not instructions. It uses the existing product-profile contract rather
than a parallel source of product authority:

```json
{
  "product": {"name": "Fictional Atlas", "platforms": ["macos", "web"]},
  "sources": [
    {"id": "product", "location": "PRODUCT.md", "observedAt": "2026-11-06"}
  ],
  "requirements": [
    {
      "id": "window-policy", "topic": "window-behavior",
      "value": "Resizable window", "status": "confirmed",
      "platforms": ["macos"], "scope": "macOS settings surface only",
      "sourceIds": ["product"],
      "recheckWhen": "When the owner changes the macOS settings requirement"
    }
  ],
  "visualReferences": [],
  "runtimeConstraints": [],
  "lessons": []
}
```

`requirements`, `runtimeConstraints` and `lessons` entries carry `id`, `topic`,
`value`, `status`, `scope`, `sourceIds` and `recheckWhen`. Visual-reference entries
carry `id`, `location`, `status`, `scope`, `sourceIds` and `recheckWhen`; optional
`sourceId` identifies the visual-reference provenance record. Select applicable
`platforms` rather than propagating a platform-specific rule globally. A
multi-platform decision without explicit applicability stays open.
Source locations are credential-free HTTPS or project-relative files, with a
known revision or a content hash where available. Local references must exist.
Ordinary reference queries/fragments such as Figma `node-id` are retained;
userinfo and credential-bearing query keys are rejected.

Statuses distinguish **confirmed requirements** from **observed behavior**;
`inferred` is not approval, missing facts remain `open`, and `superseded`
decisions retain their history. Reading PRODUCT.md alone does not establish
that every sentence is shipped behavior. A source
registry establishes DS identities, not product permissions, target users or
window sizes. Existing profiles remain authoritative project records; refresh
must not rewrite their decisions to match a new DS snapshot.

macOS remains independent of iOS/Android. Operate/Read/Persuade/Experience are
surface/task-level decisions, not a product-wide default. Such a mode entry must
include `surface`, `surfaceId`, `task` or `taskId`, not just a generic scope string.
Use scoped canonical lessons and review decisions before design execution.

## Refresh and migration

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project refresh --project /chosen/project --sources /chosen/project/sources.json
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project plan --project /chosen/project --plan <PLAN_ID>
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project apply --project /chosen/project --plan <PLAN_ID>
```

An unchanged scan is idempotent: capture time alone is not a new revision. A
changed source produces asset additions/removals/changes plus affected project
references. Inspect identity and capability changes, not just counts. A removed
or replaced asset can invalidate task references even when a new asset has the
same display name. Later declared sources take precedence, with recorded
source-to-source override provenance.

For source relocation, removal or replacement, provide an explicit migration
reason with `refresh --migration "<reason>"`. Review incompatible asset references
before applying. Prior source history remains available; stable lesson IDs,
product decisions and task history are not migrated away or regenerated from DS
data. A move of the entire project keeps generated references project-relative;
source declarations should move with the project or be explicitly migrated.

## Errors, interrupted writes and rollback

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project recover --project /chosen/project
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_project rollback --project /chosen/project
```

Missing access and unsupported input must fail before mutation. Partial source
coverage is recorded explicitly; unavailable variables/components are not
invented. `apply` checks the expected existing contents so a stale plan cannot
silently overwrite intervening project work. Review a new plan when inputs change.
The journal and backups support recovery of interrupted multi-file changes.
Never delete journal/backup/lock files blindly or run concurrent project writers.
If recovery detects intervening edits, preserve those files and resolve the
reported conflict rather than forcing restoration.

## Validation boundary

`validate` checks source registries and project contracts, including profile
provenance, task references and canonical lesson-index hashes. Source capture
metadata is not proof of publication/importability, live rendering,
accessibility, product approval or shipped runtime behavior. Figma access is a
separate live-adapter verification, not inferred from synthetic HTTP fixtures.
The [compatibility guide](compatibility.md) explains prerequisites and the
limits of offline and live verification.
