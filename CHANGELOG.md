# Changelog

## Unreleased — agent Setup and marketplace integration

- Add internal macOS Setup without existing Python/Node, using pinned CPython
  3.12.12 artifacts, HTTPS/SHA-256 verification before execution, private
  staging/locking and full bootstrap-cache verification before reuse.
- Preserve system Python, shell settings, plugin files and product data. Reject
  changed runtime files as well as changed interpreters before helper execution.
- Verify actual relocated missing-Python Setup, dependency provisioning, reuse
  and helpers on macOS ARM64. Intel native/provider/human acceptance remains
  separate.

### Trusted helper runtime

- Both providers invoke the canonical dispatcher through verified POSIX or native
  PowerShell helper mode, with explicit arbitrary package roots, quoted arguments
  and no system Python, activation or provisioning during helper invocation.
- Verify bootstrap integrity before startup and runtime ownership, requirements
  and receipts before dispatch; reject missing/tampered caches and project
  executable paths. Keep plugin/project bytes unchanged on trust failures.
- Migrate active skill/workflow instructions, including package and extracted
  verification, and OS smoke callers. Exercise the package/verify route through
  unified helper mode without PATH Python; descriptor-free regression fixtures
  remove root provider markers before dispatch. Legacy
  standalone maintainer tooling retains its separate historical prerequisites.
- Native provider sessions and Linux/Windows/Intel acceptance remain pending;
  relocated package execution is separate from native provider discovery.

### Linux runtime

- Extend the canonical internal shell Setup to GNU/Linux, with pinned CPython
  artifacts for GNU libc 2.28+ x86_64/ARM64 and no dependency on system Python,
  Node, venv or ensurepip. Reject unsupported libc/CPU before download.
- Use native SHA-256, ownership/permission checks and deterministic full-tree
  verification in private user storage. Preserve macOS pins/cache receipts;
  migrate packaging, agent instructions and smoke to the shared POSIX entrypoint.
- Native Linux missing-Python and missing-venv/ensurepip acceptance remains
  pending available Linux resources; macOS smoke does not establish Linux support.

### Windows runtime

- Add native Windows PowerShell 5.1 Setup for x64/ARM64, with pinned HTTPS
  CPython acquisition, SHA-256 before extraction/execution, private staging,
  exclusive locking and full inventory checks before reuse.
- Verify Windows ownership, ACLs and reparse-point ancestry in both bootstrap
  and shared runtime readiness; preserve unowned/corrupt caches and respect
  execution policy. No Python/Node, WSL, Git Bash, admin or PATH changes.
- Ship the canonical bootstrap/security helper in both marketplace adapters.
  Add native boundary tests and relocated acquisition/helper smoke; actual
  Windows/provider acceptance awaits resources and is not inferred from macOS.

### Shared Setup changes

- Implement shared explicit Setup with streamed phases, consent before new
  runtime provisioning, a private requirements-matched cache, verification
  receipts and real dependency-backed helper smoke before readiness.
- Reuse verified runtimes without redundant download consent; reject unowned,
  missing or changed runtimes and preserve existing data on errors. Expose
  actionable network, write, local-execution and policy guidance.
- Enable the existing Python helper dispatcher after trusted Setup. Native lifecycle integration
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
