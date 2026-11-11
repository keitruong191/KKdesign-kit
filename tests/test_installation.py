import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_install as kit


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kkdesign test spaces ')
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / 'home with spaces'
        self.project = self.base / 'project with spaces'
        self.project.mkdir()
        self.home.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def act(self, action, harness='codex', scope='project', source=ROOT):
        return kit.lifecycle(action, harness, scope, self.home, self.project, source)

    def test_all_harness_scopes_preserve_project_and_unrelated_config(self):
        for harness in kit.ADAPTERS:
            for scope in ('user', 'project'):
                with self.subTest(harness=harness, scope=scope):
                    marker = self.project / 'DESIGN.md'
                    marker.write_text('product history')
                    lessons = self.project / 'design/tasks/demo'
                    lessons.mkdir(parents=True, exist_ok=True)
                    (lessons / 'audit.json').write_text('{"private":"synthetic"}')
                    config = self.home / kit.ADAPTERS[harness] / 'settings.json'
                    config.parent.mkdir(parents=True, exist_ok=True)
                    config.write_bytes(b'{"hooks":"leave alone","credential":"invented"}')
                    self.assertEqual(self.act('install', harness, scope)['status'], 'installed')
                    self.assertEqual(self.act('install', harness, scope)['status'], 'unchanged')
                    self.assertEqual(self.act('inspect', harness, scope)['status'], 'managed')
                    self.assertEqual(self.act('uninstall', harness, scope)['status'], 'uninstalled')
                    self.assertEqual(self.act('uninstall', harness, scope)['status'], 'already-absent')
                    self.assertEqual(marker.read_text(), 'product history')
                    self.assertTrue((lessons / 'audit.json').exists())
                    self.assertEqual(config.read_bytes(), b'{"hooks":"leave alone","credential":"invented"}')

    def source_copy(self):
        archive = self.base / 'kit.zip'
        kit.package(ROOT, archive)
        with zipfile.ZipFile(archive) as z:
            z.extractall(self.base / 'extract')
        return self.base / 'extract/kkdesign-kit'

    def test_artifact_is_deterministic_integrity_checked_and_relocatable(self):
        source = self.source_copy()
        second = self.base / 'second.zip'
        kit.package(ROOT, second)
        self.assertEqual((self.base / 'kit.zip').read_bytes(), second.read_bytes())
        self.act('install', source=source)
        target, _ = kit.locations('codex', 'project', self.home, self.project)
        shutil.rmtree(source)
        # Installed script must run from an unrelated CWD and package itself.
        proc = subprocess.run([sys.executable, str(target / 'scripts/kkdesign_install.py'),
                               'package', '--output', str(self.base / 'relocated.zip')],
                              cwd=self.home, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        kit.payload(target)
        (target / 'references/commands.md').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            kit.payload(target)

    def test_extracted_verification_rejects_version_drift_and_missing_resources(self):
        source = self.source_copy()
        self.assertEqual(kit.verify(source)['status'], 'verified')
        bundle = source / 'bundle.json'
        data = json.loads(bundle.read_text())
        data['version'] = 'unrelated-version'
        bundle.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'version mismatch'):
            kit.verify(source)
        bundle.unlink()
        (source / 'references/review.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required resource'):
            kit.payload(source)

    def test_update_rollback_and_repeat_update(self):
        source = self.source_copy()
        # Modify checkout-style source rather than an integrity-protected artifact.
        (source / 'bundle.json').unlink()
        manifest = json.loads((source / 'manifest.json').read_text())
        manifest['version'] = '99.0.0'
        (source / 'manifest.json').write_text(json.dumps(manifest))
        old_skill = (ROOT / 'SKILL.md').read_bytes()
        new_skill = old_skill + b'\nUpdated release content.\n'
        (source / 'SKILL.md').write_bytes(new_skill)
        for harness in kit.ADAPTERS:
            for scope in ('user', 'project'):
                with self.subTest(harness=harness, scope=scope):
                    self.act('install', harness, scope)
                    with self.assertRaisesRegex(ValueError, 'update explicitly'):
                        self.act('install', harness, scope, source)
                    self.act('update', harness, scope, source)
                    target, _ = kit.locations(harness, scope, self.home, self.project)
                    self.assertEqual((target / 'SKILL.md').read_bytes(), new_skill)
                    self.assertEqual(self.act('update', harness, scope, source)['status'], 'unchanged')
                    self.act('rollback', harness, scope)
                    self.assertEqual((target / 'SKILL.md').read_bytes(), old_skill)
                    self.act('rollback', harness, scope)
                    self.assertEqual((target / 'SKILL.md').read_bytes(), new_skill)
                    self.act('uninstall', harness, scope)

    def test_unmanaged_and_modified_files_are_never_erased(self):
        target, _ = kit.locations('codex', 'project', self.home, self.project)
        target.mkdir(parents=True)
        marker = target / 'foreign.txt'
        marker.write_text('keep')
        with self.assertRaisesRegex(ValueError, 'unmanaged'):
            self.act('install')
        self.assertEqual(marker.read_text(), 'keep')
        shutil.rmtree(target)
        self.act('install')
        marker.write_text('keep')
        for action in ('install', 'update', 'uninstall', 'rollback'):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, 'modified'):
                self.act(action)
            self.assertEqual(marker.read_text(), 'keep')

    def test_shadow_conflict_and_no_state_on_inspect(self):
        self.assertEqual(self.act('inspect')['status'], 'absent')
        self.assertFalse((self.project / '.kkdesign-kit').exists())
        self.act('install', scope='user')
        self.assertTrue(self.act('inspect')['conflicts'])
        with self.assertRaisesRegex(ValueError, 'Other discoverable'):
            self.act('install')

    def test_invalid_bundle_and_existing_output_are_rejected(self):
        source = self.source_copy()
        (source / 'SKILL.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.act('install', source=source)
        with self.assertRaises(FileExistsError):
            kit.package(ROOT, self.base / 'kit.zip')

    def test_failed_swap_restores_old_installation(self):
        self.act('install')
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        (source / 'SKILL.md').write_text((source / 'SKILL.md').read_text() + '\nRevision.\n')
        with patch.object(kit.os, 'replace', side_effect=OSError('simulated disk failure')):
            with self.assertRaises(OSError):
                self.act('update', source=source)
        self.assertEqual(self.act('inspect')['status'], 'managed')

    def test_modified_backup_blocks_update_rollback_and_uninstall(self):
        self.act('install')
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        skill = source / 'SKILL.md'
        skill.write_text(skill.read_text() + '\nRevision.\n')
        self.act('update', source=source)
        _, state = kit.locations('codex', 'project', self.home, self.project)
        marker = state / 'previous/user-data.txt'
        marker.write_text('preserve')
        for action in ('update', 'rollback', 'uninstall'):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, 'Modified rollback'):
                self.act(action)
            self.assertEqual(marker.read_text(), 'preserve')
        self.assertEqual(self.act('inspect')['status'], 'managed')

    def test_commit_failure_preserves_existing_rollback(self):
        self.act('install')
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        skill = source / 'SKILL.md'
        skill.write_text(skill.read_text() + '\nRevision one.\n')
        self.act('update', source=source)
        target, state = kit.locations('codex', 'project', self.home, self.project)
        before = kit.hashes(target), kit.hashes(state / 'previous')
        skill.write_text(skill.read_text() + '\nRevision two.\n')
        replace = kit.os.replace

        def fail_ledger(src, dst):
            if Path(dst).name == 'state.json':
                raise OSError('simulated ledger commit failure')
            return replace(src, dst)

        with patch.object(kit.os, 'replace', side_effect=fail_ledger):
            with self.assertRaises(OSError):
                self.act('update', source=source)
        self.assertEqual((kit.hashes(target), kit.hashes(state / 'previous')), before)
        self.assertEqual(self.act('inspect')['status'], 'managed')
        self.act('rollback')

    def test_packaging_excludes_unrelated_root_and_dependency_files(self):
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        (source / 'unrelated-private.json').write_text('synthetic private marker')
        (source / 'scripts/unrelated.py').write_text('synthetic marker')
        files, _ = kit.payload(source)
        self.assertNotIn('unrelated-private.json', files)
        self.assertNotIn('scripts/unrelated.py', files)

    def test_private_resource_files_are_excluded_without_dropping_public_assets(self):
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        private_names = (
            'docs/.env.local', 'references/.hoangsa/session.md',
            'examples/prototype/node_modules/vendor/package.json',
            'templates/__pycache__/private.pyc', 'schemas/credentials.json',
            'agents/id_ed25519', 'docs/private.pem', 'references/debug.log',
        )
        private_marker = b'SYNTHETIC_PRIVATE_RESOURCE_CANARY'
        for name in private_names:
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(private_marker)
        public_name = 'docs/public-extension-guide.md'
        public_marker = b'Public extension documentation.'
        (source / public_name).write_bytes(public_marker)
        archive = self.base / 'public-resources.zip'
        kit.package(source, archive)
        with zipfile.ZipFile(archive) as packaged:
            self.assertEqual(packaged.read('kkdesign-kit/' + public_name), public_marker)
            for name in private_names:
                self.assertNotIn('kkdesign-kit/' + name, packaged.namelist())
            for name in packaged.namelist():
                self.assertNotIn(private_marker, packaged.read(name), name)
            packaged.extractall(self.base / 'public-resources')
        self.assertEqual(kit.verify(self.base / 'public-resources/kkdesign-kit')['status'],
                         'verified')

    def test_required_private_resource_fails_before_creating_archive(self):
        source = self.source_copy()
        (source / 'bundle.json').unlink()
        private_name = 'docs/.env.local'
        (source / private_name).write_text('SYNTHETIC_PRIVATE_RESOURCE_CANARY')
        manifest = json.loads((source / 'manifest.json').read_text())
        manifest['requiredResources'].append(private_name)
        (source / 'manifest.json').write_text(json.dumps(manifest))
        archive = self.base / 'required-private.zip'
        with self.assertRaisesRegex(ValueError, 'Missing required resource: docs/.env.local'):
            kit.package(source, archive)
        self.assertFalse(archive.exists())

    def test_receipted_private_resource_cannot_be_repacked(self):
        source = self.source_copy()
        private_name = 'docs/.env.local'
        (source / private_name).write_text('SYNTHETIC_PRIVATE_RESOURCE_CANARY')
        bundle = json.loads((source / 'bundle.json').read_text())
        bundle['files'][private_name] = kit.hashes(source)[private_name]
        (source / 'bundle.json').write_text(json.dumps(bundle))
        archive = self.base / 'receipted-private.zip'
        with self.assertRaisesRegex(ValueError, 'Private package resource: docs/.env.local'):
            kit.package(source, archive)
        self.assertFalse(archive.exists())

    def test_receipted_private_ancestor_cannot_be_repacked(self):
        source = self.source_copy()
        for index, directory in enumerate(('credentials', 'private.zip')):
            with self.subTest(directory=directory):
                candidate = self.base / ('private-ancestor-' + str(index))
                shutil.copytree(source, candidate)
                private_name = 'docs/' + directory + '/session.txt'
                private_path = candidate / private_name
                private_path.parent.mkdir()
                private_path.write_text('SYNTHETIC_PRIVATE_RESOURCE_CANARY')
                bundle = json.loads((candidate / 'bundle.json').read_text())
                bundle['files'][private_name] = kit.hashes(candidate)[private_name]
                (candidate / 'bundle.json').write_text(json.dumps(bundle))
                archive = self.base / ('private-ancestor-' + str(index) + '.zip')
                with self.assertRaisesRegex(ValueError, 'Private package resource:'):
                    kit.package(candidate, archive)
                self.assertFalse(archive.exists())

    def test_symlink_conflicts_and_concurrent_mutation(self):
        self.act('install')
        target, state = kit.locations('codex', 'project', self.home, self.project)
        with kit.locked(state):
            with self.assertRaisesRegex(ValueError, 'busy'):
                self.act('update')
        try:
            (target / 'linked').symlink_to(self.project / 'DESIGN.md')
        except (OSError, NotImplementedError):
            return  # Windows runners may not grant symlink privileges.
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.act('uninstall')


if __name__ == '__main__':
    unittest.main()
