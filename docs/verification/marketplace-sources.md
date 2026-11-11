# Marketplace source verification

## 0.5.0a2 — author-operated prerelease, 2026-11-11

The owner requested this publication after PR #21 merged. The authoritative
version-specific record is the [`keitruong191`-authored PR #22 description](https://github.com/keitruong191/KKdesign-kit/pull/22),
section **0.5.0a2 distribution commits**, not public comments. That description
wins if a copied verification page differs.

Canonical build commit: `7d083e35e099b2b88cdf26ea9f279a1d1f0d4143`.
Both parentless generated snapshots were atomically published to the existing
public repository; the two historical `0.5.0a1` refs were checked unchanged.

| Provider | Review ref | Immutable distribution commit | Deterministic ZIP SHA-256 |
| --- | --- | --- | --- |
| Codex | `review/codex-0.5.0a2` | `f49151a3b21501f52843385f5fce769009df39d2` | `f43df3730f10cd8cf0ae7c2f08a02238374349f5e4454d0c3b0f5ba2e146b2e5` |
| Claude Code | `review/claude-0.5.0a2` | `ec7fd565558b8adb065557382aa68d547dec13c6` | `a3b51041523a1ecde4547f454db0abe17e088fa6a2be9a8de19a778e1c94b74a` |

Public provenance: [Codex](https://github.com/keitruong191/KKdesign-kit/blob/f49151a3b21501f52843385f5fce769009df39d2/PROVENANCE.json),
[Claude](https://github.com/keitruong191/KKdesign-kit/blob/ec7fd565558b8adb065557382aa68d547dec13c6/PROVENANCE.json).
Each snapshot contains 88 catalog/plugin files plus provenance itself.
Committed blob SHA-256 values, path sets and `100644` modes were checked against
the inventory, not only working-tree bytes. Both use the existing synthetic
contributor identity. Unsafe paths, links, private paths, credentials, project
captures and binaries were checked before publication.

### Actual native public-source checks

Measured on macOS ARM64, with separate resolved private homes/configs and an
unrelated synthetic product CWD containing spaces. Provider/API/Git credentials
were not copied; global/system Git configuration was disabled. No model or
user message was sent.

| Provider / CLI | Installed verification | Explicit a1 → a2 source migration | Fresh discovery |
| --- | --- | --- | --- |
| Codex 0.167.0 | Enabled `0.5.0a2`; installed helper verified 85 files / 51 required resources | Old/new clone HEADs matched before install; native remove/unregister/re-register/reinstall; new Setup ready, reused=true without consent | App-server initialize → initialized → skills/list; namespaced skill, enabled a2 path |
| Claude Code 2.1.308 | Enabled `0.5.0a2`; installed helper verified 86 files / 51 required resources | Old/new clone HEADs matched before install; native uninstall/remove/add/install; new Setup ready, reused=true without consent | New stream-JSON initialize control response; namespaced command, idle session |

For both migrations, the same verified contract/requirements runtime was reused
from `PATH=/nonexistent`. Full private `.kkdesign-kit` and product fingerprints
had no added, removed or changed paths through Setup and native removals.
Native plugin/marketplace inventories ended empty; no standalone copy was made.
Codex retained an empty provider-cache namespace. Claude retained uninstalled
versioned plugin-cache directories with `.orphaned_at` markers; its marketplace
clone was removed. These provider-owned cache policies are not manual cleanup
or runtime/project loss.

The updated `smoke_remote_marketplaces.py` also completed both fresh a2 public
installs, exact pre-install clone checks, new-session discovery, real private
Setup/helpers, removal and data/runtime preservation with every command exit 0.
This is separate from the old-to-new migration probes.

Codex slash-named branch registration was independently measured against the
retained a1 ref before shipping branch-form snapshot guides. The README's
current Codex command instead uses the immutable a2 SHA. Claude still requires
a named branch and an expected-HEAD check; no raw-SHA retry or immutable
client-side Claude pin is claimed.

### Coding and publication limits

The empty-HOME full suite ran against the preparation tree committed as
`f71f818`: 212 cases, 203 passed, 9 native-Windows skips,
33.207 seconds. An actual pre-fix bootstrap probe reproduced HTTP 404 because
the manifest served a2 while the bootstrap asked for a1. Release pins were
aligned and the bootstrap fixture now derives its archive name from the
manifest. The subsequent real HTTP bootstrap smoke passed both harnesses/scopes,
fresh helpers, reinstall/removal, update/rollback runtime switching and
project-runtime nonexecution. It is loopback evidence, not a portable release.

No GitHub release/tag, legacy release-workflow dispatch, official listing,
main merge, primary-profile change or copied credentials were part of this
publication. Authenticated agent consent/workflows, browser/Figma behavior,
human design approval and unmeasured native platforms remain separate.

Reproduce a2 from the canonical build revision with an external Python 3.9+
environment containing requirements.txt:

```sh
python -m unittest discover -s tests -v
python -B scripts/smoke_remote_marketplaces.py --output '<new-private-directory-outside-source>' --codex-ref f49151a3b21501f52843385f5fce769009df39d2 --claude-ref review/claude-0.5.0a2 --claude-sha ec7fd565558b8adb065557382aa68d547dec13c6
```

Raw native logs, fingerprints and isolated fixture roots remain private outside
source. This post-publication source evidence is deliberately not embedded in
the frozen a2 snapshots. Do not rebuild/re-publish a2 from the later evidence
commit; use the recorded canonical revision for byte reproduction. Changed
published payload bytes require a new version.

## Historical 0.5.0a1 — WWA-11 record


**Remote source deliverable and native checks: pass for the measured surface.**
Production approval, authenticated menus/consent/workflows, non-dev observation
and unmeasured platforms remain pending. This record does not grant release,
tag, official submission or main/integration merge authority.

This is the retained **0.5.0a1 historical record**. Its exact identities,
commands and measurements are not the current version's install targets.
Reproduce these commands only from a corresponding `0.5.0a1` source checkout;
the current probe derives its expected version from the current manifest.

### Exact source revisions

- Canonical workflow/build source: `a9a51940746e6940e038792a1e4a7e9f7e2d2587`.
- Codex distribution: `e108483e7756e3ad4167531b524667a5f0beadb9`, reachable through
  `review/wwa11-codex-0.5.0a1` in `https://github.com/keitruong191/KKdesign-kit.git`.
- Claude distribution: `bea7e433f4f576068bcf2eec15317d7d73e5e065`, reachable through
  `review/wwa11-claude-0.5.0a1` in the same repository.
- Both advertise `0.5.0a1`. [Provenance](../marketplace-sources.md) records builder
  ZIP hashes, exact install commands and the Claude branch/SHA limitation.

The canonical commit contains the updated branch-based guides and the first
probe implementation. The final task commit adds this evidence, Codex SHA-pinned
guidance and probe fixes; it does not change shipped workflow/runtime bytes.
Snapshot documents link to their snapshot-era records; the integration/task
source record is authoritative for post-publication measurements. This avoids
recursively claiming a snapshot contains its own future Git commit ID.

### Native remote results — 2026-11-10

Measured on macOS ARM64, Codex CLI **0.167.0**, Claude Code **2.1.308**.
Each provider had its own clean temporary HOME/USERPROFILE, CODEX_HOME and
CLAUDE_CONFIG_DIR and an unrelated product CWD with spaces. Provider/token and
Git/SSH environment configuration was removed; system/global Git configuration
was disabled for these anonymous public clones. No primary credentials were
copied, no model/user prompt was sent and no primary profile was registered.

| Check | Observed result |
| --- | --- |
| Source remains usable without publisher session | Two public HTTPS Git distribution refs pushed to the existing repository; original temporary packaged Git trees deleted **before** the passing native probe. No loopback/server substitution or end-user build. |
| Codex native registration/install | `marketplace add` at the immutable SHA, `plugin add`, `plugin list --json`: exit 0; enabled `kkdesign-kit@kkdesign-kit-codex` at `0.5.0a1`. Native clone HEAD equals the recorded immutable Codex SHA. |
| Claude native registration/install | `marketplace add` with versioned branch, clone HEAD verified against recorded immutable Claude SHA **before** `plugin install`; inventory exit 0, enabled user-scope `kkdesign-kit@kkdesign-kit-marketplace` at `0.5.0a1`. Raw-SHA add was tried once and rejected as a nonexistent remote branch, not retried. |
| Fresh native discovery without model/authentication | New Codex app-server `initialize` → `skills/list` reports enabled `kkdesign-kit:kkdesign-kit`, correct plugin ID and native cached SKILL path. New Claude streaming SDK `initialize` control request returns success and the namespaced command. No user message/model request is needed for either. |
| Installed-cache integrity and actual helpers | Canonical bundle verification passed for both native cached skills. POSIX Setup with explicit synthetic-probe consent and PATH `/nonexistent` acquired pinned private Python/dependencies; helper-mode `kkdesign_install verify` returned verified from each native cache. Original publisher trees were absent; plugin bytes were unchanged. These are direct entrypoint runs, not authenticated agent consent/workflow observations. |
| Native removal and retained ownership | Codex `plugin remove`, Claude `plugin uninstall`, both inventories and both `marketplace remove` commands: exit 0; installed inventory empty. Synthetic DESIGN, lesson/task history and private state remained identical. Entire private runtime/bootstrap tree bytes, link targets, ownership and modes matched before/after removal. No standalone skill was created. |

Both distribution inventories have 78 extracted catalog/plugin files, plus
`PROVENANCE.json` itself. Canonical bundle verification reports 75 Codex skill
files / 76 Claude plugin files and 41 required resources each. The Claude
count includes its provider descriptor; the Codex descriptor is outside its
nested canonical skill. The allowlisted build output was checked for unsafe
paths/symlinks, local personal paths, token patterns, dependencies and binaries
before push. No customer registry, credentials, upstream binaries, `.git`,
`.hoangsa`, environment or user context was included in published payload bytes.
Git transport metadata belongs to the distribution repository, not the payload.
Hashes establish integrity, not publisher identity or human approval.

An initial remote probe reached Codex discovery and real helpers but its private
state check incorrectly used the payload verifier, which rejects legitimate
managed-Python symlinks. The probe now fingerprints link targets without following
them and preserves ownership/modes too. The subsequent complete two-provider
probe passed; this was a probe defect, not a plugin/runtime failure.

### Reproduction and coding checks

From an external Python 3.9+ development environment with requirements.txt:

```sh
python -m unittest discover -s tests -v
python -B scripts/smoke_remote_marketplaces.py --output '<new-private-directory-outside-source>' --codex-ref e108483e7756e3ad4167531b524667a5f0beadb9 --claude-ref review/wwa11-claude-0.5.0a1 --claude-sha bea7e433f4f576068bcf2eec15317d7d73e5e065
```

The opt-in probe requires both installed CLIs, native POSIX execution and approved
network access. It creates separate private profiles, verifies clone revisions
before install, discovers without model prompts, directly provisions synthetic
runtimes and checks native removal/data preservation. Its `--consent` authorizes
only its own disposable test, not human acceptance. Raw logs remain private
outside source. Final coding, canonical rebuild/integrity and CI results are
reported against the exact final task revision in the PR/coordinator handoff.
Existing CI is reused; no workflow edits or dispatch were needed.

### External acceptance and merge safety

Code/distribution are ready for coordinator review into
`feature/marketplace-installation-setup`. Do not merge main or call this a
production release. Authenticated native menus, observed human consent and
workflow, non-dev usability, macOS Intel, Linux/Windows CPUs and other provider
surfaces still need the owner-arranged cases in the
[handoff](onboarding.md). No known authentication failure was retried.
Official listings and production approval remain separate owner/provider gates.
