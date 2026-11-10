#!/usr/bin/env python3
"""Opt-in native lifecycle probe; two providers share a disposable private home.

Uses real Git smart HTTP, native plugin controls and POSIX Setup/helpers. Never
copies authentication or calls a model. Output is private raw evidence, outside
the source tree. This maintainer probe is not another plugin lifecycle command.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import selectors
import time
import subprocess
import sys
import threading
import zipfile

sys.dont_write_bytecode = True
import build_claude_marketplace as claude
import build_codex_marketplace as codex
import kkdesign_install as kit
import kkdesign_setup as runtime_setup

ROOT = Path(__file__).resolve().parents[1]


def probe(output):
    if sys.platform != 'darwin' and not sys.platform.startswith('linux'):
        raise ValueError('This native lifecycle probe requires macOS or GNU/Linux')
    providers = {name: shutil.which(name) for name in ('codex', 'claude')}
    if not all(providers.values()):
        raise ValueError('Both provider CLIs must already be available')
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    home, product, transport = (output / name for name in ('private home', 'unrelated product', 'transport'))
    home.mkdir(mode=0o700)
    (home / '.codex').mkdir(mode=0o700)
    (home / '.claude').mkdir(mode=0o700)
    product.mkdir()
    transport.mkdir()
    for name in ('DESIGN.md', 'design/LESSON.md', 'design/tasks/history/task.json'):
        path = product / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Synthetic lifecycle preservation sentinel\n')
    project_before = kit.hashes(product)
    env = {key: value for key, value in os.environ.items()
           if not any(word in key.upper() for word in
                      ('TOKEN', 'API_KEY', 'CODEX', 'OPENAI', 'CLAUDE', 'ANTHROPIC', 'AWS_', 'GOOGLE_', 'AZURE_', 'VERTEX_'))}
    env.update(HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / '.codex'),
               CLAUDE_CONFIG_DIR=str(home / '.claude'), DISABLE_TELEMETRY='1',
               DISABLE_ERROR_REPORTING='1', CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC='1',
               PYTHONDONTWRITEBYTECODE='1')
    records = []

    def run(label, command, cwd=product, execution_env=env):
        result = subprocess.run([str(arg) for arg in command], cwd=cwd, env=execution_env,
                                capture_output=True, text=True, timeout=600)
        (output / (label + '.stdout')).write_text(result.stdout)
        (output / (label + '.stderr')).write_text(result.stderr)
        records.append({'label': label, 'exit': result.returncode})
        (output / 'commands.json').write_text(json.dumps(records, indent=2))
        print(label + ': ' + str(result.returncode), flush=True)
        if result.returncode:
            raise RuntimeError(label + ': ' + result.stdout + result.stderr)
        return result.stdout

    class GitHandler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.respond()

        def do_POST(self):
            self.respond()

        def respond(self):
            path, _, query = self.path.partition('?')
            backend = dict(env, GIT_PROJECT_ROOT=str(transport), GIT_HTTP_EXPORT_ALL='1',
                           PATH_INFO=path, QUERY_STRING=query, REQUEST_METHOD=self.command,
                           CONTENT_TYPE=self.headers.get('Content-Type', ''),
                           CONTENT_LENGTH=self.headers.get('Content-Length', '0'), REMOTE_ADDR='127.0.0.1')
            if self.headers.get('Git-Protocol'):
                backend['HTTP_GIT_PROTOCOL'] = self.headers['Git-Protocol']
            body = self.rfile.read(int(backend['CONTENT_LENGTH']))
            result = subprocess.run(['git', 'http-backend'], input=body, env=backend,
                                    capture_output=True, timeout=30)
            headers, _, content = result.stdout.partition(b'\r\n\r\n')
            self.send_response(200)
            for row in headers.split(b'\r\n'):
                if b':' in row:
                    key, value = row.split(b':', 1)
                    self.send_header(key.decode(), value.strip().decode())
            self.end_headers()
            self.wfile.write(content)

    source = output / 'synthetic release source'
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))

    def release(number, changed=False):
        version = '0.5.0a' + str(number)
        for relative in ('manifest.json', '.claude-plugin/plugin.json',
                         '.claude-plugin/marketplace.json', 'packaging/codex/.codex-plugin/plugin.json'):
            path = source / relative
            data = json.loads(path.read_text())
            if relative.endswith('marketplace.json'):
                data['plugins'][0]['version'] = version
            else:
                data['version'] = version
            path.write_text(json.dumps(data, indent=2) + '\n')
        if changed:
            (source / 'requirements.txt').write_text('jsonschema>=4.19,<5\n')
        for name, builder, prefix in (('claude', claude, 'kkdesign-marketplace'),
                                      ('codex', codex, 'kkdesign-codex-marketplace')):
            archive = output / (name + '-' + version + '.zip')
            builder.package(source, archive)
            stage = output / (name + '-' + version)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(stage)
            repo = transport / (name + '.git')
            if not repo.exists():
                repo.mkdir()
                run(name + '-git-init', ['git', 'init', '-b', 'review'], cwd=repo)
            for entry in repo.iterdir():
                if entry.name != '.git':
                    shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
            shutil.copytree(stage / prefix, repo, dirs_exist_ok=True)
            run(name + '-git-add-' + version, ['git', 'add', '-A'], cwd=repo)
            run(name + '-git-commit-' + version,
                ['git', '-c', 'user.name=Synthetic Smoke', '-c', 'user.email=smoke@example.invalid',
                 'commit', '-m', 'Synthetic release ' + version], cwd=repo)
        return version

    def native(name, label, *args):
        return run(name + '-' + label, [providers[name], 'plugin', *args])

    def package(name, version):
        base = home / ('.codex/plugins/cache/kkdesign-kit-codex' if name == 'codex'
                       else '.claude/plugins/cache/kkdesign-kit-marketplace') / 'kkdesign-kit' / version
        return base / 'skills/kkdesign-kit' if name == 'codex' else base

    def setup(name, version, label, consent=False):
        skill = package(name, version)
        command = ['/bin/sh', skill / 'scripts/kkdesign_setup_posix.sh', '--package-root', skill]
        if consent:
            command.append('--consent')
        helper_env = dict(env, PATH='/nonexistent')
        events = [json.loads(line) for line in run(name + '-' + label, command, execution_env=helper_env).splitlines()]
        return events[-1].get('result', dict(events[-1], status=events[-1]['phase']))

    def helper(name, version, label):
        skill = package(name, version)
        result = json.loads(run(name + '-' + label, ['/bin/sh', skill / 'scripts/kkdesign_setup_posix.sh',
                               '--package-root', skill, '--helper', 'kkdesign_install', 'verify', '--source', skill],
                               execution_env=dict(env, PATH='/nonexistent')))
        assert result['status'] == 'verified', result

    def codex_enabled(enabled):
        # Codex CLI has no enable/disable subcommand. Exercise the provider's
        # native configuration API, then observe state from a new CLI process.
        label = 'codex-' + ('enable' if enabled else 'disable')
        with (output / (label + '.stderr')).open('w') as errors:
            process = subprocess.Popen([providers['codex'], 'app-server'], cwd=product, env=env,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors, bufsize=0)
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            pending = b''

            def request(identifier, method, params):
                nonlocal pending
                process.stdin.write((json.dumps({'id': identifier, 'method': method, 'params': params}) + '\n').encode())
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    if b'\n' not in pending:
                        if not selector.select(1):
                            continue
                        chunk = os.read(process.stdout.fileno(), 65536)
                        if not chunk:
                            raise RuntimeError('Native app-server closed before response')
                        pending += chunk
                    while b'\n' in pending:
                        line, pending = pending.split(b'\n', 1)
                        with (output / (label + '.jsonl')).open('ab') as log:
                            log.write(line + b'\n')
                        response = json.loads(line)
                        if response.get('id') == identifier:
                            if 'error' in response:
                                raise RuntimeError(str(response))
                            return response['result']
                raise RuntimeError('Native app-server request timed out')

            try:
                request(1, 'initialize', {'clientInfo': {'name': 'synthetic-lifecycle-probe', 'version': '1.0'}})
                process.stdin.write(b'{"method":"initialized"}\n')
                request(2, 'config/value/write', {'keyPath': 'plugins."kkdesign-kit@kkdesign-kit-codex".enabled',
                                                'value': enabled, 'mergeStrategy': 'replace'})
            finally:
                selector.close()
                process.terminate()
                process.wait(timeout=10)
                process.stdin.close()
                process.stdout.close()
        listing = json.loads(native('codex', label + '-inventory', 'list', '--json'))
        selected = [item for item in listing['installed'] if item['pluginId'] == 'kkdesign-kit@kkdesign-kit-codex']
        assert len(selected) == 1 and selected[0]['enabled'] is enabled, listing

    release(1)
    server = ThreadingHTTPServer(('127.0.0.1', 0), GitHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        for name in providers:
            run(name + '-version', [providers[name], '--version'])
            args = ['marketplace', 'add', 'http://127.0.0.1:' + str(server.server_port) + '/' + name + '.git']
            native(name, 'register', *args)
            native(name, 'install', 'add' if name == 'codex' else 'install',
                   'kkdesign-kit@' + ('kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'))
        assert not (home / '.kkdesign-kit').exists()
        assert setup('claude', '0.5.0a1', 'no-consent')['status'] == 'consent-required'
        first = setup('claude', '0.5.0a1', 'consented-setup', True)
        assert first['status'] == 'ready' and not first['reused'], first
        runtime = Path(first['runtimePath'])
        before = runtime_setup.fingerprint(runtime, (runtime / 'requirements.txt').read_bytes())
        assert setup('codex', '0.5.0a1', 'shared-reuse')['reused']
        for name in providers:
            helper(name, '0.5.0a1', 'initial-helper')
        for action in ('disable', 'enable'):
            native('claude', action, action, 'kkdesign-kit@kkdesign-kit-marketplace')
            codex_enabled(action == 'enable')
            assert runtime_setup.fingerprint(runtime, (runtime / 'requirements.txt').read_bytes()) == before and kit.hashes(product) == project_before
        for number in (2, 3):
            version = release(number, changed=number == 3)
            for name in providers:
                market = 'kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'
                native(name, 'refresh-' + version, 'marketplace', 'upgrade' if name == 'codex' else 'update', market)
                native(name, 'update-' + version, 'add' if name == 'codex' else 'update', 'kkdesign-kit@' + market)
                result = setup(name, version, 'check-' + version)
                if number == 2:
                    assert result['status'] == 'ready' and result['reused'], result
                    helper(name, version, 'helper-' + version)
                elif name == 'codex':
                    assert result['status'] == 'consent-required', result
                    # Claude is still natively installed at the prior version.
                    # Updating Codex must leave that active consumer usable.
                    helper('claude', '0.5.0a2', 'old-consumer-before-new-setup')
                    new = setup('codex', version, 'consented-changed-requirements', True)
                    assert new['status'] == 'ready' and new['runtimePath'] != str(runtime), new
                    helper('claude', '0.5.0a2', 'old-consumer-after-new-setup')
                else:
                    # The newly updated second consumer can reuse the cache
                    # explicitly provisioned for the first, without new consent.
                    assert result['status'] == 'ready' and result['reused'], result
                assert runtime_setup.fingerprint(runtime, (runtime / 'requirements.txt').read_bytes()) == before
        assert setup('claude', '0.5.0a3', 'shared-new-reuse')['reused']
        assert runtime_setup.fingerprint(runtime, (runtime / 'requirements.txt').read_bytes()) == before
        for name in providers:
            helper(name, '0.5.0a3', 'updated-helper')
            native(name, 'uninstall', 'remove' if name == 'codex' else 'uninstall',
                   'kkdesign-kit@' + ('kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'))
            assert runtime_setup.fingerprint(runtime, (runtime / 'requirements.txt').read_bytes()) == before
            assert kit.hashes(product) == project_before
            if name == 'codex':
                helper('claude', '0.5.0a3', 'survivor-helper')
        for name in providers:
            native(name, 'reinstall', 'add' if name == 'codex' else 'install',
                   'kkdesign-kit@' + ('kkdesign-kit-codex' if name == 'codex' else 'kkdesign-kit-marketplace'))
            assert setup(name, '0.5.0a3', 'reinstalled-reuse')['reused']
        assert not (home / '.agents/skills/kkdesign-kit').exists()
        assert not (home / '.claude/skills/kkdesign-kit').exists()
        assert kit.hashes(product) == project_before
        result = {'status': 'pass', 'nativeProviders': list(providers),
                  'scope': 'Native install/update/remove/reinstall; shared POSIX Setup and real helpers; both providers enable/disable.',
                  'pending': 'Authenticated agent menus/consent/usability, other OS/CPU surfaces.'}
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
    finally:
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Keep private evidence outside the source tree')
    probe(output)


if __name__ == '__main__':
    main()
