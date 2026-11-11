# Command menu

| Command | Availability | Purpose |
|---|---|---|
| Setup | Implemented with authorized local execution; no existing Python required; native matrix acceptance tracked separately | Check, request consent when needed, prepare and verify runtime; see [setup.md](setup.md). |
| init | Available | Scan declared sources and stage a project-kit initialization plan. |
| refresh | Available | Compare source revisions, review changes and authorize a recoverable update. |
| design | Available; live tool required for canvas mutation | Execute a scoped task; read back structure and inspect renders. |
| review | Available | Bundled UX/visual/DS findings; no edits unless requested. |
| prototype | Available; explicit request. Figma needs its authenticated tool; HTML uses local file/browser; React needs a suitable React runtime and DS. Browser verification needs browser capability. | Create or edit the explicitly selected prototype target and verify only with the required capability. |
| learn | Available | Capture feedback/lessons with evidence and regenerate the index. |
| package | Available | Build a versioned portable ZIP; validate extracted resources and checksums. |

Bare invocation shows this menu using file-reading tools, without Python or
provisioning. Show plugin loaded, runtime not checked/Setup required and external
tools unverified separately. Explicit Setup verifies/reuses a trusted runtime or
asks for permission before provisioning. Helper-dependent commands require a
verified runtime and use the stable launcher; missing or untrusted runtime
reports Setup/inspection required. Do not infer readiness from Python on PATH.
Missing tools/access block only the dependent
operation. Never simulate design edits, screenshots, navigation or native approval.
Plugin installation and removal belong to the host's native plugin controls;
see [Claude marketplace](../docs/claude-marketplace.md). The old
`scripts/kkdesign_install.py` lifecycle is for legacy standalone installations,
not plugin Setup or lifecycle.

For `init` and `refresh`, follow [project-kit.md](project-kit.md). Plans do not
authorize themselves; inspect changes and conflicts before explicit apply.

For `design`, follow [design.md](design.md); for `review`, [review.md](review.md).
For `prototype`, first resolve the requested output from the brief. If it is
unclear and context does not resolve it, ask whether the user wants Figma, HTML,
or React; do not choose a default or create multiple targets. There is no
`--target` flag. Follow [prototype.md](prototype.md) for shared planning,
design-system decisions and evidence, then only the selected execution route:
the existing authenticated Figma graph/preview workflow in that guide, or
[prototype-web.md](prototype-web.md) for HTML/React. HTML needs no Node runtime
or CDN. React requires an environment suitable for the chosen React runtime and
design system; reuse an applicable project package manager/lockfile when
available, and add dependencies only with project/host permission. Browser
verification requires browser capability. Missing capability blocks only its
dependent route or verification; it does not silently switch targets. Prototype
invocation does not authorize publication. Design and review remain separate
and do not add interactions unless the user explicitly switches to prototype.
For `learn`, follow [learn.md](learn.md); for `package`, [packaging.md](packaging.md).
Design/review must not add interactions. Packaging never authorizes publication.
