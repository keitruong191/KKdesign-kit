"""Migration trust, consent, discovery and preservation at the consumer boundary."""
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import zipfile

import test_setup as fixtures
ROOT = fixtures.ROOT
import build_claude_marketplace as claude
import build_codex_marketplace as codex
import kkdesign_install as kit
import kkdesign_migration as migration
import kkdesign_setup as setup


class MigrationTests(unittest.TestCase):
    setUp = fixtures.SetupTests.setUp
    tearDown = fixtures.SetupTests.tearDown
    verified_cache = fixtures.SetupTests.verified_cache

    def plugin(self, builder=claude):
        output = self.base / (builder.__name__ + '.zip')
        builder.package(ROOT, output)
        cache = self.base / builder.__name__
        with zipfile.ZipFile(output) as archive:
            archive.extractall(cache)
        return cache / ('kkdesign-marketplace/plugins/kkdesign-kit' if builder == claude else
                        'kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit')

    def install(self, base, harness='codex', scope='project'):
        kit.lifecycle('install', harness, scope, self.home, base, ROOT)
        return kit.locations(harness, scope, self.home, base)[0]

    def test_explicit_project_discovers_both_harnesses_all_scopes_and_legacy_paths(self):
        project = self.home / 'ancestor/project'
        project.mkdir(parents=True)
        ancestor = self.install(project.parent)
        unrelated = self.base / 'unrelated fixture project'
        unrelated.mkdir()
        user = self.install(unrelated, scope='user')
        local = self.install(project, 'claude-code')
        legacy = project.parent / '.codex/skills/kkdesign-kit'
        legacy.mkdir(parents=True)
        command = self.home / '.claude/commands/kkdesign-kit.md'
        command.parent.mkdir(parents=True)
        command.write_text('synthetic command')
        copies = migration.discover(self.home, project, ROOT)
        self.assertEqual({item['location'] for item in copies}, set(map(str, (user, local, ancestor, legacy, command))))
        self.assertEqual({item['scope'] for item in copies}, {'user', 'project', 'ancestor'})
        self.assertEqual(sum(item['ownership'] == 'managed' for item in copies), 3)
        self.assertEqual({item['version'] for item in copies if item['ownership'] == 'managed'},
                         {kit.read_json(ROOT / 'manifest.json')['version']})
        with self.assertRaises(ValueError):
            migration.discover(self.home, Path('relative'), ROOT)

    def test_declining_or_partial_consent_never_mutates_or_provisions(self):
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        first = self.install(project)
        second = self.install(project, 'claude-code', 'user')
        before = kit.hashes(self.base)
        for selected in ((), (first,)):
            with patch.object(kit, 'run_runtime', side_effect=AssertionError('execution before migration consent')):
                result = setup.setup(package, self.home, consent=True, project=project, migrate=selected)
            self.assertEqual(result['status'], 'migration-consent-required')
            self.assertEqual(kit.hashes(self.base), before)
        self.assertTrue(second.is_dir())

    def test_clean_migration_both_plugins_preserves_data_runtime_and_inactive_copy(self):
        self.verified_cache()
        project = self.home / 'project'
        project.mkdir()
        marker = project / 'DESIGN.md'
        marker.write_text('synthetic lessons profiles tasks credentials')
        for builder in (claude, codex):
            with self.subTest(provider=builder.__name__):
                package = self.plugin(builder)
                old = self.install(project)
                before_old = kit.hashes(old)
                plugin_before = kit.hashes(package)
                runtime_before = setup.fingerprint(self.runtime, self.requirements)
                result = setup.setup(package, self.home, project=project, migrate=[old])
                self.assertEqual((result['status'], result['migration']['status']), ('ready', 'migrated'))
                self.assertFalse(old.exists())
                self.assertEqual(migration.discover(self.home, project, package), [])
                retained = Path(result['migration']['retained'][0])
                self.assertEqual(kit.hashes(retained / 'skill'), before_old)
                self.assertTrue((retained / 'state.json').is_file())
                self.assertEqual(kit.hashes(package), plugin_before)
                self.assertEqual(setup.fingerprint(self.runtime, self.requirements), runtime_before)
                self.assertEqual(marker.read_text(), 'synthetic lessons profiles tasks credentials')

    def test_modified_unmanaged_invalid_ledger_symlink_and_added_data_are_preserved(self):
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        target = self.install(project)
        state = project / '.kkdesign-kit/installations/codex/state.json'
        original = state.read_bytes()
        cases = [('changed', lambda: (target / 'SKILL.md').write_text('edited'), 'modified'),
                 ('unmanaged', state.unlink, 'unmanaged'),
                 ('invalid', lambda: state.write_text('[]'), 'unknown'),
                 ('extra data', lambda: (target / 'private-project.json').write_text('synthetic'), 'modified')]
        for name, mutate, ownership in cases:
            with self.subTest(case=name):
                shutil.rmtree(target)
                # Restore exact original distribution without touching the ledger.
                target.mkdir()
                for relative, data in kit.payload(ROOT)[0].items():
                    dest = target / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                state.write_bytes(original)
                mutate()
                before = kit.hashes(self.base)
                result = setup.setup(package, self.home, project=project, migrate=[target], consent=True)
                self.assertEqual(result['status'], 'migration-conflict')
                self.assertEqual(result['migration']['copies'][0]['ownership'], ownership)
                self.assertEqual(kit.hashes(self.base), before)
        state.write_bytes(original)
        shutil.rmtree(target)
        destination = self.base / 'preserved target'
        destination.mkdir()
        (destination / 'keep').write_text('synthetic')
        target.symlink_to(destination, target_is_directory=True)
        result = setup.setup(package, self.home, project=project, migrate=[target])
        self.assertEqual(result['status'], 'migration-conflict')
        self.assertTrue(target.is_symlink())
        self.assertEqual((destination / 'keep').read_text(), 'synthetic')

    def test_plugin_and_helpers_must_pass_before_deactivation(self):
        self.verified_cache()
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        old = self.install(project)
        before = kit.hashes(old)
        with patch.object(setup, 'verify_helpers', side_effect=ValueError('real helper validation failed')):
            result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'error')
        self.assertEqual(kit.hashes(old), before)
        (package / '.claude-plugin/plugin.json').unlink()
        result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'error')
        self.assertEqual(kit.hashes(old), before)

    def test_ownership_change_and_new_conflict_during_helpers_prevent_moves(self):
        self.verified_cache()
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        old = self.install(project)
        def new_conflict(*args):
            path = project / '.claude/commands/kkdesign-kit.md'
            path.parent.mkdir(parents=True)
            path.write_text('synthetic new conflict')
        with patch.object(setup, 'verify_helpers', side_effect=new_conflict):
            result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'error')
        self.assertTrue(old.is_dir())
        self.assertFalse((project / '.kkdesign-kit/installations/codex/migrated').exists())

    def test_failed_move_restores_all_active_copies_and_ledgers(self):
        self.verified_cache()
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        first = self.install(project)
        second = self.install(project, 'claude-code')
        before = {str(p): kit.hashes(p) for p in (first, second)}
        rename = Path.rename
        def fail_second(source, target):
            if source == second:
                raise OSError('synthetic move denial')
            return rename(source, target)
        with patch.object(Path, 'rename', fail_second):
            result = setup.setup(package, self.home, project=project, migrate=[first, second])
        self.assertEqual(result['status'], 'error')
        for path in (first, second):
            self.assertEqual(kit.hashes(path), before[str(path)])
        self.assertTrue(all(item['ownership'] == 'managed' for item in migration.discover(self.home, project, package)))

    def test_runtime_consent_is_separate_and_old_shared_runtime_is_never_deleted(self):
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        old = self.install(project)
        legacy_runtime = kit.runtime_path(self.home, self.requirements)
        legacy_runtime.mkdir(parents=True)
        (legacy_runtime / 'keep').write_text('synthetic shared consumer')
        before = kit.hashes(old)
        result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'consent-required')
        self.assertEqual(kit.hashes(old), before)
        self.assertEqual((legacy_runtime / 'keep').read_text(), 'synthetic shared consumer')

    @unittest.skipIf(os.name == 'nt', 'POSIX archive permissions; Windows ACL acceptance is separate')
    def test_untrusted_archive_and_busy_owner_are_preserved(self):
        self.verified_cache()
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        old = self.install(project)
        state = project / '.kkdesign-kit/installations/codex'
        (state / 'lock').mkdir()
        result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'migration-conflict')
        self.assertTrue((state / 'lock').is_dir())
        (state / 'lock').rmdir()
        archive = state / 'migrated'
        archive.mkdir()
        archive.chmod(0o777)
        before = kit.hashes(old)
        result = setup.setup(package, self.home, project=project, migrate=[old])
        self.assertEqual(result['status'], 'error')
        self.assertEqual(kit.hashes(old), before)
        self.assertEqual(archive.stat().st_mode & 0o777, 0o777)
        archive.chmod(0o700)

    def test_unmatched_consent_never_migrates_without_explicit_project(self):
        package = self.plugin()
        project = self.home / 'project'
        project.mkdir()
        old = self.install(project, scope='user')
        result = setup.setup(package, self.home, migrate=[old])
        self.assertEqual(result['status'], 'migration-consent-required')
        self.assertTrue(old.is_dir())
        self.assertFalse(self.runtime.exists())


if __name__ == '__main__':
    unittest.main()
