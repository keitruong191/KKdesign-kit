# Compatibility, prerequisites and verification

KKdesign-kit is packaged as a skill for Codex and Claude Code. Install and
authenticate the chosen harness separately; use the native skill paths and
invocations in [installation](installation.md). Packaging and installation use
Python 3.9+ and the Python standard library. Offline contract validation also
requires `jsonschema >=4.18,<5` from `requirements.txt`.

The kit does not install Hoangsa, Impeccable, MCP servers, or hooks. Source
adapters need access to the sources declared by the project. Design and
prototype work that changes a canvas requires a separately authorized,
authenticated design-tool connection. A configured source adapter or a valid
offline fixture does not establish that a live import, render, interaction, or
product behavior works.

## Verify outcomes

Run checks in the environment and against the target project you intend to use.
From the source checkout, offline contract checks can be run with:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

For an extracted package, run `python scripts/kkdesign_install.py verify
--source .` from the extracted kit directory to check its declared resources,
inventory, version and checksums. These checks do not verify harness discovery,
external-tool access, live source behavior, design quality, rendering,
accessibility, or product correctness. Verify live results in the relevant
harness/tool by inspecting persisted changes and actual output; report blocked
access as a limitation rather than as a successful result.

Tool execution and approval are separate. A successful command or recorded
observation does not imply owner approval, publication permission, or a shipped
product capability. Obtain those decisions from the responsible owner.

Support depends on each harness version, host policy, authentication and
external-tool availability. This package does not make a broad compatibility
promise for harness releases, desktop/cloud modes, managed policies, or design
tools; verify the exact environment in which it will be used.
