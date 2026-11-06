# Command menu — B2 preview

| Command | Availability | Purpose |
|---|---|---|
| init | Implemented B2 | Scan declared sources and stage a project-kit initialization plan. |
| refresh | Implemented B2 | Compare source revisions, review changes and authorize a recoverable update. |
| design | Planned B3, unavailable | Execute a scoped design task. |
| review | Planned B3, unavailable | Review UX, visual quality and DS usage. |
| prototype | Planned B3, unavailable | Create or edit an explicit prototype. |
| learn | Planned B3, unavailable | Author lessons with evidence and regenerate the index. |
| package | Implemented B1 | Build a hash-verified portable ZIP from the bundled files. |

Bare invocation shows this menu. For an unavailable command report its status and
stop that command; do not substitute foundation utilities or simulate results.
Installation, inspection, update, rollback and uninstall are provided by
`scripts/kkdesign_install.py`, documented in `docs/installation.md`.

For `init` and `refresh`, follow [project-kit.md](project-kit.md). Plans do not
authorize themselves; inspect changes and conflicts before explicit apply.
