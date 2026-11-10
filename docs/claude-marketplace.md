# Claude Code marketplace packaging and native review

This adapter loads the canonical root `SKILL.md` as
`/kkdesign-kit:kkdesign-kit`. It does not copy or fork the workflow into a
provider-specific skill. `.claude-plugin/plugin.json` declares `skills: ["./"]`;
the source repository also supplies `.claude-plugin/marketplace.json`.
The canonical version and both descriptors must agree (`0.5.0a1`).

Native install makes instructions available; it does not provision Python,
verify helpers, authenticate design tools or grant approval. The menu needs
only file-reading tools. Explicit [Setup](../references/setup.md) checks/reuses
a trusted private runtime or, after consent, provisions and verifies real helpers. macOS/Linux Setup acquires pinned Python
internally without existing Python/Node; see [runtime evidence](verification/macos-runtime.md).
Windows PowerShell acquisition is implemented with [native acceptance pending](verification/windows-runtime.md).
Python-free helper startup uses the [verified OS entrypoints](../references/helpers.md); native end-to-end acceptance remains pending. No production release or official listing is claimed.
Linux acquisition is implemented; [native Linux acceptance](verification/linux-runtime.md) remains pending.

## Native maintainer review

Version `0.5.0a1` is available for owner/tester review from the persistent
Git source below. This is an author-operated review/prerelease channel, not a
production release or official directory listing. Git and GitHub HTTPS access
are required. For isolated testing use a clean HOME, USERPROFILE and
CLAUDE_CONFIG_DIR; these commands otherwise affect the current native profile.

```sh
claude plugin marketplace add 'https://github.com/keitruong191/KKdesign-kit.git#review/wwa11-claude-0.5.0a1'
git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD
```

On the measured POSIX surface, verify that the output is exactly
`bea7e433f4f576068bcf2eec15317d7d73e5e065`. **Stop if it differs** and ask the
owner to review that snapshot. The branch is mutable; this check is required
before installation. Only after it matches, install:

```sh
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin list --json
```

The `#ref` is part of Claude's Git source syntax; quote it. This branch is
mutable, not an immutable pin. [Source provenance](marketplace-sources.md)
records the exact distribution snapshot and measured native pin limitations.
Claude Code 2.1.308 rejects raw commit SHAs here: it tries to clone a branch
with that name. Before installing, verify the cloned marketplace as described
in the source record; expected HEAD is
`bea7e433f4f576068bcf2eec15317d7d73e5e065`. A different HEAD needs owner review;
no immutable client-side pin is claimed for this Claude command.

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

Use native lifecycle controls, including:

```text
claude plugin marketplace update kkdesign-kit-marketplace
claude plugin update kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin disable kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin enable kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin uninstall kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin marketplace remove kkdesign-kit-marketplace
```

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
