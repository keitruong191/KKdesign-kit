# KKdesign-kit

Portable design-system execution foundations for **Codex and Claude Code**.

**Status: B2 / project-kit preview (`0.3.0a1`).** The installable `kkdesign-kit`
skill now initializes and refreshes project kits from declared Figma, Git and
local sources, with reviewable plans, scoped profile drafts and recovery.
Design/review/prototype execution and lesson authoring remain planned B3 work.

## Install the skill

Python 3.9+; no third-party packages are needed for installation or packaging.
From this checkout (or the extracted portable `kkdesign-kit/` directory):

```sh
python scripts/kkdesign_install.py install --harness codex --scope project --project "/path/to/project with spaces"
python scripts/kkdesign_install.py inspect --harness codex --scope project --project "/path/to/project with spaces"
```

Use `--harness claude-code` for Claude Code, or `--scope user` for personal scope.
Restart the harness and invoke `$kkdesign-kit` in Codex or `/kkdesign-kit` in
Claude Code. Bare invocation shows the seven-command menu and actual availability.
See [installation and lifecycle](docs/installation.md) for update, rollback,
uninstall, conflicts, platform prerequisites and artifact building.

Live CLI discovery passed in isolated user/project installs on Codex `0.167.0`
and Claude Code `2.1.308` (macOS). B2 init/refresh execution passed in project
scope on both; real Figma capture ingestion and committed Git lifecycle checks
are recorded separately in [compatibility and evidence](docs/compatibility.md).
Linux/Windows live execution and Figma import/render behavior remain unverified.

## Initialize and refresh a project kit

Install the dependencies in `requirements.txt` outside the installed skill.
Declare sources using the [exact supported formats](docs/source-adapters.md).
Then stage, inspect and explicitly authorize a plan:

```sh
python scripts/kkdesign_project.py init --project /chosen/project --sources /chosen/project/sources.json
python scripts/kkdesign_project.py plan --project /chosen/project --plan <PLAN_ID>
python scripts/kkdesign_project.py apply --project /chosen/project --plan <PLAN_ID>
python scripts/kkdesign_project.py validate --project /chosen/project
python scripts/kkdesign_project.py refresh --project /chosen/project --sources /chosen/project/sources.json
```

Existing product context, profiles, lesson IDs and task history are preserved.
See [project lifecycle, context provenance and recovery](docs/project-kits.md).
Provider metadata validation is not live Figma import/render or product approval.

## Run the foundation preview

Requires Python 3.9 or newer. From the repository root:

```sh
python -m venv .venv
# macOS/Linux
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/materialize_example.py --output .demo
.venv/bin/python scripts/kkdesign_core.py validate --design .demo/design
.venv/bin/python -m unittest discover -s tests -v
```

On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. The same commands may be run from a Codex or Claude Code terminal. Automated checks do not constitute live agent or Figma-runtime testing.

For an existing project, copy the four contracts from `schemas/` to its `design/schemas/`, adopt the documented lesson/profile/task format, then run the core validator against its `design/` directory. Existing DS snapshot validation should run alongside these foundation checks. The core does not certify arbitrary provider registries.

## What Stage A implements

- One authored `design/LESSON.md`; a deterministic, hash-checked `lessons-index.json` for lookup.
- Stable lesson IDs, platform applicability, triggers, status and evidence.
- A task `lessonReview` that distinguishes pending decisions, verified decisions and retrospective evidence mapping.
- Product decisions with field-level sources, observation dates, revisions, applicability and recheck conditions.
- Separate task and evidence schemas. Evidence wrappers preserve and hash the original payload.
- Local-reference containment, missing evidence, stale index/source and unknown lesson/profile checks.
- A synthetic fixture, negative regression tests and CI on Linux, macOS and Windows.

See [contracts](docs/contracts.md), [profile provenance](docs/product-profiles.md), [compatibility](docs/compatibility.md), and the [Stage B roadmap](docs/roadmap.md).

## Boundaries

The DS provider and design destination are independent. Source adapters scan explicitly supported Figma, Git or local inputs; a Git-sourced token does not require a Figma component key. Capture limitations are part of the registry, not filled with invented values.

The public repository contains generic code and invented examples only. Project-specific DS snapshots, product profiles, screenshots and task evidence stay in their respective projects. No credentials, global hook changes, external publication or Figma access are required to run this preview.

`validate` checks saved contracts. It does not fetch remote evidence, execute instructions in a DS, prove native accessibility/performance, or grant product approval. A lesson trigger is applicability metadata, not an installed automatic hook.
