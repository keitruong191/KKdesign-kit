import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_core as core


class PrototypePathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / 'project'
        self.project.mkdir()
        self.root = self.project / 'design/prototypes/demo'
        self.root.mkdir(parents=True)
        (self.root / 'index.html').write_text('<!doctype html>', encoding='utf-8')
        (self.root / 'README.md').write_text('Synthetic launch instructions', encoding='utf-8')
        self.outside = Path(self.temp.name) / 'outside'
        self.outside.mkdir()
        self.sentinel = self.outside / 'sentinel.txt'
        self.sentinel.write_text('preserve me', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def task(self, delivery='html_prototype', entry='design/prototypes/demo/index.html',
             instructions='design/prototypes/demo/README.md', cwd='design/prototypes/demo',
             mode='file', argv=None):
        launch = {'mode': mode, 'cwd': cwd}
        if argv is not None:
            launch['argv'] = argv
        return {
            'taskId': 'demo', 'delivery': delivery,
            'target': {'destination': 'design/prototypes/demo'},
            'handoff': {'artifacts': [{'entry': entry, 'instructions': instructions, 'launch': launch}]},
        }

    def errors(self, task, required=False):
        return core._validate_web_artifacts(self.project, task, require_delivery=required)

    def test_valid_project_relative_html_artifact_and_pending_absence(self):
        self.assertEqual(self.errors(self.task()), [])
        task = self.task()
        task['handoff']['artifacts'] = []
        self.assertEqual(self.errors(task), [])
        self.assertTrue(self.errors(task, required=True))

    def test_paths_reject_absolute_urls_and_lexical_traversal(self):
        bad_paths = (
            str(self.root / 'index.html'), '/design/prototypes/demo/index.html',
            r'C:\\design\\prototypes\\demo\\index.html',
            r'\\server\\share\\index.html', 'file:///tmp/index.html',
            'https://example.test/index.html', 'design/prototypes/demo/../demo/index.html',
        )
        for path in bad_paths:
            with self.subTest(path=path):
                self.assertTrue(self.errors(self.task(entry=path)), path)
        self.assertEqual(self.sentinel.read_text(encoding='utf-8'), 'preserve me')

    def test_artifact_root_must_be_task_scoped_project_relative(self):
        for destination in ('/tmp/demo', 'design/prototypes/other',
                            'design/prototypes/demo/../other', 'https://example.test/demo'):
            with self.subTest(destination=destination):
                task = self.task()
                task['target']['destination'] = destination
                self.assertTrue(self.errors(task))

    def test_missing_files_wrong_types_and_paths_outside_artifact_root_are_rejected(self):
        self.assertTrue(self.errors(self.task(entry='design/prototypes/demo/missing.html')))
        self.assertTrue(self.errors(self.task(instructions='design/prototypes/demo/missing.md')))
        self.assertTrue(self.errors(self.task(entry='design/prototypes/demo')))
        self.assertTrue(self.errors(self.task(instructions='design/prototypes/demo')))
        (self.project / 'design/prototypes/demo/subdir').mkdir()
        self.assertTrue(self.errors(self.task(entry='design/prototypes/demo/subdir')))
        self.assertTrue(self.errors(self.task(entry='design/other.html')))
        self.assertTrue(self.errors(self.task(instructions='design/other.md')))

    def test_symlinked_entry_instructions_and_parent_are_rejected(self):
        entry_link = self.root / 'linked.html'
        instruction_link = self.root / 'linked-instructions.md'
        parent_link = self.root / 'linked-parent'
        try:
            entry_link.symlink_to(self.sentinel)
            instruction_link.symlink_to(self.sentinel)
            parent_link.symlink_to(self.outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('symlinks unavailable: ' + str(exc))
        self.assertTrue(self.errors(self.task(entry='design/prototypes/demo/linked.html')))
        self.assertTrue(self.errors(self.task(instructions='design/prototypes/demo/linked-instructions.md')))
        self.assertTrue(self.errors(self.task(entry='design/prototypes/demo/linked-parent/entry.html')))
        self.assertTrue(self.errors(self.task(instructions='design/prototypes/demo/linked-parent/sentinel.txt')))
        self.assertEqual(self.sentinel.read_text(encoding='utf-8'), 'preserve me')

    def test_file_valued_artifact_root_is_rejected(self):
        (self.root / 'index.html').unlink()
        (self.root / 'README.md').unlink()
        self.root.rmdir()
        self.root.write_text('not a directory', encoding='utf-8')
        self.assertTrue(self.errors(self.task()))

    def test_launch_contract_rejects_bad_cwd_empty_argv_and_react_file_mode(self):
        self.assertEqual(self.errors(self.task(cwd='.', mode='file')), [])
        self.assertEqual(self.errors(self.task(cwd='.', mode='command', argv=['run'])), [])
        self.assertTrue(self.errors(self.task(cwd='../outside')))
        self.assertTrue(self.errors(self.task(cwd=str(self.outside))))
        self.assertTrue(self.errors(self.task(cwd='design/prototypes/demo/index.html', mode='command', argv=['run'])))
        self.assertTrue(self.errors(self.task(mode='command', argv=[])))
        self.assertTrue(self.errors(self.task(mode='command', argv=['run', 3])))
        self.assertTrue(self.errors(self.task(delivery='react_prototype', entry='design/prototypes/demo/index.jsx', mode='file')))


    def test_valid_react_command_launch_requires_existing_project_cwd(self):
        (self.root / 'App.jsx').write_text('export default function App() {}', encoding='utf-8')
        task = self.task(delivery='react_prototype', entry='design/prototypes/demo/App.jsx',
                         mode='command', cwd='design/prototypes/demo', argv=['npm', 'run', 'dev'])
        self.assertEqual(self.errors(task), [])
        task['handoff']['artifacts'][0]['launch']['cwd'] = 'design/prototypes/missing'
        self.assertTrue(self.errors(task))
        self.assertEqual(self.sentinel.read_text(encoding='utf-8'), 'preserve me')

    def test_actual_task_schema_accepts_valid_artifact_and_rejects_invalid_paths(self):
        record = json.loads((ROOT / 'examples/minimal/design/task-template.json').read_text(encoding='utf-8'))
        record.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'demo',
            'objective': 'Synthetic prototype path validation', 'platform': 'web',
            'productProfileId': 'example-web', 'delivery': 'html_prototype',
            'target': {'destination': 'design/prototypes/demo'},
            'handoff': {'artifacts': [{
                'entry': 'design/prototypes/demo/index.html',
                'instructions': 'design/prototypes/demo/README.md',
                'launch': {'mode': 'file', 'cwd': 'design/prototypes/demo'},
            }]},
        })
        schema = ROOT / 'schemas/task.schema.json'
        self.assertEqual(core.schema_errors(record, schema), [])
        for path in ('/tmp/index.html', 'https://example.test/index.html',
                     r'C:\\demo\\index.html', 'design/prototypes/demo/../index.html'):
            with self.subTest(path=path):
                invalid = json.loads(json.dumps(record))
                invalid['handoff']['artifacts'][0]['entry'] = path
                self.assertTrue(core.schema_errors(invalid, schema), path)
        react = json.loads(json.dumps(record))
        react['delivery'] = 'react_prototype'
        react['handoff']['artifacts'][0]['launch']['mode'] = 'file'
        command = json.loads(json.dumps(record))
        command['handoff']['artifacts'][0]['launch'] = {
            'mode': 'command', 'cwd': '.', 'argv': ['run'],
        }
        self.assertEqual(core.schema_errors(command, schema), [])
        file_launch = json.loads(json.dumps(record))
        file_launch['handoff']['artifacts'][0]['launch'] = {'mode': 'file'}
        self.assertEqual(core.schema_errors(file_launch, schema), [])
        malformed_argv = json.loads(json.dumps(command))
        malformed_argv['handoff']['artifacts'][0]['launch']['argv'] = ['run', 3]
        self.assertTrue(core.schema_errors(malformed_argv, schema))
        historical = json.loads(json.dumps(record))
        historical['delivery'] = 'figma_design'
        historical['target'] = {'destination': 'design-file://historical/arbitrary'}
        historical['handoff'] = {}
        self.assertEqual(core.schema_errors(historical, schema), [])

    def test_non_web_tasks_are_unchanged_by_web_artifact_gate(self):
        for delivery in ('figma_prototype', 'source_only', None):
            with self.subTest(delivery=delivery):
                self.assertEqual(self.errors({'delivery': delivery, 'target': {}, 'handoff': {}}), [])
        self.assertEqual(self.sentinel.read_text(encoding='utf-8'), 'preserve me')
    def test_validation_does_not_execute_launch_metadata(self):
        task = self.task(mode='command', argv=['python', '-c', 'raise SystemExit(93)'])
        self.assertEqual(self.errors(task), [])
        self.assertEqual(self.sentinel.read_text(encoding='utf-8'), 'preserve me')


if __name__ == '__main__':
    unittest.main()
