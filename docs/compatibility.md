# Compatibility and measured support

No full user-ready provider/OS combination has completed acceptance yet.
Author-operated review sources are published; authenticated agent journeys,
production release approval and observed non-dev usability remain pending. Use [onboarding](installation.md) and the
[acceptance handoff](verification/onboarding.md) for the exact remaining work.
A passing schema, helper or CI job does not establish native support.

## Observed native evidence

These rows record only measured checks, not blanket platform support. Earlier
records are historical snapshots; later helper/lifecycle integration supersedes
their former implementation gaps.

| OS / CPU | Provider surface and observed version | Native evidence | Still pending |
| --- | --- | --- | --- |
| macOS ARM64 | Codex CLI 0.167.0, public Git review marketplace | WWA-11 remote snapshot: register/install, enabled inventory, fresh app-server discovery, installed-cache Setup/helpers, remove/unregister and preservation. WWA-08 historical loopback: update, enable/disable, remove/reinstall and two-consumer runtime preservation | Authenticated menu → human consent → Setup → workflow; non-dev observation |
| macOS ARM64 | Claude Code CLI 2.1.308, public Git review marketplace | WWA-11 remote snapshot: register/install, enabled inventory, fresh session-init discovery, installed-cache Setup/helpers, uninstall/unregister and preservation. WWA-08 historical loopback: update, enable/disable, uninstall/reinstall and two-consumer runtime preservation | Authenticated menu → human consent → Setup → workflow; non-dev observation |

WWA-11 uses the immutable remote snapshots in the source record (Claude installs
through a versioned branch whose native HEAD is verified first). Update,
enable/disable and reinstall remain WWA-08 evidence from synthetic versioned
loopback Git sources; those operations were not rerun against the published
WWA-11 snapshots. The rows keep these transport/revision scopes separate.

Sources: [persistent source verification](verification/marketplace-sources.md),
[Codex discovery](verification/codex-marketplace.md),
[Claude discovery](verification/claude-marketplace.md),
[two-consumer native lifecycle](verification/native-lifecycle.md),
[macOS acquisition](verification/macos-runtime.md), and
[trusted helpers](verification/trusted-helpers.md). Missing-Python Setup and
helper workflows have also run from both relocated package layouts on macOS
ARM64 with no Python/Node on PATH. That is executable package evidence,
separate from a model executing the workflow in an authenticated provider session.

## Implemented targets awaiting native acceptance

This table is an implementation inventory, not additional supported combinations.
Each CPU needs its own native OS and each provider's authorized local session.

| Target | Implemented prerequisites | Pending evidence |
| --- | --- | --- |
| macOS x86_64 | Native shell, host HTTPS/archive/hash tools, writable private user storage | Intel acquisition/reuse/helper smoke and both provider journeys |
| GNU/Linux x86_64 and ARM64 | GNU libc 2.28+, host curl, GNU tar/coreutils, writable private user storage | Each CPU/distro acquisition/helper/provider journey; genuine system Python missing venv/ensurepip; policy/write denial |
| Native Windows x64 and ARM64 | Windows PowerShell 5.1, native tar (Windows 10 1803+), private ACL-capable user storage, approved execution | Each CPU acquisition/reuse/helpers, paths/ACLs/policy/write denial and both provider journeys |

All Setup targets acquire pinned Python internally after consent; users do not
install Python/Node, venv or developer tools. Linux musl and other CPUs are
rejected before download. Windows does not require WSL or Git Bash and never
relaxes execution policy. See [Linux](verification/linux-runtime.md) and
[Windows](verification/windows-runtime.md) for implementation checks and native
handoffs. Other OS/CPU combinations are unverified and are not advertised.

## Provider and publication boundaries

| Channel or surface | Current status |
| --- | --- |
| Maintainer repo/local marketplace review | Real native CLI checks above; builders produce canonical version 0.5.0a1 for isolated review |
| Public author-operated marketplace | Version 0.5.0a1 review sources published; immutable provenance and exact remote native checks in [source verification](verification/marketplace-sources.md); production approval pending |
| OpenAI public directory | No approved/published KKdesign listing verified; local-execution eligibility/review is separate from repo CLI checks |
| Anthropic Directory / claude-plugins-official | Neither listing is verified; separate submission/review routes, neither implied by a private marketplace |
| Codex IDE, desktop app, cloud and other Claude surfaces | No KKdesign native evidence here; do not infer coverage from CLI or another product's support |
| Session without authorized local execution | Setup/helpers unavailable; use an administrator-approved local environment when available |

Provider documentation may describe broader capabilities; this matrix records
KKdesign evidence only. The package requires local execution. Repo-marketplace
support does not establish public-directory local-execution eligibility; verify
OpenAI's current [publication constraints](https://developers.openai.com/plugins/deploy/desktop-only)
before submission. Private Claude marketplace auto-update is host-controlled;
no universal automatic update is promised.

## Runtime and external tools

Provider installation loads instructions, not Python or tool authentication.
Runtime/bootstrap caches are private user-owned storage outside plugin and
project. Readiness requires matching requirements/runtime contract, ownership,
integrity receipts and actual helpers. Helper mode never provisions; native
updates with changed contracts need explicit Setup consent for a new cache.
Provider removal retains caches and project data for other consumers.

Live design operations require separately authorized, authenticated design tools.
Local/Git/Figma source reads, synthetic helper checks and contract validation do
not prove live rendering, interaction playback, accessibility, performance or
human design approval. The kit installs no hooks, MCP servers, Hoangsa or Impeccable.

Maintainer builds and coding tests use Python 3.9+ and `requirements.txt`
(`jsonschema >=4.18,<5`) in an external development environment. This prerequisite
is for contributors, not user Setup. Exact coding and installed-package smoke
entrypoints are in the [handoff](verification/onboarding.md).
