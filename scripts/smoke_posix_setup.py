#!/usr/bin/env python3
"""Real consented POSIX acquisition, relocated Setup/reuse and trust rejection.

The harness needs a development Python; the launched Setup has no Python/Node
on PATH and uses only native host tools before verified interpreter execution.
No provider install/authentication or human-consent evidence is implied.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
import build_claude_marketplace as claude
import build_codex_marketplace as codex
import kkdesign_install as kit

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd, env, success=True, events=True):
    proc = subprocess.run([str(arg) for arg in command], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=600)
    if (proc.returncode == 0) != success:
        raise RuntimeError(proc.stdout + proc.stderr)
    return [json.loads(line) for line in proc.stdout.splitlines()] if events else proc.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--incomplete-python', type=Path,
                        help='Linux system interpreter genuinely missing venv or ensurepip')
    args = parser.parse_args()
    if sys.platform != 'darwin' and not sys.platform.startswith('linux'):
        raise SystemExit('This smoke requires native macOS or GNU/Linux')
    if args.incomplete_python:
        if not sys.platform.startswith('linux') or not args.incomplete_python.is_absolute():
            raise SystemExit('--incomplete-python requires an absolute Linux interpreter path')
        probe = subprocess.run([str(args.incomplete_python), '-I', '-c', 'import venv, ensurepip'],
                               capture_output=True, text=True, timeout=20)
        if probe.returncode == 0 or 'ModuleNotFoundError' not in probe.stderr:
            raise SystemExit('The supplied interpreter must genuinely lack venv or ensurepip')
    with tempfile.TemporaryDirectory(prefix='POSIX missing Python spaces ') as temp:
        base = Path(temp).resolve()
        home, product = base / 'home', base / 'unrelated product'
        home.mkdir(mode=0o700)
        product.mkdir()
        (product / 'keep.txt').write_text('synthetic project')
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PATH='/nonexistent',
                   PYTHONDONTWRITEBYTECODE='1', PIP_TARGET=str(product / 'forbidden target'),
                   PIP_PREFIX=str(product / 'forbidden prefix'), PIP_USER='true')
        if args.incomplete_python:
            path_bin = base / 'incomplete system bin'
            path_bin.mkdir()
            (path_bin / 'python3').symlink_to(args.incomplete_python)
            env['PATH'] = str(path_bin)
        outcomes = []
        for builder, relative in ((claude, 'kkdesign-marketplace/plugins/kkdesign-kit'),
                                  (codex, 'kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit')):
            archive = base / (builder.__name__ + '.zip')
            builder.package(ROOT, archive)
            extracted = base / (builder.__name__ + ' cache')
            with zipfile.ZipFile(archive) as stream:
                stream.extractall(extracted)
            package = extracted / relative
            before = kit.hashes(extracted)
            command = ['/bin/sh', package / 'scripts/kkdesign_setup_posix.sh', '--package-root', package]
            events = run(command, product, env)
            if not outcomes:
                assert events[-1]['status'] == 'consent-required', events
                assert not (home / '.kkdesign-kit').exists()
                events = run([*command, '--consent'], product, env)
                assert events[-1]['result']['reused'] is False, events
            else:
                assert events[-1]['result']['reused'] is True, events
            result = events[-1]['result']
            assert result['status'] == 'ready', events
            again = run(command, product, env)
            assert again[-1]['result']['reused'] is True, again
            assert all(item['phase'] != 'downloading-python' for item in again)
            output = base / (builder.__name__ + ' example')
            # This is the existing dispatcher with the returned absolute managed
            # interpreter. General Python-free helper startup is WWA-07.
            launcher = [result['python'], '-I', '-B', package / 'scripts/kkdesign_run.py']
            run([*launcher, 'materialize_example', '--output', output], product, env, events=False)
            validation = json.loads(run([*launcher, 'kkdesign_core', 'validate', '--design', output / 'design'],
                                        product, env, events=False))
            assert (validation['status'], validation['errors'], validation['warnings']) == ('pass', [], [])
            assert kit.hashes(extracted) == before
            assert [p.name for p in product.iterdir()] == ['keep.txt']
            outcomes.append({'adapter': builder.__name__, 'acquiredPython': '3.12.12',
                             'runtime': 'ready', 'reuse': True, 'helpers': 'pass',
                             'pluginAndProjectPreserved': True, 'externalTools': 'unverified'})
        # Corrupt a library, keeping interpreter and artifact bytes intact:
        # bootstrap must reject it before starting acquired Python.
        acquired = next((home / '.kkdesign-kit/bootstrap').glob('cpython-*'))
        library = acquired / 'python/lib/python3.12/site.py'
        library.write_bytes(library.read_bytes() + b'\n# synthetic tamper\n')
        rejected = run(command, product, env, success=False)
        assert rejected[-1]['runtime'] == 'error', rejected
        assert library.read_bytes().endswith(b'# synthetic tamper\n')
        assert not (acquired.parent / 'lock').exists()
        print(json.dumps({'status': 'pass', 'system': os.uname().sysname,
                          'architecture': os.uname().machine, 'pathPythonAndNode': 'Python lacks venv/ensurepip; Node unavailable' if args.incomplete_python else 'unavailable',
                          'results': outcomes, 'tamperedLibrary': 'rejected and preserved',
                          'scope': 'Native host shell/acquisition/helper smoke; provider interaction, human consent and other CPUs remain separate.'}, indent=2))


if __name__ == '__main__':
    main()
