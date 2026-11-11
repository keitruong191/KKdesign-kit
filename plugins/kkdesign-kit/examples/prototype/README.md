# Fictional Atlas prototype inputs

This directory contains synthetic inputs for the DS-first interactive-prototype workflow, not a feature demo app. `ds/ds.json` contains tokens/specs/reference metadata only; `reference-shell.html` is a static visual reference. The separate `code-ds/` directory contains a small synthetic React component/theme fixture for the reuse-runtime case. No registry snapshot, revision, or content hash is pre-generated; the real init flow derives provenance and hashes from the selected project's token/spec inputs.

## Fixture assets

- Source registry: `sources.json`, local source ID `atlas-demo`, resolved source directory `ds/`.
- `ds/ds.json` declares the token/spec-only assets `button.primary`, `textfield.default`, and `card.default`, their variants, and light theme `theme.light`. These are not importable/native components.
- Product contexts: `context-web.json` (web) and `context-ios.json` (ios). Each cites the local `feature-brief.md` and `reference-shell.html` as provenance. iOS is a browser approximation at the stated fixture viewport, not native implementation evidence.
- `feature-brief.md` defines the user, required title and description, entry/end, labels/actions, form/review/success/error/loading paths, back/cancel/reset semantics, deterministic data, and verification states.
- `reference-shell.html` provides layout and style comparison only; it is not an implementation.

## Initialize a disposable project

Select a **disposable, writable project directory** for each platform run. Do not initialize in this source directory or an installed skill. Copy only the token/spec inputs and shared context files; this excludes the optional React code fixture from the token-only source project:

```sh
export SKILL_DIR="/absolute/path/to/installed/kkdesign-kit"
export FIXTURE="/path/to/KKdesign-kit/examples/prototype"
export PROJECT="/absolute/path/to/disposable/atlas-web-project"
mkdir -p "$PROJECT"
cp "$FIXTURE/sources.json" "$FIXTURE/context-web.json" \
  "$FIXTURE/feature-brief.md" "$FIXTURE/reference-shell.html" "$PROJECT/"
cp -R "$FIXTURE/ds" "$PROJECT/"
```

For an iOS-context project, use a separate disposable destination and copy `context-ios.json` instead of `context-web.json`. Replace the paths with the actual installed skill, repository, and disposable destination. Complete [Setup](../../references/setup.md) for the installed skill before helper execution; the examples below use the verified POSIX entrypoint, not Python on PATH. On native Windows, use the equivalent PowerShell helper form in [helper invocation](../../references/helpers.md). Helper mode does not provision or repair a missing/untrusted runtime.

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" \
  --package-root "$SKILL_DIR" --helper kkdesign_project init \
  --project "$PROJECT" \
  --sources "$PROJECT/sources.json" \
  --context "$PROJECT/context-web.json"
```

Review the plan ID and report from `init`, source coverage/provenance, generated changes, and conflicts. The registry resolves only the token/spec source at `ds/`; it does not declare React components as DS assets or prove runtime availability. If the selected destination has conflicting or existing user work, stop and choose/resolve the destination rather than overwrite it.

To authorize the staged changes, set `PLAN_ID` to the exact ID returned by init and run:

```sh
export PLAN_ID="<ID returned by init>"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" \
  --package-root "$SKILL_DIR" --helper kkdesign_project plan \
  --project "$PROJECT" --plan "$PLAN_ID"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" \
  --package-root "$SKILL_DIR" --helper kkdesign_project apply \
  --project "$PROJECT" --plan "$PLAN_ID"
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" \
  --package-root "$SKILL_DIR" --helper kkdesign_project validate \
  --project "$PROJECT"
```

`plan`/`apply` are explicit authorization steps; inspect the proposed changes before apply. Do not fabricate registry snapshots or skip plan review. Token/spec initialization uses the installed skill's verified private runtime; helper mode adds no dependencies and requires no Node, browser, Figma account, Figma writes, network service, or backend. React and its runtime are needed only for a project that chooses to exercise the separate code fixture.

## Optional code-reuse fixture

`code-ds/components.jsx` and `code-ds/theme.css` are authored synthetic React components and theme values corresponding to `button.primary`, `textfield.default`, and `card.default`. They are separate from the source registry: use the registry for the token/spec DS provenance, and import these source files directly only in a disposable React project that already has React available. Their presence does not mean the registry imports them or that they are native/upstream library components.

For that reuse-runtime scenario, initialize the project from the same token/spec source using the selected platform context above, then copy the code fixture into the disposable React project:

```sh
cp -R "$FIXTURE/code-ds" "$PROJECT/"
```

The source registry remains token/spec provenance; it does not invent or claim a code-component import. Keep React/project files and any generated app outside this fixture directory. Do not install dependencies as part of fixture preparation; use the project's already-provisioned React runtime.

## iOS-context run

For the iOS-profile/browser-approximation scenario, use a **separate disposable project** and `context-ios.json` in the init command in place of `context-web.json`. Keep the selected iOS platform/profile and lesson authoritative: do not switch it to web merely because a later renderer uses a browser. Use the brief's 390×844 CSS-pixel viewport and report browser/native limitations. These fixture viewports are scenario inputs only, not product defaults or a support matrix.

## Evidence and boundaries

A future interactive demo must be created in its selected disposable project from the initialized DS/context and the brief; it must not be mistaken for files already present here. Walk through the brief's required states and inspect a real render against the reference. Store task/scenario/state, viewport, and reference provenance with captures in that selected project. A static reference or successful init is not evidence of completed interaction, rendered fidelity, native behavior, or human approval. No screenshots or private/project-specific evidence belong in this synthetic fixture directory.
