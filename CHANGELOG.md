# Changelog

## Unreleased — agent Setup and marketplace integration

- Add internal macOS Setup without existing Python/Node, using pinned CPython
  3.12.12 artifacts, HTTPS/SHA-256 verification before execution, private
  staging/locking and full bootstrap-cache verification before reuse.
- Preserve system Python, shell settings, plugin files and product data. Reject
  changed runtime files as well as changed interpreters before helper execution.
- Verify actual relocated missing-Python Setup, dependency provisioning, reuse
  and helpers on macOS ARM64. Intel native/provider/human acceptance remains
  separate; Linux/Windows acquisition and general helper startup are later items.

### Shared Setup changes

- Implement shared explicit Setup with streamed phases, consent before new
  runtime provisioning, a private requirements-matched cache, verification
  receipts and real dependency-backed helper smoke before readiness.
- Reuse verified runtimes without redundant download consent; reject unowned,
  missing or changed runtimes and preserve existing data on errors. Expose
  actionable network, write, local-execution and policy guidance.
- Enable the existing Python helper dispatcher after trusted Setup. General
  Python-free launch, Linux/Windows acquisition, native lifecycle integration
  and provider/usability acceptance remain separate pending work.

### Earlier packaging changes

- Add native Codex catalog/descriptor packaging from canonical resources, with
  local-executor metadata, isolated lifecycle verification and explicit surface
  limits. Menu/Setup remain readable without Python; Setup is now available with the prerequisites above.

- Add a Claude Code plugin descriptor and private-marketplace catalog sharing
  the canonical root skill and resources, with a deterministic allowlisted
  marketplace builder and integrity inventory.
- Add a readable Setup route and distinguish loaded instructions, runtime
  Setup required and external tools unverified. Plugin helper execution is
  gated on the trusted runtime prepared by Setup.
- Keep install/removal under native provider controls with no install hooks,
  automatic provisioning, standalone fallback or project-data lifecycle changes.
- No public release, official listing, runtime readiness or cross-platform
  native acceptance is claimed by this packaging change.
