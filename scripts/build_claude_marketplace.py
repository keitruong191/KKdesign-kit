#!/usr/bin/env python3
"""Build a Claude marketplace from the existing canonical public payload, Python 3.9+."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
import kkdesign_install as kit


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')


def package(source, output):
    source = kit.canonical(source)
    kit.no_links(output.absolute())
    output = output.resolve()
    if output.is_relative_to(source):
        raise ValueError('Output must be outside the source/installed skill')
    files, version = kit.payload(source)
    adapter = source / '.claude-plugin/plugin.json'
    catalog_path = source / '.claude-plugin/marketplace.json'
    kit.no_links(adapter)
    kit.no_links(catalog_path)
    plugin = kit.read_json(adapter)
    catalog = kit.read_json(catalog_path)
    entries = catalog.get('plugins', [])
    if (plugin.get('name') != kit.IDENTIFIER or plugin.get('version') != version
            or plugin.get('skills') != ['./'] or len(entries) != 1
            or entries[0].get('name') != kit.IDENTIFIER
            or entries[0].get('version') != version
            or entries[0].get('source') != './'):
        raise ValueError('Claude adapter/catalog must match the canonical identifier, version and root skill')
    files['.claude-plugin/plugin.json'] = adapter.read_bytes()
    files.pop('bundle.json')
    files['bundle.json'] = encoded({
        'identifier': kit.IDENTIFIER, 'version': version,
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}})
    catalog['plugins'][0]['source'] = './plugins/' + kit.IDENTIFIER
    prefix = 'kkdesign-marketplace/'
    archive_files = {prefix + '.claude-plugin/marketplace.json': encoded(catalog)}
    archive_files.update({prefix + 'plugins/' + kit.IDENTIFIER + '/' + name: data
                          for name, data in files.items()})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(archive_files.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
    return {'status': 'packaged', 'version': version, 'output': str(output),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.source, args.output), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
