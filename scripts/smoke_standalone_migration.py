#!/usr/bin/env python3
"""Opt-in real POSIX Setup/migration smoke in a disposable synthetic home.

Authorizes pinned runtime acquisition for this probe only. No provider account,
credentials, native registration, model interaction or human approval is inferred.
"""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
import build_claude_marketplace as claude
import build_codex_marketplace as codex
import kkdesign_install as kit
import kkdesign_setup as setup

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != 'darwin' and not sys.platform.startswith('linux'):
        raise ValueError('This smoke needs a native POSIX executor; Windows acceptance is separate')
    with tempfile.TemporaryDirectory(prefix='standalone migration spaces ') as temp:
        base = Path(temp).resolve()
        home, project, cwd = base / 'home', base / 'ancestor/product', base / 'unrelated cwd'
        home.mkdir(mode=0o700)
        project.mkdir(parents=True)
        cwd.mkdir()
        for name in ('DESIGN.md', 'design/LESSON.md', 'design/profiles/demo.json', 'design/tasks/history/task.json'):
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic retained data')
        env = {key: value for key, value in os.environ.items()
               if not any(word in key.upper() for word in ('TOKEN', 'API_KEY', 'CODEX', 'OPENAI', 'CLAUDE', 'ANTHROPIC', 'AWS_', 'GOOGLE_', 'AZURE_', 'VERTEX_'))}
        env.update(HOME=str(home), USERPROFILE=str(home), PATH='/nonexistent')
        results = []
        for builder, relative in ((claude, 'kkdesign-marketplace/plugins/kkdesign-kit'),
                                  (codex, 'kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit')):
            archive = base / (builder.__name__ + '.zip')
            builder.package(ROOT, archive)
            cache = base / builder.__name__
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(cache)
            package = cache / relative
            plugin_before = kit.hashes(cache)
            copies = []
            for harness, scope, destination in (('codex', 'user', project),
                                                ('claude-code', 'project', project.parent)):
                # Historical installs are synthetic fixtures, never a fallback.
                kit.lifecycle('install', harness, scope, home, destination, ROOT)
                copies.append(kit.locations(harness, scope, home, destination)[0])
            before = {str(path): kit.hashes(path) for path in copies}
            command = ['/bin/sh', package / 'scripts/kkdesign_setup_posix.sh', '--package-root', package,
                       '--project-root', project]
            def run(arguments):
                proc = subprocess.run([str(arg) for arg in arguments], cwd=cwd, env=env,
                                      capture_output=True, text=True, timeout=600)
                if proc.returncode:
                    raise RuntimeError(proc.stdout + proc.stderr)
                events = [json.loads(line) for line in proc.stdout.splitlines()]
                return events[-1].get('result', events[-1])
            # Explicit synthetic acquisition consent is not migration consent.
            declined = run([*command, '--consent'])
            assert declined['status'] == 'migration-consent-required', declined
            assert all(kit.hashes(path) == before[str(path)] for path in copies)
            selected = [arg for path in copies for arg in ('--migrate', path)]
            migrated = run([*command, '--consent', *selected])
            assert migrated['status'] == 'ready' and migrated['migration']['status'] == 'migrated', migrated
            assert all(not path.exists() for path in copies)
            retained = {kit.read_json(Path(path) / 'state.json')['target']: Path(path)
                        for path in migrated['migration']['retained']}
            assert all(kit.hashes(retained[str(path)] / 'skill') == before[str(path)] for path in copies)
            runtime = Path(migrated['runtimePath'])
            runtime_before = setup.fingerprint(runtime, (package / 'requirements.txt').read_bytes())
            # A modified project-local copy blocks migration and stays intact.
            kit.lifecycle('install', 'codex', 'project', home, project, ROOT)
            conflict = kit.locations('codex', 'project', home, project)[0]
            (conflict / 'SKILL.md').write_text('synthetic owner modification')
            old = kit.hashes(conflict)
            blocked = run([*command, '--consent', '--migrate', conflict])
            assert blocked['status'] == 'migration-conflict', blocked
            assert kit.hashes(conflict) == old
            assert setup.fingerprint(runtime, (package / 'requirements.txt').read_bytes()) == runtime_before
            assert kit.hashes(cache) == plugin_before
            for name in ('DESIGN.md', 'design/LESSON.md', 'design/profiles/demo.json', 'design/tasks/history/task.json'):
                assert (project / name).read_text() == 'synthetic retained data'
            # Resolve this synthetic fixture explicitly, outside product behavior.
            shutil.rmtree(conflict)
            (project / '.kkdesign-kit/installations/codex/state.json').unlink()
            results.append({'adapter': builder.__name__, 'cleanMigration': 'pass',
                            'conflictPreserved': 'pass', 'sharedRuntimePreserved': 'pass',
                            'pluginAndProjectPreserved': 'pass', 'runtimeReused': migrated['reused']})
        print(json.dumps({'status': 'pass', 'results': results,
                          'scope': 'Actual POSIX acquisition, relocated packaged Setup, verified helpers and migration in isolated synthetic home; native registration, agent consent and usability are separate.'}, indent=2))


if __name__ == '__main__':
    main()
