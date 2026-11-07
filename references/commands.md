# Command menu

| Command | Availability | Purpose |
|---|---|---|
| init | Available | Scan declared sources and stage a project-kit initialization plan. |
| refresh | Available | Compare source revisions, review changes and authorize a recoverable update. |
| design | Available; live tool required for canvas mutation | Execute a scoped task; read back structure and inspect renders. |
| review | Available | Bundled UX/visual/DS findings; no edits unless requested. |
| prototype | Available; explicit request and live tool required | Create or edit requested interactions; verify graph and navigation. |
| learn | Available | Capture feedback/lessons with evidence and regenerate the index. |
| package | Available | Build a versioned portable ZIP; validate extracted resources and checksums. |

Bare invocation shows this menu. Missing tools/access block only the dependent
operation. Never simulate design edits, screenshots, navigation or native approval.
Installation, inspection, update, rollback and uninstall are provided by
`scripts/kkdesign_install.py`, documented in `docs/installation.md`.

For `init` and `refresh`, follow [project-kit.md](project-kit.md). Plans do not
authorize themselves; inspect changes and conflicts before explicit apply.

For `design`, follow [design.md](design.md); for `review`, [review.md](review.md);
for an explicit `prototype` request, [prototype.md](prototype.md); for `learn`,
[learn.md](learn.md); and for `package`, [packaging.md](packaging.md).
Design/review must not add interactions. Packaging never authorizes publication.
