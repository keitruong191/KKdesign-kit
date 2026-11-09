# Setup in the agent

Read this guide from the host-supplied absolute skill directory (`SKILL_DIR`).
Opening the menu or installing the plugin never authorizes provisioning. Show
**Plugin: loaded**, **Runtime: not checked / Setup required**, and **External
tools: unverified** separately. No shell or Python is needed to read the menu.

When the user explicitly chooses Setup:

1. **Check the session.** If local execution is unavailable, stop and explain:
   “Setup needs a local session that allows execution and user-cache writes.
   Open the installed plugin in an authorized local provider session.” If host
   policy denies execution, report the denial and ask the administrator for an
   approved environment; never disable policy or repeatedly retry a denial.
2. **Check the environment.** Use the host's local executor to identify OS and
   an existing Python 3.9+ interpreter. Do not download or execute acquired code
   during this check. With existing Python, run the bundled internal entrypoint:

   ```sh
   python3 -I -B "$SKILL_DIR/scripts/kkdesign_setup.py" --package-root "$SKILL_DIR"
   ```

   Use the actual discovered interpreter (Windows can use `py -3`); these are
   agent execution instructions, not terminal setup homework for the user.
   `--package-root` is the absolute directory containing the activated SKILL.md,
   including Codex's nested skill layout. Never infer it from product CWD.
3. **Explain and ask when needed.** The entrypoint emits checking and either
   verifies an existing trusted runtime or returns `consent-required` without
   writes, dependency downloads, venv creation or new-runtime execution. Explain
   the returned exact cache location, downloads, purpose and permissions in
   plain language, for example:

   “KKdesign needs to create a private Python environment and download its
   validation dependencies from the package index. It will store them at
   [returned location], outside your project and the plugin. This needs network
   access, writes to your user cache and local execution, with no admin access
   or changes to system Python or shell settings. May I proceed?”

   Wait for an explicit yes. A Setup request, install, schema pass or tool
   approval alone is not this consent. Refusal/cancellation means stop here;
   do not rerun with consent, download or execute a new runtime. After yes,
   rerun the same entrypoint with `--consent`. This flag conveys the agent's
   observed permission; no file or test can establish human approval.
4. **Show progress.** Translate streamed JSON phase events into short updates:
   checking → consent required (if needed) → preparing runtime → verifying
   helpers → complete or failed. Preparation uses venv and requirements.txt in
   the private user cache, with bounded subprocess execution. No standalone
   install lifecycle, hooks or alternate installer is invoked.
5. **Report the result.** Only `ready` following actual synthetic workspace
   materialization and dependency-backed helper validation establishes runtime
   readiness. Reuse verifies a trusted cache and runs helpers again, without
   download or a redundant consent request. Keep external tools **unverified**
   until separately connected and tested for the requested workflow. Helper
   checks do not prove native behavior, design quality or human approval.

Failures return `runtime: error`, a code, diagnostic and next action. Report
network/package-index failure as a need to restore approved network access;
cache write failure as a need for writable user storage; execution-policy
failure as a need for an administrator-approved session. Stop after the error,
resolve its cause before retry, and preserve existing caches on trust/ownership
errors. Never execute a project-provided runtime path or repair an unowned
cache silently. A failed new-runtime transaction removes only its own incomplete
runtime and never records ready. A directory or old standalone marker alone
is insufficient verification; preserve it for explicit inspection/repair.

## Remaining integration contracts

This Setup path works with available Python 3.9+ and venv/ensurepip. If Python
is absent/unsuitable or lacks provisioning components, explain that automatic
Python acquisition requires the OS bootstrap integration (WWA-04 macOS,
WWA-05 Linux, WWA-06 Windows). Do not ask the user to install Python manually,
claim success, or fall back to another installer. Those adapters must take this
same package root, explain pinned artifact sources/storage/network/execution,
and obtain consent before downloading/executing a new runtime. They must
publish a verified compatible cache only after the real helper smoke succeeds.

The current Python launcher accepts only the private cache matching package
requirements and its verification receipt. Python-free helper entrypoints and
full caller migration belong to WWA-07; native lifecycle compatibility and
migration belong to WWA-08/09. End-to-end provider/OS/authentication/usability
acceptance remains separate from coding checks. Provider owns plugin lifecycle;
cache retention never grants tool authentication or approval.
