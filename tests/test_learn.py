import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_learn as learn
from kkdesign_core import build_lesson_index, digest, validate_foundation


class LearningWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT / 'examples/minimal', self.project)
        shutil.copytree(ROOT / 'schemas', self.project / 'design/schemas')
        self.design = self.project / 'design'
        self.lesson = self.design / 'LESSON.md'
        index = build_lesson_index(self.design)
        (self.design / 'lessons-index.json').write_text(json.dumps(
            {'$schema': 'schemas/lesson-index.schema.json', **index}, indent=2) + '\n', encoding='utf-8')
        (self.project / 'evidence.txt').write_text('Synthetic evidence only.\n', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def author(self, **updates):
        args = {'title': 'Keep the selected scope explicit',
                'body': 'Apply this only to the documented scope.',
                'verification': 'Record task-specific evidence; this authoring operation is not verification.',
                'evidence': ['../evidence.txt'], 'scope': 'web', 'tags': ['scope'],
                'applies_when': 'When applying a scoped design lesson.', 'origin_task': 'demo'}
        args.update(updates)
        return learn.author_lesson(self.design, **args)

    def test_feedback_capture_is_exactly_deduplicated_and_separate(self):
        args = (self.design, 'The spacing feels unclear.', ['../evidence.txt'], 'web', 'reviewer')
        first = learn.capture_feedback(*args)
        before_lesson = self.lesson.read_bytes()
        second = learn.capture_feedback(*args)
        self.assertEqual(first, {'status': 'captured', 'id': 'FB-001', 'changed': True})
        self.assertEqual(second, {'status': 'duplicate', 'id': 'FB-001', 'changed': False})
        records = json.loads((self.design / 'feedback.json').read_text(encoding='utf-8'))
        self.assertEqual(records[0]['kind'], 'direct-feedback')
        self.assertEqual(records[0]['evidence'], ['../evidence.txt'])
        self.assertEqual(self.lesson.read_bytes(), before_lesson)

    def test_author_regenerates_index_and_keeps_prechange_snapshot(self):
        original = self.lesson.read_bytes()
        original_hash = digest(original)
        result = self.author()
        self.assertEqual(result['id'], 'DL-002')
        current = build_lesson_index(self.design)
        self.assertEqual(current['sourceHash'], result['sourceHash'])
        self.assertEqual(json.loads((self.design / 'lessons-index.json').read_text())['sourceHash'],
                         current['sourceHash'])
        snapshot = self.design / 'lesson-history' / original_hash
        self.assertEqual((snapshot / 'LESSON.md').read_bytes(), original)
        self.assertEqual(json.loads((snapshot / 'lessons-index.json').read_text())['sourceHash'], original_hash)
        meta = current['lessons'][-1]
        self.assertEqual(meta['kind'], 'inferred')
        self.assertEqual(meta['originTask'], 'demo')

    def test_exact_lesson_repeat_returns_existing_id_without_rewriting(self):
        first = self.author()
        lesson_before = self.lesson.read_bytes()
        index_before = (self.design / 'lessons-index.json').read_bytes()
        second = self.author()
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(second['status'], 'duplicate')
        self.assertFalse(second['changed'])
        self.assertEqual(self.lesson.read_bytes(), lesson_before)
        self.assertEqual((self.design / 'lessons-index.json').read_bytes(), index_before)

    def test_crlf_lesson_replay_preserves_canonical_bytes_and_index_hash(self):
        first = self.author(body='First line.\r\nSecond line.')
        self.lesson.write_bytes(self.lesson.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        index = build_lesson_index(self.design)
        (self.design / 'lessons-index.json').write_text(
            json.dumps({'$schema': 'schemas/lesson-index.schema.json', **index}), encoding='utf-8')
        before = {path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}
        replay = self.author(body='First line.\nSecond line.')
        self.assertEqual(replay, {'status': 'duplicate', 'id': first['id'], 'changed': False})
        self.assertEqual({path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}, before)

    def test_replaying_earlier_lesson_after_another_author_returns_original_id(self):
        first = self.author()
        self.author(title='Different practice')
        before = {path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}
        replay = self.author()
        self.assertEqual(replay, {'status': 'duplicate', 'id': first['id'], 'changed': False})
        self.assertEqual({path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}, before)

    def test_replaying_superseded_lesson_does_not_reactivate_it(self):
        first = self.author()
        replacement = self.author(title='Replacement practice')
        learn.supersede_lesson(self.design, first['id'], replacement['id'])
        before = {path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}
        replay = self.author()
        self.assertEqual(replay, {'status': 'duplicate', 'id': first['id'], 'changed': False})
        self.assertEqual({path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}, before)

    def test_exhausted_ids_still_allow_exact_replay_without_mutation(self):
        self.author()
        self.lesson.write_text(self.lesson.read_text(encoding='utf-8').replace('DL-002', 'DL-999'), encoding='utf-8')
        index = build_lesson_index(self.design)
        (self.design / 'lessons-index.json').write_text(
            json.dumps({'$schema': 'schemas/lesson-index.schema.json', **index}), encoding='utf-8')
        before = {path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}
        self.assertEqual(self.author(), {'status': 'duplicate', 'id': 'DL-999', 'changed': False})
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            self.author(title='A genuinely new practice')
        self.assertEqual({path: path.read_bytes() for path in self.design.rglob('*') if path.is_file()}, before)

    def test_history_symlinks_cannot_copy_private_lessons_into_public_docs(self):
        outside = self.design.parent / 'public-docs'
        outside.mkdir()
        source_before = self.lesson.read_bytes()
        index_before = (self.design / 'lessons-index.json').read_bytes()
        history = self.design / 'lesson-history'
        for destination in (history, history / digest(source_before)):
            with self.subTest(destination=destination.name):
                destination.parent.mkdir(parents=True, exist_ok=True)
                try:
                    destination.symlink_to(outside.resolve(), target_is_directory=True)
                except OSError as error:
                    self.skipTest('Directory symlinks unavailable: ' + str(error))
                try:
                    with self.assertRaisesRegex(ValueError, '[Ss]ymlink'):
                        self.author()
                    self.assertEqual(list(outside.iterdir()), [])
                    self.assertEqual(self.lesson.read_bytes(), source_before)
                    self.assertEqual((self.design / 'lessons-index.json').read_bytes(), index_before)
                finally:
                    destination.unlink()


    def test_invalid_evidence_leaves_all_learning_files_unchanged(self):
        source_before = self.lesson.read_bytes()
        index_before = (self.design / 'lessons-index.json').read_bytes()
        with self.assertRaises(ValueError):
            self.author(evidence=['../../outside.txt'])
        self.assertEqual(self.lesson.read_bytes(), source_before)
        self.assertEqual((self.design / 'lessons-index.json').read_bytes(), index_before)
        self.assertFalse((self.design / 'lesson-history').exists())

    def test_remote_only_feedback_is_not_accepted_as_inspected_evidence(self):
        with self.assertRaisesRegex(ValueError, 'project-local evidence'):
            learn.capture_feedback(self.design, 'Uninspected remote claim.',
                                   ['https://example.com/evidence'], 'web', 'reviewer')
        self.assertFalse((self.design / 'feedback.json').exists())

    def test_invalid_feedback_evidence_does_not_create_feedback_file(self):
        with self.assertRaises(ValueError):
            learn.capture_feedback(self.design, 'A direct comment.', ['missing.txt'], 'web', 'reviewer')
        self.assertFalse((self.design / 'feedback.json').exists())

    def test_supersession_is_explicit_idempotent_and_keeps_history(self):
        self.author()
        old_source = self.lesson.read_bytes()
        old_hash = digest(old_source)
        first = learn.supersede_lesson(self.design, 'DL-001', 'DL-002')
        self.assertEqual(first['status'], 'superseded')
        self.assertEqual((self.design / 'lesson-history' / old_hash / 'LESSON.md').read_bytes(), old_source)
        second = learn.supersede_lesson(self.design, 'DL-001', 'DL-002')
        self.assertEqual(second['status'], 'duplicate')
        self.assertFalse(second['changed'])
        current = build_lesson_index(self.design)
        old = next(row for row in current['lessons'] if row['id'] == 'DL-001')
        self.assertEqual(old['status'], 'superseded')
        self.assertEqual(old['supersededBy'], 'DL-002')

    def test_reviewed_task_hash_and_evidence_truth_are_not_rewritten(self):
        old_index = build_lesson_index(self.design)
        task_path = self.design / 'tasks/demo/task.json'
        task = json.loads(task_path.read_text(encoding='utf-8'))
        task['lessonReview'] = {'status': 'reviewed', 'sourceHash': old_index['sourceHash'], 'entries': [
            {'lessonId': 'DL-001', 'decision': 'apply', 'reason': 'Synthetic fixture decision.',
             'verification': 'pending', 'evidence': []}]}
        original_task = (json.dumps(task, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        task_path.write_bytes(original_task)
        self.author()
        learn.supersede_lesson(self.design, 'DL-001', 'DL-002')
        self.assertEqual(task_path.read_bytes(), original_task)
        snapshot = self.design / 'lesson-history' / old_index['sourceHash']
        self.assertEqual(digest((snapshot / 'LESSON.md').read_bytes()), task['lessonReview']['sourceHash'])
        self.assertEqual(task['lessonReview']['entries'][0]['verification'], 'pending')
        result = validate_foundation(self.design)
        self.assertEqual(result['status'], 'pass', result)

    def test_corrupt_historical_snapshot_is_rejected(self):
        old_index = build_lesson_index(self.design)
        task_path = self.design / 'tasks/demo/task.json'
        task = json.loads(task_path.read_text(encoding='utf-8'))
        task['lessonReview'] = {'status': 'reviewed', 'sourceHash': old_index['sourceHash'], 'entries': [
            {'lessonId': 'DL-001', 'decision': 'apply', 'reason': 'Synthetic fixture decision.',
             'verification': 'pending', 'evidence': []}]}
        task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        self.author()
        snapshot = self.design / 'lesson-history' / old_index['sourceHash'] / 'LESSON.md'
        snapshot.write_bytes(snapshot.read_bytes() + b'\nTampered snapshot.\n')
        result = validate_foundation(self.design)
        self.assertEqual(result['status'], 'fail', result)
        self.assertTrue(any('historical' in error.lower() or 'snapshot' in error.lower()
                            for error in result['errors']), result['errors'])
    def test_supersession_rejects_unknown_lesson_without_mutation(self):
        source_before = self.lesson.read_bytes()
        index_before = (self.design / 'lessons-index.json').read_bytes()
        with self.assertRaises(ValueError):
            learn.supersede_lesson(self.design, 'DL-001', 'DL-999')
        self.assertEqual(self.lesson.read_bytes(), source_before)
        self.assertEqual((self.design / 'lessons-index.json').read_bytes(), index_before)
        self.assertFalse((self.design / 'lesson-history').exists())


if __name__ == '__main__':
    unittest.main()
