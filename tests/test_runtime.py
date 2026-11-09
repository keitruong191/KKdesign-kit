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
        env = dict(os.environ, HOME=str(self.home))
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
        self.assertFalse(kit.runtime_path(state, (ROOT / 'requirements.txt').read_bytes()).exists())
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
        runtime = kit.runtime_path(state, (ROOT / 'requirements.txt').read_bytes())
        runtime.mkdir(parents=True)
        marker = runtime / 'user-file.txt'
        marker.write_text('preserve this environment')
        with self.assertRaisesRegex(ValueError, 'Unowned or incomplete runtime'):
            self.act('install', runtime=True)
        self.assertEqual(marker.read_text(), 'preserve this environment')
        self.assertFalse(target.exists())
        self.assertEqual(self.act('inspect')['status'], 'absent')


if __name__ == '__main__':
    unittest.main()
