# Setup

Use the installed skill's absolute directory, supplied by the host, to read
resources. No Python is needed to read this guide or the command menu.

For the Codex or Claude Code plugin packaging preview, report:

1. **Plugin loaded**: the host has made this skill's instructions available.
2. **Setup required**: there is no supported plugin runtime provisioner or
   managed plugin helper execution in this preview. Do not claim runtime ready,
   even when Python, dependencies or an old standalone runtime exist.
3. **External tools unverified**: installation does not configure or authenticate
   live design tools and is not human approval of any project or design.

Explain the current boundary plainly: the plugin can open its menu and bundled
workflow instructions; it cannot yet prepare a runtime or run helper-dependent
workflows from its plugin cache. There is no download or execution action to
approve in this preview. Tell the user that a release with supported runtime
Setup is required before those operations can run. Do not ask them to install
Python, clone source, activate a venv, or use the standalone installer as a
fallback. Do not present an assessment as completed runtime Setup.

Future runtime Setup needs a separate, explicit user action and consent before
download/execution; install and bare menu never grant that consent. Runtime and
state must live in a private user-owned location outside the provider cache and
outside project data. This guide does not implement that future capability.

For an existing standalone installation, explain that its runtime and lifecycle
are separate; do not migrate or alter it from this route. Preserve conflicts and
project data for explicit migration in a supported release.
