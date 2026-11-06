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

    def test_update_rollback_and_repeat_update(self):
        source = self.source_copy()
        # Modify checkout-style source rather than an integrity-protected artifact.
        (source / 'bundle.json').unlink()
        manifest = json.loads((source / 'manifest.json').read_text())
        manifest['version'] = '0.2.0a2'
        (source / 'manifest.json').write_text(json.dumps(manifest))
        for harness in kit.ADAPTERS:
            for scope in ('user', 'project'):
                with self.subTest(harness=harness, scope=scope):
                    self.act('install', harness, scope)
                    with self.assertRaisesRegex(ValueError, 'update explicitly'):
                        self.act('install', harness, scope, source)
                    self.assertEqual(self.act('update', harness, scope, source)['version'], '0.2.0a2')
                    self.assertEqual(self.act('update', harness, scope, source)['status'], 'unchanged')
                    self.assertEqual(self.act('rollback', harness, scope)['version'], '0.2.0a1')
                    self.assertEqual(self.act('rollback', harness, scope)['version'], '0.2.0a2')
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
        for required in ('SKILL.md', 'references/commands.md', 'agents/openai.yaml',
                         'schemas/task.schema.json', 'docs/installation.md'):
            self.assertIn(required, files)

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
