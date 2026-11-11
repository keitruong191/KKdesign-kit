import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import kkdesign_project as project
import kkdesign_task as tasks


class ProjectLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'work space'
        self.root.mkdir()
        self.config = Path(self.temp.name) / 'sources.json'
        self.declarations = [{'id': 'ds', 'provider': 'local', 'location': 'one'}]
        self.write_source('one')

    def write_source(self, location, tokens=None):
        source = self.root.parent / location
        source.mkdir(parents=True, exist_ok=True)
        document = {'schemaVersion': '1.0.0', **{name: [] for name in project.CATEGORIES}}
        document['tokens'] = tokens or []
        (source / 'ds.json').write_text(json.dumps(document), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, refresh=False, context=None, migration=None):
        self.config.write_text(json.dumps({'sources': self.declarations}), encoding='utf-8')
        context_path = None
        if context is not None:
            context_path = self.root.parent / 'context.json'
            context_path.write_text(json.dumps(context), encoding='utf-8')
        return project._plan(self.root, self.config, context_path, migration, refresh)

    def test_init_stages_portable_stage_a_files_until_explicit_apply(self):
        plan = self.plan()
        self.assertEqual(plan['status'], 'review-required')
        self.assertFalse((self.root / 'design/sources.json').exists())
        details = project.inspect_plan(self.root, plan['id'])
        self.assertTrue(any(change['diff'] for change in details['changes']))
        self.assertEqual(project.apply_plan(self.root, plan['id'])['status'], 'applied')
        self.assertTrue((self.root / 'design/sources.json').is_file())
        self.assertTrue((self.root / 'design/lessons-index.json').is_file())
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')

    def test_existing_design_and_product_are_preserved_and_never_overwritten(self):
        self.root.joinpath('PRODUCT.md').write_text('Owner approved facts.\\n')
        self.root.joinpath('DESIGN.md').write_text('Custom guide.\\n')
        plan = self.plan()
        preserved = {item['path'] for item in plan['preserved']}
        self.assertIn('DESIGN.md', preserved)
        self.assertIn('PRODUCT.md', preserved)
        self.assertFalse(plan['conflicts'])
        project.apply_plan(self.root, plan['id'])
        self.assertEqual((self.root / 'PRODUCT.md').read_text(), 'Owner approved facts.\\n')
        self.assertEqual((self.root / 'DESIGN.md').read_text(), 'Custom guide.\\n')

    def test_refresh_preserves_existing_profile_and_lesson_bytes(self):
        first = self.plan(); project.apply_plan(self.root, first['id'])
        profile = self.root / 'design/profiles/adaptive.json'
        lesson = self.root / 'design/LESSON.md'
        profile.write_bytes(profile.read_bytes() + b' ')
        lesson.write_bytes(lesson.read_bytes() + b'\n<!-- preserved -->\n')
        before = profile.read_bytes(), lesson.read_bytes()
        second = self.plan(refresh=True)
        project.apply_plan(self.root, second['id'])
        self.assertEqual((profile.read_bytes(), lesson.read_bytes()), before)

    def test_refresh_preserves_delivered_react_artifacts_and_ignores_runtime_dependencies(self):
        self.write_source('one', [{'id': 'color.primary', 'name': 'Primary', 'data': {'value': '#123456'}}])
        initial = self.plan()
        project.apply_plan(self.root, initial['id'])
        design = self.root / 'design'
        record = project.load(design / 'task-template.json')
        index = project.load(design / 'lessons-index.json')
        profile = project.load(design / 'profiles/adaptive.json')
        record.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'react-refresh',
            'objective': 'Offline artifact integrity fixture, not browser acceptance.',
            'platform': 'web', 'productProfileId': profile['id'], 'delivery': 'react_prototype',
            'target': {'destination': 'design/prototypes/react-refresh'},
            'sourceDecisions': [{'surface': 'fixture', 'sourceId': 'ds', 'assetIds': ['color.primary']}],
            'designPlan': {
                'platformProfileId': 'web', 'layoutDecisions': [{'decision': 'Synthetic fixture layout.'}],
                'stateDispositions': [{'state': 'default', 'disposition': 'planned'}],
                'referenceExamples': []},
            'lessonReview': {
                'status': 'reviewed', 'sourceHash': index['sourceHash'],
                'entries': [{'lessonId': lesson['id'], 'decision': 'apply',
                             'reason': 'Apply the initialized project lesson to this fixture.',
                             'verification': 'pending', 'evidence': []} for lesson in index['lessons']]}
        })
        record_path = self.root / 'react-record.json'
        record_path.write_text(json.dumps(record), encoding='utf-8')
        tasks.begin(self.root, record_path)
        artifact = design / 'prototypes/react-refresh'
        artifact.mkdir(parents=True)
        entry = artifact / 'App.jsx'
        entry.write_text('export const fixture = true;\n', encoding='utf-8')
        (artifact / 'README.md').write_text('Offline integrity fixture only.\n', encoding='utf-8')
        (artifact / 'package.json').write_text('{"private":true}\n', encoding='utf-8')
        dependency = self.root.parent / 'runtime-command'
        dependency.write_text('color.primary: dependency content must not be a project contract.\n', encoding='utf-8')
        binaries = artifact / 'node_modules/.bin'
        binaries.mkdir(parents=True)
        (binaries / 'vite').symlink_to(dependency)
        payload = self.root / 'fixture-evidence.json'
        payload.write_text('{"scope":"offline integrity fixture, no browser observation"}', encoding='utf-8')
        tasks.add_evidence(self.root, 'react-refresh', 'audit', 'Synthetic integrity fixture.',
                           payload, ['../../prototypes/react-refresh/App.jsx'])
        handoff = self.root / 'fixture-handoff.json'
        handoff.write_text(json.dumps({
            'frameLinks': [], 'createdNodeIds': [], 'modifiedNodeIds': [], 'remainingGaps': [],
            'checks': [{'evidence': ['evidence-0001.json']}],
            'requirementStateMapping': [{'requirement': 'fixture', 'state': 'default'}],
            'artifacts': [{'entry': 'design/prototypes/react-refresh/App.jsx',
                           'instructions': 'design/prototypes/react-refresh/README.md',
                           'launch': {'mode': 'command', 'cwd': 'design/prototypes/react-refresh',
                                      'argv': ['npm', 'run', 'dev']}}]
        }), encoding='utf-8')
        tasks.update_handoff(self.root, 'react-refresh', handoff, 'design_delivered')
        task_path = design / 'tasks/react-refresh/task.json'
        before = task_path.read_bytes(), entry.read_bytes(), dependency.read_bytes()
        self.write_source('one', [{'id': 'color.primary', 'name': 'Primary', 'data': {'value': '#abcdef'}}])

        refresh = self.plan(refresh=True)
        self.assertEqual(refresh['candidateErrors'], [])
        affected = next(item for item in refresh['affectedReferences'] if item['id'] == 'color.primary')
        self.assertIn('design/tasks/react-refresh/task.json', affected['files'])
        self.assertNotIn('design/prototypes/react-refresh/node_modules/.bin/vite', affected['files'])
        project.inspect_plan(self.root, refresh['id'])
        project.apply_plan(self.root, refresh['id'])
        self.assertEqual((task_path.read_bytes(), entry.read_bytes(), dependency.read_bytes()), before)
        self.assertTrue((binaries / 'vite').is_symlink())
        self.assertEqual(tasks.check_task(self.root, 'react-refresh')['status'], 'checked')
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')

        entry.unlink()
        invalid = self.plan(refresh=True)
        self.assertTrue(invalid['candidateErrors'])
        with self.assertRaises(ValueError):
            project.apply_plan(self.root, invalid['id'])
        self.assertEqual(task_path.read_bytes(), before[0])

    def test_relocation_requires_reason_and_records_migration(self):
        first = self.plan(); project.apply_plan(self.root, first['id'])
        self.write_source('two')
        self.declarations[0]['location'] = 'two'
        with self.assertRaisesRegex(ValueError, 'requires --migration'):
            self.plan(refresh=True)
        migrated = self.plan(refresh=True, migration='Repository moved by owner')
        details = project.inspect_plan(self.root, migrated['id'])
        self.assertEqual(details['migration']['reason'], 'Repository moved by owner')
        self.assertEqual(details['migration']['sources'][0]['id'], 'ds')

    def test_refresh_reuses_profile_evidence_outside_design_directory(self):
        initial = self.plan()
        project.apply_plan(self.root, initial['id'])
        evidence = self.root / 'docs/brief.md'
        evidence.parent.mkdir()
        evidence.write_text('Owner-confirmed adaptive settings requirement.\n', encoding='utf-8')
        profile = self.root / 'design/profiles/adaptive.json'
        document = json.loads(profile.read_text())
        document['sources'].append({
            'id': 'brief', 'location': 'docs/brief.md', 'revision': None,
            'observedAt': '2026-11-06', 'sha256': project._hash(evidence.read_bytes())})
        document['decisions'].append({
            'id': 'settings', 'topic': 'Settings scope', 'value': 'Adaptive settings',
            'status': 'confirmed', 'scope': 'Settings surface only', 'sourceIds': ['brief'],
            'recheckWhen': 'When the approved brief changes'})
        profile.write_text(json.dumps(document), encoding='utf-8')
        before = profile.read_bytes()
        refresh = self.plan(refresh=True)
        self.assertEqual(refresh['candidateErrors'], [])
        project.apply_plan(self.root, refresh['id'])
        self.assertEqual(profile.read_bytes(), before)
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')

    def test_source_selection_change_is_a_migration(self):
        self.write_source('repo')
        self.write_source('repo/tokens')
        repo = self.root.parent / 'repo'
        for command in (
                ['git', 'init', '-q'],
                ['git', 'add', '.'],
                ['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Synthetic committed source']):
            subprocess.run(command, cwd=repo, check=True, capture_output=True)
        self.declarations = [{'id': 'ds', 'provider': 'git', 'location': 'repo'}]
        first = self.plan(); project.apply_plan(self.root, first['id'])
        self.declarations[0]['subdir'] = 'tokens'
        with self.assertRaisesRegex(ValueError, 'requires --migration'):
            self.plan(refresh=True)
        plan = self.plan(refresh=True, migration='Narrowed source selection by owner')
        self.assertEqual(plan['sourceChanges'][0]['after']['selection'], {'subdir': 'tokens'})


    def test_asset_refresh_lists_added_removed_changed_and_actual_references(self):
        self.write_source('one', [
            {'id': 'color.primary', 'name': 'Primary', 'data': {'$value': '#111'}},
            {'id': 'color.old', 'name': 'Old', 'data': {'$value': '#222'}}])
        (self.root / 'design').mkdir()
        (self.root / 'design/asset-notes.txt').write_text('Use color.primary for links.')
        initial = self.plan(); project.apply_plan(self.root, initial['id'])
        self.write_source('one', [
            {'id': 'color.primary', 'name': 'Primary', 'data': {'$value': '#333'}},
            {'id': 'color.new', 'name': 'New', 'data': {'$value': '#444'}}])
        refresh = self.plan(refresh=True)
        delta = refresh['assetChanges']['tokens']
        self.assertEqual(delta['added'], ['color.new'])
        self.assertEqual(delta['removed'], ['color.old'])
        self.assertEqual(delta['changed'], ['color.primary'])
        affected = {item['id']: item['files'] for item in refresh['affectedReferences']}
        self.assertIn('design/asset-notes.txt', affected['color.primary'])
    def test_unmanaged_file_is_conflict_on_refresh(self):
        first = self.plan(); project.apply_plan(self.root, first['id'])
        path = self.root / 'design/task-template.json'
        path.write_text('{"owner":"custom"}\n')
        before = path.read_bytes()
        next_plan = self.plan(refresh=True)
        self.assertIn('design/task-template.json', {x['path'] for x in next_plan['conflicts']})
        with self.assertRaisesRegex(ValueError, 'Unresolved plan conflicts'):
            project.apply_plan(self.root, next_plan['id'])
        self.assertEqual(path.read_bytes(), before)

    def test_platform_decisions_remain_scoped_and_surface_modes_need_scope(self):
        context = {'product': {'name': 'Demo', 'platforms': ['macos', 'ios']},
                   'requirements': [{'id': 'desktop', 'topic': 'Window behavior', 'value': 'resizable',
                                     'status': 'confirmed', 'scope': 'macOS only', 'platforms': ['macos'],
                                     'sourceIds': ['brief'], 'recheckWhen': 'Window model changes'}],
                   'sources': [{'id': 'brief', 'location': 'PRODUCT.md'}]}
        p = project._profile(context, self.root / 'PRODUCT.md', 'macos')
        self.assertEqual(p['decisions'][0]['status'], 'confirmed')
        self.assertEqual(project._profile(context, self.root / 'PRODUCT.md', 'ios')['decisions'][0]['status'], 'open')
        bad = {'requirements': [{'topic': 'Operate', 'value': 'x'}]}
        with self.assertRaisesRegex(ValueError, 'surface or task locator'):
            project._context_decisions(bad, 'macos')

    def test_interrupted_multifile_apply_recovers_last_valid_state(self):
        plan = self.plan()
        original = project.os.replace
        calls = {'n': 0}

        def fail_second(source, target):
            if Path(target).suffix != '.json':
                calls['n'] += 1
                if calls['n'] == 2:
                    raise OSError('simulated interruption')
            return original(source, target)
        with mock.patch.object(project.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                project.apply_plan(self.root, plan['id'])
        journal = self.root / '.kkdesign-kit/project/recovery' / (plan['id'] + '.json')
        original_journal = journal.read_text()
        damaged = json.loads(original_journal)
        damaged['entries'][0]['backup'] = 'not the recorded preimage'
        journal.write_text(json.dumps(damaged))
        with self.assertRaisesRegex(ValueError, 'backup does not match'):
            project.recover(self.root, plan['id'])
        self.assertTrue((self.root / 'DESIGN.md').exists())
        journal.write_text(original_journal)
        recovered = project.recover(self.root, plan['id'])
        self.assertEqual(recovered['status'], 'recovered')
        self.assertFalse((self.root / 'DESIGN.md').exists())
        self.assertFalse((self.root / 'design/sources.json').exists())

    def test_symlink_target_is_rejected_before_plan_writes(self):
        external = self.root.parent / 'external'
        external.mkdir()
        (self.root / 'design').symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.plan()


    def test_unchanged_refresh_has_no_file_updates(self):
        first = self.plan(); project.apply_plan(self.root, first['id'])
        repeated = self.plan(refresh=True)
        self.assertTrue(all(item['action'] == 'unchanged' for item in repeated['changes']))
        self.assertFalse(repeated['sourceChanges'])

    def test_corrupted_staged_content_fails_hash_integrity(self):
        plan = self.plan()
        path = project._plan_path(self.root, plan['id'])
        document = json.loads(path.read_text())
        document['files']['DESIGN.md']['content'] = 'tampered'
        path.write_text(json.dumps(document))
        with self.assertRaisesRegex(ValueError, 'content hash mismatch'):
            project.apply_plan(self.root, plan['id'])
        self.assertFalse((self.root / 'DESIGN.md').exists())

    def test_rollback_restores_the_last_valid_workspace(self):
        plan = self.plan()
        project.apply_plan(self.root, plan['id'])
        result = project.rollback(self.root)
        self.assertEqual(result['status'], 'rolled-back')
        self.assertFalse((self.root / 'PRODUCT.md').exists())
        self.assertFalse((self.root / 'design/sources.json').exists())

    def test_cli_string_paths_apply_and_release_lock(self):
        self.config.write_text(json.dumps({'sources': self.declarations}), encoding='utf-8')
        script = Path(project.__file__)
        initial = subprocess.run([sys.executable, str(script), 'init', '--project', str(self.root),
                                  '--sources', str(self.config)], capture_output=True, text=True)
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        plan_id = json.loads(initial.stdout)['id']
        applied = subprocess.run([sys.executable, str(script), 'apply', '--project', str(self.root),
                                  '--plan', plan_id], capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')
        repeated = self.plan(refresh=True)
        project.apply_plan(str(self.root), repeated['id'])
        self.assertFalse((self.root / '.kkdesign-kit/project/lock').exists())

    def test_interrupted_rollback_recovery_restores_complete_applied_kit(self):
        initial = self.plan()
        project.apply_plan(self.root, initial['id'])
        before = {path.relative_to(self.root).as_posix(): path.read_bytes()
                  for path in self.root.rglob('*')
                  if path.is_file() and '.kkdesign-kit' not in path.parts}
        restore = project._atomic_restore
        calls = 0

        def interrupt(path, data):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated rollback interruption')
            restore(path, data)

        with mock.patch.object(project, '_atomic_restore', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'rollback interruption'):
                project.rollback(self.root, initial['id'])
        project.recover(self.root)
        after = {path.relative_to(self.root).as_posix(): path.read_bytes()
                 for path in self.root.rglob('*')
                 if path.is_file() and '.kkdesign-kit' not in path.parts}
        self.assertEqual(after, before)
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')

    def test_live_owner_lock_rejects_concurrent_apply(self):
        plan = self.plan()
        lock = project._acquire_lock(self.root)
        try:
            with self.assertRaisesRegex(ValueError, 'in progress'):
                project.apply_plan(self.root, plan['id'])
        finally:
            project._release_lock(lock)
        self.assertFalse((self.root / 'DESIGN.md').exists())

    def test_process_death_during_refresh_recovers_previous_valid_kit(self):
        initial = self.plan()
        project.apply_plan(self.root, initial['id'])
        registry = (self.root / 'design/sources.json').read_bytes()
        self.write_source('one', [{'id': 'space.small', 'name': 'Small', 'data': {'value': 8}}])
        refresh = self.plan(refresh=True)
        code = (
            "import os,sys; from pathlib import Path; "
            "sys.path.insert(0,sys.argv[1]); import kkdesign_project as project\n"
            "original=project._durable_json\n"
            "def interrupt(path,value):\n"
            "    original(path,value)\n"
            "    if value.get('status')=='applying' and any(e['path']=='design/sources.json' "
            "and e.get('written') for e in value.get('entries',[])):\n"
            "        os._exit(77)\n"
            "project._durable_json=interrupt\n"
            "project.apply_plan(sys.argv[2],sys.argv[3])\n")
        crashed = subprocess.run([sys.executable, '-c', code, str(Path(project.__file__).parent),
                                  str(self.root), refresh['id']], capture_output=True, text=True)
        self.assertEqual(crashed.returncode, 77, crashed.stdout + crashed.stderr)
        self.assertNotEqual((self.root / 'design/sources.json').read_bytes(), registry)
        recovered = project.recover(self.root)
        self.assertEqual(recovered['status'], 'recovered')
        self.assertEqual((self.root / 'design/sources.json').read_bytes(), registry)
        self.assertEqual(project.validate_project(self.root)['status'], 'pass')

    def test_visual_reference_is_separate_provenance_and_context_paths_are_rejected(self):
        context = {'visualReferences': [{'id': 'board', 'location': 'https://www.figma.com/design/KEY/title',
                                         'scope': 'Current billing surface', 'status': 'observed'}]}
        profile = project._profile(context, self.root / 'PRODUCT.md', 'adaptive')
        self.assertEqual(profile['decisions'][0]['value']['designation'], 'visual reference; not a product requirement')
        self.assertIn('visual-board', {source['id'] for source in profile['sources']})
        with self.assertRaisesRegex(ValueError, 'absolute paths'):
            project._validate_context_safety({'requirements': [{'value': '/Users/private/file'}]})

    def test_context_credentials_do_not_reach_staged_files(self):
        for value in ('https://example.invalid/?access_token=synthetic-private-value',
                      {'authorization': 'synthetic-private-value'}):
            with self.subTest(valueType=type(value).__name__):
                with self.assertRaisesRegex(ValueError, 'credential') as error:
                    self.plan(context={'requirements': [{'id': 'unsafe', 'value': value}]})
                self.assertNotIn('synthetic-private-value', str(error.exception))
                self.assertFalse((self.root / '.kkdesign-kit/project/plans').exists())

if __name__ == '__main__':
    unittest.main()
