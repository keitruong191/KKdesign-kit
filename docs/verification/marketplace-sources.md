# WWA-11 persistent marketplace source verification

**Remote source deliverable and native checks: pass for the measured surface.**
Production approval, authenticated menus/consent/workflows, non-dev observation
and unmeasured platforms remain pending. This record does not grant release,
tag, official submission or main/integration merge authority.

This is the retained **0.5.0a1 historical record**. Its exact identities,
commands and measurements are not the current version's install targets.
Reproduce these commands only from a corresponding `0.5.0a1` source checkout;
the current probe derives its expected version from the current manifest.

## Exact source revisions

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

## Native remote results — 2026-11-10

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

## Reproduction and coding checks

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

## External acceptance and merge safety

Code/distribution are ready for coordinator review into
`feature/marketplace-installation-setup`. Do not merge main or call this a
production release. Authenticated native menus, observed human consent and
workflow, non-dev usability, macOS Intel, Linux/Windows CPUs and other provider
surfaces still need the owner-arranged cases in the
[handoff](onboarding.md). No known authentication failure was retried.
Official listings and production approval remain separate owner/provider gates.
