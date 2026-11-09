# Claude Code marketplace packaging preview

This adapter loads the canonical root `SKILL.md` as
`/kkdesign-kit:kkdesign-kit`. It does not copy or fork the workflow into a
provider-specific skill. `.claude-plugin/plugin.json` declares `skills: ["./"]`;
the source repository also supplies `.claude-plugin/marketplace.json`.
The canonical version and both descriptors must agree (`0.5.0a1`).

This is a packaging preview, not a public release or a working runtime Setup
release. Native install can make instructions available; it does not provision
Python, verify helpers, authenticate design tools, or grant approval. The menu
and **Setup** route need only the host's file-reading tools. They report
**Setup required**; helper-dependent workflows remain blocked. Automatic Setup
and trusted helper execution from plugin caches are separate work still needed
before release. The plugin launcher refuses helper execution in this preview.

## Native review flow

Use a clean isolated Claude Code profile and a trusted marketplace source at the
reviewed revision. These are maintainer review instructions; no hosted release
or official listing is claimed. Once a marketplace source has actually been
published and verified, native registration and installation use:

```text
claude plugin marketplace add <reviewed-marketplace-source>
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user
claude plugin list --json
```

Start a new Claude session in the selected product project and invoke:

```text
/kkdesign-kit:kkdesign-kit
/kkdesign-kit:kkdesign-kit Setup
```

The bare menu must show Setup, plugin loaded, runtime Setup required and external
tools unverified. The Setup route describes the current capability boundary;
it does not complete runtime setup. Do not run the standalone installer, create
another skill copy, or download dependencies from either route.

Use native lifecycle controls, including:

```text
claude plugin uninstall kkdesign-kit@kkdesign-kit-marketplace --scope user
```

Provider-owned plugin files are separate from project `design/`, lessons, task
history and any private user runtime cache. No uninstall hook is bundled.
Retained user runtime/state is outside the host's plugin ownership. This task
does not implement runtime compatibility on update or standalone migration.

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

Register the extracted directory with native Claude commands for a local
review. To test host cache relocation rather than local in-place loading,
maintainers can serve the extracted marketplace through a disposable Git smart
HTTP endpoint on loopback and register that URL. Claude Code 2.1.308 rejected
`file://` registration; a plain static HTTP server also failed because the host
requests a shallow clone. The smoke endpoint uses Git's actual `http-backend`,
not an emulated install response. The host performs its own clone/install; the
end user does not manually clone source or run a standalone installer.
Keep that test's home, `CLAUDE_CONFIG_DIR`, CWD and project data temporary;
never change a user's primary provider settings or copy their credentials.

Manifest validation, bundle verification and native CLI inventory each prove
different things. Only an actual Claude session showing the namespaced menu
can complete native discovery/menu acceptance; authentication or policy blocks
must remain explicit. Public publication and end-to-end Setup/workflow
acceptance are later gates.

Observed acceptance and the authentication blocker are recorded in
[native verification](verification/claude-marketplace.md).

Provider references: [manifest paths](https://code.claude.com/docs/en/plugins-reference),
[marketplace creation](https://code.claude.com/docs/en/plugin-marketplaces), and
[skill substitutions](https://code.claude.com/docs/en/skills).
