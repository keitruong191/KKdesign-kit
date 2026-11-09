#!/usr/bin/env python3
"""Maintainer smoke: actual agent Setup contract in relocated marketplace packages.

Creates temporary user caches and uses real venv/pip network provisioning after
explicit test consent. Does not install/authenticate a provider or prove native
menu interaction, missing-Python bootstrap, live tools or human approval.
"""
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


def run(command, cwd, env):
    proc = subprocess.run([str(arg) for arg in command], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=240)
    if proc.returncode:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def main():
    with tempfile.TemporaryDirectory(prefix='agent Setup relocated spaces ') as temp:
        base = Path(temp).resolve()
        home, product = base / 'home', base / 'unrelated product'
        home.mkdir()
        product.mkdir()
        sentinel = product / 'keep.txt'
        sentinel.write_text('synthetic project data')
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PYTHONDONTWRITEBYTECODE='1')
        for key in ('PYTHONHOME', 'PYTHONPATH', 'VIRTUAL_ENV'):
            env.pop(key, None)
        # Hostile inherited pip destinations must never escape the cache.
        env.update(PIP_TARGET=str(product / 'forbidden pip target'), PIP_USER='true',
                   PIP_PREFIX=str(product / 'forbidden pip prefix'))
        outcomes = []
        for builder, relative in ((claude, 'kkdesign-marketplace/plugins/kkdesign-kit'),
                                  (codex, 'kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit')):
            output = base / (builder.__name__ + '.zip')
            builder.package(ROOT, output)
            cache = base / (builder.__name__ + ' cache')
            with zipfile.ZipFile(output) as archive:
                archive.extractall(cache)
            package = cache / relative
            before = kit.hashes(cache)
            command = [sys.executable, '-I', '-B', package / 'scripts/kkdesign_setup.py',
                       '--package-root', package]
            events = [json.loads(line) for line in run(command, product, env).splitlines()]
            if not outcomes:
                assert events[-1]['phase'] == 'consent-required', events
                assert not (home / '.kkdesign-kit').exists()
                events = [json.loads(line) for line in run([*command, '--consent'], product, env).splitlines()]
                assert events[-1]['result']['reused'] is False, events
            else:
                assert events[-1]['result']['reused'] is True, events
            assert events[-1]['result']['runtime'] == 'ready', events
            again = [json.loads(line) for line in run(command, product, env).splitlines()]
            assert again[-1]['result']['reused'] is True, again
            assert all(event['phase'] != 'consent-required' for event in again)
            example = base / (builder.__name__ + ' example')
            launcher = [sys.executable, '-I', '-B', package / 'scripts/kkdesign_run.py', '--package-root', package]
            run([*launcher, 'materialize_example', '--output', example], product, env)
            validation = json.loads(run([*launcher, 'kkdesign_core', 'validate', '--design', example / 'design'], product, env))
            assert (validation['status'], validation['errors'], validation['warnings']) == ('pass', [], []), validation
            assert kit.hashes(cache) == before
            assert sentinel.read_text() == 'synthetic project data'
            assert list(product.iterdir()) == [sentinel]
            outcomes.append({'adapter': builder.__name__, 'runtime': 'ready', 'reuse': 'verified',
                             'relocatedHelpers': 'pass', 'pluginAndProjectPreserved': True,
                             'externalTools': 'unverified'})
        print(json.dumps({'status': 'pass', 'results': outcomes,
                          'scope': 'Existing-Python Setup and real venv/pip/helper execution only; native provider and missing-Python acceptance pending.'}, indent=2))


if __name__ == '__main__':
    main()
