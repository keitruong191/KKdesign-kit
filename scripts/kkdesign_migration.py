"""Conservative standalone discovery and consented deactivation for native Setup."""
from contextlib import ExitStack
import hashlib
import os
from pathlib import Path
import tempfile

import kkdesign_install as kit


def plugin_identity(package):
    """Require an intact distributed payload and a matching native descriptor."""
    kit.verify(package)
    version = kit.read_json(package / 'manifest.json')['version']
    descriptors = [(package / '.claude-plugin/plugin.json', ['./'])]
    if package.parent.name == 'skills' and package.name == kit.IDENTIFIER:
        descriptors.append((package.parent.parent / '.codex-plugin/plugin.json', './skills/'))
    for path, skills in descriptors:
        kit.no_links(path)
        if path.is_file():
            data = kit.read_json(path)
            if (data.get('name') == kit.IDENTIFIER and data.get('version') == version
                    and data.get('skills') == skills):
                return {'location': str(package), 'version': version, 'descriptor': str(path)}
    raise ValueError('Migration requires the identified native plugin, with a matching descriptor and verified bundle')


def present(path):
    return path.exists() or path.is_symlink()


def discover(home, project, package):
    """Use explicit project ancestry, never process CWD or ledger-supplied paths."""
    home = kit.canonical(home)
    bases = {home: 'user'}
    if project is not None:
        if not project.is_absolute() or not project.is_dir():
            raise ValueError('Project root must be an explicit existing absolute directory')
        project = kit.canonical(project)
        for base in (project, *project.parents):
            if base not in bases:
                bases[base] = 'project' if base == project else 'ancestor'
    results = []
    for base, scope in sorted(bases.items(), key=lambda item: str(item[0])):
        for harness, adapter in kit.ADAPTERS.items():
            state = base / '.kkdesign-kit/installations' / harness
            target = base / adapter / 'skills' / kit.IDENTIFIER
            # The active plugin may itself live in a legacy-shaped directory;
            # never touch provider bytes or accept dual ownership there.
            if target == package and not present(state / 'state.json'):
                continue
            if present(target) or present(state / 'state.json'):
                results.append(classify(target, state, harness, scope, home, package))
        for target, harness in ((base / '.codex/skills' / kit.IDENTIFIER, 'codex'),
                                (base / '.claude/commands' / (kit.IDENTIFIER + '.md'), 'claude-code')):
            if present(target):
                results.append({'location': str(target), 'harness': harness, 'scope': scope,
                                'ownership': 'unmanaged', 'version': None,
                                'reason': 'Legacy location has no supported managed ownership ledger'})
    return results


def classify(target, state, harness, scope, home, package, locked=False):
    result = {'location': str(target), 'state': str(state), 'harness': harness,
              'scope': scope, 'version': None, 'ownership': 'unknown'}
    try:
        for path in (target, state, state / 'state.json'):
            kit.no_links(path)
        if (target == package or package.is_relative_to(target)
                or target.is_relative_to(package) or state.is_relative_to(package)):
            raise ValueError('Native plugin bytes overlap standalone ownership; preserve and inspect')
        if not (state / 'state.json').is_file():
            result.update(ownership='unmanaged', reason='No supported ownership ledger')
            return result
        data = kit.read_json(state / 'state.json')
        if (not isinstance(data, dict) or data.get('identifier') != kit.IDENTIFIER
                or data.get('target') != str(target)
                or not isinstance(data.get('version'), str)
                or not isinstance(data.get('files'), dict)
                or not data['files']
                or set(data) - {'identifier', 'target', 'version', 'files', 'runtime'}):
            raise ValueError('Ownership record does not match this supported managed target')
        result['version'] = data['version']
        result['ledgerSha256'] = hashlib.sha256((state / 'state.json').read_bytes()).hexdigest()
        if 'runtime' in data and data['runtime'] != str(kit.runtime_root(home) / data['files']['requirements.txt']):
            raise ValueError('Unexpected runtime ownership record; runtime is preserved')
        if present(state / 'lock') and not locked:
            raise ValueError('Standalone installation is busy or interrupted')
        # Never deactivate a provider-owned plugin misidentified as standalone.
        if any(present(target / name) for name in ('.claude-plugin', '.codex-plugin', 'plugin.json')):
            raise ValueError('Provider descriptor at standalone location; ownership requires inspection')
        if not target.is_dir() or kit.hashes(target) != data['files']:
            result.update(ownership='modified', reason='Installed bytes differ from the managed inventory')
            return result
        for path in (state.parent.parent, state.parent, state, state / 'state.json',
                     target.parent.parent, target.parent, target, *target.rglob('*')):
            info = path.lstat()
            if ((hasattr(os, 'getuid') and info.st_uid != os.getuid())
                    or (os.name != 'nt' and info.st_mode & 0o022)):
                raise ValueError('Unsafe ownership or writable installation metadata/files')
        # These historical backups are not active and are never deleted.
        result.update(ownership='managed', reason='Exact supported ownership record and intact file inventory')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.update(ownership='unknown', reason=str(exc))
    return result


def deactivate(copies, home, project, package, secure=lambda path, base: None):
    """Retain verified copies outside discovery paths; restore on caught failure.

    Caller must identify the plugin, verify helpers and obtain specific consent.
    Lock every historical owner and recheck the entire conflict set before moves.
    No runtime, previous backup, project data or provider bytes are deleted.
    """
    with ExitStack() as stack:
        for item in copies:
            state = Path(item['state'])
            secure(state, state.parents[2])
            secure(Path(item['location']), state.parents[2])
            stack.enter_context(kit.locked(state))
        # Our own locks should not be interpreted as historical busy owners.
        current = []
        for item in copies:
            # Validate with the lock temporarily acknowledged through a narrow
            # parameter, rather than removing a live lock during verification.
            current.append(classify(Path(item['location']), Path(item['state']), item['harness'],
                                    item['scope'], home, package, locked=True))
        fresh = discover(home, project, package)
        if {item['location'] for item in fresh} != {item['location'] for item in copies}:
            raise ValueError('Standalone discovery changed since consent; inspect again')
        if current != copies or any(item['ownership'] != 'managed' for item in current):
            raise ValueError('Standalone ownership or contents changed since consent; copies preserved')
        moves, retained = [], []
        try:
            for item in current:
                target, state = Path(item['location']), Path(item['state'])
                archive = state / 'migrated'
                kit.no_links(archive)
                archive.mkdir(mode=0o700, exist_ok=True)
                secure(archive, state.parents[2])
                info = archive.stat()
                if ((hasattr(os, 'getuid') and info.st_uid != os.getuid())
                        or (os.name != 'nt' and info.st_mode & 0o022)):
                    raise ValueError('Unsafe migration archive ownership or permissions; preserve and inspect')
                destination = Path(tempfile.mkdtemp(prefix='standalone-', dir=archive))
                retained.append(str(destination))
                for source, dest in ((target, destination / 'skill'),
                                     (state / 'state.json', destination / 'state.json')):
                    source.rename(dest)
                    moves.append((source, dest))
        except BaseException:
            for source, dest in reversed(moves):
                dest.rename(source)
            raise
    return retained

