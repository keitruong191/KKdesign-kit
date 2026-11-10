#!/usr/bin/env python3
"""Opt-in persistent Git marketplace probe, with isolated profiles and no model calls.

Requires both installed provider CLIs, Python 3.9+ with requirements.txt and
approved network access. Logs stay in a new private directory outside source.
Setup consent here applies only to this disposable synthetic probe.
"""
import argparse
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


def probe(output, codex_ref, claude_ref):
    if output.absolute().resolve().is_relative_to(ROOT):
        raise ValueError('Output must be outside source')
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

        run('version', [providers[name], '--version'])
        ref = codex_ref if name == 'codex' else claude_ref
        if name == 'codex':
            native('register', 'marketplace', 'add', REPOSITORY, '--ref', ref, '--json')
        else:
            native('register', 'marketplace', 'add', REPOSITORY + '#' + ref, '--scope', 'user')
        market = 'kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'
        identifier = 'kkdesign-kit@' + market
        args = ['add' if name == 'codex' else 'install', identifier]
        if name == 'claude':
            args += ['--scope', 'user']
        native('install', *args)
        inventory = json.loads(native('inventory', 'list', '--json'))
        rows = inventory['installed'] if name == 'codex' else inventory
        selected = [row for row in rows if row.get('pluginId', row.get('id')) == identifier]
        assert len(selected) == 1 and selected[0]['enabled'] is True, inventory
        assert selected[0]['version'] == '0.5.0a1', selected
        plugin = config / 'plugins/cache' / market / 'kkdesign-kit/0.5.0a1'
        skill = plugin / 'skills/kkdesign-kit' if name == 'codex' else plugin
        kit.verify(skill)
        # Record the actual native clone revision, including when the CLI only
        # accepts a named branch. A branch name itself is never an immutable pin.
        clones = [path.parent for path in config.rglob('.git')]
        revisions = [run('clone-' + str(i), ['git', '-C', path, 'rev-parse', 'HEAD']).strip()
                     for i, path in enumerate(clones)]
        assert revisions, 'No native Git marketplace clone found'
        (base / 'native-revisions.json').write_text(json.dumps(revisions, indent=2) + '\n')
        if re.fullmatch(r'[0-9a-f]{40}', ref):
            assert ref in revisions, revisions

        # Fresh process, no source override and no user/model prompt.
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
        # Runtime/entrypoint evidence is direct execution, not agent/human acceptance.
        helper_env = dict(env, PATH='/nonexistent')
        prefix = ['/bin/sh', skill / 'scripts/kkdesign_setup_posix.sh', '--package-root', skill]
        run('setup', prefix + ['--consent'], helper_env)
        run('helper', prefix + ['--helper', 'kkdesign_install', 'verify', '--source', skill], helper_env)
        private_before = kit.hashes(home / '.kkdesign-kit')
        assert kit.hashes(skill) == package_before
        native('remove', 'remove' if name == 'codex' else 'uninstall', identifier)
        inventory = json.loads(native('removed-inventory', 'list', '--json'))
        assert not (inventory['installed'] if name == 'codex' else inventory), inventory
        native('unregister', 'marketplace', 'remove', market)
        assert kit.hashes(product) == before
        assert kit.hashes(home / '.kkdesign-kit') == private_before
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
    args = parser.parse_args()
    probe(args.output, args.codex_ref, args.claude_ref)


if __name__ == '__main__':
    main()
