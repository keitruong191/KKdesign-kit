"""Consent, trusted-cache readiness and failure preservation at the Setup boundary."""
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_claude_marketplace as claude
import build_codex_marketplace as codex
import kkdesign_install as kit
import kkdesign_setup as setup


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='setup consumer spaces ')
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / 'home'
        self.home.mkdir()
        self.requirements = (ROOT / 'requirements.txt').read_bytes()
        self.runtime = kit.runtime_path(self.home, self.requirements)

    def tearDown(self):
        self.temp.cleanup()

    def verified_cache(self):
        # Real interpreter and installed suite dependencies, with no network.
        # Acquisition itself is exercised by the changed-path network smoke.
        self.runtime.parent.mkdir(parents=True, mode=0o700)
        venv.EnvBuilder(with_pip=False).create(self.runtime)
        purelib = subprocess.check_output([str(kit.runtime_python(self.runtime)), '-c',
                                          'import sysconfig; print(sysconfig.get_path("purelib"))'],
                                         text=True).strip()
        (Path(purelib) / 'suite-dependencies.pth').write_text('\n'.join(site.getsitepackages()) + '\n')
        (self.runtime / 'requirements.txt').write_bytes(self.requirements)
        kit.write_json(self.runtime / 'runtime.json', {'identifier': kit.IDENTIFIER,
                                                     'requirementsSha256': self.runtime.name})
        kit.write_json(self.runtime / 'setup.json', setup.fingerprint(self.runtime, self.requirements))

    def test_no_consent_does_not_create_execute_or_download_runtime(self):
        events = []
        with patch.object(kit, 'run_runtime', side_effect=AssertionError('execution before consent')):
            result = setup.setup(ROOT, self.home, emit=events.append)
        self.assertEqual(result['status'], 'consent-required')
        self.assertFalse((self.home / '.kkdesign-kit').exists())
        self.assertEqual(events[-1]['location'], str(self.runtime))
        self.assertEqual(result['externalTools'], 'unverified')

    def test_relocated_both_provider_packages_reuse_and_launch_real_helpers(self):
        self.verified_cache()
        original_runtime = (self.runtime / 'setup.json').read_bytes()
        for builder, relative in ((claude, 'kkdesign-marketplace/plugins/kkdesign-kit'),
                                  (codex, 'kkdesign-codex-marketplace/plugins/kkdesign-kit/skills/kkdesign-kit')):
            archive_path = self.base / (builder.__name__ + '.zip')
            builder.package(ROOT, archive_path)
            cache = self.base / builder.__name__
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(cache)
            package = cache / relative
            before = kit.hashes(cache)
            events = []
            result = setup.setup(package, self.home, emit=events.append)
            self.assertEqual((result['status'], result['reused'], result['externalTools']),
                             ('ready', True, 'unverified'))
            self.assertNotIn('consent-required', [event['phase'] for event in events])
            output = self.base / (builder.__name__ + ' example')
            env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
            launcher = package / 'scripts/kkdesign_run.py'
            for args in (['materialize_example', '--output', str(output)],
                         ['kkdesign_core', 'validate', '--design', str(output / 'design')]):
                proc = subprocess.run([sys.executable, '-I', '-B', str(launcher), *args],
                                      cwd=self.base, env=env, capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)['status'], 'pass')
            self.assertEqual(kit.hashes(cache), before)
            self.assertFalse((self.base / '.kkdesign-kit').exists())
        self.assertEqual((self.runtime / 'setup.json').read_bytes(), original_runtime)

    def test_plugin_in_legacy_shaped_directory_keeps_native_ownership(self):
        self.verified_cache()
        output = self.base / 'marketplace.zip'
        claude.package(ROOT, output)
        with zipfile.ZipFile(output) as archive:
            archive.extractall(self.base / 'extracted')
        package = self.base / '.agents/skills/kkdesign-kit'
        shutil.copytree(self.base / 'extracted/kkdesign-marketplace/plugins/kkdesign-kit', package)
        before = kit.hashes(package)
        destination = self.base / 'legacy shaped example'
        proc = subprocess.run([sys.executable, '-I', '-B', str(package / 'scripts/kkdesign_run.py'),
                               'materialize_example', '--output', str(destination)],
                              cwd=self.base, env=dict(os.environ, HOME=str(self.home)),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((destination / 'design/tasks/demo/task.json').is_file())
        self.assertEqual(kit.hashes(package), before)
        self.assertFalse((self.base / '.kkdesign-kit').exists())

    def test_receipt_requirements_and_missing_interpreter_fail_before_execution(self):
        self.verified_cache()
        receipt = self.runtime / 'setup.json'
        valid = receipt.read_bytes()
        cases = [('receipt', lambda: receipt.write_text('{}')),
                 ('requirements', lambda: (self.runtime / 'requirements.txt').write_text('other')),
                 ('interpreter', lambda: kit.runtime_python(self.runtime).unlink())]
        for name, tamper in cases:
            with self.subTest(name=name):
                receipt.write_bytes(valid)
                (self.runtime / 'requirements.txt').write_bytes(self.requirements)
                tamper()
                before = receipt.read_bytes()
                with patch.object(kit, 'run_runtime', side_effect=AssertionError('untrusted execution')):
                    result = setup.setup(ROOT, self.home, consent=True)
                self.assertEqual(result['runtime'], 'error')
                self.assertEqual(receipt.read_bytes(), before)
                self.assertTrue(self.runtime.exists())

    def test_project_supplied_runtime_is_ignored_and_symlink_cache_rejected(self):
        project = self.base / 'project'
        project.mkdir()
        (project / 'runtime.json').write_text(json.dumps({'runtime': str(sys.executable)}))
        self.assertEqual(setup.setup(ROOT, self.home)['status'], 'consent-required')
        (self.home / '.kkdesign-kit').symlink_to(project, target_is_directory=True)
        with patch.object(kit, 'run_runtime', side_effect=AssertionError('symlink execution')):
            result = setup.setup(ROOT, self.home, consent=True)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(list(project.iterdir()), [project / 'runtime.json'])

    @unittest.skipIf(os.name == 'nt', 'POSIX permissions; Windows policy needs native acceptance')
    def test_shared_writable_cache_is_preserved_and_never_executed(self):
        self.verified_cache()
        self.runtime.chmod(0o777)
        receipt = (self.runtime / 'setup.json').read_bytes()
        with patch.object(kit, 'run_runtime', side_effect=AssertionError('unsafe execution')):
            result = setup.setup(ROOT, self.home, consent=True)
        self.assertEqual((result['status'], result['code']), ('error', 'ownership'))
        self.assertEqual((self.runtime / 'setup.json').read_bytes(), receipt)

    def test_failed_new_provision_leaves_no_ready_cache(self):
        for failure in (ValueError('package index network unavailable'), PermissionError('cache denied'),
                        subprocess.TimeoutExpired('runtime', 180)):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(kit, 'run_runtime', side_effect=failure):
                    result = setup.setup(ROOT, self.home, consent=True)
                self.assertEqual((result['status'], result['runtime']), ('error', 'error'))
                self.assertTrue(result['nextAction'])
                self.assertFalse(self.runtime.exists())
                self.assertFalse((self.runtime.parent / 'lock').exists())

    def test_failed_helper_verification_never_reports_ready_or_removes_existing_runtime(self):
        self.verified_cache()
        source = self.base / 'broken helper package'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
        (source / 'schemas/task.schema.json').write_text('{}')
        # Invalid synthetic project data must be rejected by the actual helper.
        (source / 'examples/minimal/design/tasks/demo/task.json').write_text('{}')
        before = (self.runtime / 'setup.json').read_bytes()
        result = setup.setup(source, self.home)
        self.assertEqual((result['status'], result['runtime']), ('error', 'error'))
        self.assertEqual((self.runtime / 'setup.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
