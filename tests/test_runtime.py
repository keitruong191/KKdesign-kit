import json
import os
from pathlib import Path
import shutil
import site
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import venv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_install as kit


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kkdesign runtime spaces ')
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / 'home'
        self.project = self.base / 'product project'
        self.home.mkdir()
        self.project.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def act(self, action, source=ROOT, runtime=False):
        return kit.lifecycle(action, 'codex', 'project', self.home, self.project, source, runtime)

    def local_runtime(self, command):
        # No network in regressions. Real venv uses the suite's installed dependencies;
        # bootstrap HTTP smoke separately exercises actual venv + pip provisioning.
        if '-m' in command and command[command.index('-m') + 1] == 'venv':
            venv.EnvBuilder(with_pip=False).create(command[-1])
            purelib = subprocess.check_output(
                [str(kit.runtime_python(command[-1])), '-c',
                 'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip()
            (Path(purelib) / 'suite-dependencies.pth').write_text(
                '\n'.join(site.getsitepackages()) + '\n')
            return ''
        if '-m' in command and command[command.index('-m') + 1] == 'pip':
            return ''
        return self.real_run(command)

    def install(self):
        self.real_run = kit.run_runtime
        with patch.object(kit, 'run_runtime', side_effect=self.local_runtime):
            return self.act('install', runtime=True)

    def test_fresh_shell_launcher_and_lifecycle_preserve_skill_hashes(self):
        installed = self.install()
        target = Path(installed['target'])
        runtime = Path(installed['runtime'])
        before = kit.hashes(target)
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
        for key in ('VIRTUAL_ENV', 'PYTHONHOME', 'PYTHONPATH'):
            env.pop(key, None)
        example = self.base / 'fresh shell example'
        launcher = target / 'scripts/kkdesign_run.py'
        for args in (['materialize_example', '--output', str(example)],
                     ['kkdesign_core', 'validate', '--design', str(example / 'design')]):
            proc = subprocess.run([sys.executable, '-B', str(launcher), *args],
                                  cwd=self.home, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual((result['status'], result['errors'], result['warnings']), ('pass', [], []))
        self.assertEqual(self.act('install', runtime=True)['status'], 'unchanged')
        self.assertEqual(kit.hashes(target), before)
        self.assertEqual(self.act('uninstall')['status'], 'uninstalled')
        self.assertFalse(target.exists())
        self.assertTrue((runtime / 'runtime.json').is_file())
        self.assertEqual(self.act('inspect')['status'], 'absent')

    def test_inspect_reports_missing_requirements_and_target_as_modified(self):
        installed = self.install()
        target = Path(installed['target'])
        (target / 'requirements.txt').unlink()
        self.assertEqual(self.act('inspect')['status'], 'modified')
        with self.assertRaisesRegex(ValueError, 'modified'):
            self.act('install', runtime=True)
        shutil.rmtree(target)
        self.assertEqual(self.act('inspect')['status'], 'modified')

    def test_runtime_failure_leaves_no_managed_install_or_incomplete_environment(self):
        with patch.object(kit, 'run_runtime', side_effect=ValueError('dependency download failed')):
            with self.assertRaisesRegex(ValueError, 'dependency download failed'):
                self.act('install', runtime=True)
        target, state = kit.locations('codex', 'project', self.home, self.project)
        self.assertFalse(target.exists())
        self.assertFalse((state / 'state.json').exists())
        self.assertFalse(kit.runtime_path(self.home, (ROOT / 'requirements.txt').read_bytes()).exists())
        self.assertFalse((state / 'lock').exists())
        self.assertEqual(self.act('inspect')['status'], 'absent')

    def test_failed_installed_smoke_restores_previous_tree_and_ledger(self):
        self.install()
        target, state = kit.locations('codex', 'project', self.home, self.project)
        before = kit.hashes(target), (state / 'state.json').read_bytes()
        source = self.base / 'source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
        (source / 'SKILL.md').write_text((source / 'SKILL.md').read_text() + '\nRevision.\n')
        with patch.object(kit, 'smoke_runtime', side_effect=ValueError('installed validation failed')):
            with self.assertRaisesRegex(ValueError, 'installed validation failed'):
                self.act('update', source)
        self.assertEqual((kit.hashes(target), (state / 'state.json').read_bytes()), before)
        self.assertEqual(self.act('inspect')['status'], 'managed')

    def test_update_rollback_select_matching_dependency_runtime(self):
        installed = self.install()
        target = Path(installed['target'])
        original_runtime = installed['runtime']
        source = self.base / 'source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
        (source / 'requirements.txt').write_text((source / 'requirements.txt').read_text() + '\n# next dependency contract\n')
        with self.assertRaisesRegex(ValueError, 'update explicitly'):
            self.act('install', source, runtime=True)
        with patch.object(kit, 'run_runtime', side_effect=self.local_runtime):
            updated = self.act('update', source)
        self.assertNotEqual(updated['runtime'], original_runtime)
        self.assertEqual(self.act('rollback')['runtime'], original_runtime)
        self.assertEqual((target / 'requirements.txt').read_bytes(), (ROOT / 'requirements.txt').read_bytes())
        self.assertEqual(self.act('rollback')['runtime'], updated['runtime'])
        self.assertEqual(self.act('uninstall')['status'], 'uninstalled')
        self.assertTrue(Path(original_runtime).is_dir())
        self.assertTrue(Path(updated['runtime']).is_dir())

    def test_unowned_runtime_is_preserved_without_installing_skill(self):
        target, state = kit.locations('codex', 'project', self.home, self.project)
        runtime = kit.runtime_path(self.home, (ROOT / 'requirements.txt').read_bytes())
        runtime.mkdir(parents=True)
        marker = runtime / 'user-file.txt'
        marker.write_text('preserve this environment')
        with self.assertRaisesRegex(ValueError, 'Unowned or incomplete runtime'):
            self.act('install', runtime=True)
        self.assertEqual(marker.read_text(), 'preserve this environment')
        self.assertFalse(target.exists())
        self.assertEqual(self.act('inspect')['status'], 'absent')

    @unittest.skipIf(os.name == 'nt', 'synthetic executable uses a POSIX shell')
    def test_project_supplied_runtime_is_never_executed(self):
        _, state = kit.locations('codex', 'project', self.home, self.project)
        digest = kit.runtime_path(self.home, (ROOT / 'requirements.txt').read_bytes()).name
        untrusted = state / 'runtimes' / digest
        python = kit.runtime_python(untrusted)
        python.parent.mkdir(parents=True)
        executed = self.base / 'untrusted-executed'
        python.write_text('#!/bin/sh\nprintf executed > "' + str(executed) + '"\nexit 23\n')
        python.chmod(0o755)
        kit.write_json(untrusted / 'runtime.json',
                       {'identifier': kit.IDENTIFIER, 'requirementsSha256': digest})
        malicious_bytes = python.read_bytes()
        installed = self.install()
        self.assertFalse(executed.exists())
        self.assertEqual(python.read_bytes(), malicious_bytes)
        self.assertFalse(Path(installed['runtime']).is_relative_to(self.project))
        self.assertEqual(Path(installed['runtime']).parent, self.home / '.kkdesign-kit/runtimes')
        # Even a forged project ledger cannot redirect the launcher into that executable.
        record = kit.read_json(state / 'state.json')
        record['runtime'] = str(untrusted)
        kit.write_json(state / 'state.json', record)
        proc = subprocess.run(
            [sys.executable, '-B', str(Path(installed['target']) / 'scripts/kkdesign_run.py'),
             'kkdesign_core', '--help'], env=dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home)),
            cwd=self.home, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('No matching managed runtime', proc.stderr)
        self.assertFalse(executed.exists())

    def test_manual_install_and_baseline_update_use_current_interpreter(self):
        source = self.base / 'baseline source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
        manifest = kit.read_json(source / 'manifest.json')
        manifest['version'] = '0.4.0a1'
        kit.write_json(source / 'manifest.json', manifest)
        self.assertEqual(self.act('install', source)['status'], 'installed')
        for step in ('install', 'update'):
            if step == 'update':
                self.assertEqual(self.act('update')['status'], 'updated')
            target, state = kit.locations('codex', 'project', self.home, self.project)
            self.assertNotIn('runtime', kit.read_json(state / 'state.json'))
            launcher = str(target / 'scripts/kkdesign_run.py')
            example = self.base / (step + ' manual example')
            env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
            for args in (['materialize_example', '--output', str(example)],
                         ['kkdesign_core', 'validate', '--design', str(example / 'design')]):
                proc = subprocess.run([sys.executable, '-B', launcher, *args], cwd=self.home,
                                      env=env, capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual((result['status'], result['errors'], result['warnings']), ('pass', [], []))
            # An explicit but invalid runtime must never fall back to this interpreter.
            record = kit.read_json(state / 'state.json')
            for invalid in (None, '', str(self.home / '.kkdesign-kit/runtimes/wrong-hash')):
                record['runtime'] = invalid
                kit.write_json(state / 'state.json', record)
                refused = subprocess.run([sys.executable, '-B', launcher, 'kkdesign_core', '--help'],
                                         cwd=self.home, env=env, capture_output=True, text=True)
                self.assertNotEqual(refused.returncode, 0)
                self.assertIn('No matching managed runtime', refused.stderr)
            record.pop('runtime')
            kit.write_json(state / 'state.json', record)
        self.assertFalse(kit.runtime_root(self.home).exists())

    def test_shared_user_cache_survives_another_project_uninstall(self):
        installed = self.install()
        other = self.base / 'second project'
        other.mkdir()
        with kit.locked(kit.runtime_root(self.home)):
            with self.assertRaisesRegex(ValueError, 'busy'):
                kit.lifecycle('install', 'claude-code', 'project', self.home, other, ROOT, True)
        second = kit.lifecycle('install', 'claude-code', 'project', self.home, other, ROOT, True)
        self.assertEqual(second['runtime'], installed['runtime'])
        removed = self.act('uninstall')
        self.assertEqual(removed['retainedRuntimeRoot'], str(kit.runtime_root(self.home)))
        target = Path(second['target'])
        example = self.base / 'shared-runtime example'
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
        launcher = str(target / 'scripts/kkdesign_run.py')
        for args in (['materialize_example', '--output', str(example)],
                     ['kkdesign_core', 'validate', '--design', str(example / 'design')]):
            proc = subprocess.run([sys.executable, '-B', launcher, *args], cwd=other,
                                  env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'], 'pass')

    def test_project_cannot_contain_the_trusted_user_runtime_cache(self):
        nested_home = self.project / 'nested home'
        nested_home.mkdir()
        with self.assertRaisesRegex(ValueError, 'outside the destination project'):
            kit.lifecycle('install', 'codex', 'project', nested_home, self.project, ROOT, True)
        target, state = kit.locations('codex', 'project', nested_home, self.project)
        self.assertFalse(target.exists())
        self.assertFalse((state / 'state.json').exists())
        self.assertFalse(kit.runtime_root(nested_home).exists())


if __name__ == '__main__':
    unittest.main()
