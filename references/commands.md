# Command menu

| Command | Availability | Purpose |
|---|---|---|
| Setup | Instructions and capability assessment available; automatic runtime setup unavailable in plugin preview | Explain plugin, runtime and external-tool states; see [setup.md](setup.md). |
| init | Available | Scan declared sources and stage a project-kit initialization plan. |
| refresh | Available | Compare source revisions, review changes and authorize a recoverable update. |
| design | Available; live tool required for canvas mutation | Execute a scoped task; read back structure and inspect renders. |
| review | Available | Bundled UX/visual/DS findings; no edits unless requested. |
| prototype | Available; explicit request and live tool required | Create or edit requested interactions; verify graph and navigation. |
| learn | Available | Capture feedback/lessons with evidence and regenerate the index. |
| package | Available | Build a versioned portable ZIP; validate extracted resources and checksums. |

Bare invocation shows this menu using file-reading tools, without Python or
provisioning. In plugin mode, report **Setup required**, and mark all
helper-dependent operations as blocked: this preview has no plugin runtime
provisioner or managed plugin launcher yet. Instructions remain readable.
Do not infer readiness from a standalone install or Python on PATH.
Missing tools/access block only the dependent
operation. Never simulate design edits, screenshots, navigation or native approval.
Plugin installation and removal belong to the host's native plugin controls;
see [Claude marketplace](../docs/claude-marketplace.md). The old
`scripts/kkdesign_install.py` lifecycle is for legacy standalone installations,
not plugin Setup or lifecycle.

For `init` and `refresh`, follow [project-kit.md](project-kit.md). Plans do not
authorize themselves; inspect changes and conflicts before explicit apply.

For `design`, follow [design.md](design.md); for `review`, [review.md](review.md);
for an explicit `prototype` request, [prototype.md](prototype.md); for `learn`,
[learn.md](learn.md); and for `package`, [packaging.md](packaging.md).
Design/review must not add interactions. Packaging never authorizes publication.
