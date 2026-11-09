# Package the kit

For the new Claude Code marketplace artifact, use the maintainer builder and
native review flow in [docs/claude-marketplace.md](../docs/claude-marketplace.md).
It reuses this package's canonical allowlisted resources. The portable package
and release workflow below are legacy and are not a plugin installation or
Setup fallback. Building an artifact does not authorize release/publication.

Run Python 3.9+ with the installed skill's absolute path:

```sh
python3 -I -B "/absolute/path/to/kkdesign-kit/scripts/kkdesign_install.py" package --output "/chosen/output/kkdesign-kit-0.5.0a1.zip"
```

Ask for an output location only when none can be inferred from the user's request.
Output must be outside the installed skill. Existing files are never overwritten.
The archive contains a single `kkdesign-kit/` directory and `bundle.json` with
SHA-256 for every payload file. The same script works from the source checkout or
an extracted bundle, without Hoangsa, Impeccable or Python packages. Unzip before
installing. No project data, credentials or local configuration is collected.

## Verify after clean extraction

Extract into an empty directory, then use the EXTRACTED script, not the checkout:

```sh
python3 -I -B "/clean/extraction/kkdesign-kit/scripts/kkdesign_install.py" verify --source "/clean/extraction/kkdesign-kit"
```

`manifest.json` declares the version, command capabilities and required resources.
`bundle.json` pins every payload file by SHA-256. Verification checks exact file
inventory, required paths and matching versions without repairing the bundle.
Run from an unrelated working directory to check relocation. A modified, missing
or additional file fails integrity. These checks do not establish publisher identity.
For a transport checksum, compute SHA-256 of the ZIP itself; the `package` result
prints that digest. Two packages from identical input bytes are byte-identical.

## Release workflow

The repository's manually dispatched `Approved portable release` workflow runs
only from `main` after PR review/merge. It builds the `0.5.0a1` ZIP and transport
`.sha256` outside the source, uploads temporary workflow artifacts, and exercises
actual loopback HTTP downloads on Ubuntu and macOS for both harnesses/scopes,
fresh-shell helpers, update, rollback and uninstall. The final job uses the
`release-approval` environment: configure required reviewers in repository
settings before dispatch. It creates a new **draft** release for `v0.5.0a1` and
refuses an existing release; it never overwrites assets. Draft creation is not
publication. This PR does not authorize dispatch, tag creation or publication.
Do not document a public `curl` URL as ready until an authorized owner publishes
the release and the exact pinned public command has been smoke-tested against it.

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
