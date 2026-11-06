# Package the kit

Run Python 3.9+ with the installed skill's absolute script path:

```sh
python "/absolute/path/to/kkdesign-kit/scripts/kkdesign_install.py" package --output "/chosen/output/kkdesign-kit.zip"
```

Ask for an output location only when none can be inferred from the user's request.
Output must be outside the installed skill. Existing files are never overwritten.
The archive contains a single `kkdesign-kit/` directory and `bundle.json` with
SHA-256 for every payload file. The same script works from the source checkout or
an extracted bundle, without Hoangsa, Impeccable or Python packages. Unzip before
installing. No project data, credentials or local configuration is collected.
