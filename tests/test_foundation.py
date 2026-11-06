import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from kkdesign_core import build_lesson_index, save, validate_foundation
from materialize_example import materialize


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = materialize(Path(self.temp.name) / 'project with spaces')
        self.design = self.root / 'design'
        self.task_path = self.design / 'tasks/demo/task.json'

    def tearDown(self):
        self.temp.cleanup()

    def change(self, path, operation):
        doc = json.loads(path.read_text(encoding='utf-8'))
        operation(doc)
        save(path, doc)

    def result(self):
        return validate_foundation(self.design)

    def fails(self, text):
        result = self.result()
        self.assertEqual(result['status'], 'fail', result)
        self.assertIn(text, '\n'.join(result['errors']))

    def review(self, **updates):
        index = json.loads((self.design / 'lessons-index.json').read_text())
        review = {'status': 'reviewed', 'sourceHash': index['sourceHash'], 'entries': [
            {'lessonId': 'DL-001', 'decision': 'apply', 'reason': 'Explicit task selection.',
             'verification': 'pending', 'evidence': []}]}
        review.update(updates)
        self.change(self.task_path, lambda d: d.update(lessonReview=review))

    def test_portable_fixture_passes_without_memory_figma_or_installed_skills(self):
        self.assertEqual(self.result()['status'], 'pass', self.result())

    def test_markdown_change_stales_index(self):
        path = self.design / 'LESSON.md'
        path.write_text(path.read_text() + '\nNew advice.\n')
        self.fails('stale index')

    def test_index_rebuild_is_deterministic(self):
        self.assertEqual(build_lesson_index(self.design), build_lesson_index(self.design))

    def test_duplicate_lesson_id_rejected(self):
        path = self.design / 'LESSON.md'
        path.write_text(path.read_text() + '\n' + path.read_text())
        self.fails('Duplicate lesson ID')

    def test_missing_lesson_evidence_fails(self):
        (self.root / 'PRODUCT.md').unlink()
        self.fails('Missing reference')

    def test_unknown_lesson_id_fails(self):
        self.review()
        self.change(self.task_path, lambda d: d['lessonReview']['entries'][0].update(lessonId='DL-999'))
        self.fails('unknown lesson ID')

    def test_stale_task_lesson_hash_fails(self):
        self.review(sourceHash='0' * 64)
        self.fails('sourceHash is stale')

    def test_pass_without_evidence_fails(self):
        self.review()
        self.change(self.task_path, lambda d: d['lessonReview']['entries'][0].update(verification='pass'))
        self.fails('claim lacks evidence')

    def test_retrospective_does_not_create_a_pass(self):
        self.review(status='retrospective', reason='Historical mapping.')
        self.change(self.task_path, lambda d: d['lessonReview']['entries'][0].update(verification='pass', evidence=['audit.json']))
        self.fails('cannot declare new pass')

    def test_retrospective_mapping_passes_with_explicit_warning(self):
        self.review(status='retrospective', reason='Historical mapping.')
        self.change(self.task_path, lambda d: d['lessonReview']['entries'][0].update(verification='evidence-mapped', evidence=['audit.json']))
        result = self.result()
        self.assertEqual(result['status'], 'pass', result)
        self.assertTrue(result['warnings'])

    def test_unknown_product_profile_fails(self):
        self.change(self.task_path, lambda d: d.update(productProfileId='missing'))
        self.fails('unknown productProfileId')

    def test_wrong_platform_profile_fails(self):
        self.change(self.task_path, lambda d: d.update(platform='macos'))
        self.fails('profile platform mismatch')

    def test_wrong_platform_lesson_fails(self):
        path = self.design / 'LESSON.md'
        path.write_text(path.read_text(encoding='utf-8').replace('"platforms":["any"]', '"platforms":["macos"]'), encoding='utf-8')
        save(self.design / 'lessons-index.json', {'$schema': 'schemas/lesson-index.schema.json', **build_lesson_index(self.design)})
        self.review()
        self.fails('lesson platform mismatch')

    def test_delivered_task_needs_lesson_review(self):
        self.change(self.task_path, lambda d: d.update(status='delivered'))
        self.fails('pending lesson review')

    def test_stale_profile_source_fails(self):
        (self.root / 'PRODUCT.md').write_text('Changed product record.\n')
        self.fails('stale source')

    def test_observation_without_source_fails(self):
        self.change(self.design / 'profiles/example-web.json', lambda d: d['decisions'][0].update(status='observed'))
        self.fails('lacks evidence')

    def test_profile_schema_does_not_require_figma_keys(self):
        self.assertEqual(self.result()['status'], 'pass')

    def test_unknown_schema_does_not_get_silently_skipped(self):
        self.change(self.design / 'tasks/demo/audit.json', lambda d: d.update({'$schema': '../../schemas/unknown.schema.json'}))
        self.fails('incorrect schema')

    def test_untyped_task_evidence_fails(self):
        save(self.design / 'tasks/demo/new-evidence.json', {'raw': 'untyped'})
        self.fails('missing $schema')

    def test_evidence_payload_tampering_fails(self):
        self.change(self.design / 'tasks/demo/audit.json', lambda d: d.update(checks=['invented pass']))
        self.fails('payload hash mismatch')

    def test_task_directory_identity_fails(self):
        self.change(self.task_path, lambda d: d.update(taskId='other'))
        self.fails('taskId differs')

    def test_project_path_escape_fails(self):
        self.review()
        outside = Path(self.temp.name) / 'outside.txt'
        outside.write_text('not project evidence')
        self.change(self.task_path, lambda d: d['lessonReview']['entries'][0].update(evidence=['../../../../outside.txt']))
        self.fails('escapes project')

    def test_external_schema_is_not_fetched(self):
        path = self.design / 'schemas/task.schema.json'
        self.change(path, lambda d: d.update({'$ref': 'https://invalid.example/schema.json'}))
        self.fails('non-local $ref')

    def test_malformed_profile_fails_without_traceback(self):
        self.change(self.design / 'profiles/example-web.json', lambda d: d.update(sources='wrong type'))
        self.fails('is not of type')

    def test_shared_template_cannot_hold_task_decisions(self):
        self.change(self.design / 'task-template.json', lambda d: d.update(status='done'))
        self.fails('Shared task-template.json')

    def test_materialize_refuses_overwrite(self):
        with self.assertRaises(ValueError):
            materialize(self.root)

    def test_cli_nonzero_exit_on_invalid_data(self):
        self.change(self.task_path, lambda d: d.update(productProfileId='unknown'))
        script = Path(__file__).resolve().parents[1] / 'scripts/kkdesign_core.py'
        result = subprocess.run([sys.executable, str(script), 'validate', '--design', str(self.design)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['status'], 'fail')


if __name__ == '__main__':
    unittest.main()
