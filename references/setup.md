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
2. **Check the environment.** Identify the OS using the local executor. On
   macOS use the internal shell entrypoint, even if system Python is present:

   ```sh
   /bin/sh "$SKILL_DIR/scripts/kkdesign_setup_macos.sh" --package-root "$SKILL_DIR"
   ```

   It needs no Python, Node or developer tooling on PATH. It uses a pinned
   CPython distribution with venv/ensurepip, so missing or unsuitable system
   Python, venv or pip does not send the user to manual installation. Native
   macOS ARM64 smoke is recorded separately from provider acceptance; the Intel
   artifact is implemented with native acceptance pending. See
   [macOS runtime verification](../docs/verification/macos-runtime.md).

   On other OSes, WWA-05/06 acquisition remains pending. With an existing Python
   3.9+ and working venv/ensurepip, the existing shared Setup remains usable:

   ```sh
   python3 -I -B "$SKILL_DIR/scripts/kkdesign_setup.py" --package-root "$SKILL_DIR"
   ```

   Use the actual discovered interpreter (Windows can use `py -3`). These are
   agent execution instructions, not terminal homework. `--package-root` is the
   absolute directory containing the activated SKILL.md, including Codex's
   nested skill layout; never infer it from product CWD.
3. **Explain and ask when needed.** The entrypoint emits checking and either
   verifies an existing trusted runtime or returns `consent-required` without
   writes, dependency downloads, venv creation or new-runtime execution. Explain
   the returned exact cache location, downloads, purpose and permissions in
   plain language.

   On macOS also disclose the pinned CPython 3.12.12 archive from Astral's
   python-build-standalone GitHub release 20251014, stored under
   `~/.kkdesign-kit/bootstrap/`; its HTTPS source and SHA-256 are pinned in the
   bundled entrypoint. It uses macOS system curl, tar and shasum, without a
   second downloaded bootstrap executable. For example:

   “KKdesign needs to create a private Python environment and download its
   validation dependencies from the package index. It will store them at
   [returned location], outside your project and the plugin. This needs network
   access, writes to your user cache and local execution, with no admin access
   or changes to system Python or shell settings. May I proceed?”

   Wait for an explicit yes. A Setup request, install, schema pass or tool
   approval alone is not this consent. Refusal/cancellation means stop here;
   do not rerun with consent, download or execute a new runtime. After yes,
   rerun the same OS entrypoint with `--consent`. This flag conveys the agent's
   observed permission; no file or test can establish human approval.
4. **Show progress.** Translate streamed JSON phase events into short updates:
   checking → consent required (if needed) → downloading pinned Python (macOS,
   if needed) → preparing runtime → verifying helpers → complete or failed. Preparation uses venv and requirements.txt in
   the private user cache, with bounded subprocess execution. No standalone
   install lifecycle, hooks or alternate installer is invoked.
5. **Use the result.** On macOS use the absolute `python` path returned by a
   successful Setup to invoke the existing `scripts/kkdesign_run.py` dispatcher,
   with `-I -B`, for the remainder of this agent session. Never substitute a
   project-provided executable or PATH Python. In a new session run the macOS
   Setup check again to verify/reuse the cache and obtain that path. General
   Python-free helper startup and full caller migration remain WWA-07.
6. **Report the result.** Only `ready` following actual synthetic workspace
   materialization and dependency-backed helper validation establishes runtime
   readiness. Reuse verifies a trusted cache and runs helpers again, without
   download or a redundant consent request. Keep external tools **unverified**
   until separately connected and tested for the requested workflow. Helper
   checks do not prove provider behavior, design quality or human approval.

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

macOS Setup acquires pinned CPython internally and reuses it only after checking
its archive and full file/link/directory inventory. The user-owned private cache
is the trust boundary; hashes detect corruption/modification, not publisher
identity or protection against an attacker controlling the same user account.
The package must come from a trusted provider/reviewed source. The CPython
archive remains in the private cache to verify reuse. Cache conflicts and
checksum failures preserve existing data and stop; never delete a suspicious
cache automatically or use arbitrary fallback interpreters.

Linux and Windows acquisition remain WWA-05/06. Without suitable Python on
those OSes, explain that their bootstrap integration is pending, without asking
for manual Python installation or offering a standalone fallback. Their adapters
must preserve the same package-root, consent, private-cache, integrity and real
helper-validation contracts.

The current Python launcher accepts only the private cache matching package
requirements and its verification receipt. Python-free helper entrypoints and
full caller migration belong to WWA-07; native lifecycle compatibility and
migration belong to WWA-08/09. End-to-end provider/OS/authentication/usability
acceptance remains separate from coding checks. Provider owns plugin lifecycle;
cache retention never grants tool authentication or approval.
