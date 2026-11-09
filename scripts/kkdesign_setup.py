#!/usr/bin/env python3
"""Internal agent Setup; provider installation and lifecycle remain native."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
# Isolated invocation must work from an arbitrary installed package directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kkdesign_install as kit


class SetupError(ValueError):
    def __init__(self, code, message, action):
        super().__init__(message)
        self.code, self.action = code, action


def package_root(path):
    if not path.is_absolute():
        raise SetupError('package', 'Package root must be absolute.',
                         'Use the skill directory supplied by the host, outside the product project.')
    path = kit.canonical(path)
    # Validate the shipped resource inventory when present. Source review uses
    # the same allowlist; a project cannot supply an interpreter through metadata.
    if (path / 'bundle.json').exists():
        kit.verify(path)
    kit.payload(path)
    return path


def windows_private(path, home, tree=False):
    """Use the same native ACL/reparse policy as the Python-free bootstrap."""
    if os.name != 'nt':
        return
    powershell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    command = [str(powershell), '-NoProfile', '-NonInteractive', '-File',
               str(Path(__file__).with_name('kkdesign_windows_security.ps1')),
               '-Path', str(path), '-UserHome', str(home)]
    if tree:
        command.append('-Recurse')
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise SetupError('ownership-or-policy', result.stderr.strip() or 'Windows cache verification was denied.',
                         'Preserve the cache and inspect ownership/ACLs or ask the administrator for authorized execution; never bypass policy.')


def cache_paths(home, requirements):
    runtime = kit.runtime_path(home, requirements)
    windows_private(runtime, home)
    kit.no_links(runtime)
    # Private cache provenance is rooted in the actual user's home, never a
    # project setting or a runtime path read from package/project JSON.
    for path in (home / '.kkdesign-kit', kit.runtime_root(home), runtime):
        if path.exists():
            info = path.stat()
            if ((hasattr(os, 'getuid') and info.st_uid != os.getuid())
                    or (os.name != 'nt' and info.st_mode & 0o022)):
                raise SetupError('ownership', 'Runtime cache is writable by another account or has another owner.',
                                 'Have the account owner inspect the cache permissions; Setup preserves it.')
    return runtime


def fingerprint(runtime, requirements):
    windows_private(runtime, runtime.parents[2], tree=True)
    python = kit.runtime_python(runtime)
    if not python.is_file():
        raise SetupError('runtime-missing', 'Managed interpreter is missing.',
                         'Inspect the retained cache, then run Setup again; no PATH fallback is used.')
    files = {}
    for path in sorted(runtime.rglob('*')):
        info = path.lstat()
        if ((hasattr(os, 'getuid') and info.st_uid != os.getuid())
                or (not path.is_symlink() and os.name != 'nt' and info.st_mode & 0o022)):
            raise SetupError('ownership', 'Managed runtime contains unsafe ownership or permissions: ' + str(path),
                             'Preserve and inspect the cache; do not execute or overwrite it.')
        if path.name == 'setup.json' and path.parent == runtime:
            continue
        name = path.relative_to(runtime).as_posix()
        if path.is_symlink():
            files[name] = {'link': os.readlink(path)}
            if path.is_file():
                files[name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_file():
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            files[name] = 'directory'
        else:
            raise SetupError('runtime-unverified', 'Unexpected managed runtime file type.',
                             'Preserve and inspect the cache before repair.')
    return {'identifier': kit.IDENTIFIER, 'requirementsSha256': hashlib.sha256(requirements).hexdigest(),
            'pythonSha256': hashlib.sha256(python.read_bytes()).hexdigest(),
            'filesSha256': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


def trusted_runtime(home, requirements):
    runtime = cache_paths(home, requirements)
    if not runtime.exists():
        return None
    for name in ('runtime.json', 'setup.json', 'requirements.txt'):
        kit.no_links(runtime / name)
    marker = {'identifier': kit.IDENTIFIER, 'requirementsSha256': runtime.name}
    if (not (runtime / 'runtime.json').is_file()
            or kit.read_json(runtime / 'runtime.json') != marker
            or not (runtime / 'setup.json').is_file()
            or not (runtime / 'requirements.txt').is_file()
            or (runtime / 'requirements.txt').read_bytes() != requirements
            or kit.read_json(runtime / 'setup.json') != fingerprint(runtime, requirements)):
        raise SetupError('runtime-unverified', 'Runtime ownership, requirements or verification receipt does not match.',
                         'Preserve and inspect the cache with its owner before repair; do not run or overwrite it.')
    return runtime


def verify_helpers(package, runtime):
    # All scratch data is user cache data, outside both plugin and project.
    with tempfile.TemporaryDirectory(prefix='setup-check-', dir=runtime.parent) as temp:
        kit.smoke_runtime(package, runtime, Path(temp))


def setup(package, home, consent=False, emit=lambda event: None):
    state = {'plugin': 'loaded', 'runtime': 'setup-required', 'externalTools': 'unverified'}
    def phase(name, **values):
        emit(dict(state, phase=name, **values))
    try:
        phase('checking')
        package = package_root(package)
        requirements = (package / 'requirements.txt').read_bytes()
        runtime = trusted_runtime(home, requirements)
        if runtime is None and not consent:
            phase('consent-required', location=str(kit.runtime_path(home, requirements)),
                  purpose='Create a private Python environment and download requirements.txt dependencies from the package index.',
                  permissions='Network access, user-cache writes and local execution; no admin or system Python changes.',
                  nextAction='Explain these actions and obtain an explicit yes in the agent before retrying with --consent.')
            return dict(state, status='consent-required')
        if runtime is None:
            phase('preparing-runtime')
            # Reuse the existing provisioning transaction, without installing a
            # skill or invoking any standalone lifecycle. Failed smoke removes
            # only the runtime created by this transaction.
            with kit.prepared_runtime(home, requirements) as runtime:
                phase('verifying-helpers')
                verify_helpers(package, runtime)
                receipt = runtime / 'setup.json'
                with receipt.open('x', encoding='utf-8') as stream:
                    if os.name != 'nt':
                        os.chmod(receipt, 0o600)
                    json.dump(fingerprint(runtime, requirements), stream, sort_keys=True)
            reused = False
        else:
            phase('verifying-helpers', reuse=True)
            verify_helpers(package, runtime)
            reused = True
        state['runtime'] = 'ready'
        result = dict(state, status='ready', reused=reused, runtimePath=str(runtime),
                      python=str(kit.runtime_python(runtime)),
                      scope='Synthetic helper materialization and dependency-backed contract validation; not live tools or human approval.')
        phase('complete', result=result)
        return result
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        state['runtime'] = 'error'
        if isinstance(exc, SetupError):
            code, action = exc.code, exc.action
        elif isinstance(exc, PermissionError):
            code, action = 'write-or-policy', 'Allow user-cache writes/local execution through your administrator or choose an authorized local session; do not bypass policy.'
        elif isinstance(exc, OSError):
            code, action = 'local-execution', 'Check free space and local execution permissions; ask the administrator if execution is blocked.'
        else:
            code, action = 'provision-or-verification', 'Check network/package-index access and venv/ensurepip availability, or inspect the helper error; retry Setup only after resolving the cause.'
        result = dict(state, status='error', code=code, message=str(exc), nextAction=action)
        phase('failed', result=result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, required=True)
    parser.add_argument('--consent', action='store_true', help='Agent obtained explicit permission for the disclosed provisioning action')
    args = parser.parse_args()
    result = setup(args.package_root, Path.home(), args.consent,
                   emit=lambda event: print(json.dumps(event), flush=True))
    return 1 if result['status'] == 'error' else 0


if __name__ == '__main__':
    sys.exit(main())
