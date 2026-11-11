# KKdesign-kit

Design and prototype with your project's design system, in Codex or Claude Code.

Give your agent the product context and design-system sources. Use KKdesign-kit
to design a feature, review an existing flow, or create an interactive demo in
Figma, HTML or React. Keep decisions, feedback and evidence with the project.

- **Start from your DS.** Use the project's components, tokens and references.
- **Demo a feature in context.** Turn a PM/PO brief into a scoped prototype that
  feels like part of the existing product, with simulated behavior labeled.
- **Keep the work reviewable.** Retain source decisions, task history, checks
  and lessons instead of relying on the chat alone.

[Install](#install) · [First project](#first-project) · [Commands](#commands) · [Common questions](#common-questions) · [Changelog](CHANGELOG.md)

## Install

Current version: `0.5.0a2`, an author-operated review/prerelease. Production
approval and official directory listings are still pending.

You need Codex or Claude Code, Git, and HTTPS access to GitHub. Choose your
provider below and run its commands in a terminal. You do not need to clone or
build this repository.

<details>
<summary>Codex</summary>

```sh
codex plugin marketplace add https://github.com/keitruong191/KKdesign-kit.git --ref f49151a3b21501f52843385f5fce769009df39d2
codex plugin add kkdesign-kit@kkdesign-kit-codex
```

This installs from an immutable distribution commit. Open a new Codex session
after installation.

</details>

<details>
<summary>Claude Code</summary>

Register the marketplace and check the downloaded revision:

```sh
claude plugin marketplace add 'https://github.com/keitruong191/KKdesign-kit.git#review/claude-0.5.0a2'
git -C "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/kkdesign-kit-marketplace" rev-parse HEAD
```

Before installing, the output must be exactly:

```text
ec7fd565558b8adb065557382aa68d547dec13c6
```

**Stop if it differs** and ask the owner to review the snapshot. Claude uses a
mutable branch, so this check is required. The path command above was measured
on POSIX; see [installation guidance](docs/installation.md) for support limits.
Only after the revision matches, install:

```sh
claude plugin install kkdesign-kit@kkdesign-kit-marketplace --scope user
```

Open a new Claude Code session after installation.

</details>

These commands use built marketplace snapshots, not the repository's default
branch. If you already have a different KKdesign installation, use a separate
provider profile for review.

Exact commits and checksums are recorded in the
[`keitruong191`-authored PR #22 description](https://github.com/keitruong191/KKdesign-kit/pull/22),
under **0.5.0a2 distribution commits**, not public comments. That description is
authoritative if a copied evidence page differs. See
[source provenance and pin limits](docs/marketplace-sources.md) for details.

<details>
<summary>Already installed? Upgrade from an older pin</summary>

An older registration does not automatically move to the a2 source. In the
provider profile that owns the installation:

1. Remove the old plugin, then its marketplace registration using provider controls.
2. Follow the installation steps above with the a2 source, including Claude's
   revision check before installation.
3. Open a new provider session and run Setup to verify or reuse the runtime.

Your project data and private runtimes are separate from the plugin. Do not
delete them to change the marketplace source; compatible verified runtimes can
be reused. Existing standalone users should use
[Setup's consented migration flow](references/setup.md), not reinstall standalone
as an onboarding fallback.

</details>

## First project

Open the skill menu in your installed provider session:

| Codex | Claude Code |
| --- | --- |
| `$kkdesign-kit:kkdesign-kit` | `/kkdesign-kit:kkdesign-kit` |

Then work through these steps with the agent:

1. **Run `Setup`.** It explains any downloads, cache location and permissions,
   asks for consent, and prepares or checks the helper runtime. You do not need
   to install Python or activate an environment yourself. Installing the plugin
   or opening its menu does not authorize a runtime download.
2. **Run `init`.** Choose the product folder, platform and design-system sources.
   Provide a `sources.json`, or ask the agent to prepare one using the
   [local, Git or Figma source formats](docs/source-adapters.md). Review the
   staged project plan before allowing apply.
3. **Choose the work.** Ask for `design`, `review` or an explicit `prototype`.
   Live design tools need their own connection and permissions, separately from
   Setup. Refresh the project when its sources change.

For example, after initialization, select `prototype` and ask:

> Create a local HTML prototype of the invite-a-teammate flow using this
> project's design system. Cover success, invalid email, retry and cancel.
> Use synthetic data and label simulated behavior. Do not call real APIs.

Choose Figma, HTML or React in the brief. If the target is unclear, the agent
asks; there is no default renderer or `--target` flag. Design and review do not
add prototype interactions unless you request them.

## How it works

1. **Read the project.** Use its product context, platform/profile, design-system
   sources and applicable lessons.
2. **Agree on the scope.** Record the feature, flows, states, acceptance criteria,
   source choices and open questions before changing artifacts.
3. **Design or build the demo.** Reuse suitable DS code, or recreate from the
   declared tokens/specs and record the gaps. A browser demo keeps the product's
   platform/profile; it does not turn an iOS project into a web product.
4. **Check and hand off.** Inspect the actual destination and exercise agreed
   scenarios. Include run/demo instructions, observations and remaining gaps.
   A valid saved record alone does not prove rendered quality or playable flows.

HTML prototypes open locally without Node or a CDN. React prototypes need a
working project runtime and DS implementation; reuse its package manager and
lockfile, and ask permission before adding dependencies. Browser verification
needs browser capability. Missing capability blocks the dependent work rather
than silently switching targets. Creating a prototype does not authorize
publishing or sharing it.

Follow the [prototype workflow](references/prototype.md) or the
[HTML/React guide](references/prototype-web.md) for planning and handoff details.

## Commands

<details>
<summary>All commands and guides</summary>

Choose these from the skill menu or invoke them through your provider's
namespaced skill command.

| Command | Use it to | Guide |
| --- | --- | --- |
| `Setup` | Prepare, check or reuse the private helper runtime with consent. | [Setup](references/setup.md) |
| `init` | Connect DS sources and stage the project-kit plan. | [Project setup](references/project-kit.md) |
| `refresh` | Stage source updates while preserving project history. | [Project setup](references/project-kit.md) |
| `design` | Execute an agreed design task with authorized tools and inspect the result. | [Design](references/design.md) |
| `review` | Report UX, visual and DS findings; edit only when requested. | [Review](references/review.md) |
| `prototype` | Create or change an explicitly requested Figma, HTML or React prototype. | [Prototype](references/prototype.md) |
| `learn` | Capture feedback and evidence-backed lessons without rewriting history. | [Learning](references/learn.md) |
| `package` | Build a portable skill ZIP with a manifest and checksums. | [Packaging](references/packaging.md) |

</details>

## Common questions

**Do I need Figma?**  
Only for work that uses Figma as a source or destination. Local HTML demos do
not require it. Figma canvas changes and preview checks need separately
authorized tools and an authenticated session.

**Is a prototype a production app?**  
It demonstrates the agreed feature with synthetic data and scoped interactions.
Real business APIs, authentication and production storage are not default
prototype scope. Label simulated validation, loading, errors and timing. Human
design approval remains separate from automated checks.

**Where does my project data go?**  
In the selected product project: `PRODUCT.md` and `DESIGN.md` hold context;
`design/` holds sources, profiles, lessons, tasks and evidence;
`.kkdesign-kit/project/` holds staged plans and recovery state. HTML/React
artifacts live in `design/prototypes/<taskId>`, separate from task/evidence
records. Refresh preserves existing project history. See
[project lifecycle and recovery](docs/project-kits.md).

**What has been verified?**  
Native CLI checks on macOS ARM64 covered fresh public installs, discovery,
Setup/helpers and explicit a1-to-a2 migration for both providers, including
runtime reuse and project-data preservation. Authenticated agent/non-dev
observation, browser/Figma acceptance, human approval and unmeasured native
platforms remain separate. See the [support matrix](docs/compatibility.md) and
[publication verification record](docs/verification/marketplace-sources.md).

**Do I need Hoangsa, Impeccable or hooks?**  
No local Hoangsa or Impeccable installation is required. The review guidance and
[upstream attribution/licenses](docs/review-attribution.md) are bundled.
Installation does not enable hooks or configure external tools.

## More documentation

- [Installation and troubleshooting](docs/installation.md)
- [Source adapters](docs/source-adapters.md) and [profile provenance](docs/product-profiles.md)
- [Saved data contracts](docs/contracts.md) and [trusted helper entrypoints](references/helpers.md)
- [Maintainer acceptance and marketplace handoff](docs/verification/onboarding.md)

<details>
<summary>Contributing and source-package checks</summary>

Use Python 3.9+ and an environment containing `requirements.txt`. These commands
are for repository development, not plugin onboarding. The source checkout also
carries a plugin descriptor; its launcher still requires a verified private
Setup runtime. Direct maintainer script checks are not a plugin Setup fallback.

```sh
python3 -m venv "$HOME/.venvs/kkdesign-dev"
"$HOME/.venvs/kkdesign-dev/bin/python" -m pip install -r requirements.txt
"$HOME/.venvs/kkdesign-dev/bin/python" -B -m unittest discover -s tests -v
"$HOME/.venvs/kkdesign-dev/bin/python" -B scripts/materialize_example.py --output ../kkdesign-example
"$HOME/.venvs/kkdesign-dev/bin/python" -B scripts/kkdesign_core.py validate --design ../kkdesign-example/design
```

Choose an unused example-output directory. The example checks offline contract
integrity, not live design-tool behavior or approval.

For a source-package smoke, choose fresh output and extraction paths:

```sh
python3 -I -B scripts/kkdesign_install.py package --output ../kkdesign-kit-0.5.0a2.zip
python3 -m zipfile -e ../kkdesign-kit-0.5.0a2.zip ../kkdesign-kit-extracted
python3 -I -B ../kkdesign-kit-extracted/kkdesign-kit/scripts/kkdesign_install.py verify --source ../kkdesign-kit-extracted/kkdesign-kit
```

These commands build and inspect a source artifact; they do not install a plugin,
authenticate the publisher or authorize publication. Use the
[marketplace handoff](docs/verification/onboarding.md) for native builders and
installed-package smoke. Published a2 snapshots remain frozen at their recorded
canonical build commit; do not rebuild/re-publish them from later source edits.

Packaging collects reusable skill resources, not the surrounding product project,
and uploads nothing. Keep private source captures, credentials, product profiles
and task evidence outside the public checkout and its resource folders.

</details>
