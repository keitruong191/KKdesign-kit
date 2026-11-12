# Marketplace onboarding and troubleshooting

## Installation availability

The distribution channel for new users is a provider-native marketplace plugin.
Author-operated **review/prerelease** sources for version `0.5.0a2` are available
in the existing public repository; production release approval and official
listings remain pending. Git and HTTPS access to GitHub are needed for these
native Git sources; the provider must already be installed. No manual source
clone, build or Python installation is required to install the plugin.

Choose **New installation** below only for a clean profile. If KKdesign-kit is
already registered, use [Upgrade an existing installation](#upgrade-an-existing-installation).
The following commands use a POSIX shell; keep each `&&` chain intact so a failed
registration cannot be followed by installation from the old source.

## New installation

### Codex

```sh
codex plugin marketplace add https://github.com/keitruong191/KKdesign-kit.git --ref f49151a3b21501f52843385f5fce769009df39d2 &&
codex plugin add kkdesign-kit@kkdesign-kit-codex
```

This source is pinned to the immutable a2 distribution commit.

### Claude Code

```sh
claude plugin marketplace add 'https://github.com/keitruong191/KKdesign-kit.git#review/claude-0.5.0a2' --scope user &&
test "$(git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD)" = ec7fd565558b8adb065557382aa68d547dec13c6 &&
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user
```

Claude requires a named branch, which is mutable. The `test` gate must succeed
before installation: a Git error or different HEAD stops the chain. Do not
bypass it or install separately. The expected SHA comes from the
[`keitruong191`-authored release PR #22 description](https://github.com/keitruong191/KKdesign-kit/pull/22),
section **0.5.0a2 distribution commits**, not comments. Stop and ask the owner if
that version is missing or the clone differs. [Source provenance](marketplace-sources.md)
explains the pin limits.

Use the [Codex guide](codex-marketplace.md) or
[Claude Code guide](claude-marketplace.md) for discovery and scope controls.
The [handoff](verification/onboarding.md) tracks remaining authenticated/native
human acceptance. No approved production release or directory listing is implied.

## Upgrade an existing installation

Use the same provider profile that owns the installation. Inspect installed
plugins and marketplace sources first, then follow the concrete native recipe:

- [Codex source migration](codex-marketplace.md#upgrade-an-existing-installation):
  remove the old plugin and marketplace, register the a2 SHA, then install.
  `marketplace upgrade` refreshes the existing source; it cannot move an old
  immutable pin to a different commit.
- [Claude source migration and scope selection](claude-marketplace.md#upgrade-an-existing-installation):
  inspect `user` / `project` / `local` copies and the marketplace declaration
  scope separately. The user-scope recipe preserves plugin data with `--keep-data`,
  checks a2 HEAD before install, and ends disabled until you explicitly enable it.
  Do not remove unrelated scopes or override managed settings.

If `marketplace add` reports a different source or an `extraKnownMarketplaces`
source mismatch, **stop**. The old registration remains; running install
separately can install a1 again. Do not use same-source refresh as a source
migration or delete provider caches by hand.

Product design data and private runtimes remain separate. After the migration
and required restart, choose Setup when enabled to verify/reuse compatible
caches. A new plugin installation is not runtime download consent.

## In the installed agent

1. In the provider's native plugin browser, select the review marketplace,
   KKdesign-kit version and intended scope, or use the commands above. Install
   using that provider's controls and reopen the session when required.
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
| Marketplace/version cannot be found | Check the exact provider source/ref above, GitHub access and installed provider version; report a redacted error and the expected snapshot from the provenance record. Do not substitute the default branch. |
| Marketplace already added from a different source / source does not match `extraKnownMarketplaces` | Stop before install. Use the explicit upgrade recipe in this profile and inspect Claude's plugin/declaration scopes; the failed registration leaves the old source selected. |
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
