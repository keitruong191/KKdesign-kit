#!/usr/bin/env python3
"""Self-contained, conservative KKdesign-kit packaging and installation (Python 3.9+)."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
IDENTIFIER = 'kkdesign-kit'
ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = {'codex': '.agents', 'claude-code': '.claude'}
SINGLE_FILES = ('SKILL.md', 'manifest.json', 'requirements.txt', 'LICENSE')
DIRECTORIES = ('agents', 'references', 'docs', 'schemas', 'templates', 'examples')
SCRIPTS = ('kkdesign_install.py', 'kkdesign_core.py', 'kkdesign_project.py',
           'kkdesign_sources.py', 'figma_capture.js', 'materialize_example.py')


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
    else:
        if (state / 'previous').exists() or (state / 'previous-state.json').exists():
            raise ValueError('Orphan rollback state; inspect interrupted installation before recovery')
        result['status'] = 'conflict' if target.exists() else 'absent'
    return result


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


def lifecycle(action, harness, scope, home, project, source):
    target, state = locations(harness, scope, home, project)
    if action == 'inspect':
        return inspect(harness, scope, home, project)
    with locked(state):
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
            return dict(current, status='uninstalled', rollbackAvailable=False)
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
        if current['status'] == 'managed' and new_hashes == read_json(state / 'state.json')['files']:
            return dict(current, status='unchanged')
        if action == 'install' and current['status'] == 'managed':
            raise ValueError('Different version already installed; use update explicitly')
        new_record = {'identifier': IDENTIFIER, 'version': version, 'target': str(target), 'files': new_hashes}
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='staging-', dir=state) as temp:
            staging = Path(temp) / 'skill'
            staging.mkdir()
            for name, data in files.items():
                dest = staging / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            # Snapshot before mutation. Stage the ledger, then restore on any caught failure.
            old_record = read_json(state / 'state.json') if current['status'] == 'managed' else None
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
                if previous.exists():
                    previous.rename(old_backup)
                if old_record:
                    moved.rename(previous)
                    write_json(Path(temp) / 'previous-state.json', old_record)
                    os.replace(Path(temp) / 'previous-state.json', backup_record)
                os.replace(new_ledger, ledger)
            except OSError:
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
    parser.add_argument('action', choices=('package', 'install', 'inspect', 'update', 'rollback', 'uninstall'))
    parser.add_argument('--harness', choices=ADAPTERS)
    parser.add_argument('--scope', choices=('user', 'project'))
    parser.add_argument('--home', type=Path, default=Path.home(), help='Override user root (isolated testing)')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--source', type=Path, default=ROOT, help='Checkout or extracted skill directory')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'package':
            if not args.output:
                parser.error('package requires --output')
            result = package(canonical(args.source), canonical(args.output))
        else:
            if not args.harness or not args.scope:
                parser.error('lifecycle actions require --harness and --scope')
            result = lifecycle(args.action, args.harness, args.scope, canonical(args.home),
                               canonical(args.project), canonical(args.source))
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
