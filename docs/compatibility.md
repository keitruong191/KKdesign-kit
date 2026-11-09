# Compatibility, prerequisites and verification

Codex marketplace packaging has native CLI evidence on macOS ARM64; see
[Codex packaging and surface limits](codex-marketplace.md). Native discovery
uses `$kkdesign-kit:kkdesign-kit`; authenticated menu/Setup acceptance is pending.
No IDE/cloud/desktop-app or other OS/CPU support is inferred.

Both [Claude](claude-marketplace.md) and [Codex](codex-marketplace.md) use the
shared [Setup](../references/setup.md): the menu requires no Python; explicit
Setup provisions after consent. macOS/Linux use an internal shell bootstrap with
pinned CPython, without system Python/Node or venv prerequisites. See
[macOS runtime evidence and Intel acceptance limits](verification/macos-runtime.md).
A trusted runtime is reused only after full cache checks and actual helper
verification. Linux acquisition targets GNU libc 2.28+ x86_64/ARM64 with host
curl, GNU tar and coreutils; musl and other CPUs are rejected before download.
[Linux native acceptance](verification/linux-runtime.md) is pending; implementation
is not a tested-distribution support claim. Windows acquisition and general
Python-free launcher integration remain pending (WWA-06/07). Setup smoke does not establish native
provider support or live design-tool authentication. Native and usability acceptance remain separate.

KKdesign-kit is packaged as a skill for Codex and Claude Code. Install and
authenticate the chosen harness separately; use the native skill paths and
invocations in [installation](installation.md). Packaging and installation use
Python 3.9+ and the Python standard library. Offline contract validation also
requires `jsonschema >=4.18,<5` from `requirements.txt`.
The POSIX bootstrap also requires `curl`, network access to the pinned release
and package index, and Python's working `venv`/`ensurepip`. It always provisions
the workflow dependencies in `~/.kkdesign-kit/runtimes/`, outside destination
repositories. Manual installation enables this with `--runtime`; without a
recorded runtime the launcher uses its invoking interpreter, which must have
the workflow dependencies installed. An invalid recorded runtime is refused.
Use `python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" HELPER`, without activation.
A fresh or restarted harness still needs Python 3 available and its separately
authenticated design tools.

The kit does not install Hoangsa, Impeccable, MCP servers, or hooks. Source
adapters need access to the sources declared by the project. Design and
prototype work that changes a canvas requires a separately authorized,
authenticated design-tool connection. A configured source adapter or a valid
offline fixture does not establish that a live import, render, interaction, or
product behavior works.

## Verify outcomes

Run checks in the environment and against the target project you intend to use.
From the source checkout, use an external development environment (macOS/Linux):

```sh
python3 -m venv "$HOME/.venvs/kkdesign-dev"
"$HOME/.venvs/kkdesign-dev/bin/python" -m pip install -r requirements.txt
"$HOME/.venvs/kkdesign-dev/bin/python" -B -m unittest discover -s tests -v
```

On Windows use `py -3 -m venv "$HOME\\.venvs\\kkdesign-dev"` and invoke that
environment's `Scripts\\python.exe` directly. No activation or profile edit is
needed; never install dependencies into the hash-managed skill directory.

For an extracted package, run `python3 -I -B scripts/kkdesign_install.py verify
--source .` from the extracted kit directory to check declared resources,
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
