#!/usr/bin/env python3
"""Maintainer acceptance: real curl/HTTP bootstrap, isolated destinations, real pip.

Uses loopback release transport, not a public release or native harness discovery.
No credentials, user configuration, activation, or existing installation is used.
"""
import argparse
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading

sys.dont_write_bytecode = True
from kkdesign_install import ADAPTERS, ROOT, hashes, package


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def run(command, cwd, env):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Command failed: ' + shlex.join(map(str, command)) + '\n' +
                         result.stdout + result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, help='Existing candidate ZIP/checksum/install.sh directory')
    args = parser.parse_args()
    if os.name == 'nt':
        raise ValueError('POSIX bootstrap smoke requires macOS or Linux')
    with tempfile.TemporaryDirectory(prefix='kkdesign bootstrap smoke ') as temp:
        base = Path(temp).resolve()
        assets = args.assets.resolve() if args.assets else base / 'release assets'
        version = json.loads((ROOT / 'manifest.json').read_text())['version']
        archive = assets / ('kkdesign-kit-' + version + '.zip')
        if args.assets:
            artifact = {'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
        else:
            assets.mkdir()
            artifact = package(ROOT, archive)
            archive.with_suffix('.zip.sha256').write_text(artifact['sha256'] + '  ' + archive.name + '\n')
            shutil.copy2(ROOT / 'install.sh', assets / 'install.sh')
        handler = functools.partial(QuietHandler, directory=str(assets))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        records = []
        try:
            url = 'http://127.0.0.1:' + str(server.server_port)
            for harness, adapter in ADAPTERS.items():
                for scope in ('project', 'user'):
                    case = base / (harness + '-' + scope)
                    home, project, elsewhere = case / 'home spaces', case / 'project spaces', case / 'other cwd'
                    for directory in (home, project, elsewhere):
                        directory.mkdir(parents=True)
                    env = dict(os.environ, HOME=str(home), KKDESIGN_BOOTSTRAP_TEST_BASE_URL=url)
                    for key in ('VIRTUAL_ENV', 'PYTHONHOME', 'PYTHONPATH'):
                        env.pop(key, None)
                    executed = case / 'project-runtime-executed'
                    if harness == 'codex' and scope == 'project':
                        digest = hashlib.sha256((ROOT / 'requirements.txt').read_bytes()).hexdigest()
                        untrusted = project / '.kkdesign-kit/installations/codex/runtimes' / digest
                        fake_python = untrusted / 'bin/python'
                        fake_python.parent.mkdir(parents=True)
                        fake_python.write_text('#!/bin/sh\nprintf executed > ' +
                                               shlex.quote(str(executed)) + '\nexit 23\n')
                        fake_python.chmod(0o755)
                        (untrusted / 'runtime.json').write_text(json.dumps(
                            {'identifier': 'kkdesign-kit', 'requirementsSha256': digest}))
                    # Exact release-shaped pipe. Only transport is loopback, explicitly set above.
                    command = 'curl -fsSL ' + shlex.quote(url + '/install.sh') + ' | sh -s -- --harness ' + harness
                    cwd = project
                    if scope == 'user':
                        command += ' --scope user'
                    elif harness == 'claude-code':
                        command += ' --project ' + shlex.quote(str(project))
                        cwd = elsewhere
                    run(['/bin/sh', '-c', command], cwd, env)
                    target = (home if scope == 'user' else project) / adapter / 'skills/kkdesign-kit'
                    installer = [sys.executable, '-I', '-B', str(target / 'scripts/kkdesign_install.py')]
                    flags = ['--harness', harness, '--scope', scope, '--home', str(home), '--project', str(project)]
                    inspected = json.loads(run(installer + ['inspect', *flags], elsewhere, env))
                    if inspected['status'] != 'managed' or not inspected.get('runtimeReady') or inspected['conflicts']:
                        raise ValueError('Unexpected inspect: ' + json.dumps(inspected))
                    if executed.exists() or Path(inspected['runtime']).parent != home / '.kkdesign-kit/runtimes':
                        raise ValueError('Runtime crossed the trusted user-cache boundary')
                    before = hashes(target)
                    example = case / 'fresh shell example'
                    launcher = str(target / 'scripts/kkdesign_run.py')
                    run(['/bin/sh', '-c', 'exec python3 -B "$@"', 'fresh-shell', launcher,
                         'materialize_example', '--output', str(example)], elsewhere, env)
                    validation = json.loads(run(['/bin/sh', '-c', 'exec python3 -B "$@"', 'fresh-shell', launcher,
                                                 'kkdesign_core', 'validate', '--design', str(example / 'design')], elsewhere, env))
                    if validation['status'] != 'pass' or validation['errors'] or validation['warnings']:
                        raise ValueError('Installed validation failed: ' + json.dumps(validation))
                    run(['/bin/sh', '-c', command], cwd, env)
                    repeated = json.loads(run(installer + ['install', *flags, '--source', str(target), '--runtime'], elsewhere, env))
                    if repeated['status'] != 'unchanged' or hashes(target) != before:
                        raise ValueError('Identical reinstall changed the managed skill')
                    if harness == 'codex' and scope == 'project':
                        import zipfile
                        with zipfile.ZipFile(archive) as bundle:
                            bundle.extractall(case / 'next')
                        source = case / 'next/kkdesign-kit'
                        (source / 'bundle.json').unlink()
                        manifest = json.loads((source / 'manifest.json').read_text())
                        manifest['version'] = '0.5.0a2-smoke'
                        (source / 'manifest.json').write_text(json.dumps(manifest))
                        (source / 'requirements.txt').write_text((source / 'requirements.txt').read_text() + '\n# smoke next runtime\n')
                        refused = subprocess.run(installer + ['install', *flags, '--source', str(source)],
                                                 cwd=elsewhere, env=env, capture_output=True, text=True)
                        if refused.returncode == 0 or 'use update explicitly' not in refused.stderr:
                            raise ValueError('Different version did not require explicit update')
                        updated = json.loads(run(installer + ['update', *flags, '--source', str(source)], elsewhere, env))
                        if updated['status'] != 'updated' or updated['runtime'] == inspected['runtime']:
                            raise ValueError('Update failed to switch runtime contract')
                        restored = json.loads(run(installer + ['rollback', *flags], elsewhere, env))
                        if restored['status'] != 'rolled-back' or restored['runtime'] != inspected['runtime']:
                            raise ValueError('Rollback failed to restore runtime contract')
                        validation = json.loads(run([sys.executable, '-B', launcher, 'kkdesign_core', 'validate',
                                                     '--design', str(example / 'design')], elsewhere, env))
                        if validation['status'] != 'pass':
                            raise ValueError('Helper failed after rollback')
                    removed = json.loads(run(installer + ['uninstall', *flags], elsewhere, env))
                    if removed['status'] != 'uninstalled' or target.exists() or not Path(inspected['runtime']).is_dir():
                        raise ValueError('Uninstall violated skill removal/runtime retention contract')
                    records.append({'harness': harness, 'scope': scope, 'inspect': 'managed',
                                    'validation': 'pass', 'reinstall': 'unchanged', 'uninstall': 'uninstalled',
                                    'runtimeRetained': True, 'runtimeLocation': 'user-private-cache',
                                    'explicitOtherCwd': harness == 'claude-code' and scope == 'project'})
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        print(json.dumps({'platform': platform.platform(), 'python': platform.python_version(),
                          'transport': 'actual curl HTTP loopback; not public release',
                          'artifactSha256': artifact['sha256'], 'cases': records,
                          'updateRollbackRuntimeSwitch': 'pass', 'projectRuntimeNeverExecuted': 'pass',
                          'nativeHarnessDiscovery': 'not checked'}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write(str(exc) + '\n')
        sys.exit(1)
