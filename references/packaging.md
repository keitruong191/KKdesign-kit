# Package the kit

Run Python 3.9+ with the installed skill's absolute script path:

```sh
python "/absolute/path/to/kkdesign-kit/scripts/kkdesign_install.py" package --output "/chosen/output/kkdesign-kit-0.4.0a1.zip"
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
python "/clean/extraction/kkdesign-kit/scripts/kkdesign_install.py" verify --source "/clean/extraction/kkdesign-kit"
```

`manifest.json` declares the version, command capabilities and required resources.
`bundle.json` pins every payload file by SHA-256. Verification checks exact file
inventory, required paths and matching versions without repairing the bundle.
Run from an unrelated working directory to check relocation. A modified, missing
or additional file fails integrity. These checks do not establish publisher identity.
For a transport checksum, compute SHA-256 of the ZIP itself; the `package` result
prints that digest. Two packages from identical input bytes are byte-identical.

## Public skill versus private project kit

This command packages only the reusable skill's allowlisted scripts and public
resource directories. It never walks the selected project, its `design/`, source
captures, credentials or surrounding workspace. Private project kits and task
evidence remain in their owner-selected project. Do not place private material in
the public skill's `docs/`, `examples/` or other resource directories. A project
archive/export needs its own explicit content scope and distribution authorization;
`package` does not grant either and never uploads an artifact.
