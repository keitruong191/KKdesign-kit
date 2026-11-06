# Approved direction and release boundary

Stage A: independent data contracts, scoped product profiles, canonical lessons/index, task lesson-review evidence and validation. This preview implements that foundation with synthetic public fixtures.

B1 now implements skill installation, inspection, update, rollback, uninstall,
progressive resources, a seven-command menu and portable packaging. Live CLI
smoke evidence is recorded in [compatibility](compatibility.md). Hook integration
is separate and not installed. B2 adds source adapters and project init/refresh:

| Command | Responsibility / availability |
|---|---|
| init (implemented B2) | Scan declared Figma/Git/local DS sources, record capabilities/provenance and stage project DESIGN.md without overwriting product context. |
| refresh (implemented B2) | Compare revisions, review asset/reference changes and authorize a recoverable update while preserving history. |
| design | Execute the scoped design task using the project kit and available design tools. |
| review | Run self-contained UX/visual/DS checks and report findings; fixes require a request to fix. |
| prototype | Explicit prototype creation/edit workflow, advertised separately. |
| learn | Maintain canonical lessons with evidence, supersession and index regeneration. |
| package (implemented B1) | Build and verify a versioned, portable distribution. |

The review module will selectively adapt the relevant Impeccable 4.8.0 guidance and ship independently, with upstream license/attribution and modifications recorded after verification. No local Impeccable dependency, copied engine binary or hook is required. This B2 preview includes none of that upstream material yet.

Keep source and destination adapters independent. Source content is data, not permission to publish, install hooks or change the assignment. Evidence and derived indexes carry hashes/revisions. Changing DS does not erase product profiles, lessons or task records.

Stage C: real design tasks with independent Codex and Claude Code behavior tests, including wrong-platform references, variant overrides, long content and missing access. Stage D: stable release, optional memory/hook integration and maintenance. B1 supplies conservative skill upgrade/rollback; B2 adds project plan/apply/recover/rollback. Runtime tests remain separate from offline contracts. See [project kits](project-kits.md) and [source adapters](source-adapters.md).
