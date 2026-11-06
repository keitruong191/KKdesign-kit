# Codex and Claude Code

Stage A ships the same Python contracts and project layout for both targets. It does not install a skill, mutate user configuration, or depend on Hoangsa or Impeccable being installed. The preview can be invoked through the shell tool exposed by either environment.

Stage B will supply one `SKILL.md` source with the technical identifier `kkdesign-kit` and display name `KKdesign-kit`, plus harness-specific installation/discovery and optional-hook adapters. Each adapter must validate its current supported paths and event/tool semantics. Hooks are opt-in and separate from skill installation.

Acceptance must be reported per layer: file-format/installer tests, actual skill discovery in Codex, actual discovery in Claude Code, live design-tool capability, and Figma mutation/readback. Cross-platform Python CI only tests the first layer; it does not assert the other layers passed.

The installer must support user/project scope, detect existing installs, show a plan for conflicts, preserve unrelated configuration and credentials, and permit update/rollback without erasing project lessons or task history. No automatic global-hook activation. Exact installation instructions will ship with the tested Stage-B installer, not a nonfunctional command in this preview.
