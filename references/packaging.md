# Package the kit

For provider marketplace artifacts, use the maintainer builders and native
review flows for [Claude Code](../docs/claude-marketplace.md) and
[Codex](../docs/codex-marketplace.md).
It reuses this package's canonical allowlisted resources. The portable package
and release workflow below are legacy and are not a plugin installation or
Setup fallback. Building an artifact does not authorize release/publication.

For the active installed-plugin package command, use the trusted runtime prepared
by Setup through [helper invocation](helpers.md). `SKILL_DIR` is the host-supplied
absolute directory containing the activated SKILL.md. On macOS/GNU Linux:

```sh
/bin/sh "$SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$SKILL_DIR" --helper kkdesign_install package --output "$OUTPUT_ZIP"
```

On native Windows, run in the authorized Windows PowerShell 5.1 host using the
same helper contract:

```powershell
& "$SKILL_DIR\scripts\kkdesign_setup_windows.ps1" -PackageRoot "$SKILL_DIR" -Helper kkdesign_install -HelperArguments @('package', '--output', "$OUTPUT_ZIP")
```

Ask for an output location only when none can be inferred from the user's request.
Output must be outside the installed skill. Existing files are never overwritten.
The archive contains a single `kkdesign-kit/` directory and `bundle.json` with
SHA-256 for every payload file. Installed-plugin helper invocation requires the verified private runtime, with
no system Python, activation or special CWD. Creating a portable artifact does
not install a plugin or authorize a standalone distribution fallback. No project data, credentials or local configuration is collected.

## Verify after clean extraction

Extract into an empty directory and set `EXTRACTED_SKILL_DIR` to its absolute
`kkdesign-kit/` directory. Invoke the EXTRACTED entrypoint and dispatcher with
that explicit root, from an unrelated working directory:

```sh
/bin/sh "$EXTRACTED_SKILL_DIR/scripts/kkdesign_setup_posix.sh" --package-root "$EXTRACTED_SKILL_DIR" --helper kkdesign_install verify --source "$EXTRACTED_SKILL_DIR"
```

Native Windows equivalent (same authorized host and argument-array rules):

```powershell
& "$EXTRACTED_SKILL_DIR\scripts\kkdesign_setup_windows.ps1" -PackageRoot "$EXTRACTED_SKILL_DIR" -Helper kkdesign_install -HelperArguments @('verify', '--source', "$EXTRACTED_SKILL_DIR")
```

Both forms verify the existing private caches and never provision. Missing or
untrusted runtime state requires explicit Setup/inspection, not PATH Python or
a project executable. See [helper invocation](helpers.md) for error handling.

`manifest.json` declares the version, command capabilities and required resources.
`bundle.json` pins every payload file by SHA-256. Verification checks exact file
inventory, required paths and matching versions without repairing the bundle.
Run from an unrelated working directory to check relocation. A modified, missing
or additional file fails integrity. These checks do not establish publisher identity.
For a transport checksum, compute SHA-256 of the ZIP itself; the `package` result
prints that digest. Two packages from identical input bytes are byte-identical.

## Historical source-only maintainer commands

These Python 3.9+ commands are retained for source-checkout or historical portable
bundle maintenance. They are not the installed-plugin package/verify route and
must not be used as a plugin Setup or distribution fallback:

```sh
python3 -I -B scripts/kkdesign_install.py package --output "$OUTPUT_ZIP"
python3 -I -B "$EXTRACTED_SKILL_DIR/scripts/kkdesign_install.py" verify --source "$EXTRACTED_SKILL_DIR"
```

These packaging/verification operations use the standard library. They do not
establish runtime readiness or permission to install or publish.

## Historical release workflow

The repository's manually dispatched `Approved portable release` workflow runs
only from `main` after PR review/merge. It builds the `0.5.0a1` ZIP and transport
`.sha256` outside the source, uploads temporary workflow artifacts, and exercises
actual loopback HTTP downloads on Ubuntu and macOS for both harnesses/scopes,
fresh-shell helpers, update, rollback and uninstall. The final job uses the
`release-approval` environment: configure required reviewers in repository
settings before dispatch. It creates a new **draft** release for `v0.5.0a1` and
refuses an existing release; it never overwrites assets. Draft creation is not
publication. This PR does not authorize dispatch, tag creation or publication.
This historical workflow is not the marketplace release path. Do not dispatch it
or publish a curl/standalone installation channel for marketplace onboarding.
Owner-approved marketplace publication and exact native install verification
remain separate pending work in the [handoff](../docs/verification/onboarding.md).

For the same real-download check locally, run
`python3 -B scripts/smoke_bootstrap.py` from the source checkout. It uses only
synthetic temporary projects/homes and actual pip provisioning. Its loopback
transport override is `KKDESIGN_BOOTSTRAP_TEST_BASE_URL`; this is maintainer
verification, not evidence of public release availability or native discovery.

## Public skill versus private project kit

This command packages only the reusable skill's allowlisted scripts and public
resource directories. It never walks the selected project, its `design/`, source
captures, credentials or surrounding workspace. Private project kits and task
evidence remain in their owner-selected project. Do not place private material in
the public skill's `docs/`, `examples/` or other resource directories. A project
archive/export needs its own explicit content scope and distribution authorization;
`package` does not grant either and never uploads an artifact.
