# Codex marketplace packaging and native review

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
this review channel is not a production release or official listing.
Linux acquisition is implemented; [native Linux acceptance](verification/linux-runtime.md) remains pending.

## Fresh installation

Version `0.5.0a2` is available for owner/tester review from the persistent
Git source below. This is an author-operated review/prerelease channel, not a
production release or official directory listing. Git and GitHub HTTPS access
are required. For isolated testing use a clean HOME, USERPROFILE and CODEX_HOME;
these commands otherwise affect the current native profile.

The Codex distribution commit for `0.5.0a2` is
`f49151a3b21501f52843385f5fce769009df39d2`. It is the immutable `--ref` value;
do not substitute the mutable review branch or another snapshot. The release
record is maintained in the owner's
[release description authored by `keitruong191`](https://github.com/keitruong191/KKdesign-kit/pull/22)
(section **0.5.0a2 distribution commits**, not comments). Stop if it does not
list this version and commit. Keep registration and install in one fail-fast
chain: if marketplace registration fails, do not run a separate plugin install;
the previously registered source may still point at a1.

```sh
codex plugin marketplace add https://github.com/keitruong191/KKdesign-kit.git --ref f49151a3b21501f52843385f5fce769009df39d2 &&
codex plugin add kkdesign-kit@kkdesign-kit-codex &&
codex plugin list --json
```

The plugin-add marketplace argument is the catalog name, not its repository
URL. For an existing installation, use the upgrade guidance below rather than
treating a same-source refresh as a version pin.

## Upgrade an existing installation

First inventory `codex plugin list --json` and `codex plugin marketplace list`.
Identify the installed plugin, its marketplace, and the registered source/ref
before changing anything. Do not remove an entry unless it is the intended
source and scope; retain other plugin declarations and marketplace sources.

A same-source refresh keeps the registered ref. It cannot move an immutable a1
pin to the a2 commit. After confirming this profile owns the intended plugin
and marketplace, remove the plugin first, then replace its source:

```sh
codex plugin remove kkdesign-kit@kkdesign-kit-codex &&
codex plugin marketplace remove kkdesign-kit-codex &&
codex plugin marketplace add https://github.com/keitruong191/KKdesign-kit.git --ref f49151a3b21501f52843385f5fce769009df39d2 &&
codex plugin add kkdesign-kit@kkdesign-kit-codex &&
codex plugin list --json
```

If there is no existing plugin/registration, use the fresh-install path above
instead. If add reports `already added from a different source`, stop: the old
source remains registered. Never run plugin add independently after that failure.
The final installed path must end in `kkdesign-kit/0.5.0a2`. Project data and
private runtimes are separate; do not delete them or provider caches manually.

The immutable review source is for the Codex CLI native lifecycle. Snapshot
documents cannot embed their own future commit; use the owner's release record
above if it ever changes.

## In the installed agent

Start a new session in the selected product project, then invoke:

```text
$kkdesign-kit:kkdesign-kit
$kkdesign-kit:kkdesign-kit Setup
$kkdesign-kit:kkdesign-kit init
```

For `init`, supply the selected product project and declared sources, inspect
the staged plan and authorize apply only after review. External design-tool
authorization is separate. These are invocation instructions, not a claim that
authenticated menu/Setup/workflow observation has passed.

Resolve bundled resources from the activation-provided skill directory, never
from product CWD or the author's checkout. Do not create a standalone skill
copy, run the legacy installer, or write runtime/state into the plugin cache.

### Same-source refresh and removal
Native lifecycle remains owned by Codex. These refresh commands keep using the
already-registered marketplace source; they do not pin/migrate its ref:

```text
codex plugin marketplace upgrade kkdesign-kit-codex
codex plugin add kkdesign-kit@kkdesign-kit-codex
codex plugin remove kkdesign-kit@kkdesign-kit-codex
codex plugin marketplace remove kkdesign-kit-codex
```

Project design data, lessons, task history and private user runtime/state have
separate ownership. No uninstall hook deletes them. Native same-source refresh
uses the registered marketplace's current snapshot and installs its current
plugin version; source migration to the immutable a2 commit is a separate flow
described above. The host controls plugin files and enable/disable settings.
After updates, open the new session and choose Setup to verify compatibility.
Unchanged requirements and runtime contracts reuse a verified cache; changes
require explicit consent to provision a separate cache. Remove/reinstall
preserves and reevaluates shared runtimes.
See [lifecycle evidence and acceptance limits](verification/native-lifecycle.md).
Setup now discovers standalone conflicts using the explicitly selected project
root. It preserves modified/unmanaged copies and requests separate consent
before archiving verified managed copies after helper validation; see
[standalone migration](../references/setup.md#standalone-conflicts-and-migration)
and [migration evidence](verification/standalone-migration.md).

## Build from canonical resources

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

Native evidence currently covers Codex CLI 0.167.0 on macOS ARM64 for
install/discovery/lifecycle and direct installed-cache Setup/helpers; see the
[measured matrix](compatibility.md). Authenticated agent interaction, Intel,
Linux/Windows and other surfaces remain pending. No IDE, desktop-app or cloud
coverage is inferred from CLI checks. Sessions without an authorized local
executor cannot run Setup/helpers. Public-directory local-execution eligibility
has separate publication constraints; repo CLI evidence does not establish it.
Provider installation never establishes design-tool access or human approval.

See [native verification](verification/codex-marketplace.md) for observed
results and pending acceptance. Official sources:
[packaging and catalog](https://developers.openai.com/plugins/build/plugins),
[Codex surfaces and new sessions](https://learn.chatgpt.com/docs/plugins),
[local-executor metadata and Desktop only publication](https://developers.openai.com/plugins/deploy/desktop-only).
