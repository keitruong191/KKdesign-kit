#!/usr/bin/env python3
"""Self-contained, conservative KKdesign-kit packaging and installation (Python 3.9+)."""
import argparse
from contextlib import contextmanager, ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import zipfile

sys.dont_write_bytecode = True
IDENTIFIER = 'kkdesign-kit'
ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = {'codex': '.agents', 'claude-code': '.claude'}
SINGLE_FILES = ('SKILL.md', 'manifest.json', 'requirements.txt', 'LICENSE')
DIRECTORIES = ('agents', 'references', 'docs', 'schemas', 'templates', 'examples')
SCRIPTS = ('kkdesign_install.py', 'kkdesign_core.py', 'kkdesign_project.py',
           'kkdesign_sources.py', 'figma_capture.js', 'materialize_example.py',
           'kkdesign_task.py', 'kkdesign_review.py', 'kkdesign_learn.py',
           'figma_prototype.js', 'kkdesign_run.py')


def canonical(path):
    no_links(path.absolute())
    return path.resolve()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def no_links(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink conflict: ' + str(part))


def hashes(root):
    no_links(root)
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink conflict: ' + str(path))
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('Non-regular package entry: ' + str(path))
    return result


def payload(source):
    """Allowlisted public resources only; never collect arbitrary project files."""
    no_links(source)
    source = source.resolve()
    if (source / 'bundle.json').exists():
        actual = hashes(source)
        actual.pop('bundle.json', None)
        bundle = read_json(source / 'bundle.json')
        if bundle.get('identifier') != IDENTIFIER or actual != bundle.get('files'):
            raise ValueError('Bundle integrity mismatch')
        names = list(actual)
    else:
        names = list(SINGLE_FILES) + ['scripts/' + name for name in SCRIPTS]
        for directory in DIRECTORIES:
            base = source / directory
            no_links(base)
            for entry in base.rglob('*'):
                no_links(entry)
                if entry.is_file():
                    names.append(entry.relative_to(source).as_posix())
    result = {}
    for name in sorted(names):
        path = source / name
        no_links(path)
        result[name] = path.read_bytes()
    manifest = json.loads(result['manifest.json'])
    if manifest.get('identifier') != IDENTIFIER:
        raise ValueError('Wrong package identifier')
    for name in manifest.get('requiredResources', []):
        if name not in result:
            raise ValueError('Missing required resource: ' + name)
    bundle = {'identifier': IDENTIFIER, 'version': manifest['version'],
              'files': {name: hashlib.sha256(data).hexdigest() for name, data in result.items()}}
    result['bundle.json'] = (json.dumps(bundle, indent=2, sort_keys=True) + '\n').encode()
    return result, manifest['version']


def package(source, output):
    files, version = payload(source)
    no_links(output)
    output = output.resolve()
    source = source.resolve()
    if output.is_relative_to(source):
        raise ValueError('Output must be outside the source/installed skill')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create: do not replace an existing artifact.
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in files.items():
                info = zipfile.ZipInfo(IDENTIFIER + '/' + name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
    return {'status': 'packaged', 'version': version, 'output': str(output),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def verify(source):
    """Check an extracted distribution without repairing or regenerating it."""
    no_links(source)
    if not (source / 'bundle.json').is_file():
        raise ValueError('Verification requires an extracted bundle.json')
    bundle = read_json(source / 'bundle.json')
    manifest = read_json(source / 'manifest.json')
    actual = hashes(source)
    actual.pop('bundle.json', None)
    if (bundle.get('identifier') != IDENTIFIER
            or manifest.get('identifier') != IDENTIFIER
            or bundle.get('version') != manifest.get('version')
            or actual != bundle.get('files')):
        raise ValueError('Bundle integrity or version mismatch')
    required = manifest.get('requiredResources')
    if not isinstance(required, list) or not required:
        raise ValueError('Manifest must declare requiredResources')
    for name in required:
        if name not in actual:
            raise ValueError('Missing required resource: ' + str(name))
    return {'status': 'verified', 'identifier': IDENTIFIER,
            'version': manifest['version'], 'files': len(actual),
            'requiredResources': len(required),
            'scope': 'Extracted resource completeness and SHA-256 integrity; not publisher authenticity or runtime approval.'}


def locations(harness, scope, home, project):
    base = home if scope == 'user' else project
    target = base / ADAPTERS[harness] / 'skills' / IDENTIFIER
    state = base / '.kkdesign-kit' / 'installations' / harness
    for path in (target, state):
        no_links(path)
    return target, state


def conflicts(harness, target, home, project):
    candidates = [home / ADAPTERS[harness] / 'skills' / IDENTIFIER]
    candidates.extend(base / ADAPTERS[harness] / 'skills' / IDENTIFIER
                      for base in (project, *project.parents))
    if harness == 'codex':
        candidates.append(home / '.codex' / 'skills' / IDENTIFIER)
    else:
        candidates.extend(base / '.claude' / 'commands' / (IDENTIFIER + '.md')
                          for base in (home, project, *project.parents))
    return sorted({str(p) for p in candidates if p != target and (p.exists() or p.is_symlink())})


def inspect(harness, scope, home, project):
    target, state = locations(harness, scope, home, project)
    record = state / 'state.json'
    result = {'target': str(target), 'scope': scope, 'harness': harness,
              'conflicts': conflicts(harness, target, home, project)}
    if record.exists():
        no_links(record)
        data = read_json(record)
        if data.get('identifier') != IDENTIFIER or data.get('target') != str(target):
            raise ValueError('Installation record does not match target')
        actual = hashes(target) if target.is_dir() else None
        result.update(status='managed' if actual == data['files'] else 'modified',
                      version=data['version'], rollbackAvailable=(state / 'previous').is_dir())
        if 'runtime' in data:
            expected = runtime_root(home) / data['files']['requirements.txt']
            if data['runtime'] != str(expected):
                raise ValueError('Runtime ownership mismatch')
            no_links(expected)
            result.update(runtime=str(expected), runtimeReady=(
                runtime_python(expected).is_file() and (expected / 'runtime.json').is_file()))
    else:
        if (state / 'previous').exists() or (state / 'previous-state.json').exists():
            raise ValueError('Orphan rollback state; inspect interrupted installation before recovery')
        result['status'] = 'conflict' if target.exists() else 'absent'
    return result


def runtime_root(home):
    """Executable cache belongs to the user, never to a destination repository."""
    return home / '.kkdesign-kit' / 'runtimes'


def runtime_path(home, requirements):
    return runtime_root(home) / hashlib.sha256(requirements).hexdigest()


def runtime_python(runtime):
    return runtime / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def run_runtime(command):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    result = subprocess.run([str(arg) for arg in command], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        raise ValueError('Runtime command failed: ' + str(command[0]) + '\n' +
                         result.stdout + result.stderr)
    return result.stdout


@contextmanager
def prepared_runtime(home, requirements):
    """Build/reuse only a user-private cache; project markers prove no provenance."""
    root = runtime_root(home)
    runtime = runtime_path(home, requirements)
    no_links(runtime)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Different installations can share this cache. Hold its lock through smoke
    # and ledger commit so failed creation cannot remove a runtime another uses.
    with locked(root):
        marker = {'identifier': IDENTIFIER, 'requirementsSha256': runtime.name}
        created = False
        if runtime.exists():
            no_links(runtime / 'runtime.json')
            if not (runtime / 'runtime.json').is_file() or read_json(runtime / 'runtime.json') != marker:
                raise ValueError('Unowned or incomplete runtime; preserve and inspect: ' + str(runtime))
        else:
            runtime.mkdir(mode=0o700)
            created = True
        try:
            if created:
                run_runtime([sys.executable, '-I', '-B', '-m', 'venv', runtime])
                requirement_file = runtime / 'requirements.txt'
                requirement_file.write_bytes(requirements)
                run_runtime([runtime_python(runtime), '-I', '-B', '-m', 'pip',
                             '--disable-pip-version-check', 'install', '-r', requirement_file])
                write_json(runtime / 'runtime.json', marker)
            yield runtime
        except BaseException:
            if created:
                shutil.rmtree(runtime)
            raise


def smoke_runtime(target, runtime, state):
    """Exercise installed resources and dependency-backed validation, not an import echo."""
    with tempfile.TemporaryDirectory(prefix='runtime-smoke-', dir=state) as temp:
        example = Path(temp) / 'example'
        python = runtime_python(runtime)
        run_runtime([python, '-B', target / 'scripts/materialize_example.py',
                     '--output', example])
        result = json.loads(run_runtime([python, '-B', target / 'scripts/kkdesign_core.py',
                                        'validate', '--design', example / 'design']))
        if result.get('status') != 'pass' or result.get('errors') or result.get('warnings'):
            raise ValueError('Installed helper smoke failed: ' + json.dumps(result))


@contextmanager
def locked(state):
    state.mkdir(parents=True, exist_ok=True)
    lock = state / 'lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('Installation busy or interrupted; inspect lock: ' + str(lock))
    try:
        yield
    finally:
        lock.rmdir()


def lifecycle(action, harness, scope, home, project, source, runtime=False):
    target, state = locations(harness, scope, home, project)
    if action == 'inspect':
        return inspect(harness, scope, home, project)
    with locked(state), ExitStack() as resources:
        current = inspect(harness, scope, home, project)
        if current['conflicts'] and action in ('install', 'update', 'rollback'):
            raise ValueError('Other discoverable installation(s); inspect/remove explicitly: ' +
                             ', '.join(current['conflicts']))
        if current['status'] in ('conflict', 'modified'):
            raise ValueError('Refusing to change unmanaged or modified files: ' + str(target))
        if (state / 'previous').exists() != (state / 'previous-state.json').exists():
            raise ValueError('Incomplete rollback state; preserve and inspect it first')
        if (state / 'previous').exists():
            no_links(state / 'previous-state.json')
            previous = read_json(state / 'previous-state.json')
            if hashes(state / 'previous') != previous['files']:
                raise ValueError('Modified rollback backup; preserve and inspect it first')
        if action == 'uninstall':
            if current['status'] == 'absent':
                return dict(current, status='already-absent')
            shutil.rmtree(target)
            if (state / 'previous').exists():
                shutil.rmtree(state / 'previous')
                (state / 'previous-state.json').unlink()
            (state / 'state.json').unlink()
            result = dict(current, status='uninstalled', rollbackAvailable=False, runtimeReady=False)
            if runtime_root(home).exists():
                result['retainedRuntimeRoot'] = str(runtime_root(home))
            return result
        if action in ('update', 'rollback') and current['status'] == 'absent':
            raise ValueError('No managed installation; run install first')
        if action == 'rollback':
            if not (state / 'previous').is_dir():
                raise ValueError('No rollback version available')
            old = read_json(state / 'previous-state.json')
            if hashes(state / 'previous') != old['files']:
                raise ValueError('Modified rollback backup')
            files = {name: (state / 'previous' / name).read_bytes() for name in old['files']}
            version = old['version']
        else:
            files, version = payload(source)
        new_hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
        old_record = read_json(state / 'state.json') if current['status'] == 'managed' else None
        identical = old_record is not None and new_hashes == old_record['files']
        if action == 'install' and old_record and not identical:
            raise ValueError('Different version already installed; use update explicitly')
        environment = None
        if runtime or (old_record and old_record.get('runtime')):
            if scope == 'project' and runtime_root(home).is_relative_to(project):
                raise ValueError('User runtime cache must be outside the destination project; '
                                 'choose another project or --scope user')
            environment = resources.enter_context(prepared_runtime(home, files['requirements.txt']))
        new_record = {'identifier': IDENTIFIER, 'version': version, 'target': str(target), 'files': new_hashes}
        if environment:
            new_record['runtime'] = str(environment)
        if identical:
            if environment:
                smoke_runtime(target, environment, state)
            if new_record != old_record:
                with tempfile.TemporaryDirectory(prefix='ledger-', dir=state) as temp:
                    ledger = Path(temp) / 'state.json'
                    write_json(ledger, new_record)
                    os.replace(ledger, state / 'state.json')
            return dict(inspect(harness, scope, home, project), status='unchanged')
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='staging-', dir=state) as temp:
            staging = Path(temp) / 'skill'
            staging.mkdir()
            for name, data in files.items():
                dest = staging / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            # Snapshot before mutation. Stage the ledger, then restore on any caught failure.
            new_ledger = Path(temp) / 'new-state.json'
            write_json(new_ledger, new_record)
            moved = Path(temp) / 'old'
            old_backup = Path(temp) / 'old-backup'
            backup_record = state / 'previous-state.json'
            old_backup_record = backup_record.read_bytes() if backup_record.exists() else None
            ledger = state / 'state.json'
            old_ledger = ledger.read_bytes() if ledger.exists() else None
            previous = state / 'previous'
            # Keep all displaced trees recoverable until target AND ledgers commit.
            if old_record:
                target.rename(moved)
            try:
                staging.rename(target)
                if environment:
                    smoke_runtime(target, environment, state)
                if previous.exists():
                    previous.rename(old_backup)
                if old_record:
                    moved.rename(previous)
                    write_json(Path(temp) / 'previous-state.json', old_record)
                    os.replace(Path(temp) / 'previous-state.json', backup_record)
                os.replace(new_ledger, ledger)
            except (OSError, ValueError):
                if target.exists():
                    shutil.rmtree(target)
                if old_record:
                    (moved if moved.exists() else previous).rename(target)
                if old_backup.exists():
                    old_backup.rename(previous)
                if old_backup_record is not None:
                    backup_record.write_bytes(old_backup_record)
                elif backup_record.exists():
                    backup_record.unlink()
                if old_ledger is not None:
                    ledger.write_bytes(old_ledger)
                elif ledger.exists():
                    ledger.unlink()
                raise
        return dict(inspect(harness, scope, home, project), status={'install': 'installed', 'update': 'updated', 'rollback': 'rolled-back'}[action])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('package', 'verify', 'install', 'inspect', 'update', 'rollback', 'uninstall'))
    parser.add_argument('--harness', choices=ADAPTERS)
    parser.add_argument('--scope', choices=('user', 'project'))
    parser.add_argument('--home', type=Path, default=Path.home(), help='Override user root (isolated testing)')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--source', type=Path, default=ROOT, help='Checkout or extracted skill directory')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--runtime', action='store_true',
                        help='Provision an external venv and smoke installed helpers (network required)')
    args = parser.parse_args()
    try:
        if args.action == 'package':
            if not args.output:
                parser.error('package requires --output')
            result = package(canonical(args.source), canonical(args.output))
        elif args.action == 'verify':
            result = verify(canonical(args.source))
        else:
            if not args.harness or not args.scope:
                parser.error('lifecycle actions require --harness and --scope')
            result = lifecycle(args.action, args.harness, args.scope, canonical(args.home),
                               canonical(args.project), canonical(args.source), runtime=args.runtime)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
