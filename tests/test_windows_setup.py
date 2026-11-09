"""Native Windows consent, integrity, ACL and transaction preservation boundaries."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'nt', 'Requires native Windows PowerShell and ACLs')
class WindowsSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='Windows Setup spaces ')
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / 'home'
        self.shell = str(Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe')
        self.security = ROOT / 'scripts/kkdesign_windows_security.ps1'
        self.ps('. $testPaths[0]; New-PrivateDirectory $testPaths[1]', self.security, self.home)
        self.product = self.base / 'unrelated product'
        self.product.mkdir()
        self.sentinel = self.product / 'keep.txt'
        self.sentinel.write_text('synthetic project')
        self.env = dict(os.environ, USERPROFILE=str(self.home), PATH=str(self.base / 'no interpreters'))
        self.root = self.home / '.kkdesign-kit/bootstrap'
        arch = os.environ.get('PROCESSOR_ARCHITEW6432', os.environ.get('PROCESSOR_ARCHITECTURE'))
        target = 'aarch64' if arch.upper() == 'ARM64' else 'x86_64'
        self.cache = self.root / ('cpython-3.12.12-20251014-' + target + '-pc-windows-msvc')

    def tearDown(self):
        self.temp.cleanup()

    def ps(self, code, *args):
        # stdin script avoids PowerShell -Command argument re-parsing of paths.
        env = dict(os.environ, KK_TEST_ARGS=json.dumps([str(a) for a in args]))
        result = subprocess.run([self.shell, '-NoProfile', '-NonInteractive', '-Command', '-'],
                                input="$env:PSModulePath = [IO.Path]::Combine($PSHOME, 'Modules')\n"
                                      '$testPaths = ConvertFrom-Json $env:KK_TEST_ARGS\n' + code + '\n',
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stderr, result.stderr)
        return result

    def invoke(self, *args):
        return subprocess.run([self.shell, '-NoProfile', '-NonInteractive', '-File',
                               str(ROOT / 'scripts/kkdesign_setup_windows.ps1'),
                               '-PackageRoot', str(ROOT), *args], env=self.env, cwd=self.product,
                              capture_output=True, text=True, timeout=30)

    def test_no_python_node_or_consent_leaves_runtime_and_product_untouched(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'consent-required')
        # Native PowerShell can maintain its own AppData module-analysis cache;
        # no KKdesign runtime/state may be created before consent.
        self.assertFalse((self.home / '.kkdesign-kit').exists())
        self.assertEqual(list(self.product.iterdir()), [self.sentinel])

    def test_corrupt_cache_never_executes_and_is_preserved(self):
        self.cache.mkdir(parents=True)
        artifact = self.cache / 'archive.tar.gz'
        artifact.write_bytes(b'synthetic invalid archive')
        result = self.invoke('-Consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout.splitlines()[-1])['runtime'], 'error')
        self.assertEqual(artifact.read_bytes(), b'synthetic invalid archive')
        self.assertFalse((self.home / '.kkdesign-kit/runtimes').exists())
        self.assertFalse((self.root / 'setup.lock').exists())

    def test_foreign_write_acl_rejected_without_repair_or_download(self):
        cache = self.home / '.kkdesign-kit'
        cache.mkdir()
        self.ps('$acl = Get-Acl -LiteralPath $testPaths[0]; '
                '$sid = New-Object Security.Principal.SecurityIdentifier("S-1-1-0"); '
                '$rule = New-Object Security.AccessControl.FileSystemAccessRule($sid,"Modify","Allow"); '
                '$acl.AddAccessRule($rule); Set-Acl -LiteralPath $testPaths[0] -AclObject $acl', cache)
        result = self.invoke('-Consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['runtime'], 'error')
        self.assertEqual(list(cache.iterdir()), [])
        self.ps('$acl = Get-Acl -LiteralPath $testPaths[0]; '
                'if (-not ($acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]) | Where-Object { $_.IdentityReference.Value -eq "S-1-1-0" })) { throw "ACL was changed" }', cache)

    def test_actual_write_denial_preserves_existing_cache(self):
        cache = self.home / '.kkdesign-kit'
        cache.mkdir()
        self.ps('$acl = Get-Acl -LiteralPath $testPaths[0]; '
                '$acl.Sddl | Set-Content -LiteralPath $testPaths[1]; '
                '$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User; '
                '$rule = New-Object Security.AccessControl.FileSystemAccessRule($sid,"CreateFiles,CreateDirectories","Deny"); '
                '$acl.AddAccessRule($rule); Set-Acl -LiteralPath $testPaths[0] -AclObject $acl',
                cache, self.base / 'original-acl.txt')
        try:
            result = self.invoke('-Consent')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['runtime'], 'error')
            self.assertEqual(list(cache.iterdir()), [])
        finally:
            self.ps('$acl = New-Object Security.AccessControl.DirectorySecurity; '
                    '$acl.SetSecurityDescriptorSddlForm((Get-Content -Raw -LiteralPath $testPaths[1]).Trim()); '
                    'Set-Acl -LiteralPath $testPaths[0] -AclObject $acl', cache, self.base / 'original-acl.txt')

    def test_interrupted_lock_is_preserved(self):
        self.root.mkdir(parents=True)
        lock = self.root / 'setup.lock'
        lock.write_text('synthetic interrupted transaction')
        result = self.invoke('-Consent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(lock.read_text(), 'synthetic interrupted transaction')
        self.assertEqual(list(self.root.iterdir()), [lock])

    def test_junction_is_rejected_without_traversing_product(self):
        cache = self.home / '.kkdesign-kit'
        self.ps('New-Item -ItemType Junction -Path $testPaths[0] -Target $testPaths[1] | Out-Null', cache, self.product)
        try:
            result = self.invoke('-Consent')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['runtime'], 'error')
            self.assertEqual(list(self.product.iterdir()), [self.sentinel])
        finally:
            os.rmdir(cache)

    def test_relative_package_root_is_rejected_without_state(self):
        result = subprocess.run([self.shell, '-NoProfile', '-NonInteractive', '-File',
                                 str(ROOT / 'scripts/kkdesign_setup_windows.ps1'), '-PackageRoot', '.'],
                                env=self.env, cwd=self.product, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / '.kkdesign-kit').exists())


if __name__ == '__main__':
    unittest.main()
