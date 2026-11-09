# WWA-02 native verification

**Code implementation and tests: ready for coordinator review and integration.**
**Authenticated native menu/Setup acceptance: pending.** The owner explicitly
separated acceptance requiring unavailable resources from code readiness and
will arrange authenticated installation and feedback later. This clarification
supersedes the original evidence gate for code integration: missing native
authentication does not block review, the open PR or integration. It does not
establish an unobserved pass, publication, runtime readiness or approval.

Environment: macOS ARM64, Codex CLI `0.167.0`, Python 3.9 development venv with
`requirements.txt`. Native commands used a fresh temporary HOME, USERPROFILE
and CODEX_HOME, an unrelated product CWD containing spaces, no copied provider
credentials and no inherited OpenAI API/token configuration. Primary provider
settings were not changed. All preservation sentinels were synthetic.

| Acceptance criterion | Actual evidence | Result |
| --- | --- | --- |
| Clean native add/install at correct version without standalone installer | Built marketplace ZIP served through actual Git smart HTTP (`git http-backend`) on loopback; `marketplace add --ref <snapshot-sha> --json` and `plugin add --json` exit 0. Inventory reports enabled `kkdesign-kit@kkdesign-kit-codex`, version `0.5.0a1`, in native cache. | Met for native packaging review; no public endpoint claimed. |
| New session recognizes skill; menu and Setup readable without Python | New real Codex app-server `skills/list` reports enabled `kkdesign-kit:kkdesign-kit`, the plugin ID and cache SKILL path. Actual namespaced menu and Setup `codex exec` attempts both exit 1 with HTTP 401, missing bearer/basic authentication. | Discovery met; rendered menu/Setup **pending**, not a pass. Reading-only instructions are implemented but not authenticated acceptance. |
| Cache resources resolve without checkout or standalone copy | Stop loopback server and delete temporary Git source before new-session discovery. Native cache remains discoverable. Extracted canonical skill verifier exits 0 from unrelated CWD; no author checkout used for native activation. Native remove deletes cache; no standalone skill path created. | Met for package/resource relocation; helper workflow execution remains blocked pending runtime integration. |
| Accurate surface and local-execution limits | Descriptor declares `requires_local_executor: true`. Guidance limits observed evidence to macOS ARM64 CLI, excludes IDE plugins and does not infer desktop-app, cloud, public-directory or other OS coverage. | Metadata/guidance implemented; no untested host coverage claimed. |
| Real native install/discovery/menu/remove evidence | Native registration/install, app-server discovery and removal observed. Remove and marketplace remove exit 0; installed inventory empty; synthetic design/lesson/task-history/private-runtime sentinels unchanged. | Lifecycle met; authenticated menu is the remaining native acceptance gap. |

## Exact checks and reproduction sequence

Paths, port and snapshot SHA below are placeholders for disposable review
locations, not install endpoints. Build the final reviewed source with:

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -B scripts/build_codex_marketplace.py --output <outside-source>/marketplace.zip
```

Full suite: **130 tests passed**. Regression coverage checks deterministic
canonical payload bytes, relocated verification, tamper rejection, refusal to
execute a plugin helper or mutate cache/output before runtime integration,
version-drift rejection and preservation of existing artifacts.

Extract `kkdesign-codex-marketplace/`, initialize a disposable Git snapshot of
that directory and serve it with Git's real `http-backend` on loopback. This
is transport for native testing; the end user does not manually clone a source
checkout. With isolated environment and unrelated product CWD:

```text
codex plugin marketplace add <loopback-git-url> --ref <snapshot-sha> --json
codex plugin add kkdesign-kit@kkdesign-kit-codex --json
codex plugin list --json
```

Stop the source server and delete its temporary repository. In a new real
`codex app-server` process, send JSON-RPC `initialize`, `initialized`, then:

```json
{"id":2,"method":"skills/list","params":{"cwds":["<temporary-product>"],"forceReload":true}}
```

Observed skill name is `kkdesign-kit:kkdesign-kit`, enabled, with plugin ID
`kkdesign-kit@kkdesign-kit-codex` and a path below
`<CODEX_HOME>/plugins/cache/kkdesign-kit-codex/kkdesign-kit/0.5.0a1/skills/kkdesign-kit/`.
A root `skills: "./"` layout installed but did not discover the skill; the
final builder emits `skills/kkdesign-kit/` from the single canonical source.

Actual authenticated-route attempts (both failed before model/menu rendering):

```text
codex exec --skip-git-repo-check --ephemeral --json -s read-only '$kkdesign-kit:kkdesign-kit'
codex exec --skip-git-repo-check --ephemeral --json -s read-only '$kkdesign-kit:kkdesign-kit Setup'
```

Verify canonical resources directly from the installed cache with the
development interpreter (a package-integrity check, not runtime Setup):

```text
python -I -B <cached-skill>/scripts/kkdesign_install.py verify --source <cached-skill>
codex plugin remove kkdesign-kit@kkdesign-kit-codex --json
codex plugin list --json
codex plugin marketplace remove kkdesign-kit-codex --json
```

Removal preserves synthetic files under the selected project's design,
lessons and task-history directories, and a private user runtime directory.
No hooks, MCP, provider permission changes or security-policy bypass are used.

Integration assessment: **code-ready**, subject to coordinator review into
`feature/marketplace-installation-setup`; **native acceptance pending** and
not release-ready. Missing authenticated acceptance does not block code
integration under the owner clarification. An authenticated clean Codex profile must still
open the full bare menu and Setup route, verify no Python/download is used just
to display them, and confirm the displayed readiness states. No credentials
should be copied into this repository to supply that evidence. Runtime Setup,
OS provisioning, trusted workflow execution, migration and update acceptance
remain the separate backlog items; this task does not claim those outcomes.
