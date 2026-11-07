# KKdesign-kit

A design-system skill for Codex and Claude Code. Use it to prepare project design context, execute and review design tasks, create explicitly requested prototypes, and retain evidence-backed lessons.

The skill includes command guides, Python helpers, schemas and synthetic examples. Live canvas edits and prototype playback use your separately configured design tools.

## Install

You need Python 3.9+ and an installed, authenticated Codex CLI or Claude Code. Installation and packaging use the Python standard library; project workflows and contract validation also need the packages in `requirements.txt`.

From this checkout or an extracted portable `kkdesign-kit/` folder, create an environment **outside the skill directory**:

```sh
# macOS / Linux
python3 -m venv ../kkdesign-env
source ../kkdesign-env/bin/activate
python -m pip install -r requirements.txt
```

On Windows, use `py -3 -m venv ..\kkdesign-env` and activate it with `..\kkdesign-env\Scripts\Activate.ps1` in PowerShell. You can also invoke the environment's Python directly without activation.

Install into your product project:

```sh
python scripts/kkdesign_install.py install --harness codex --scope project --project "/path/to/your-project"
python scripts/kkdesign_install.py inspect --harness codex --scope project --project "/path/to/your-project"
```

For Claude Code, replace `codex` with `claude-code`. Use `--scope user` for a personal installation instead. Restart the agent in your product project after installation.

| Agent | Project installation | Invocation |
| --- | --- | --- |
| Codex | `.agents/skills/kkdesign-kit` | `$kkdesign-kit` |
| Claude Code | `.claude/skills/kkdesign-kit` | `/kkdesign-kit` |

Bare invocation shows the command menu. For example, use `$kkdesign-kit init` in Codex or `/kkdesign-kit init` in Claude Code. Helper commands need the dependency-equipped Python environment; give the agent its absolute interpreter path if it does not inherit that environment.

See [installation and lifecycle](docs/installation.md) for personal scope, updates, rollback, uninstall and conflicts, or [requirements and tool access](docs/compatibility.md) for environment limitations.

## Commands

| Command | What it does | Guide |
| --- | --- | --- |
| `init` | Scan declared design-system sources and stage a project-kit plan for review. | [Project setup](references/project-kit.md) |
| `refresh` | Compare source changes and stage an update while preserving project history. | [Project setup](references/project-kit.md) |
| `design` | Resolve scope and lesson decisions, execute with authorized tools, then inspect saved structure and rendered output. | [Design](references/design.md) |
| `review` | Report UX, visual and design-system findings. Make edits only when requested. | [Review](references/review.md) |
| `prototype` | Create or change explicitly requested interactions and verify actual navigation. | [Prototype](references/prototype.md) |
| `learn` | Capture feedback separately from inferred lessons; preserve stable IDs, supersession and historical sources. | [Learning](references/learn.md) |
| `package` | Build a portable ZIP with a versioned manifest and checksums. | [Packaging](references/packaging.md) |

Design and review never create prototype interactions as a side effect. Review guidance is bundled with [upstream attribution and licenses](docs/review-attribution.md); no installed Impeccable or Hoangsa is required. Installation does not enable hooks or configure external tools.

## Set up a project

Create a `sources.json` using the [supported local, Git or Figma input formats](docs/source-adapters.md). Give the agent the product-project path, source-config path and relevant platform or surface. Source locations resolve relative to the configuration file.

For direct CLI use, run these from the checkout or extracted skill folder:

```sh
python scripts/kkdesign_project.py init --project "/path/to/your-project" --sources "/path/to/your-project/sources.json"
python scripts/kkdesign_project.py plan --project "/path/to/your-project" --plan PLAN_ID
python scripts/kkdesign_project.py apply --project "/path/to/your-project" --plan PLAN_ID
python scripts/kkdesign_project.py validate --project "/path/to/your-project"
```

Replace `PLAN_ID` with the ID returned by `init`. Inspect its file changes, conflicts and source limitations before authorizing `apply`. Use `refresh` when those sources change, then review and apply its new plan in the same way.

Existing product context, profiles, lessons and task history are preserved. Project files stay in the selected product project:

- `PRODUCT.md` and `DESIGN.md` provide product context and the design entry point.
- `design/` holds source registries, scoped profiles, canonical `LESSON.md`, its derived index, task records and evidence.
- `.kkdesign-kit/project/` holds staged plans and recovery state.

Design-system sources and design destinations are independent: a Git token source does not require a Figma component key. See [project lifecycle and recovery](docs/project-kits.md) and [profile provenance](docs/product-profiles.md) for details.

## Package and verify

Choose fresh output and extraction paths. Existing archives are not overwritten.

```sh
python scripts/kkdesign_install.py package --output ../kkdesign-kit-0.4.0a1.zip
python -m zipfile -e ../kkdesign-kit-0.4.0a1.zip ../kkdesign-kit-extracted
python ../kkdesign-kit-extracted/kkdesign-kit/scripts/kkdesign_install.py verify --source ../kkdesign-kit-extracted/kkdesign-kit
```

The extracted script checks the payload inventory, required resources, version and SHA-256 integrity. This does not authenticate the publisher or approve a design.

Packaging collects reusable skill resources from the skill directory. It does not export the surrounding product project or upload anything. Keep private source captures, credentials, project profiles and task evidence outside the public checkout and its resource folders.

## Verify work at the right boundary

Contract validation checks saved schemas, references, hashes and task records. It cannot establish rendered quality, playable navigation, native accessibility or performance.

For design work, inspect the actual destination, read back saved properties and view rendered output. For prototypes, check effective timing in the design tool and run the requested transitions, including back/cancel with valid history. Label simulated data, APIs, validation and timing. Human design approval remains separate.

For repository development, use the dependency-equipped Python environment:

```sh
python -m unittest discover -s tests -v
python scripts/materialize_example.py --output ../kkdesign-example
python scripts/kkdesign_core.py validate --design ../kkdesign-example/design
```

Use an unused example-output directory. The example is synthetic; passing it is not evidence of live design-tool or product behavior. See [data contracts](docs/contracts.md) for the saved formats and validation rules.
