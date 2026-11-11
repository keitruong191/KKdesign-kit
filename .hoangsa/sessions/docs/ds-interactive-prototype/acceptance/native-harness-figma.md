# Native harness and Figma acceptance — proto-15

**Overall: PARTIAL; full E2E-04 is not passed.** Native target routing was exercised in Codex and Claude; explicit HTML/React artifacts were generated in synthetic projects. No native CLI exposed an authorized browser, so browser behavior, visual comparison, and complete handoff remain **PENDING**. Figma remains **PENDING**.

## Capability and project setup

- `codex --version` → exit 0, `codex-cli 0.167.0`; `codex login status` → exit 0, already authenticated.
- `claude --version` → exit 0, `2.1.308`; `claude auth status` → exit 0, already authenticated. No login was performed.
- The extracted canonical installer ran project-scope `install` then `inspect` for Codex and Claude in separate disposable projects. All four commands exited 0; both reported `managed`, version `0.5.0a1`. No `--runtime`, user-scope install, dependency installation, or user-config modification.
- HTML and React synthetic projects were initialized from the extracted `examples/prototype` token/spec source and `context-web.json`; the init plan was inspected and applied before any task/artifact generation. The projects preserve the JSON profile id `product-web` and web platform. React alone has the separate synthetic `code-ds` fixture.
- Project helper init/plan/apply/validate operations exited 0 with the existing Python runtime. Synthetic source/plan and invocation evidence is retained under each selected project’s `transcripts/`; app/task/evidence files remain under their project roots.

## Codex — native route PASS; full surface PENDING

The native `$kkdesign-kit` skill was discovered and its installed shared `prototype.md` and `prototype-web.md` guides were read in the session transcript.

- **Target selection:** `$kkdesign-kit prototype` with no delivery target exited 0 and asked whether Figma, HTML, or React; it created no prototype artifact.
- **Design boundary:** `$kkdesign-kit design` exited 0 and stopped because the synthetic fixture has no design destination/complete design brief and Figma access was disallowed. No interaction or app was created.
- **Review boundary:** `$kkdesign-kit review` exited 0 and reported fixture evidence limits without edits or prototype activity.
- **Explicit HTML target:** `$kkdesign-kit prototype` with the initialized Atlas brief and HTML target exited 0. Shared planning/preflight passed; the dependency-free artifact is `design/prototypes/atlas-request-html/`. Source/static checks and task integrity passed. Task status remains `in_progress`; no browser run or screenshot exists.
- **Explicit React target:** `$kkdesign-kit prototype` with the initialized brief and React target exited 0. Shared preflight passed; the React artifact is `design/prototypes/atlas-request-react/`; seven Node model tests passed. Initial production build failed to resolve React from the external synthetic `code-ds` fixture. The Vite config was corrected **inside this disposable artifact** to dedupe React/React DOM; using only the existing read-only dependency tree through an artifact-local symlink (no install/download), `npm run build` then passed with Vite 5.4.21. The existing Vite cache is artifact-local. Task remains `in_progress`; build/model tests are not browser proof.
- **Scope deviation / FAIL for that side effect:** the Codex React transcript records a scratch audit payload written to a system temporary directory outside the selected project. It is not used as evidence here and was not read, moved, or deleted. Task-local evidence is `design/tasks/atlas-request-react/evidence-0001.json` and `evidence-0002.json`.
- Evidence: each project’s `transcripts/target-selection.jsonl`, `design-boundary.jsonl`, `review-boundary.jsonl`, `html-prototype-native.jsonl`, and `react-prototype-native.jsonl`; React build/test logs and task evidence are project-local.

## Claude Code — target question PASS; route-generation scope failures disclosed

The normal native `/kkdesign-kit prototype` target-selection session discovered the installed slash command (`kkdesign-kit` appeared in native `slash_commands`), read the installed prototype guide, and asked Figma/HTML/React. The native `design` and `review` boundary probes exited 0 and made no prototype interaction/artifact.

- **Explicit HTML target, first attempt — FAIL:** the native slash invocation read the installed HTML guide, but its task helper failed with `No module named 'jsonschema'` because the CLI used the default interpreter. The session then wrote a task-plan scratch file to a system temporary directory outside the selected project. The out-of-scope scratch was not read, moved, or deleted.
- **Bounded HTML retry:** with the existing runtime on `PATH` and `DYLD_LIBRARY_PATH`, preflight passed and the HTML artifact/task were created in the selected project. However, `--restricted` omitted `/kkdesign-kit` from that invocation’s native slash-command list; the model treated the prompt as a direct request and manually read the installed guide files. This is **not** a successful native slash-route retry. The task remains `in_progress`; no browser/Node execution, screenshot, or visual/flow pass.
- **Explicit React target:** the restricted native attempt also did not expose `/kkdesign-kit`; it manually read the installed guide and generated a React artifact/task. The app’s own transcript reports React/Vite/Node unavailable through that CLI and browser absent; no build or browser observation was claimed. A later normal, read-only `/kkdesign-kit prototype` invocation did discover the slash command and confirmed the installed React route/task state, but did not build or launch the app. The Claude React artifact has no independent runtime/browser pass.
- **Scope deviation / FAIL for that side effect:** the first HTML attempt wrote a plan to a system temporary directory outside the project. It was not read, moved, or deleted.
- Evidence: project-local `transcripts/target-selection.jsonl`, `design-boundary.jsonl`, `review-boundary.jsonl`, `html-prototype-native.jsonl`, `html-prototype-native-runtime.jsonl`, `react-prototype-native.jsonl`, and the read-only `react-route-confirm.jsonl`.

## Browser and final handoff — PENDING for every generated app

Neither native CLI transcript exposed an authorized interactive browser tool. No local server was started in these native projects, and the parent browser device is not evidence of browser capability inside either CLI.

- **HTML prerequisite:** expose an authorized browser in the relevant native CLI and separately authorize local-file/loopback launch; open the actual artifact at 1280×800, exercise every documented fixture scenario, compare against `reference-shell.html`, and store genuine screenshots/results under the selected project/task.
- **React prerequisite:** same native-CLI browser and loopback-launch authorization, plus React/React DOM/Vite resolving from the selected artifact and code fixture. Codex’s disposable artifact now builds with an existing-runtime symlink; Claude’s artifact has no recorded build. Exercise the same scenario set at 1280×800 and capture actual results.
- Tasks remain `in_progress`; source presence, model tests, static checks, schema/path checks, and a successful build do not prove browser flow, timing, accessibility, rendered DS conformance, or complete handoff.

## Native Figma — PENDING

No Figma tool is mounted in the available context and no authorized synthetic Figma Plugin API project was available. No graph inspection, mutation/readback, or preview was attempted. Prerequisite: an authorized Figma Plugin API context and synthetic file/project authorized for graph changes and preview. No Figma pass is inferred from helper/package checks.

## Legacy smoke and other evidence limits

- The native `design`/`review` probes were inspected after execution and had no prototype artifacts; this supports the route-boundary observation only. The exact `smoke_workflow_harness.py` runner was not executed, so its own `noPrototypeArtifact` assertion is not claimed as passed.
- `python3 -I -B scripts/materialize_example.py --help` exited 1 with `ModuleNotFoundError: No module named 'kkdesign_core'`; this was an exploratory invocation, not the documented supported call. The materializer is not an installed launcher helper; its documented form is `python3 -B scripts/materialize_example.py <destination>`. This diagnostic is not reported as a source defect.
- The earlier full suite result belongs to proto-11; no full unittest/runtime suite was rerun here.
- No credential was copied or persisted; no login, dependency provisioning/download, business API call, publish, or upload was performed. Project-scope installation and existing runtime reuse are not user-scope config changes.
