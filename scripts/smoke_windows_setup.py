#!/usr/bin/env python3
"""Real consented Windows acquisition, relocated Setup/reuse and trust rejection.

The harness needs a development Python; the launched Setup has no Python/Node
on PATH and uses only Windows PowerShell before verified interpreter execution.
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
import hashlib
import tarfile
import urllib.request
import platform

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


WINDOWS_PINS = {
    'x86_64': '2d670beb3b930d30e3a13cc909923a001dbdfcb5537692d5da40b6b41643ce1c',
    'aarch64': 'd708734581e8cb03f4cf95f39f17ea331bc4761dfdad99b6b738a245444c9c54',
}


def inspect_artifacts():
    results = []
    with tempfile.TemporaryDirectory(prefix='Windows artifact inspection ') as temp:
        for target, digest in WINDOWS_PINS.items():
            name = 'cpython-3.12.12%2B20251014-' + target + '-pc-windows-msvc-install_only.tar.gz'
            url = 'https://github.com/astral-sh/python-build-standalone/releases/download/20251014/' + name
            path = Path(temp) / (target + '.tar.gz')
            with urllib.request.urlopen(url, timeout=240) as response, path.open('xb') as stream:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    stream.write(chunk)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Windows artifact integrity failed: ' + target)
            with tarfile.open(path) as archive:
                names = set(archive.getnames())
                for required in ('python/python.exe', 'python/Lib/venv/__init__.py',
                                 'python/Lib/ensurepip/__init__.py', 'python/Lib/site.py'):
                    if required not in names:
                        raise ValueError('Incomplete acquired archive: ' + required)
                executable = archive.extractfile('python/python.exe').read(2)
                if executable != b'MZ':
                    raise ValueError('Expected a Windows executable')
            results.append({'target': target, 'sha256': digest, 'archive': 'verified',
                            'venvAndEnsurepip': 'present'})
    print(json.dumps({'status': 'pass', 'results': results,
                      'scope': 'Downloaded Windows archive integrity and contents only; no native execution, provider or consent evidence.'}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect-artifacts', action='store_true',
                        help='Verify both pinned Windows archives without executing them; not native acceptance')
    args = parser.parse_args()
    if args.inspect_artifacts:
        return inspect_artifacts()
    if os.name != 'nt':
        raise SystemExit('Native acquisition smoke requires Windows; use --inspect-artifacts only for portable integrity inspection')
    shell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    with tempfile.TemporaryDirectory(prefix='Windows missing Python spaces ') as temp:
        base = Path(temp).resolve()
        home, product = base / 'home', base / 'unrelated product'
        # The production helper creates the isolated profile with a private ACL.
        script = ROOT / 'scripts/kkdesign_windows_security.ps1'
        quoted_script = str(script).replace("'", "''")
        quoted_home = str(home).replace("'", "''")
        run([shell, '-NoProfile', '-NonInteractive', '-Command',
             ". '" + quoted_script + "'; New-PrivateDirectory '" + quoted_home + "'"],
            base, os.environ, events=False)
        product.mkdir()
        (product / 'keep.txt').write_text('synthetic project')
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PATH=str(base / 'no Python or Node'),
                   PYTHONDONTWRITEBYTECODE='1', PIP_TARGET=str(product / 'forbidden target'),
                   PIP_PREFIX=str(product / 'forbidden prefix'), PIP_USER='true')
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
            command = [shell, '-NoProfile', '-NonInteractive', '-File',
                       package / 'scripts/kkdesign_setup_windows.ps1', '-PackageRoot', package]
            events = run(command, product, env)
            if not outcomes:
                assert events[-1]['status'] == 'consent-required', events
                assert not (home / '.kkdesign-kit').exists()
                events = run([*command, '-Consent'], product, env)
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
        library = acquired / 'python/Lib/site.py'
        library.write_bytes(library.read_bytes() + b'\n# synthetic tamper\n')
        rejected = run(command, product, env, success=False)
        assert rejected[-1]['runtime'] == 'error', rejected
        assert library.read_bytes().endswith(b'# synthetic tamper\n')
        assert not (acquired.parent / 'setup.lock').exists()
        print(json.dumps({'status': 'pass', 'system': platform.system(),
                          'architecture': platform.machine(), 'pathPythonAndNode': 'unavailable',
                          'results': outcomes, 'tamperedLibrary': 'rejected and preserved',
                          'scope': 'Native PowerShell/acquisition/helper smoke; provider interaction, human consent and other CPUs remain separate.'}, indent=2))


if __name__ == '__main__':
    main()
