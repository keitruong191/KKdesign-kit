import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_task as tasks
from kkdesign_core import validate_foundation
from materialize_example import materialize


class PrototypeHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = materialize(Path(self.temp.name) / 'project with spaces')
        self.prototypes = self.project / 'design/prototypes/settings-prototype'
        self.prototypes.mkdir(parents=True)
        (self.prototypes / 'index demo.html').write_text('<!doctype html><title>Synthetic</title>', encoding='utf-8')
        (self.prototypes / 'README launch.md').write_text('Open index demo.html; synthetic offline demo.', encoding='utf-8')
        (self.prototypes / 'package.json').write_text('{"private":true}', encoding='utf-8')
        self.record_path = Path(self.temp.name) / 'task record.json'
        self.task = json.loads((self.project / 'design/task-template.json').read_text(encoding='utf-8'))
        self.task.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'settings-prototype',
            'objective': 'Exercise a synthetic settings interaction.', 'product': 'Synthetic product',
            'platform': 'web', 'productProfileId': 'example-web', 'delivery': 'html_prototype',
            'target': {'destination': 'design/prototypes/settings-prototype'},
            'designPlan': {
                'recipeId': None, 'platformProfileId': 'web',
                'layoutDecisions': [{'decision': 'Use a synthetic static HTML fixture.'}],
                'stateDispositions': [{'state': 'default', 'disposition': 'planned'}],
                'accessibilityChecks': [], 'referenceExamples': [], 'policyOverrides': []
            },
            'lessonReview': {
                'status': 'reviewed',
                'sourceHash': json.loads((self.project / 'design/lessons-index.json').read_text(encoding='utf-8'))['sourceHash'],
                'entries': [{'lessonId': 'DL-001', 'decision': 'apply', 'reason': 'Synthetic test fixture.',
                             'verification': 'pending', 'evidence': []}]
            },
            'handoff': {'artifacts': [{
                'entry': 'design/prototypes/settings-prototype/index demo.html',
                'instructions': 'design/prototypes/settings-prototype/README launch.md',
                'launch': {'mode': 'file', 'cwd': 'design/prototypes/settings-prototype'}
            }]}
        })
        self.record_path.write_text(json.dumps(self.task), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def launcher(self, *args):
        return subprocess.run(
            [sys.executable, '-B', str(ROOT / 'scripts/kkdesign_run.py'), 'kkdesign_task', *map(str, args)],
            cwd=ROOT, text=True, capture_output=True)

    def begin(self):
        result = self.launcher('begin', '--project', self.project, '--record', self.record_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.project / 'design/tasks/settings-prototype/task.json'

    def evidence(self, references=None):
        payload = Path(self.temp.name) / 'browser evidence.json'
        payload.write_text(json.dumps({'browser': 'synthetic fixture', 'viewport': '800x600',
                                       'actions': ['open settings'], 'observation': 'static fixture only',
                                       'simulations': ['offline'], 'gaps': ['no browser run claimed']}), encoding='utf-8')
        args = ['evidence', '--project', self.project, '--task-id', 'settings-prototype',
                '--type', 'snapshot', '--description', 'Synthetic fixture evidence; not browser acceptance.',
                '--payload', payload]
        for reference in references or []:
            args.extend(['--reference', reference])
        result = self.launcher(*args)
        self.assertEqual(result.returncode, 0, result.stderr)

    def handoff(self, overrides=None):
        body = {'frameLinks': [], 'createdNodeIds': [], 'modifiedNodeIds': [], 'remainingGaps': [],
                'checks': [{'requirement': 'Synthetic settings route', 'evidence': ['evidence-0001.json']}],
                'requirementStateMapping': [{'requirement': 'Synthetic settings route', 'state': 'default',
                                             'evidence': ['evidence-0001.json']}],
                'artifacts': self.task['handoff']['artifacts']}
        if overrides:
            body.update(overrides)
        path = Path(self.temp.name) / 'handoff.json'
        path.write_text(json.dumps(body), encoding='utf-8')
        return path

    def test_launcher_begin_evidence_check_and_artifact_only_delivery(self):
        task_path = self.begin()
        self.evidence()
        check = self.launcher('check', '--project', self.project, '--task-id', 'settings-prototype')
        self.assertEqual(check.returncode, 0, check.stderr)
        checked = json.loads(check.stdout)
        self.assertEqual(checked['evidenceRecords'], 1)
        self.assertIn('not live behavior', checked['scope'])
        update = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(update.returncode, 0, update.stderr)
        stored = json.loads(task_path.read_text(encoding='utf-8'))
        self.assertEqual(stored['status'], 'design_delivered')
        self.assertEqual(stored['schemaVersion'], self.task['schemaVersion'])
        self.assertEqual(stored['handoff']['frameLinks'], [])
        self.assertTrue((self.prototypes / 'package.json').is_file())
        self.assertEqual(len(list((task_path.parent).glob('*.json'))), 2)
        self.assertEqual(validate_foundation(self.project / 'design')['status'], 'pass')

    def test_missing_artifact_or_mapping_or_citation_cannot_be_bypassed_and_preserves_task(self):
        task_path = self.begin()
        self.evidence()
        original = task_path.read_bytes()
        cases = [
            ({'artifacts': [], 'blockedDisposition': 'blocked',
              'frameLinks': ['https://figma.example.invalid/file/fake']}, 'artifact'),
            ({'requirementStateMapping': [], 'blockedDisposition': 'blocked'}, 'mapping'),
            ({'checks': [], 'blockedDisposition': 'blocked'}, 'empty checks'),
            ({'checks': [{'requirement': 'Synthetic', 'evidence': []}],
              'blockedDisposition': 'blocked'}, 'empty citation'),
            ({'checks': [{'requirement': 'Synthetic', 'evidence': ['missing.json']}],
              'blockedDisposition': 'blocked'}, 'missing citation'),
            ({'artifacts': [{'entry': 'https://invalid.example/app.html',
                             'instructions': 'design/prototypes/settings-prototype/README launch.md',
                             'launch': {'mode': 'file', 'cwd': 'design/prototypes/settings-prototype'}}]},
             'malformed artifact refs'),
        ]
        for updates, message in cases:
            with self.subTest(message=message):
                result = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                       '--record', self.handoff(updates), '--status', 'design_delivered')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(task_path.read_bytes(), original)
                self.assertEqual(json.loads(task_path.read_text())['status'], 'in_progress')

    def test_deleted_entry_is_rejected_by_check_and_foundation_after_delivery(self):
        task_path = self.begin()
        self.evidence()
        result = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.prototypes / 'index demo.html').unlink()
        check = self.launcher('check', '--project', self.project, '--task-id', 'settings-prototype')
        self.assertNotEqual(check.returncode, 0)
        self.assertIn('artifact', check.stderr.lower())
        foundation = validate_foundation(self.project / 'design')
        self.assertEqual(foundation['status'], 'fail', foundation)
        self.assertIn('artifact', '\n'.join(foundation['errors']).lower())
        self.assertEqual(json.loads(task_path.read_text())['status'], 'design_delivered')

    def test_incomplete_artifact_does_not_allow_partial_application_to_be_delivered(self):
        (self.prototypes / 'index demo.html').unlink()
        result = self.launcher('begin', '--project', self.project, '--record', self.record_path)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project / 'design/tasks/settings-prototype').exists())

    def test_empty_begin_then_artifact_refs_and_delivery_gates(self):
        shutil.rmtree(self.prototypes)
        self.task['handoff']['artifacts'] = []
        self.record_path.write_text(json.dumps(self.task), encoding='utf-8')
        task_path = self.begin()
        self.prototypes.mkdir(parents=True)
        (self.prototypes / 'index demo.html').write_text('<!doctype html>', encoding='utf-8')
        (self.prototypes / 'README launch.md').write_text('Open index demo.html.', encoding='utf-8')
        self.task['handoff']['artifacts'] = [{
            'entry': 'design/prototypes/settings-prototype/index demo.html',
            'instructions': 'design/prototypes/settings-prototype/README launch.md',
            'launch': {'mode': 'file', 'cwd': 'design/prototypes/settings-prototype'}
        }]
        self.evidence(['../../prototypes/settings-prototype/index demo.html'])
        result = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.launcher('check', '--project', self.project,
                                       '--task-id', 'settings-prototype').returncode, 0)
        self.assertEqual(validate_foundation(self.project / 'design')['status'], 'pass')
        self.assertEqual(json.loads(task_path.read_text())['status'], 'design_delivered')

    def test_partial_entry_only_can_be_blocked_then_completed_without_deleting_user_work(self):
        shutil.rmtree(self.prototypes)
        self.task['handoff']['artifacts'] = []
        self.record_path.write_text(json.dumps(self.task), encoding='utf-8')
        task_path = self.begin()
        self.prototypes.mkdir(parents=True)
        entry = self.prototypes / 'index demo.html'
        entry.write_text('<!doctype html>', encoding='utf-8')
        self.evidence(['../../prototypes/settings-prototype/index demo.html'])
        partial = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                '--record', self.handoff({'artifacts': [], 'blockedDisposition': 'README incomplete'}),
                                '--status', 'in_progress')
        self.assertEqual(partial.returncode, 0, partial.stderr)
        self.assertTrue(entry.is_file())
        self.assertEqual(json.loads(task_path.read_text())['status'], 'in_progress')
        (self.prototypes / 'README launch.md').write_text('Open index demo.html.', encoding='utf-8')
        self.task['handoff']['artifacts'] = [{
            'entry': 'design/prototypes/settings-prototype/index demo.html',
            'instructions': 'design/prototypes/settings-prototype/README launch.md',
            'launch': {'mode': 'file', 'cwd': 'design/prototypes/settings-prototype'}
        }]
        delivered = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                  '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(delivered.returncode, 0, delivered.stderr)
        self.assertTrue(entry.is_file())

    def test_react_command_mode_does_not_execute_recorded_argv_or_count_package_json_as_evidence(self):
        task = json.loads(json.dumps(self.task))
        task['delivery'] = 'react_prototype'
        task['handoff']['artifacts'] = []
        self.record_path.write_text(json.dumps(task), encoding='utf-8')
        task_path = self.begin()
        (self.prototypes / 'App.jsx').write_text('export default function App() {}', encoding='utf-8')
        sentinel = Path(self.temp.name) / 'unexpected execution.txt'
        task['handoff']['artifacts'] = [{
            'entry': 'design/prototypes/settings-prototype/App.jsx',
            'instructions': 'design/prototypes/settings-prototype/README launch.md',
            'launch': {'mode': 'command', 'cwd': '.', 'argv': [sys.executable, '-c',
                    "open(" + repr(str(sentinel)) + ", 'w').write('ran')"]}
        }]
        self.task = task
        self.evidence(['../../prototypes/settings-prototype/App.jsx'])
        result = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(sentinel.exists())
        self.assertEqual({path.name for path in task_path.parent.glob('*.json')},
                         {'task.json', 'evidence-0001.json'})
        self.assertEqual(self.launcher('check', '--project', self.project,
                                       '--task-id', 'settings-prototype').returncode, 0)
        self.assertEqual(validate_foundation(self.project / 'design')['status'], 'pass')

    def test_handoff_after_delivered_entry_rename_uses_new_candidate_paths(self):
        task_path = self.begin()
        self.evidence()
        first = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                              '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.prototypes / 'index demo.html').rename(self.prototypes / 'renamed entry.html')
        (self.prototypes / 'README launch.md').rename(self.prototypes / 'renamed guide.md')
        self.task['handoff']['artifacts'][0].update(
            entry='design/prototypes/settings-prototype/renamed entry.html',
            instructions='design/prototypes/settings-prototype/renamed guide.md')
        corrected = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                  '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        stored = json.loads(task_path.read_text())
        self.assertEqual(stored['handoff']['artifacts'][0]['entry'],
                         'design/prototypes/settings-prototype/renamed entry.html')
        downgraded = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                   '--record', self.handoff({'artifacts': [],
                                                             'blockedDisposition': 'No current runnable build'}),
                                   '--status', 'in_progress')
        self.assertEqual(downgraded.returncode, 0, downgraded.stderr)
        self.assertEqual(json.loads(task_path.read_text())['status'], 'in_progress')
        self.assertTrue((self.prototypes / 'renamed entry.html').is_file())

    def test_deleted_readme_after_delivery_is_detected_by_check_and_foundation(self):
        task_path = self.begin()
        self.evidence()
        result = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff(), '--status', 'design_delivered')
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.prototypes / 'README launch.md').unlink()
        check = self.launcher('check', '--project', self.project, '--task-id', 'settings-prototype')
        self.assertNotEqual(check.returncode, 0)
        foundation = validate_foundation(self.project / 'design')
        self.assertEqual(foundation['status'], 'fail', foundation)
        self.assertIn('artifact', '\n'.join(foundation['errors']).lower())
        self.assertEqual(json.loads(task_path.read_text())['status'], 'design_delivered')

    def test_partial_app_after_begin_remains_in_progress_when_readme_disappears(self):
        task_path = self.begin()
        self.evidence()
        (self.prototypes / 'README launch.md').unlink()
        original = task_path.read_bytes()
        handoff = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                '--record', self.handoff(), '--status', 'design_delivered')
        self.assertNotEqual(handoff.returncode, 0)
        self.assertEqual(task_path.read_bytes(), original)
        self.assertEqual(json.loads(original)['status'], 'in_progress')
        check = self.launcher('check', '--project', self.project, '--task-id', 'settings-prototype')
        self.assertNotEqual(check.returncode, 0)

    def test_legacy_figma_delivery_keeps_existing_frame_link_gate(self):
        task = json.loads(json.dumps(self.task))
        task['delivery'] = 'figma_prototype'
        task['handoff'].pop('artifacts')
        task['target'] = {'destination': 'design-file://synthetic/settings'}
        self.record_path.write_text(json.dumps(task), encoding='utf-8')
        task_path = self.begin()
        self.evidence()
        no_link = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                                '--record', self.handoff({'artifacts': []}), '--status', 'design_delivered')
        self.assertNotEqual(no_link.returncode, 0)
        self.assertEqual(json.loads(task_path.read_text())['status'], 'in_progress')
        linked = self.launcher('handoff', '--project', self.project, '--task-id', 'settings-prototype',
                               '--record', self.handoff({'artifacts': [], 'frameLinks': [
                                   'https://figma.example.invalid/file/synthetic']}), '--status', 'design_delivered')
        self.assertEqual(linked.returncode, 0, linked.stderr)
        self.assertEqual(json.loads(task_path.read_text())['status'], 'design_delivered')

    def test_failed_temp_creation_or_replace_preserves_existing_task_bytes(self):
        task_path = self.begin()
        self.evidence()
        original = task_path.read_bytes()
        handoff_path = self.handoff()
        real_open = Path.open
        def fail_temp_open(path, *args, **kwargs):
            if path.name == 'task.json.tmp':
                raise OSError('synthetic temp creation failure')
            return real_open(path, *args, **kwargs)
        with mock.patch.object(Path, 'open', fail_temp_open):
            with self.assertRaisesRegex(OSError, 'temp creation'):
                tasks.update_handoff(self.project, 'settings-prototype', handoff_path, 'design_delivered')
        self.assertEqual(task_path.read_bytes(), original)
        with mock.patch.object(Path, 'replace', side_effect=OSError('synthetic replace failure')):
            with self.assertRaisesRegex(OSError, 'replace failure'):
                tasks.update_handoff(self.project, 'settings-prototype', handoff_path, 'design_delivered')
        self.assertEqual(task_path.read_bytes(), original)
        self.assertEqual(list(task_path.parent.glob('task.json.tmp')), [])


if __name__ == '__main__':
    unittest.main()
