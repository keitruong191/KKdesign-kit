# Compatibility and observed evidence

B1 (`0.2.0a1`) ships one canonical `SKILL.md`, technical identifier `kkdesign-kit`
and Codex display name **KKdesign-kit**. Claude Code uses that same frontmatter
and native skill/slash-command handling. See [installation](installation.md).

The discovery paths were checked against the official
[Codex skills documentation](https://learn.chatgpt.com/docs/build-skills) and
[Claude Code skills documentation](https://code.claude.com/docs/en/skills).
Compatibility below is limited to the versions actually run, not all later or
earlier releases. Desktop sync, cloud sessions and managed enterprise policies
are unverified.

| Layer / environment | User scope | Project scope |
|---|---|---|
| Codex CLI 0.167.0, macOS 26.5 arm64 | Discovery, menu, actual bundled read: PASS | Discovery, menu, actual bundled read: PASS |
| Claude Code 2.1.308, macOS 26.5 arm64 | Discovery, menu, actual bundled read: PASS | Discovery, menu, actual bundled read: PASS |
| Installer, Python 3.9.6, macOS | Lifecycle / conflicts / integrity: PASS | Lifecycle / conflicts / integrity: PASS |
| Linux / Windows installer, Python 3.9 and 3.12 | CI matrix configured; remote result not observed here | Same |
| Linux / Windows live harness | Unverified | Unverified |
| Other harness versions / Figma / design tools | Unverified, outside B1 | Unverified, outside B1 |

[Reviewed smoke evidence](evidence/b1-harness-smoke.json) records harness versions,
normalized tool calls, final menu responses and SHA-256 of the private raw
transcripts. Paths use `<ISOLATED_ROOT>`; no account metadata, credentials,
session identifiers or customer data are published. This is a reviewed summary,
not a substitute for rerunning the probes in your target environment.

Each probe installed an extracted portable package in a fresh home and synthetic
project with spaces in its path, removed the source extraction, and launched the
actual CLI. Only authentication was reused. No user settings, Hoangsa,
Impeccable, optional hooks or MCP servers were installed. Harness-bundled system
skills/plugins remain present. Codex read SKILL.md and commands.md through its
shell; Claude's native skill activation supplied SKILL.md, and its Read tool
opened commands.md. All four responses rendered the full menu and correctly
reported `init` unavailable. Claude initially failed with revoked OAuth; after
reauthentication both scopes passed. Failed attempts are not counted as passes.

## Reproduce offline checks

From the source checkout:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/materialize_example.py --output .demo
.venv/bin/python scripts/kkdesign_core.py validate --design .demo/design
.venv/bin/python scripts/kkdesign_install.py package --output ../kkdesign-kit-0.2.0a1.zip
```

On Windows use `.venv\Scripts\python.exe`. The 38 tests include all existing
Stage-A regressions plus all four harness/scope combinations, idempotent installs,
updates, rollback, preserved project/configuration data, unmanaged/modified file
conflicts, backup protection, swap failures, deterministic packages, integrity,
relocation and paths with spaces. Symlink tests run when OS privileges permit.
No offline result claims successful model or Figma behavior.

## Reproduce live CLI probes

The source checkout's `scripts/smoke_harness.py` is an opt-in acceptance runner;
it is not automatically run by the installer, package or CI. It uses your
existing executable and its default model, so ordinary account access is needed.
It copies only the explicitly supplied authentication file into a temporary
private home, removes it at exit and never prints credential contents. It does
not change the real user's configuration. macOS Claude keychain auth may need
exporting to a temporary private credentials file; never commit that file.

```sh
python scripts/smoke_harness.py --harness codex --scope project --codex-auth-file "/private/auth/auth.json" --output "/private/results/codex-project"
python scripts/smoke_harness.py --harness codex --scope user --codex-auth-file "/private/auth/auth.json" --output "/private/results/codex-user"
python scripts/smoke_harness.py --harness claude-code --scope project --claude-credentials-file "/private/auth/claude-credentials.json" --output "/private/results/claude-project"
python scripts/smoke_harness.py --harness claude-code --scope user --claude-credentials-file "/private/auth/claude-credentials.json" --output "/private/results/claude-user"
```

Choose new output directories outside the checkout. Credentials remain external
to the artifact; use short-lived private files and remove any supplied exports
after testing. The runner captures raw local logs: review/redact them before
sharing. Exit zero still requires transcript review: confirm discovery from the
installed path, a real successful resource read, the seven-command menu and
honest unavailable-command status. Model self-report alone is insufficient.

Hooks remain opt-in future integration; installation does not add or enable
hooks at either scope. DS scanning and design-tool execution are not part of
these tests and are still unavailable B2/B3 commands.
