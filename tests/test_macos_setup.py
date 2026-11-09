"""macOS bootstrap refusal and trust failures without acquired-code execution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'darwin', 'Uses native macOS system tools')
class MacSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mac Setup spaces ')
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / 'home'
        self.home.mkdir(mode=0o700)
        self.product = self.base / 'unrelated product'
        self.product.mkdir()
        self.sentinel = self.product / 'keep.txt'
        self.sentinel.write_text('synthetic')
        self.env = dict(os.environ, HOME=str(self.home), PATH='/nonexistent')
        self.target = 'aarch64' if os.uname().machine == 'arm64' else 'x86_64'
        self.cache = self.home / '.kkdesign-kit/bootstrap' / ('cpython-3.12.12-20251014-' + self.target)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *args):
        return subprocess.run(['/bin/sh', str(ROOT / 'scripts/kkdesign_setup_macos.sh'),
                               '--package-root', str(ROOT), *args], env=self.env, cwd=self.product,
                              capture_output=True, text=True, timeout=20)

    def test_refusal_with_no_python_or_node_has_no_cache_or_project_writes(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'consent-required')
        self.assertFalse((self.home / '.kkdesign-kit').exists())
        self.assertEqual(list(self.product.iterdir()), [self.sentinel])
        self.assertEqual(self.sentinel.read_text(), 'synthetic')

    def test_corrupt_retained_artifact_is_rejected_and_preserved_without_download(self):
        self.cache.mkdir(parents=True, mode=0o700)
        artifact = self.cache / 'archive.tar.gz'
        artifact.write_bytes(b'synthetic corrupt artifact')
        result = self.invoke('--consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['runtime'], 'error')
        self.assertEqual(artifact.read_bytes(), b'synthetic corrupt artifact')
        self.assertFalse((self.home / '.kkdesign-kit/runtimes').exists())
        self.assertFalse((self.cache.parent / 'lock').exists())

    def test_symlink_ancestry_and_shared_writable_cache_are_preserved(self):
        base = self.home / '.kkdesign-kit'
        base.symlink_to(self.product, target_is_directory=True)
        result = self.invoke('--consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(base.is_symlink())
        self.assertEqual(list(self.product.iterdir()), [self.sentinel])
        base.unlink()
        base.mkdir(mode=0o777)
        base.chmod(0o777)
        result = self.invoke('--consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(base.iterdir()), [])
        self.assertEqual(base.stat().st_mode & 0o777, 0o777)

    def test_real_connection_failure_cleans_staging_without_ready_state(self):
        # A refused loopback proxy is a real bounded curl failure, without an
        # external service, fake downloader or test-only production override.
        self.env.update(https_proxy='http://127.0.0.1:1', HTTPS_PROXY='http://127.0.0.1:1',
                        no_proxy='', NO_PROXY='')
        result = self.invoke('--consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout.splitlines()[-1])['runtime'], 'error')
        self.assertFalse(self.cache.exists())
        self.assertEqual(list(self.cache.parent.iterdir()), [])
        self.assertFalse((self.home / '.kkdesign-kit/runtimes').exists())

    @unittest.skipIf(hasattr(os, 'getuid') and os.getuid() == 0, 'Root bypasses write permissions')
    def test_real_write_denial_preserves_existing_cache(self):
        base = self.home / '.kkdesign-kit'
        base.mkdir(mode=0o500)
        try:
            result = self.invoke('--consent')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['runtime'], 'error')
            self.assertEqual(list(base.iterdir()), [])
        finally:
            base.chmod(0o700)

    def test_relative_package_is_rejected_before_cache_writes(self):
        result = subprocess.run(['/bin/sh', str(ROOT / 'scripts/kkdesign_setup_macos.sh'),
                                 '--package-root', '.', '--consent'], env=self.env, cwd=self.product,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / '.kkdesign-kit').exists())


if __name__ == '__main__':
    unittest.main()
