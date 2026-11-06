#!/usr/bin/env python3
"""Opt-in live B2 init/refresh probe in a disposable synthetic project.

Raw output is private and must stay outside the checkout. Authentication is
copied only from explicit files and removed with the temporary home. The model
must execute the installed skill; postconditions independently inspect the kit.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
from kkdesign_install import ROOT, lifecycle, package


def run_probe(harness, output, python, auth_file=None, credentials=None):
    executable = shutil.which('codex' if harness == 'codex' else 'claude')
    if not executable:
        raise ValueError('Harness executable unavailable')
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    version = subprocess.check_output([executable, '--version'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='kkdesign B2 live spaces ') as temp:
        base = Path(temp).resolve()
        home, project = base / 'home', base / 'synthetic project'
        home.mkdir()
        project.mkdir()
        config = home / ('.codex' if harness == 'codex' else '.claude')
        config.mkdir()
        credential = auth_file if harness == 'codex' else credentials
        if credential:
            destination = config / ('auth.json' if harness == 'codex' else '.credentials.json')
            shutil.copyfile(credential, destination)
            destination.chmod(0o600)
        archive = base / 'kit.zip'
        package(ROOT, archive)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(base / 'artifact')
        source = base / 'artifact/kkdesign-kit'
        lifecycle('install', harness, 'project', home, project, source)
        shutil.rmtree(source)
        (project / 'ds').mkdir()
        source_data = {'schemaVersion': '1.0.0',
                       'tokens': [{'id': 'space.small', 'name': 'Small space', 'data': {'value': 4}}],
                       'styles': [], 'components': [], 'variants': [], 'modes': []}
        (project / 'ds/ds.json').write_text(json.dumps(source_data) + '\n')
        (project / 'sources.json').write_text(json.dumps({'sources': [
            {'id': 'synthetic', 'provider': 'local', 'location': 'ds'}]}) + '\n')
        product = b'# Fictional Atlas\n\nSynthetic macOS settings product. No shipped runtime claims.\n'
        (project / 'PRODUCT.md').write_bytes(product)
        invocation = '$kkdesign-kit' if harness == 'codex' else '/kkdesign-kit'
        prompt = invocation + ' init\n' + (
            'This is an authorized live acceptance probe in a disposable synthetic project. '
            'Use the discovered installed skill, read its project-kit routing, and execute '
            'its actual bundled kkdesign_project.py (not replacement code). Use Python '
            + str(python) + '. Selected project is the current directory, sources.json '
            'is the declared source config. First init, inspect the plan and apply it. '
            'I explicitly authorize applying each non-conflicting plan in this synthetic '
            'probe after inspection. Validate the resulting kit. Then edit only '
            'ds/ds.json tokens[0].data.value from 4 to 8; refresh, inspect/apply its plan '
            'and validate. Refresh unchanged once more and report its idempotent status. '
            'Do not alter PRODUCT.md, existing profiles, canonical lessons or task history. '
            'Do not access the network, user config, original repository or credentials. '
            'Report actual command outcomes, source coverage and the offline/live boundary. '
            'Do not merely describe commands or simulate output.')
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('CODEX_', 'CLAUDE_', 'ANTHROPIC_')) and k != 'HOME'}
        env.update(HOME=str(home), PYTHONDONTWRITEBYTECODE='1')
        if harness == 'codex':
            env['CODEX_HOME'] = str(config)
            command = [executable, 'exec', '--ignore-user-config', '--ignore-rules',
                       '--ephemeral', '--skip-git-repo-check', '--sandbox', 'workspace-write',
                       '--json', prompt]
        else:
            env['CLAUDE_CONFIG_DIR'] = str(config)
            command = [executable, '-p', '--setting-sources', 'user,project',
                       '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                       '--tools', 'Skill,Read,Bash,Edit,Write',
                       '--allowedTools', 'Skill,Read,Bash,Edit,Write',
                       '--output-format', 'stream-json', '--verbose',
                       '--no-session-persistence', prompt]
        try:
            result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                    input='', text=True, timeout=600)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ''
            if isinstance(stdout, bytes):
                stdout = stdout.decode('utf-8', errors='replace')
            stderr, code = 'Harness timed out after 600 seconds', 124
        (output / 'stdout.jsonl').write_text(stdout, encoding='utf-8')
        (output / 'stderr.txt').write_text(stderr, encoding='utf-8')
        registry_path = project / 'design/sources.json'
        registry = json.loads(registry_path.read_text()) if registry_path.is_file() else None
        validation = subprocess.run([str(python), str(project / (
            '.agents' if harness == 'codex' else '.claude') /
            'skills/kkdesign-kit/scripts/kkdesign_project.py'),
            'validate', '--project', str(project)], capture_output=True, text=True)
        (output / 'validation.json').write_text(validation.stdout + validation.stderr)
        checks = {
            'harnessExitZero': code == 0,
            'productPreserved': (project / 'PRODUCT.md').read_bytes() == product,
            'kitValidationPass': validation.returncode == 0,
            'refreshedTokenValue': bool(registry and any(
                token['id'] == 'space.small' and token['data'].get('value') == 8
                for token in registry['assets']['tokens'])),
        }
        if registry:
            (output / 'source-registry.json').write_text(json.dumps(registry, indent=2) + '\n')
        record = {'harness': harness, 'version': version, 'scope': 'project',
                  'checks': checks, 'exitCode': code,
                  'rawTranscriptSha256': hashlib.sha256(stdout.encode()).hexdigest(),
                  'verdict': 'postconditions pass; transcript review required' if all(checks.values())
                             else 'failed; inspect private transcript',
                  'isolation': 'fresh home/project; extracted installed package; source extraction removed'}
        (output / 'probe.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record, indent=2))
        return 0 if all(checks.values()) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', required=True, choices=('codex', 'claude-code'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--python', type=Path, default=Path(sys.executable))
    parser.add_argument('--codex-auth-file', type=Path)
    parser.add_argument('--claude-credentials-file', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Keep private raw evidence outside the repository')
    try:
        return run_probe(args.harness, output, args.python.absolute(),
                         args.codex_auth_file, args.claude_credentials_file)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    sys.exit(main())
