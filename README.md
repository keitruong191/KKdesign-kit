# KKdesign-kit

Portable design-system execution foundations for **Codex and Claude Code**.

**Status: Stage A / foundation preview (`0.1.0a1`).** This repository provides working lesson indexing, product-profile and task/evidence contracts, and offline validation. The installable `kkdesign-kit` skill, DS scanning, Figma execution/review/prototype commands, installers, and hook adapters are Stage B work and are not advertised as implemented.

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

The DS provider and design destination are independent. Future source adapters can scan Figma, a Git revision or a local folder; a Git-sourced token does not require a Figma component key. No provider scan runs in Stage A.

The public repository contains generic code and invented examples only. Project-specific DS snapshots, product profiles, screenshots and task evidence stay in their respective projects. No credentials, global hook changes, external publication or Figma access are required to run this preview.

`validate` checks saved contracts. It does not fetch remote evidence, execute instructions in a DS, prove native accessibility/performance, or grant product approval. A lesson trigger is applicability metadata, not an installed automatic hook.
