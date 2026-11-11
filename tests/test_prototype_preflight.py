import json
import multiprocessing
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_project as project
import kkdesign_task as tasks
from kkdesign_core import build_lesson_index
from materialize_example import materialize


def _write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _begin_at_barrier(project, record_path, barrier, reached, results):
    original_mkdir = Path.mkdir
    task_directory = (Path(project).resolve() / 'design/tasks/prototype-race').resolve()

    def synchronized_mkdir(path, *args, **kwargs):
        if path.resolve() == task_directory:
            reached.put(os.getpid())
            barrier.wait(timeout=10)
        return original_mkdir(path, *args, **kwargs)

    with patch.object(Path, 'mkdir', synchronized_mkdir):
        try:
            results.put(('begun', tasks.begin(project, record_path)))
        except Exception as exc:
            results.put(('error', type(exc).__name__, str(exc)))


class PrototypePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = materialize(self.root / 'project')
        self.design = self.project / 'design'
        self.record_path = self.root / 'task.json'
        self.record = json.loads((self.design / 'task-template.json').read_text(encoding='utf-8'))
        self.record.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'prototype-preflight',
            'objective': 'Record a synthetic prototype plan.', 'product': 'Fictional example',
            'platform': 'web', 'productProfileId': 'example-web',
            'delivery': 'html_prototype',
            'target': {'destination': 'design/prototypes/prototype-preflight'},
            'states': {'required': ['default'], 'notApplicable': []},
            'designPlan': {
                'recipeId': None, 'platformProfileId': 'web',
                'layoutDecisions': [{'decision': 'Use the existing product layout and bindings.'}],
                'stateDispositions': [{'state': 'default', 'disposition': 'planned'}],
                'accessibilityChecks': [], 'referenceExamples': [], 'policyOverrides': []
            },
            'lessonReview': {'status': 'reviewed', 'sourceHash': self._lesson_index()['sourceHash'],
                             'entries': [self._lesson_decision('DL-001')]}
        })
        self._save_record()

    def tearDown(self):
        self.temp.cleanup()

    def _lesson_index(self):
        return json.loads((self.design / 'lessons-index.json').read_text(encoding='utf-8'))

    @staticmethod
    def _lesson_decision(lesson_id):
        return {'lessonId': lesson_id, 'decision': 'apply',
                'reason': 'Apply guidance relevant to this product platform.',
                'verification': 'pending', 'evidence': []}

    def _save_record(self):
        _write_json(self.record_path, self.record)

    def _initialized_ios_task(self):
        source_root = self.root / 'one'
        source_root.mkdir()
        source = {'schemaVersion': '1.0.0', **{name: [] for name in project.CATEGORIES}}
        _write_json(source_root / 'ds.json', source)
        sources = self.root / 'sources.json'
        _write_json(sources, {'sources': [{'id': 'ds', 'provider': 'local', 'location': 'one'}]})
        context = self.root / 'context.json'
        _write_json(context, {'product': {'name': 'Synthetic iOS product', 'platforms': ['ios']}})
        initialized = self.root / 'initialized-ios'

        plan = project.init_project(initialized, sources, context)
        project.inspect_plan(initialized, plan['id'])
        project.apply_plan(initialized, plan['id'])

        design = initialized / 'design'
        profile = json.loads((design / 'profiles/ios.json').read_text(encoding='utf-8'))
        index = json.loads((design / 'lessons-index.json').read_text(encoding='utf-8'))
        record = json.loads((design / 'task-template.json').read_text(encoding='utf-8'))
        record.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'initialized-prototype',
            'objective': 'Record a synthetic initialized-project prototype plan.',
            'product': 'Synthetic iOS product', 'platform': 'ios',
            'productProfileId': profile['id'], 'delivery': 'html_prototype',
            'target': {'destination': 'design/prototypes/initialized-prototype'},
            'states': {'required': ['default'], 'notApplicable': []},
            'designPlan': {
                'recipeId': None, 'platformProfileId': 'ios',
                'layoutDecisions': [{'decision': 'Use the generated product profile and existing DS.'}],
                'stateDispositions': [{'state': 'default', 'disposition': 'planned'}],
                'accessibilityChecks': [], 'referenceExamples': [], 'policyOverrides': []
            },
            'lessonReview': {
                'status': 'reviewed', 'sourceHash': index['sourceHash'],
                'entries': [self._lesson_decision('DL-001')]
            }
        })
        record_path = self.root / 'initialized-task.json'
        _write_json(record_path, record)
        return initialized, design, record_path, record, profile

    def _task_directory(self):
        return self.design / 'tasks' / self.record['taskId']

    def _assert_rejected_before_mutation(self):
        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse(self._task_directory().exists())
        self.assertFalse((self.project / 'design/prototypes/prototype-preflight').exists())

    def test_both_web_deliveries_begin_without_generating_app_files(self):
        for delivery in ('html_prototype', 'react_prototype'):
            with self.subTest(delivery=delivery):
                self.record['delivery'] = delivery
                self._save_record()
                result = tasks.begin(self.project, self.record_path)
                self.assertEqual(result['status'], 'begun')
                self.assertEqual(result['taskId'], 'prototype-preflight')
                saved = json.loads((self._task_directory() / 'task.json').read_text(encoding='utf-8'))
                self.assertEqual(saved['platform'], 'web')
                self.assertEqual(saved['delivery'], delivery)
                self.assertFalse((self.project / 'design/prototypes/prototype-preflight').exists())
                shutil.rmtree(self._task_directory())

    def test_ios_product_and_lessons_stay_platform_specific_with_browser_delivery(self):
        lesson_source = self.design / 'LESSON.md'
        lesson_source.write_text(lesson_source.read_text(encoding='utf-8') + '\n'
                                 '<a id="DL-002"></a>\n'
                                 '### DL-002 · iOS-only synthetic guidance\n\n'
                                 '<!-- kkdesign-lesson {"id":"DL-002","status":"active",'
                                 '"platforms":["ios"],"tags":[],"appliesWhen":"For iOS tasks.",'
                                 '"evidence":["../PRODUCT.md"],"originTask":null} -->\n\n'
                                 'Use the native product platform constraints.\n\n'
                                 '**Verification:** Record platform-specific readback before claiming compliance.\n',
                                 encoding='utf-8')
        index = build_lesson_index(self.design)
        _write_json(self.design / 'lessons-index.json',
                    {'$schema': 'schemas/lesson-index.schema.json', **index})
        ios_profile = json.loads((self.design / 'profiles/example-web.json').read_text(encoding='utf-8'))
        ios_profile.update(id='example-ios', platform='ios')
        _write_json(self.design / 'profiles/example-ios.json', ios_profile)
        self.record.update(platform='ios', productProfileId='example-ios', delivery='html_prototype')
        self.record['designPlan']['platformProfileId'] = 'ios'
        self.record['lessonReview'] = {
            'status': 'reviewed', 'sourceHash': index['sourceHash'],
            'entries': [self._lesson_decision('DL-001'), self._lesson_decision('DL-002')]
        }
        self._save_record()

        result = tasks.begin(self.project, self.record_path)
        self.assertEqual(result['status'], 'begun')
        saved = json.loads((self._task_directory() / 'task.json').read_text(encoding='utf-8'))
        self.assertEqual(saved['platform'], 'ios')
        self.assertEqual(saved['productProfileId'], 'example-ios')
        self.assertEqual(saved['delivery'], 'html_prototype')
        self.assertEqual({entry['lessonId'] for entry in saved['lessonReview']['entries']},
                         {'DL-001', 'DL-002'})
        self.assertFalse((self.project / 'design/prototypes/prototype-preflight').exists())

    def test_initialized_project_generates_profile_then_begin_check_and_foundation_pass(self):
        initialized, design, record_path, _, profile = self._initialized_ios_task()
        self.assertEqual(profile['platform'], 'ios')

        tasks.begin(initialized, record_path)
        task_path = design / 'tasks/initialized-prototype/task.json'
        saved = json.loads(task_path.read_text(encoding='utf-8'))
        self.assertEqual(saved['productProfileId'], profile['id'])
        self.assertEqual(saved['platform'], 'ios')
        self.assertEqual(tasks.check_task(initialized, 'initialized-prototype')['status'], 'checked')
        result = project.validate_project(initialized)
        self.assertEqual(result['status'], 'pass', result)

    def test_generated_ios_profile_rejects_mismatched_task_platform_before_begin(self):
        initialized, design, record_path, record, _ = self._initialized_ios_task()
        record['platform'] = 'web'
        record['designPlan']['platformProfileId'] = 'web'
        _write_json(record_path, record)

        with self.assertRaises(ValueError):
            tasks.begin(initialized, record_path)
        self.assertFalse((design / 'tasks/initialized-prototype').exists())
        self.assertFalse((initialized / record['target']['destination']).exists())

    def test_invalid_destination_forms_reject_before_begin(self):
        invalid_destinations = (
            'design/prototypes/other',
            'https://example.invalid/prototype',
            '/tmp/prototype-preflight',
            'design/prototypes/../prototype-preflight',
        )
        for destination in invalid_destinations:
            with self.subTest(destination=destination):
                self.record['target']['destination'] = destination
                self._save_record()
                with self.assertRaises(ValueError):
                    tasks.begin(self.project, self.record_path)
                self.assertFalse(self._task_directory().exists())
                self.assertFalse((self.project / 'design/prototypes/prototype-preflight').exists())

    def test_symlink_destination_root_rejects_before_begin(self):
        prototype_parent = self.design / 'prototypes'
        prototype_parent.mkdir()
        outside = self.root / 'outside-root'
        outside.mkdir()
        (prototype_parent / 'prototype-preflight').symlink_to(outside, target_is_directory=True)

        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse(self._task_directory().exists())

    def test_regular_file_destination_root_rejects_before_begin(self):
        prototype_parent = self.design / 'prototypes'
        prototype_parent.mkdir()
        (prototype_parent / 'prototype-preflight').write_text('not a directory', encoding='utf-8')

        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse(self._task_directory().exists())

    def test_regular_file_destination_ancestor_rejects_before_begin(self):
        (self.design / 'prototypes').write_text('not a directory', encoding='utf-8')

        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse(self._task_directory().exists())

    def test_symlink_destination_ancestor_rejects_before_begin(self):
        outside = self.root / 'outside-parent'
        outside.mkdir()
        (self.design / 'prototypes').symlink_to(outside, target_is_directory=True)

        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse(self._task_directory().exists())

    def test_duplicate_begin_preserves_existing_task_and_artifact_bytes(self):
        tasks.begin(self.project, self.record_path)
        task_path = self._task_directory() / 'task.json'
        original_task = task_path.read_bytes()
        artifact_root = self.project / 'design/prototypes/prototype-preflight'
        artifact_root.mkdir(parents=True)
        artifact = artifact_root / 'index.html'
        artifact.write_text('<!doctype html><title>synthetic</title>\n', encoding='utf-8')
        original_artifact = artifact.read_bytes()

        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertEqual(task_path.read_bytes(), original_task)
        self.assertEqual(artifact.read_bytes(), original_artifact)

    def test_stale_task_lesson_source_hash_rejects_before_mutation(self):
        self.record['lessonReview']['sourceHash'] = '0' * 64
        self._save_record()
        self._assert_rejected_before_mutation()

    def test_stale_lesson_index_source_rejects_before_mutation(self):
        lesson_source = self.design / 'LESSON.md'
        lesson_source.write_text(lesson_source.read_text(encoding='utf-8') + '\nChanged source.\n',
                                 encoding='utf-8')
        self._assert_rejected_before_mutation()

    def test_missing_product_profile_rejects_before_mutation(self):
        (self.design / 'profiles/example-web.json').unlink()
        self._assert_rejected_before_mutation()

    def test_missing_destination_rejects_before_mutation(self):
        self.record['target'].pop('destination')
        self._save_record()
        self._assert_rejected_before_mutation()

    def test_invalid_planning_rejects_before_mutation(self):
        self.record['designPlan']['layoutDecisions'] = []
        self._save_record()
        self._assert_rejected_before_mutation()

    def test_concurrent_begin_has_one_owner_and_preserves_saved_task(self):
        self.record['taskId'] = 'prototype-race'
        self.record['target']['destination'] = 'design/prototypes/prototype-race'
        self._save_record()
        context = multiprocessing.get_context('spawn')
        barrier = context.Barrier(2)
        reached = context.Queue()
        results = context.Queue()
        processes = [context.Process(target=_begin_at_barrier,
                                     args=(str(self.project), str(self.record_path),
                                           barrier, reached, results))
                     for _ in range(2)]
        for process in processes:
            process.start()
        reached_processes = [reached.get(timeout=20) for _ in processes]
        outcomes = [results.get(timeout=20) for _ in processes]
        for process in processes:
            process.join(timeout=20)
            self.assertFalse(process.is_alive(), 'begin process did not finish')
            self.assertEqual(process.exitcode, 0)

        self.assertEqual(len(set(reached_processes)), 2, reached_processes)
        self.assertEqual(sum(outcome[0] == 'begun' for outcome in outcomes), 1, outcomes)
        self.assertEqual(sum(outcome[0] == 'error' for outcome in outcomes), 1, outcomes)
        saved_path = self.design / 'tasks/prototype-race/task.json'
        saved_bytes = saved_path.read_bytes()
        saved = json.loads(saved_bytes.decode('utf-8'))
        self.assertEqual(saved['taskId'], 'prototype-race')
        self.assertEqual(saved['objective'], self.record['objective'])
        self.assertEqual(saved['lessonReview'], self.record['lessonReview'])
        self.assertEqual(saved_path.read_bytes(), saved_bytes)
        self.assertFalse((self.project / 'design/prototypes/prototype-race').exists())

    def test_non_object_profile_rejects_before_task_or_artifact_mutation(self):
        (self.design / 'profiles/example-web.json').write_text('[]', encoding='utf-8')
        with self.assertRaises(ValueError):
            tasks.begin(self.project, self.record_path)
        self.assertFalse((self.design / 'tasks' / self.record['taskId']).exists())
        self.assertFalse((self.project / self.record['target']['destination']).exists())


if __name__ == '__main__':
    unittest.main()
