# KKdesign-kit

A design-system skill for Codex and Claude Code. Use it to prepare project design context, execute and review design tasks, create explicitly requested prototypes, and retain evidence-backed lessons.

The skill includes command guides, Python helpers, schemas and synthetic examples. Live canvas edits and prototype playback use your separately configured design tools.

## Install

The new distribution direction is marketplace-only. The Codex
[marketplace packaging preview](docs/codex-marketplace.md) uses `$kkdesign-kit:kkdesign-kit`. The Claude Code
[marketplace packaging preview](docs/claude-marketplace.md) loads the canonical
skill as `/kkdesign-kit:kkdesign-kit`, including a readable **Setup** route.
Choose **Setup** to check/reuse a trusted runtime or, after explicit consent,
prepare one using available Python and verify real helpers. Automatic Python
acquisition and Python-free launch integration remain pending. No public marketplace release or official listing is claimed.
Do not use the old standalone installer as a plugin Setup fallback.

### Legacy standalone instructions

The commands below describe the existing standalone implementation, not the
new marketplace onboarding flow. Marketplace packaging does not authorize
publication of the old bootstrap or a standalone fallback.

The approved one-command bootstrap and public release are **pending PR approval and release**. There is no public download URL ready to use yet; do not run a guessed `curl` command. After the exact release artifact and checksum are published, the release instructions will provide a pinned command and that exact command will be smoke-tested before it is called ready.

Run the future bootstrap from the **destination product directory**; project scope defaults to that directory. It will require an explicit `--harness codex` or `--harness claude-code`, with `--project "/absolute/other project"` and `--scope user` available. The checked-in `install.sh` still downloads the pinned release; running it from a checkout is not a source fallback before publication.

### Source route while release is gated

Acquire the public source into a new path, then enter it (reviewers must use the PR revision containing this change):

```sh
git clone https://github.com/keitruong191/KKdesign-kit.git "$HOME/KKdesign-kit-source"
cd "$HOME/KKdesign-kit-source"
```

Do not overwrite an existing checkout; use that checkout's reviewed revision instead. From the source root, install into an existing destination you own:

```sh
python3 -I -B scripts/kkdesign_install.py install --harness codex --scope project --project "/absolute/path/to/product project" --runtime
```

To install for the product project that is your current working directory, call the checkout installer by its absolute path:

```sh
python3 -I -B "/path/to/kkdesign-kit/scripts/kkdesign_install.py" install --harness codex --scope project --project "$PWD" --runtime
```

To target another project, provide its quoted absolute path:

```sh
python3 -I -B scripts/kkdesign_install.py install --harness claude-code --scope project --project "/path/to/another-project" --runtime
```

For personal scope, choose the harness and pass `--scope user` (plus `--project` as context for conflict checks):

```sh
python3 -I -B scripts/kkdesign_install.py install --harness codex --scope user --project "/path/to/project-for-conflict-check" --runtime
python3 -I -B scripts/kkdesign_install.py install --harness claude-code --scope user --project "/path/to/project-for-conflict-check" --runtime
```

Requirements: Python 3.9+ (`python3` on macOS/Linux; Windows `py -3`), `curl` and network access for bootstrap downloads, and working `venv`/`ensurepip` plus network/package-index access for runtime provisioning. Bootstrap always provisions a workflow runtime in the user's private cache; manual stdlib install/update may omit `--runtime` and use the launcher's current dependency-equipped interpreter instead. Neither route needs activation or system pip.

These are usable local-source commands from the checkout; for the manual secondary route after release, acquire `kkdesign-kit-0.5.0a1.zip` and its `.sha256` from a trusted release, verify the checksum, extract it, `cd` into `kkdesign-kit/`, then run the installer command there. This upcoming version is not evidence that the public archive exists. On Windows use `py -3 -I -B scripts\kkdesign_install.py install --harness codex --scope project --project "C:\Work\Your Project" --runtime`.

Use `--harness claude-code` for Claude Code and `--scope user` for personal scope. Project installation should receive an explicit absolute `--project` path, which may contain spaces.

| Agent | Project installation | Invocation |
| --- | --- | --- |
| Codex | `.agents/skills/kkdesign-kit` | `$kkdesign-kit` |
| Claude Code | `.claude/skills/kkdesign-kit` | `/kkdesign-kit` |

After installation, restart the agent in the intended product project. A bare `$kkdesign-kit` or `/kkdesign-kit` shows the command menu; it is not an installer, discovery guarantee, or proof of live-tool readiness. Invoke a route explicitly, such as `$kkdesign-kit init` or `/kkdesign-kit init`. Live design work still requires separately authenticated design tools.

The installed launcher resolves helper scripts from the absolute installed `SKILL_DIR`, not the product's current working directory. You can work from another CWD; do not construct `../scripts/...` paths from there. If `python` is missing or resolves to Python 2, use Python 3 explicitly (`python3`, or `py -3` on Windows).

Installation writes `<BASE>/.agents/skills/kkdesign-kit` (Codex) or `<BASE>/.claude/skills/kkdesign-kit` (Claude Code), plus ownership/rollback state in `<BASE>/.kkdesign-kit/installations/<harness>/`. `BASE` is the destination project or your home for personal scope. Managed runtimes always live in `~/.kkdesign-kit/runtimes/<requirements-sha256>/`, shared across installations and outside destination repositories; both scopes require a writable user home. A marker or runtime path supplied by a project is never trusted as executable provenance. No hooks, MCP settings, shell profiles, login or product design files are changed.

See [installation and lifecycle](docs/installation.md) for manual acquisition/extraction, inspect, update, rollback, uninstall, and troubleshooting. SHA-256 verifies integrity, not publisher authenticity. See [requirements and tool access](docs/compatibility.md) for environment limitations.

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

The helper commands in this section describe legacy standalone installations.
The marketplace Setup route can prepare a verified runtime with available Python;
helper execution then uses that trusted cache. See [Setup](references/setup.md)
for current prerequisites and remaining integration boundaries.

Create a `sources.json` using the [supported local, Git or Figma input formats](docs/source-adapters.md). Give the agent the product-project path, source-config path and relevant platform or surface. Source locations resolve relative to the configuration file.

For direct CLI use from an installed skill, invoke the stable launcher with the helper name (without `.py`). Set `SKILL_DIR` to the absolute installed directory containing `SKILL.md`; the launcher resolves scripts there, independently of the product CWD:

```sh
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_project init --project "/path/to/your-project" --sources "/path/to/your-project/sources.json"
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_project plan --project "/path/to/your-project" --plan PLAN_ID
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_project apply --project "/path/to/your-project" --plan PLAN_ID
python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_project validate --project "/path/to/your-project"
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

