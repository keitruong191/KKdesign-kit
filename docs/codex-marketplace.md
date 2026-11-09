# Codex marketplace packaging preview

The Codex adapter packages the canonical skill/resources under
`skills/kkdesign-kit/`, without a second workflow source. The generated
`.codex-plugin/plugin.json` uses the supported compatibility
format, declares `./skills/` and `requires_local_executor: true`.
The descriptor version must match `manifest.json`. The generated Codex catalog is
`.agents/plugins/marketplace.json`; it is distinct from Claude's catalog.

The menu uses file-reading tools only and does not provision anything. Explicit
[Setup](../references/setup.md) checks/reuses a trusted private runtime or asks
for consent before provisioning and verifying real helpers. macOS/Linux Setup can
acquire pinned Python internally without Python/Node on PATH; see
[runtime evidence](verification/macos-runtime.md).
Plugin loaded, runtime readiness and external tools unverified remain separate.
Windows PowerShell acquisition is implemented with [native acceptance pending](verification/windows-runtime.md).
Python-free helper startup uses the [verified OS entrypoints](../references/helpers.md); native end-to-end acceptance remains pending;
this is not a public release or official listing.
Linux acquisition is implemented; [native Linux acceptance](verification/linux-runtime.md) remains pending.

## Native maintainer review

Use a clean isolated HOME and CODEX_HOME with a reviewed marketplace source.
No published marketplace endpoint or public-directory approval is claimed.
Register the source using native controls (the marketplace argument to plugin
add is its name, not its repository URL):

```text
codex plugin marketplace add <reviewed-marketplace-source>
codex plugin add kkdesign-kit@kkdesign-kit-codex
codex plugin list
```

Start a new session in the selected product project, then invoke:

```text
$kkdesign-kit:kkdesign-kit
$kkdesign-kit:kkdesign-kit Setup
```

Resolve bundled resources from the activation-provided skill directory, never
from product CWD or the author's checkout. Do not create a standalone skill
copy, run the legacy installer, or write runtime/state into the plugin cache.
Native lifecycle remains owned by Codex:

```text
codex plugin marketplace upgrade kkdesign-kit-codex
codex plugin add kkdesign-kit@kkdesign-kit-codex
codex plugin remove kkdesign-kit@kkdesign-kit-codex
codex plugin marketplace remove kkdesign-kit-codex
```

Project design data, lessons, task history and private user runtime/state have
separate ownership. No uninstall hook deletes them. Native update refreshes the
marketplace snapshot and installs its current plugin version; the host controls
its files and enable/disable settings. After updates, open the new session and
choose Setup to verify compatibility. Unchanged requirements and runtime
contracts reuse a verified cache; changes require explicit consent to provision
a separate cache. Remove/reinstall preserves and reevaluates shared runtimes.
See [lifecycle evidence and acceptance limits](verification/native-lifecycle.md).
Setup now discovers standalone conflicts using the explicitly selected project
root. It preserves modified/unmanaged copies and requests separate consent
before archiving verified managed copies after helper validation; see
[standalone migration](../references/setup.md#standalone-conflicts-and-migration)
and [migration evidence](verification/standalone-migration.md).

## Canonical build

Maintainers need Python 3.9+ to build, independently of the end-user menu:

```sh
python3 -B scripts/build_codex_marketplace.py --output ../kkdesign-codex-marketplace.zip
python3 -m zipfile -e ../kkdesign-codex-marketplace.zip ../codex-review
```

Descriptor/catalog build inputs live under `packaging/codex/`; the source
checkout is not itself the Codex marketplace. Register the built artifact.
The deterministic ZIP contains `kkdesign-codex-marketplace/` with the native
catalog and `plugins/kkdesign-kit/` containing the canonical allowlisted payload
under `skills/kkdesign-kit/`, plus the Codex descriptor at plugin root.
The skill inventory covers canonical resources; the archive SHA-256 covers
the entire artifact including provider metadata. Output cannot
replace existing files or live inside source. This is a marketplace artifact,
not a standalone installer. No runtime, hooks, MCP server or binaries are added.
Register the extracted marketplace for local review; a Git marketplace at a
reviewed ref can instead distribute it through the host's clone/cache flow.

## Surface boundaries

Native review targets Codex CLI on macOS ARM64 only. This does not advertise
working Setup/runtime support on that combination. Linux, Windows, other CPUs,
and the ChatGPT desktop app have no native evidence for this adapter yet.
The Codex IDE extension does not support plugins. Cloud/web/mobile sessions
without a local executor cannot run helper workflows; no fallback installer is
provided. Public-directory local-execution plugins have Desktop only limits;
local CLI marketplace evidence does not establish public-directory coverage.
Unsupported surfaces should use a supported local host when a verified release
is available. Provider installation never establishes design-tool access or
human approval.

See [native verification](verification/codex-marketplace.md) for observed
results and pending acceptance. Official sources:
[packaging and catalog](https://developers.openai.com/plugins/build/plugins),
[Codex surfaces and new sessions](https://learn.chatgpt.com/docs/plugins),
[local-executor metadata and Desktop only publication](https://developers.openai.com/plugins/deploy/desktop-only).
