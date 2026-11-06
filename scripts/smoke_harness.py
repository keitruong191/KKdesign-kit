#!/usr/bin/env python3
"""Opt-in LIVE harness probe, not an offline test or a discovery simulator.

Uses an isolated home/project, optionally copying only a supplied Codex auth file.
Raw logs stay at the user-selected output outside the repository; review them
before sharing. Claude may need separately authenticated credentials for the
isolated configuration. No model selection, hooks, MCP, or installed plugins.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from kkdesign_install import ROOT, lifecycle, package


def run_probe(harness, scope, output, auth_file=None, claude_credentials=None):
    executable = shutil.which('codex' if harness == 'codex' else 'claude')
    if not executable:
        raise ValueError('Harness executable not installed')
    version = subprocess.check_output([executable, '--version'], text=True).strip()
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='kkdesign live spaces ') as temp:
        base = Path(temp).resolve()
        home, project = base / 'home', base / 'synthetic project'
        home.mkdir()
        project.mkdir()
        # Only authentication is reused. Never copy user settings, skills or hooks.
        config = home / ('.codex' if harness == 'codex' else '.claude')
        config.mkdir()
        if auth_file:
            shutil.copyfile(auth_file, config / 'auth.json')
            (config / 'auth.json').chmod(0o600)
        if claude_credentials:
            shutil.copyfile(claude_credentials, config / '.credentials.json')
            (config / '.credentials.json').chmod(0o600)
        archive = base / 'kit.zip'
        package(ROOT, archive)
        import zipfile
        with zipfile.ZipFile(archive) as z:
            z.extractall(base / 'artifact')
        source = base / 'artifact/kkdesign-kit'
        install = lifecycle('install', harness, scope, home, project, source)
        shutil.rmtree(source)  # Discovery/read must use only the relocated installed copy.
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('CODEX_', 'CLAUDE_', 'ANTHROPIC_')) and k != 'HOME'}
        env.update(HOME=str(home), PYTHONDONTWRITEBYTECODE='1')
        invocation = '$kkdesign-kit' if harness == 'codex' else '/kkdesign-kit'
        prompt = invocation + (
            '\nThis is a read-only installation acceptance probe. Invoke the discovered skill '
            'and show its bare command menu with availability. Actually read its bundled '
            'references/commands.md using a file tool or shell read, and report its resolved '
            'installed location. Do not search for the source checkout or use network/tools '
            'other than the local skill and local file reads. State whether init can execute '
            'in this release. Do not create or edit files.')
        if harness == 'codex':
            env['CODEX_HOME'] = str(config)
            command = [executable, 'exec', '--ignore-user-config', '--ignore-rules',
                       '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only',
                       '--json', prompt]
        else:
            env['CLAUDE_CONFIG_DIR'] = str(config)
            command = [executable, '-p', '--setting-sources', 'user,project', '--strict-mcp-config',
                       '--mcp-config', '{"mcpServers":{}}', '--tools', 'Skill,Read',
                       '--allowedTools', 'Skill,Read', '--output-format', 'stream-json',
                       '--verbose', '--no-session-persistence', prompt]
        try:
            result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                    text=True, input='', timeout=240)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = 'Harness timeout after 240 seconds'
            code = 124
        (output / 'stdout.jsonl').write_text(stdout, encoding='utf-8')
        (output / 'stderr.txt').write_text(stderr, encoding='utf-8')
        record = {'harness': harness, 'version': version, 'scope': scope,
                  'exitCode': code, 'installationStatus': install['status'],
                  'isolation': 'fresh home, synthetic project, extracted package; no user config/skills/hooks',
                  'verdict': 'manual transcript review required'}
        (output / 'probe.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record, indent=2))
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', required=True, choices=('codex', 'claude-code'))
    parser.add_argument('--scope', required=True, choices=('user', 'project'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--codex-auth-file', type=Path)
    parser.add_argument('--claude-credentials-file', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Keep private raw harness logs outside the repository')
    try:
        return run_probe(args.harness, args.scope, output, args.codex_auth_file,
                         args.claude_credentials_file)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    sys.exit(main())
