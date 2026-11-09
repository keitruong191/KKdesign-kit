# KKdesign-kit

A design-system skill for Codex and Claude Code. Use it to prepare project design context, execute and review design tasks, create explicitly requested prototypes, and retain evidence-backed lessons.

The skill includes command guides, Python helpers, schemas and synthetic examples. Live canvas edits and prototype playback use your separately configured design tools.

## Get started

**Marketplace publication is pending.** Version `0.5.0a1` is the canonical
review package version, not a publicly installable release. There is currently
no verified published KKdesign marketplace source/version to give users. The
owner must approve and publish a source, then verify that exact version through
the native provider flow before user installation instructions can name it.
No release, marketplace endpoint or directory listing is claimed here.

For maintainer review, use the [Codex](docs/codex-marketplace.md) or
[Claude Code](docs/claude-marketplace.md) native packaging instructions and the
[acceptance handoff](docs/verification/onboarding.md). These instructions use
review packages and isolated profiles; they are not a second installation channel.

Once a reviewed plugin is installed in your authorized local provider session:

| Step | Codex | Claude Code |
| --- | --- | --- |
| Open the command menu | `$kkdesign-kit:kkdesign-kit` | `/kkdesign-kit:kkdesign-kit` |
| Prepare or check the runtime | `$kkdesign-kit:kkdesign-kit Setup` | `/kkdesign-kit:kkdesign-kit Setup` |
| Start a project | `$kkdesign-kit:kkdesign-kit init` | `/kkdesign-kit:kkdesign-kit init` |

Choose your product project and give the agent your design-system sources.
Setup explains any needed downloads, private cache location and permissions,
and waits for your consent. You do not need to install Python, activate an
environment or run runtime commands in a terminal. Opening the menu and installing
the plugin do not authorize a runtime download. A verified runtime can be reused.

After Setup reports helpers ready, `init` stages a project plan. Review its
changes before allowing the agent to apply it, then choose `design`, `review`
or another command below. Live design tools need their own connection and
permissions; helper readiness does not establish that connection or design approval.
Use provider controls to update, enable, disable or remove the plugin.

See [installation and troubleshooting](docs/installation.md), the measured
[support matrix](docs/compatibility.md), and [Setup](references/setup.md).
Authenticated agent and non-dev observation are still pending; partial native
checks do not establish a fully accepted user journey. Existing standalone users
should choose Setup's consented migration flow; standalone installation is not
an onboarding fallback.

## Commands

| Command | What it does | Guide |
| --- | --- | --- |
| `Setup` | Check, request consent, prepare/reuse and verify the private runtime; keep external-tool state separate. | [Setup](references/setup.md) |
| `init` | Scan declared design-system sources and stage a project-kit plan for review. | [Project setup](references/project-kit.md) |
| `refresh` | Compare source changes and stage an update while preserving project history. | [Project setup](references/project-kit.md) |
| `design` | Resolve scope and lesson decisions, execute with authorized tools, then inspect saved structure and rendered output. | [Design](references/design.md) |
| `review` | Report UX, visual and design-system findings. Make edits only when requested. | [Review](references/review.md) |
| `prototype` | Create or change explicitly requested interactions and verify actual navigation. | [Prototype](references/prototype.md) |
| `learn` | Capture feedback separately from inferred lessons; preserve stable IDs, supersession and historical sources. | [Learning](references/learn.md) |
| `package` | Build a portable ZIP with a versioned manifest and checksums. | [Packaging](references/packaging.md) |

Design and review never create prototype interactions as a side effect. Review guidance is bundled with [upstream attribution and licenses](docs/review-attribution.md); no installed Impeccable or Hoangsa is required. Installation does not enable hooks or configure external tools.

## Set up a project

In the installed provider session, choose `init` after Setup. Give the agent
the product-project path, source-config path and relevant platform or surface.
Create a `sources.json` using the [supported local, Git or Figma formats](docs/source-adapters.md);
source locations resolve relative to that configuration file. The agent uses
the trusted [helper entrypoints](references/helpers.md) from the activated plugin,
independently of the product CWD.

Inspect the staged plan's file changes, conflicts and source limitations before
authorizing apply. Use `refresh` when sources change and review its new plan in
the same way. Maintainer executable examples are in the
[acceptance handoff](docs/verification/onboarding.md), separate from onboarding.

Existing product context, profiles, lessons and task history are preserved. Project files stay in the selected product project:

- `PRODUCT.md` and `DESIGN.md` provide product context and the design entry point.
- `design/` holds source registries, scoped profiles, canonical `LESSON.md`, its derived index, task records and evidence.
- `.kkdesign-kit/project/` holds staged plans and recovery state.

Design-system sources and design destinations are independent: a Git token source does not require a Figma component key. See [project lifecycle and recovery](docs/project-kits.md) and [profile provenance](docs/product-profiles.md) for details.

## Maintainer package verification

These commands build and inspect a source artifact; they do not install a
plugin or authorize publication. For both native marketplace builders and
installed-package smoke, use the [handoff](docs/verification/onboarding.md).

Choose fresh output and extraction paths. Existing archives are not overwritten.

```sh
python3 -I -B scripts/kkdesign_install.py package --output ../kkdesign-kit-0.5.0a1.zip
python3 -m zipfile -e ../kkdesign-kit-0.5.0a1.zip ../kkdesign-kit-extracted
python3 -I -B ../kkdesign-kit-extracted/kkdesign-kit/scripts/kkdesign_install.py verify --source ../kkdesign-kit-extracted/kkdesign-kit
```

The extracted script checks the payload inventory, required resources, version and SHA-256 integrity. This does not authenticate the publisher or approve a design.

Packaging collects reusable skill resources from the skill directory. It does not export the surrounding product project or upload anything. Keep private source captures, credentials, project profiles and task evidence outside the public checkout and its resource folders.

## Verify work at the right boundary

Contract validation checks saved schemas, references, hashes and task records. It cannot establish rendered quality, playable navigation, native accessibility or performance.

For design work, inspect the actual destination, read back saved properties and view rendered output. For prototypes, check effective timing in the design tool and run the requested transitions, including back/cancel with valid history. Label simulated data, APIs, validation and timing. Human design approval remains separate.

For repository development, use a dependency-equipped Python environment.
The source checkout also carries the plugin descriptor, so its launcher
requires the same verified runtime as the installed plugin. Maintainer verification
can run the helper scripts directly; this is not a plugin Setup fallback:
```sh
python3 -m venv "$HOME/.venvs/kkdesign-dev"
"$HOME/.venvs/kkdesign-dev/bin/python" -m pip install -r requirements.txt
"$HOME/.venvs/kkdesign-dev/bin/python" -B -m unittest discover -s tests -v
"$HOME/.venvs/kkdesign-dev/bin/python" -B scripts/materialize_example.py --output ../kkdesign-example
"$HOME/.venvs/kkdesign-dev/bin/python" -B scripts/kkdesign_core.py validate --design ../kkdesign-example/design
```

Use an unused example-output directory. The example is synthetic; passing it is not evidence of live design-tool or product behavior. See [data contracts](docs/contracts.md) for the saved formats and validation rules. 

