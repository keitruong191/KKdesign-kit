#!/usr/bin/env python3
"""Opt-in persistent Git marketplace probe, with isolated profiles and no model calls.

Fresh mode tests target installs. Migration mode also accepts the all-or-none
--from-codex-ref, --from-claude-ref, --from-claude-sha, and --from-version flags.
Requires both installed provider CLIs, Python 3.9+ with requirements.txt and
approved network access. Logs stay in a new private directory outside source.
Setup consent here applies only to this disposable synthetic probe.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import kkdesign_install as kit

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/keitruong191/KKdesign-kit.git'


def exchange(process, output, payload, accepts):
    process.stdin.write((json.dumps(payload) + '\n').encode())
    process.stdin.flush()
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    pending = b''
    deadline = time.monotonic() + 60
    try:
        while time.monotonic() < deadline:
            if not selector.select(1):
                continue
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError('Native discovery process closed before response')
            pending += chunk
            while b'\n' in pending:
                line, pending = pending.split(b'\n', 1)
                with output.open('ab') as log:
                    log.write(line + b'\n')
                value = json.loads(line)
                if accepts(value):
                    return value
        raise RuntimeError('Native discovery response timed out')
    finally:
        selector.close()


def private_state(root):
    # Managed Python includes legitimate symlinks. Preserve link targets without
    # following them, plus file bytes/ownership/mode for the whole private tree.
    result = {}
    for path in sorted(root.rglob('*')):
        info = path.lstat()
        value = (os.readlink(path) if path.is_symlink() else
                 hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
        result[path.relative_to(root).as_posix()] = (info.st_uid, info.st_gid, info.st_mode, value)
    return result


def probe(output, codex_ref, claude_ref, claude_sha, from_codex_ref=None,
          from_claude_ref=None, from_claude_sha=None, from_version=None):
    migration = from_codex_ref is not None
    if not re.fullmatch(r'[0-9a-f]{40}', codex_ref) or not re.fullmatch(r'[0-9a-f]{40}', claude_sha):
        raise ValueError('Expected immutable target SHA required')
    if migration and (not re.fullmatch(r'[0-9a-f]{40}', from_codex_ref)
                      or not re.fullmatch(r'[0-9a-f]{40}', from_claude_sha)):
        raise ValueError('Expected immutable old-source SHA required')
    if output.absolute().resolve().is_relative_to(ROOT):
        raise ValueError('Output must be outside source')
    expected_version = kit.read_json(ROOT / 'manifest.json')['version']
    providers = {name: shutil.which(name) for name in ('codex', 'claude')}
    if not all(providers.values()):
        raise ValueError('Both provider CLIs must already be installed')
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    records = []
    for name in providers:
        base = output / name
        home, product = base / 'private home', base / 'unrelated product with spaces'
        home.mkdir(mode=0o700, parents=True)
        product.mkdir()
        config = home / ('.codex' if name == 'codex' else '.claude')
        config.mkdir(mode=0o700)
        env = {key: value for key, value in os.environ.items()
               if not any(word in key.upper() for word in
                          ('TOKEN', 'API_KEY', 'CODEX', 'OPENAI', 'CLAUDE', 'ANTHROPIC',
                           'AWS_', 'GOOGLE_', 'AZURE_', 'VERTEX_', 'SSH_', 'GIT_'))}
        env.update(HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / '.codex'),
                   CLAUDE_CONFIG_DIR=str(home / '.claude'), DISABLE_TELEMETRY='1',
                   DISABLE_ERROR_REPORTING='1', CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC='1',
                   PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_NOSYSTEM='1',
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
        for relative in ('DESIGN.md', 'design/LESSON.md', 'design/tasks/history/task.json'):
            path = product / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Synthetic remote-source preservation sentinel\n')
        sentinel = home / '.kkdesign-kit' / 'preserved synthetic state'
        sentinel.parent.mkdir(mode=0o700)
        sentinel.write_text('Synthetic shared-state preservation sentinel\n')
        before = kit.hashes(product)

        def run(label, args, execution_env=env):
            result = subprocess.run([str(arg) for arg in args], cwd=product, env=execution_env,
                                    capture_output=True, text=True, timeout=600)
            (base / (label + '.stdout')).write_text(result.stdout)
            (base / (label + '.stderr')).write_text(result.stderr)
            records.append({'provider': name, 'label': label, 'exit': result.returncode})
            (output / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
            print(name + ' ' + label + ': ' + str(result.returncode), flush=True)
            if result.returncode:
                raise RuntimeError(label + ': ' + result.stdout + result.stderr)
            return result.stdout

        def native(label, *args):
            return run(label, [providers[name], 'plugin', *args])

        def revisions(label):
            clones = [path.parent for path in config.rglob('.git')]
            values = [run(label + '-' + str(i), ['git', '-C', path, 'rev-parse', 'HEAD']).strip()
                      for i, path in enumerate(clones)]
            assert values, 'No native Git marketplace clone found'
            (base / 'native-revisions.json').write_text(json.dumps(values, indent=2) + '\n')
            return values

        def inventory():
            value = json.loads(native('inventory', 'list', '--json'))
            rows = value['installed'] if name == 'codex' else value
            return value, rows

        def assert_plugin(expected, enabled):
            value, rows = inventory()
            selected = [row for row in rows if row.get('pluginId', row.get('id')) == identifier]
            assert len(selected) == 1 and selected[0]['enabled'] is enabled, value
            assert selected[0]['version'] == expected, selected

        def setup(label, package, consent, reused=None):
            prefix = ['/bin/sh', package / 'scripts/kkdesign_setup_posix.sh',
                      '--package-root', package]
            if consent:
                prefix += ['--consent']
            stdout = run(label, prefix, dict(env, PATH='/nonexistent'))
            completion = json.loads(stdout.strip().splitlines()[-1])
            assert completion['phase'] == 'complete', completion
            result = completion['result']
            assert result.get('status') == 'ready', result
            if reused is not None:
                assert result.get('reused') is reused, result
            return result

        run('version', [providers[name], '--version'])
        market = 'kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'
        identifier = 'kkdesign-kit@' + market

        if migration:
            old_ref = from_codex_ref if name == 'codex' else from_claude_ref
            old_sha = from_codex_ref if name == 'codex' else from_claude_sha
            if name == 'codex':
                native('register-old', 'marketplace', 'add', REPOSITORY, '--ref', old_ref, '--json')
            else:
                native('register-old', 'marketplace', 'add', REPOSITORY + '#' + old_ref, '--scope', 'user')
            assert revisions('old-clone') == [old_sha], 'Old marketplace clone SHA mismatch'
            old_args = ['add' if name == 'codex' else 'install', identifier]
            if name == 'claude':
                old_args += ['--scope', 'user']
            native('install-old', *old_args)
            assert_plugin(from_version, True)
            old_plugin = config / 'plugins/cache' / market / 'kkdesign-kit' / from_version
            old_skill = old_plugin / 'skills/kkdesign-kit' if name == 'codex' else old_plugin
            descriptor = '.codex-plugin/plugin.json' if name == 'codex' else '.claude-plugin/plugin.json'
            assert kit.read_json(old_plugin / descriptor)['version'] == from_version
            assert kit.read_json(old_skill / 'manifest.json')['version'] == from_version
            setup('setup-old', old_skill, True)
            private_before = private_state(home / '.kkdesign-kit')
            if name == 'claude':
                native('disable-old', 'disable', identifier, '--scope', 'user')
                assert_plugin(from_version, False)
                native('uninstall-old', 'uninstall', identifier, '--scope', 'user', '--keep-data')
                native('remove-old-marketplace', 'marketplace', 'remove', market, '--scope', 'user')
            else:
                native('remove-old', 'remove', identifier)
                native('unregister-old', 'marketplace', 'remove', market)
            assert kit.hashes(product) == before
            assert private_state(home / '.kkdesign-kit') == private_before
        else:
            private_before = None

        if name == 'codex':
            native('register', 'marketplace', 'add', REPOSITORY, '--ref', codex_ref, '--json')
        else:
            native('register', 'marketplace', 'add', REPOSITORY + '#' + claude_ref, '--scope', 'user')
        revisions_target = revisions('target-clone')
        expected_sha = codex_ref if name == 'codex' else claude_sha
        assert re.fullmatch(r'[0-9a-f]{40}', expected_sha), 'Expected immutable SHA required'
        assert revisions_target == [expected_sha], revisions_target
        args = ['add' if name == 'codex' else 'install', identifier]
        if name == 'claude':
            args += ['--scope', 'user']
        native('install', *args)
        if name == 'claude' and migration:
            native('disable-target', 'disable', identifier, '--scope', 'user')
            assert_plugin(expected_version, False)
        plugin = config / 'plugins/cache' / market / 'kkdesign-kit' / expected_version
        skill = plugin / 'skills/kkdesign-kit' if name == 'codex' else plugin
        descriptor = '.codex-plugin/plugin.json' if name == 'codex' else '.claude-plugin/plugin.json'
        assert kit.read_json(plugin / descriptor)['version'] == expected_version
        assert kit.read_json(skill / 'manifest.json')['version'] == expected_version
        assert_plugin(expected_version, not (name == 'claude' and migration))
        if migration:
            assert kit.hashes(product) == before
            assert private_state(home / '.kkdesign-kit') == private_before
        # migration install remains disabled until explicitly enabled for smoke.
        if name == 'claude' and migration:
            native('enable-target-smoke', 'enable', identifier, '--scope', 'user')
            assert_plugin(expected_version, True)
        command = ([providers[name], 'app-server'] if name == 'codex' else
                   [providers[name], '--print', '--input-format', 'stream-json',
                    '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
                    '--strict-mcp-config', '--setting-sources', 'user', '--no-chrome'])
        with (base / 'discovery.stderr').open('wb') as errors:
            process = subprocess.Popen(command, cwd=product, env=env, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=errors)
            try:
                log = base / 'discovery.jsonl'
                if name == 'codex':
                    result = exchange(process, log, {'id': 1, 'method': 'initialize', 'params': {
                        'clientInfo': {'name': 'remote-marketplace-probe', 'version': '1.0'}}},
                        lambda row: row.get('id') == 1)
                    assert 'error' not in result, result
                    process.stdin.write(b'{"method":"initialized"}\n')
                    result = exchange(process, log, {'id': 2, 'method': 'skills/list', 'params': {
                        'cwds': [str(product)], 'forceReload': True}}, lambda row: row.get('id') == 2)
                    assert 'error' not in result, result
                else:
                    result = exchange(process, log, {'type': 'control_request', 'request_id': 'init',
                        'request': {'subtype': 'initialize'}},
                        lambda row: row.get('type') == 'control_response')
                assert 'kkdesign-kit:kkdesign-kit' in json.dumps(result), result
            finally:
                process.terminate()
                process.wait(timeout=10)
                process.stdin.close()
                process.stdout.close()
        print(name + ' fresh-session discovery: pass (no model prompt)', flush=True)
        package_before = kit.hashes(skill)
        if migration:
            setup('setup-target-reuse', skill, False, reused=True)
        else:
            setup('setup', skill, True)
            private_before = private_state(home / '.kkdesign-kit')
        helper_env = dict(env, PATH='/nonexistent')
        prefix = ['/bin/sh', skill / 'scripts/kkdesign_setup_posix.sh', '--package-root', skill]
        run('helper', prefix + ['--helper', 'kkdesign_install', 'verify', '--source', skill], helper_env)
        assert kit.hashes(skill) == package_before
        assert private_state(home / '.kkdesign-kit') == private_before
        if name == 'codex':
            native('remove', 'remove', identifier)
            native('unregister', 'marketplace', 'remove', market)
        else:
            native('uninstall', 'uninstall', identifier, '--scope', 'user', '--keep-data')
            native('remove-marketplace', 'marketplace', 'remove', market, '--scope', 'user')
        inventory_value, rows = inventory()
        assert not any(row.get('pluginId', row.get('id')) == identifier for row in rows), inventory_value
        assert kit.hashes(product) == before
        assert private_state(home / '.kkdesign-kit') == private_before
        assert sentinel.read_text() == 'Synthetic shared-state preservation sentinel\n'
        for relative in ('.agents/skills/kkdesign-kit', '.claude/skills/kkdesign-kit'):
            assert not (home / relative).exists()
            assert not (product / relative).exists()
        print(name + ' removal/project/private-runtime preservation: pass', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--codex-ref', required=True)
    parser.add_argument('--claude-ref', required=True)
    parser.add_argument('--claude-sha', required=True, help='Expected immutable distribution commit; checked before install')
    parser.add_argument('--from-codex-ref')
    parser.add_argument('--from-claude-ref')
    parser.add_argument('--from-claude-sha')
    parser.add_argument('--from-version')
    args = parser.parse_args()
    migration_values = (args.from_codex_ref, args.from_claude_ref,
                        args.from_claude_sha, args.from_version)
    if any(value is not None for value in migration_values) and not all(
            value is not None for value in migration_values):
        parser.error('migration requires all of --from-codex-ref, --from-claude-ref, '
                     '--from-claude-sha, and --from-version')
    probe(args.output, args.codex_ref, args.claude_ref, args.claude_sha, *migration_values)


if __name__ == '__main__':
    main()


