#!/usr/bin/env python3
"""Run bundled helpers with the recorded external runtime; no shell activation."""
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
import kkdesign_install as installer

HELPERS = ('kkdesign_core', 'kkdesign_project', 'kkdesign_sources', 'kkdesign_task',
           'kkdesign_review', 'kkdesign_learn', 'kkdesign_install', 'materialize_example')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in HELPERS:
        sys.stderr.write('Usage: python3 kkdesign_run.py {' + ','.join(HELPERS) + '} [arguments]\n')
        return 2
    root = Path(__file__).resolve().parent.parent
    python = Path(sys.executable)
    adapter = root.parent.parent.name
    if root.parent.name == 'skills' and adapter in installer.ADAPTERS.values():
        base = root.parents[2]
        harness = next(key for key, value in installer.ADAPTERS.items() if value == adapter)
        state = base / '.kkdesign-kit/installations' / harness
        installer.no_links(state / 'state.json')
        record = installer.read_json(state / 'state.json')
        if record.get('identifier') != installer.IDENTIFIER or record.get('target') != str(root):
            raise ValueError('Installation record does not own this skill')
        expected = installer.runtime_path(state, (root / 'requirements.txt').read_bytes())
        if record.get('runtime') != str(expected):
            raise ValueError('No matching managed runtime; rerun install/update with --runtime')
        installer.no_links(expected / 'runtime.json')
        installer.no_links(expected)
        marker = installer.read_json(expected / 'runtime.json')
        if marker != {'identifier': installer.IDENTIFIER, 'requirementsSha256': expected.name}:
            raise ValueError('Runtime ownership mismatch; inspect the installation')
        python = installer.runtime_python(expected)
        if not python.is_file():
            raise ValueError('Managed runtime is missing; rerun install with --runtime')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    return subprocess.call([str(python), '-B', str(root / 'scripts' / (sys.argv[1] + '.py')),
                            *sys.argv[2:]], env=env)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write(str(exc) + '\n')
        sys.exit(1)
