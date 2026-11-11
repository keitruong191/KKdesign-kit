#!/usr/bin/env python3
"""Historical standalone maintainer probe; not a marketplace helper entrypoint.

Opt-in B3 installed-workflow probe. Raw transcripts stay outside the public repo."""
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
from kkdesign_install import ROOT, lifecycle, package, verify
from materialize_example import materialize
from kkdesign_core import build_lesson_index


def run_probe(harness, output, credential=None):
    executable = shutil.which('codex' if harness == 'codex' else 'claude')
    if not executable:
        raise ValueError('Harness executable unavailable')
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    version = subprocess.check_output([executable, '--version'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='kkdesign B3 live spaces ') as temp:
        base = Path(temp).resolve()
        home = base / 'home'
        home.mkdir()
        project = materialize(base / 'synthetic project')
        (project / 'review-notes.md').write_text(
            '# Synthetic feedback evidence\n\nThe selected control is hard to distinguish.\n'
            'Invented feedback for this acceptance probe, not a real product finding.\n')
        product = (project / 'PRODUCT.md').read_bytes()
        before = (project / 'design/LESSON.md').read_bytes()
        config = home / ('.codex' if harness == 'codex' else '.claude')
        config.mkdir()
        if credential:
            target = config / ('auth.json' if harness == 'codex' else '.credentials.json')
            shutil.copyfile(credential, target)
            target.chmod(0o600)
        archive = base / 'kit.zip'
        package(ROOT, archive)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(base / 'extracted')
        source = base / 'extracted/kkdesign-kit'
        verify(source)
        lifecycle('install', harness, 'project', home, project, source, runtime=True)
        shutil.rmtree(source)
        installed = project / ('.agents' if harness == 'codex' else '.claude') / 'skills/kkdesign-kit'
        invocation = '$kkdesign-kit' if harness == 'codex' else '/kkdesign-kit'
        prompt = invocation + ' design\n' + (
            'Authorized B3 acceptance probe in this disposable SYNTHETIC project. Use only '
            'the discovered installed skill and its actual bundled helpers, not replacement '
            'implementations. Read the command routes needed below. Use python3 -B '
            'SKILL_DIR/scripts/kkdesign_run.py HELPER. Project is the current directory. No network, MCP, installed '
            'Impeccable/Hoangsa, original checkout, user config or credential reads. '
            '1. Read project context, scoped example-web profile and canonical lessons. '
            'Begin a task named harness-design: Operate-mode web settings with default, '
            'error and long-content states. This is an offline planned fixture, not a Figma '
            'file: target location is the local review-notes.md fixture. Record tool access '
            'as unavailable; do not fabricate frames, renders or a delivered design. '
            'Record reviewed applicable lessons, pending verification and explicit gaps. '
            '2. Invoke the review route and run its bundled review helper on '
            'examples/review/flawed-design.json under the installed skill. Report all '
            'supported seeded defects as findings, no fixes/native approval. '
            '3. Invoke learn: capture the synthetic feedback in review-notes.md, scope web, '
            'origin acceptance-probe; author one inferred lesson about distinguishable '
            'control states linked to that feedback and local evidence, then repeat BOTH '
            'identical operations to demonstrate deduplication. Do not change existing '
            'task decisions. Read the updated canonical lesson and begin a SECOND task '
            'harness-after-learn with a reasoned apply decision for that new lesson, '
            'verification pending, same offline scope. '
            '4. Invoke package: build public-kit.zip outside the installed skill, extract '
            'to public-extraction/, and run the EXTRACTED verify command. Validate the '
            'project foundation. Leave all outputs for independent checks. '
            'This prompt requests design/review/learn/package ONLY. Do not create or change '
            'prototype interactions. Report exact commands/results and all scoped limitations; '
            'do not merely describe commands. Do not claim live Figma/native/human approval.')
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
            proc = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                  input='', text=True, timeout=600)
            stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ''
            if isinstance(stdout, bytes):
                stdout = stdout.decode('utf-8', errors='replace')
            stderr, code = 'Harness timed out after 600 seconds', 124
        (output / 'stdout.jsonl').write_text(stdout, encoding='utf-8')
        (output / 'stderr.txt').write_text(stderr, encoding='utf-8')
        validation = subprocess.run([sys.executable, '-B', str(installed / 'scripts/kkdesign_run.py'),
                                     'kkdesign_core', 'validate', '--design', str(project / 'design')],
                                    capture_output=True, text=True)
        (output / 'validation.json').write_text(validation.stdout + validation.stderr)
        index = build_lesson_index(project / 'design')
        feedback_path = project / 'design/feedback.json'
        feedback = json.loads(feedback_path.read_text()) if feedback_path.exists() else None
        after_path = project / 'design/tasks/harness-after-learn/task.json'
        after = json.loads(after_path.read_text()) if after_path.exists() else {}
        new_lessons = [item for item in index['lessons'] if item['id'] != 'DL-001']
        entries = after.get('lessonReview', {}).get('entries', [])
        package_check = None
        extracted = project / 'public-extraction/kkdesign-kit'
        if extracted.is_dir():
            package_check = verify(extracted)
        checks = {
            'harnessExitZero': code == 0,
            'productPreserved': (project / 'PRODUCT.md').read_bytes() == product,
            'foundationValid': validation.returncode == 0,
            'designTaskCreated': (project / 'design/tasks/harness-design/task.json').is_file(),
            'oneNewCanonicalLesson': len(new_lessons) == 1 and (project / 'design/LESSON.md').read_bytes() != before,
            'oneDirectFeedbackRecord': isinstance(feedback, list) and len(feedback) == 1,
            'subsequentTaskDecision': bool(new_lessons and any(
                entry.get('lessonId') == new_lessons[0]['id'] and entry.get('decision') == 'apply'
                and entry.get('verification') == 'pending' for entry in entries)),
            'extractedPackageVerified': bool(package_check and package_check['status'] == 'verified'),
            'noPrototypeArtifact': (
                not any((project / 'design/tasks').rglob('*prototype*'))
                and not any((project / 'design/prototypes').rglob('*'))
            ),
        }
        for name in ('design/LESSON.md', 'design/lessons-index.json', 'design/feedback.json',
                     'design/tasks/harness-design/task.json', 'design/tasks/harness-after-learn/task.json'):
            path = project / name
            if path.exists():
                destination = output / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
        record = {'harness': harness, 'version': version, 'scope': 'project',
                  'checks': checks, 'exitCode': code,
                  'feedbackRecord': feedback,
                  'rawTranscriptSha256': hashlib.sha256(stdout.encode()).hexdigest(),
                  'verdict': 'postconditions pass; transcript review required' if all(checks.values()) else 'failed; inspect transcript',
                  'isolation': 'fresh home/project; extracted installed skill; no Impeccable/Hoangsa/MCP; original extraction removed',
                  'boundary': 'Offline task/fixture/learn/package execution, not live canvas/native approval'}
        (output / 'probe.json').write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps(record, indent=2))
        return 0 if all(checks.values()) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', required=True, choices=('codex', 'claude-code'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--credential', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Keep private raw evidence outside the repository')
    try:
        return run_probe(args.harness, output, args.credential)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    sys.exit(main())
