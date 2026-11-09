# Changelog

## Unreleased — Codex and Claude marketplace packaging preview

- Add native Codex catalog/descriptor packaging from canonical resources, with
  local-executor metadata, isolated lifecycle verification and explicit surface
  limits. Menu/Setup remain readable without Python; runtime integration is pending.

- Add a Claude Code plugin descriptor and private-marketplace catalog sharing
  the canonical root skill and resources, with a deterministic allowlisted
  marketplace builder and integrity inventory.
- Add a readable Setup route and distinguish loaded instructions, runtime
  Setup required and external tools unverified. Plugin helper execution is
  blocked until supported runtime Setup/dispatch is implemented.
- Keep install/removal under native provider controls with no install hooks,
  automatic provisioning, standalone fallback or project-data lifecycle changes.
- No public release, official listing, runtime readiness or cross-platform
  native acceptance is claimed by this packaging change.
