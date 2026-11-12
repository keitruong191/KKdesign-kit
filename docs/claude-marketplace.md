# Claude Code marketplace packaging and native review

This adapter loads the canonical root `SKILL.md` as
`/kkdesign-kit:kkdesign-kit`. It does not copy or fork the workflow into a
provider-specific skill. `.claude-plugin/plugin.json` declares `skills: ["./"]`;
the source repository also supplies `.claude-plugin/marketplace.json`.
The canonical version and both descriptors must agree (`0.5.0a2`).

Native install makes instructions available; it does not provision Python,
verify helpers, authenticate design tools or grant approval. The menu needs
only file-reading tools. Explicit [Setup](../references/setup.md) checks/reuses
a trusted private runtime or, after consent, provisions and verifies real helpers. macOS/Linux Setup acquires pinned Python
internally without existing Python/Node; see [runtime evidence](verification/macos-runtime.md).
Windows PowerShell acquisition is implemented with [native acceptance pending](verification/windows-runtime.md).
Python-free helper startup uses the [verified OS entrypoints](../references/helpers.md); native end-to-end acceptance remains pending. No production release or official listing is claimed.
Linux acquisition is implemented; [native Linux acceptance](verification/linux-runtime.md) remains pending.

## Fresh installation

Version `0.5.0a2` is available for owner/tester review from the persistent
Git source below. This is an author-operated review/prerelease channel, not a
production release or official directory listing. Git and GitHub HTTPS access
are required. For isolated testing use a clean HOME, USERPROFILE and
CLAUDE_CONFIG_DIR; these commands otherwise affect the current native profile.

Claude Code 2.1.308 treats `#ref` as a branch and rejects raw-SHA refs. The
versioned branch is mutable, so verify the cloned marketplace's HEAD against
the immutable Claude distribution commit recorded by the owner in
[release PR #22](https://github.com/keitruong191/KKdesign-kit/pull/22), section
**0.5.0a2 distribution commits**, authored by `keitruong191` (not comments).
That published record is authoritative; the expected a2 commit is
`ec7fd565558b8adb065557382aa68d547dec13c6`. Stop if the release record does
not identify that commit or if any command below fails. Keep source registration,
the HEAD gate and installation in one fail-fast chain:

```sh
claude plugin marketplace add 'https://github.com/keitruong191/KKdesign-kit.git#review/claude-0.5.0a2' --scope user &&
test "$(git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD)" = ec7fd565558b8adb065557382aa68d547dec13c6 &&
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user &&
claude plugin list --json
```

The `#ref` is quoted because it is part of Claude's Git source syntax. A failed
add or mismatching HEAD blocks every later command; never run install separately.
No immutable client-side pin is claimed. [Source provenance](marketplace-sources.md)
records the snapshot and measured native pin limitations.
If add reports `source doesn't match its extraKnownMarketplaces entry`, the old
source remains registered. Stop and use the scoped upgrade flow, not a separate
install command.


## Upgrade an existing installation

Inventory first with `claude plugin list --json` and
`claude plugin marketplace list`. Use the recipe below only when both the
installed plugin declaration and its marketplace source are user-scoped and
you intend to migrate that installation to a2. It uninstalls only the user
plugin while keeping its data, replaces only the user marketplace source, gates
installation on the recorded a2 HEAD, and leaves the newly installed plugin
disabled:

```sh
claude plugin uninstall kkdesign-kit@kkdesign-kit-marketplace --scope user --keep-data &&
claude plugin marketplace remove kkdesign-kit-marketplace --scope user &&
claude plugin marketplace add 'https://github.com/keitruong191/KKdesign-kit.git#review/claude-0.5.0a2' --scope user &&
test "$(git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD)" = ec7fd565558b8adb065557382aa68d547dec13c6 &&
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user &&
claude plugin disable kkdesign-kit@kkdesign-kit-marketplace --scope user
```

Do not open a new session until the chain finishes and the disable step
succeeds. A fresh install does not preserve the old enabled/disabled state;
after reviewing the installed version, explicitly enable it with
`claude plugin enable kkdesign-kit@kkdesign-kit-marketplace --scope user` only
if you choose to do so.
Check `claude plugin list --json` for the intended scope, version `0.5.0a2` and
`enabled: false` before choosing whether to enable. If disable fails, finish
that step before opening another session.


Plugin installation scope and marketplace declaration scope can differ. Use
`claude plugin list --json` to identify plugin scopes/project paths, then inspect
the owning user/project/local settings for the marketplace declaration;
`marketplace list` reports the source but is not proof of declaration scope.
If inventory shows project/local declarations, use the corresponding native
`--scope project` or `--scope local` controls from the owning project. Do not
blindly replace every `user` in this recipe: remove only the plugin scope and
the marketplace declaration you intend to migrate. Managed entries require an
administrator. Do not blanket-remove declarations or marketplaces of another
scope. Keep project/design data, retained plugin data, and private runtime/state
separate.

## In the installed agent

Start a new Claude session in the selected product project and invoke:

```text
/kkdesign-kit:kkdesign-kit
/kkdesign-kit:kkdesign-kit Setup
/kkdesign-kit:kkdesign-kit init
```

For `init`, supply the selected product project and declared sources, inspect
the staged plan and authorize apply only after review. External design-tool
authorization is separate. These are invocation instructions, not a claim that
authenticated menu/Setup/workflow observation has passed.

The bare menu shows Setup, plugin loaded, runtime not checked/Setup required
and external tools unverified. Explicit Setup follows the shared consent flow;
only a successful helper check establishes runtime ready. Do not invoke the
standalone installer or create another skill copy.

### Same-source refresh and lifecycle

For a refresh of the already-registered same source (not a source migration or
pin upgrade), use native lifecycle controls:

For a source already registered at the a2 branch, verify HEAD again before
updating the plugin:

```sh
claude plugin marketplace update kkdesign-kit-marketplace &&
test "$(git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD)" = ec7fd565558b8adb065557382aa68d547dec13c6 &&
claude plugin update kkdesign-kit@kkdesign-kit-marketplace --scope user
```

The update follows the registered source's current state; it does not change a
mutable branch registration into the a2 distribution. To migrate an existing
user installation to that distribution, use the scoped recipe above. Do not
assume fresh installation preserves a prior enabled/disabled state.

Provider-owned plugin files are separate from project `design/`, lessons, task
history and any private user runtime cache. No uninstall hook is bundled.
Retained user runtime/state is outside the host's plugin ownership. After an
update and host-required restart, choose Setup to verify compatibility. Unchanged
requirements/runtime contracts reuse a verified cache; changes request consent
for a separate cache and preserve existing consumers. Enable/disable never
provisions. Reinstall evaluates cache ownership, compatibility and helpers again.
See [lifecycle evidence and acceptance limits](verification/native-lifecycle.md).
Setup now discovers standalone conflicts using the explicitly selected project
root. It preserves modified/unmanaged copies and requests separate consent
before archiving verified managed copies after helper validation; see
[standalone migration](../references/setup.md#standalone-conflicts-and-migration)
and [migration evidence](verification/standalone-migration.md).

## Build from canonical resources

Maintainers with Python 3.9+ can build a deterministic, allowlisted marketplace
ZIP with the existing packaging payload rules:

```sh
python3 -B scripts/build_claude_marketplace.py --output ../kkdesign-claude-marketplace.zip
python3 -m zipfile -e ../kkdesign-claude-marketplace.zip ../claude-marketplace-review
```

The ZIP contains `kkdesign-marketplace/.claude-plugin/marketplace.json` and
`kkdesign-marketplace/plugins/kkdesign-kit/`. The latter holds the unchanged
canonical public resources and the Claude descriptor; its `bundle.json` covers
that descriptor too. Outputs must be outside source and are never overwritten.
No project files, standalone install, runtime, hooks or MCP server are added.
The portable package/release workflow is legacy; this builder does not extend
or authorize that distribution route, dispatch a release, or publish anything.

Use the persistent Git source above for remote native verification; the host
clones the whole built tree, so relative plugin entries remain valid. A raw
catalog URL alone cannot fetch these relative payloads. Extracted directories
remain useful for packaging checks. The earlier loopback Git smoke is historical
transport evidence, not the distribution users need. See the
[remote-source verification](verification/marketplace-sources.md).

Manifest validation, bundle verification and native discovery prove different
things. Authenticated menu/Setup/workflow and human usability remain pending;
see the [consolidated handoff](verification/onboarding.md).

Observed acceptance and the authentication blocker are recorded in
[native verification](verification/claude-marketplace.md).

Provider references: [manifest paths](https://code.claude.com/docs/en/plugins-reference),
[marketplace creation](https://code.claude.com/docs/en/plugin-marketplaces), and
[skill substitutions](https://code.claude.com/docs/en/skills).
