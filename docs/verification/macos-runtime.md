# macOS runtime implementation and acceptance

WWA-04 adds an internal `/bin/sh` Setup entrypoint to the canonical marketplace
payload. It is an agent-invoked Setup action, never a public installer, install
hook, alternate skill distribution or provider lifecycle command.

## Trust and provisioning

- The agent supplies an explicit absolute skill root. On macOS the shell uses
  bundled OS tools, without discovering or running PATH Python/Node. It always
  selects its pinned CPython with venv/ensurepip rather than relying on an
  incomplete system installation. Linux now uses the same POSIX entrypoint; Windows retains existing-Python Setup.
- Download requires explicit agent-observed consent. Initial checking without
  consent returns the source, private storage, purpose and permissions without
  creating cache state. The flag conveys consent; tests cannot establish it.
- CPython 3.12.12, python-build-standalone release **20251014**, is pinned for
  `aarch64-apple-darwin` and `x86_64-apple-darwin`. The exact artifact URLs and
  SHA-256 values live in the shipped shell entrypoint. Hashes were checked
  against both the upstream `SHA256SUMS` and GitHub asset digest metadata.
  Sources: [upstream release](https://github.com/astral-sh/python-build-standalone/releases/tag/20251014)
  and [Python distribution project](https://github.com/astral-sh/python-build-standalone).
  Updating these pins requires review and a new smoke on the affected matrix.
  Pinning is integrity control, not a claim that a historical patch is newest.
- macOS curl uses HTTPS-only transport/redirects, default certificate verification,
  bounded connection/download time and no curl configuration file. SHA-256 is
  checked before extraction/execution; host policy remains enabled. No upstream
  binaries are committed and no downloaded bootstrap executable is needed.
- Acquired Python and its verified archive live in
  `~/.kkdesign-kit/bootstrap/cpython-3.12.12-20251014-<architecture>/`.
  Dependencies and the actual workflow interpreter remain in the existing
  requirements-matched `~/.kkdesign-kit/runtimes/` cache. The provider owns plugin
  bytes; neither cache belongs to a project or to provider uninstall.
- Ownership, unsafe write permissions, symlinked cache ancestry, artifact hash
  and the full extracted file/link/directory inventory are checked before
  acquired Python reuse. The shared Setup checks runtime file inventory,
  interpreter, requirements, ownership and verification receipt before helper
  reuse. A changed library/startup file cannot pass merely because the Python
  executable is unchanged. Same-account compromise is outside this user-cache
  trust model; hashes and receipts are not publisher signatures.
- Private staging is removed on failed acquisition. Existing suspicious caches
  are preserved and rejected with no fallback. A lock prevents concurrent
  bootstrap mutations; interrupted locks require inspection before recovery.
  Canonical Setup retains its own runtime transaction/lock and publishes a
  receipt only after dependency installation and actual helper verification.
- No sudo, system pip/Python changes, shell profile/PATH edits, activation,
  provider credentials, hooks or security-policy bypass are involved.

## Coding verification

Observed host: macOS 26.5, Darwin ARM64. No Intel host was available; the Intel
artifact is implemented but native Intel support is not claimed.

| Check | Recorded result | Scope |
|---|---|---|
| `python -m unittest discover -s tests -v` in an external Python 3.9 development venv populated from `requirements.txt` | PASS, 145 tests | Core regressions and consent, trust, ownership, real refused-network and write-denial boundaries. |
| `python -B scripts/smoke_posix_setup.py` | PASS on macOS ARM64 | Actual pinned CPython download, real requirements provisioning and materialize/validate, both relocated marketplace layouts, repeat reuse and acquired-library tamper rejection. |
| `git diff --check` | PASS | Whitespace check only. |

The first developer invocation found no `python` command; a Python 3.9 run then
failed because that environment lacked `jsonschema`. Installing requirements
into a separate development venv resolved that prerequisite without modifying
system Python. The first smoke reached readiness/helper execution but found a
harness parser error for helper output; the parser was corrected before the
passing smoke. Neither failed attempt is counted as a successful check.

The real changed-path smoke is `python -B scripts/smoke_posix_setup.py`; it downloads
CPython and installs requirements into temporary user storage after explicit
harness consent. Its Setup subprocess has `PATH=/nonexistent`, uses relocated
real Claude/Codex artifacts and an unrelated synthetic product CWD with spaces,
then verifies repeated reuse and real materialize/validate helpers. It also
checks plugin/project preservation, inherited pip destination isolation and
rejection/preservation of a changed acquired standard-library file.

A development Python runs the harness and coding suite. That interpreter is
unavailable to the shell Setup via PATH. This is a real missing-PATH-Python
execution path on the observed macOS host, not proof of an erased machine,
native marketplace discovery, authenticated agent interaction or human consent.

## Acceptance mapping and remaining integration

| WWA-04 criterion | Implementation verdict | Acceptance boundary |
|---|---|---|
| Missing Python/Node → consented Setup → actual helpers | Implemented | Native ARM64 shell/acquisition smoke is reachable here; provider-agent interaction remains external. |
| Existing Python only when sufficient; missing provisioning components controlled | Implemented | macOS deliberately uses complete pinned CPython regardless of system Python, so absent/old Python and missing system venv/ensurepip need no manual installation. |
| No system changes, activation or committed binaries | Implemented | Private-cache subprocesses only; relocated smoke checks plugin/project preservation. |
| Pinned verified artifacts; download/checksum/write errors never ready | Implemented | Pre-execution SHA check, staged download, bounded curl, ownership/write checks, rollback and rejection tests; real organizational firewall/policy acceptance remains external. |
| Trusted repeat Setup, spaces and unrelated CWD; each advertised CPU smoked | Implemented, matrix bounded by evidence | ARM64 smoke is recorded here; Intel artifact acquisition is implemented but native Intel acceptance is pending and Intel support is not advertised. |

WWA-05 adds Linux acquisition to the shared POSIX shell; WWA-06 owns Windows acquisition. WWA-07 now supplies [verified helper invocation](../../references/helpers.md)
through the same OS entrypoint and dispatcher, without system Python. WWA-08/09 own native
update/uninstall compatibility and standalone migration. Earlier Setup receipts
without the new runtime tree fingerprint are rejected and preserved for
inspection rather than silently trusted; compatibility/repair policy remains
WWA-08. Full native install → agent consent → workflow → update/uninstall and
non-dev usability remain integrated external acceptance, not a code blocker.

WWA-05 renames the internal shell to `scripts/kkdesign_setup_posix.sh` and the
maintainer smoke to `scripts/smoke_posix_setup.py`; macOS pins, cache locations
and inventory format are retained so existing macOS bootstrap caches remain reusable.
