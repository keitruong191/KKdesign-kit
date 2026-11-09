# Marketplace onboarding and troubleshooting

## Installation availability

The sole distribution channel for new users is a provider-native marketplace
plugin. **Public installation is pending**: no approved published marketplace
source/version or public-directory listing is verified. `0.5.0a1` identifies the
canonical review payload, not an available public release. Do not guess a URL
or install from the default repository branch. The owner must publish and verify
an exact source/revision and package version before adding user-ready commands.

Maintainers can review actual packages now through the
[Codex native flow](codex-marketplace.md) and
[Claude Code native flow](claude-marketplace.md). Their placeholder sources refer
to disposable reviewed catalogs, not live install endpoints. The
[handoff](verification/onboarding.md) gives build/smoke commands and the remaining
acceptance cases. No public standalone, curl, npm or Homebrew fallback is offered.

## In the installed agent

1. In the provider's native plugin browser, select the owner-verified marketplace,
   KKdesign-kit version and intended scope. Install using that provider's controls;
   reopen the session when required. This step becomes user-ready only after
   the publication and native acceptance above.
2. Open `$kkdesign-kit:kkdesign-kit` in Codex or
   `/kkdesign-kit:kkdesign-kit` in Claude Code. The namespaced skill was observed
   in native discovery; authenticated menu rendering remains pending. The menu
   includes Setup and reads instructions without Python or runtime provisioning.
3. Choose the corresponding `Setup` command and your product project. The agent
   checks the environment and distinguishes plugin loaded, runtime/helpers
   readiness and external design-tool connection. If acquisition is needed it
   explains what will be downloaded, the exact private user cache, network/write
   access and execution, then waits for your permission. Declining stops it.
4. Setup prepares pinned Python and dependencies internally, or verifies and
   reuses compatible caches. No Python installation, terminal runtime commands,
   environment activation or system settings changes are user steps. Only actual
   helper validation allows a ready result. See [measured platform limits](compatibility.md).
5. Choose `$kkdesign-kit:kkdesign-kit init` or
   `/kkdesign-kit:kkdesign-kit init`. Give the agent the selected project and
   [source configuration](source-adapters.md). Review the staged plan before
   authorizing apply. Then choose a design/review workflow. Connect and authorize
   external design tools separately when the workflow needs them.

## When something stops

| What you see | Next action |
| --- | --- |
| Marketplace/version cannot be found | Ask the maintainer for the approved published source, revision and version; public installation is currently pending. Do not guess download URLs. |
| Skill/menu missing or multiple copies | Check the provider's installed/enabled inventory and selected scope, then open a fresh session. Give Setup the selected project so it can inspect user, project and ancestor duplicates. |
| Consent declined or cancelled | Stop; no new runtime should be downloaded or executed. Choose Setup later if you decide to grant the disclosed permission. |
| No local executor or host blocks execution | Use an authorized local provider surface or ask your administrator for an approved environment. Do not disable policy or change security settings. |
| Download/package-index/network failure | Restore approved network/proxy access with your administrator, then retry Setup after resolving the cause. Do not switch installation channels. |
| User cache cannot be written | Ask for writable storage owned by your user and report the redacted diagnostic. Do not use sudo/admin or change system Python/PATH. |
| Runtime missing, changed, incompatible or unowned | Stop helper execution and choose Setup for diagnosis. A missing compatible cache needs fresh consent; suspicious existing caches need owner inspection and are preserved. Never trust a project-provided executable or delete unknown folders. |
| Duplicate standalone installation | Setup lists verifiable ownership, locations and versions. Intact managed copies need separate migration consent for every copy; modified/unmanaged copies remain untouched for owner inspection. Refusal preserves them. Restart the provider after completed migration. |
| Busy/interrupted operation | Preserve locks, caches, copies and migration archives for owner inspection; do not delete a lock while an owner may be active. |
| Helpers ready, design tools unavailable | Connect/authenticate the design tool separately and grant only the needed project access. Runtime checks do not prove live rendering or human approval. |

Report the plugin version/revision, provider version/surface, OS/CPU, step and
redacted error code using the [feedback template](verification/onboarding.md#feedback-record).
Do not send tokens, private source IDs, personal paths, customer data or raw logs.

## Updates and removal

Use the provider's native update, enable/disable and uninstall controls in the
provider guide. After an update and required restart, choose Setup to recheck
compatibility. Matching requirements/runtime contracts reuse verified caches;
changes request consent for a separate cache. Install/update/enable never grants
that consent. Uninstall preserves project design data, lessons, task history and
private shared runtime/bootstrap caches; provider cache retention is host-owned.
Reinstall checks those caches again rather than trusting directory existence.

Existing standalone maintenance is documented separately in
[historical maintenance](legacy-maintenance.md). It does not manage native plugins.
