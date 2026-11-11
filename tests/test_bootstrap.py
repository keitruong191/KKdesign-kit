import hashlib
import http.server
import json
import os
from pathlib import Path
import socketserver
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / 'install.sh'
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_install as kit
SH = shutil.which('sh')


class FixtureHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@unittest.skipUnless(os.name != 'nt' and SH and shutil.which('curl'), 'POSIX bootstrap requires sh and curl')
class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='bootstrap with spaces ')
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / 'project path with spaces'
        self.project.mkdir()
        self.home = self.base / 'home path with spaces'
        self.home.mkdir()
        self.assets = self.base / 'assets'
        self.assets.mkdir()
        version = kit.read_json(ROOT / 'manifest.json')['version']
        self.archive = self.assets / ('kkdesign-kit-' + version + '.zip')
        kit.package(ROOT, self.archive)
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        (self.assets / (self.archive.name + '.sha256')).write_text(
            digest + '  ' + self.archive.name + '\n', encoding='ascii')
        handler = lambda *args, **kwargs: FixtureHandler(*args, directory=str(self.assets), **kwargs)
        self.server = socketserver.TCPServer(('127.0.0.1', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = dict(os.environ, KKDESIGN_BOOTSTRAP_TEST_BASE_URL=
                        'http://127.0.0.1:%d' % self.server.server_address[1], HOME=str(self.home))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def run_bootstrap(self, *args, env=None):
        return subprocess.run([SH, str(BOOTSTRAP), *args], cwd=self.project,
                              env=env or self.env, input='unexpected prompt input\n',
                              text=True, capture_output=True)

    def test_unmanaged_target_is_preserved_after_real_download(self):
        target = self.project / '.agents/skills/kkdesign-kit'
        target.mkdir(parents=True)
        marker = target / 'user-file.txt'
        marker.write_text('keep')
        actual_temp = self.base / 'physical temp'
        actual_temp.mkdir()
        linked_temp = self.base / 'linked temp'
        linked_temp.symlink_to(actual_temp, target_is_directory=True)
        self.env['TMPDIR'] = str(linked_temp)
        result = self.run_bootstrap('--harness', 'codex', '--project', str(self.project))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unmanaged', result.stderr)
        self.assertEqual(marker.read_text(), 'keep')
        self.assertFalse((self.project / '.kkdesign-kit/installations/codex/state.json').exists())

    def test_checksum_mismatch_refuses_to_extract_or_install(self):
        (self.assets / (self.archive.name + '.sha256')).write_text('0' * 64 + '  ' + self.archive.name + '\n')
        result = self.run_bootstrap('--harness', 'codex')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SHA-256 mismatch', result.stderr)
        self.assertFalse((self.project / '.kkdesign-kit/installations/codex/state.json').exists())

    def test_download_failure_is_nonzero_and_never_reaches_installer(self):
        env = dict(self.env, KKDESIGN_BOOTSTRAP_TEST_BASE_URL='http://127.0.0.1:1')
        result = self.run_bootstrap('--harness', 'codex', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('release archive download failed', result.stderr)
        self.assertFalse((self.project / '.kkdesign-kit/installations/codex/state.json').exists())

    def test_unsafe_archive_path_refuses_extraction(self):
        with zipfile.ZipFile(self.archive, 'w') as package:
            package.writestr('../escaped', 'must not escape')
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        (self.assets / (self.archive.name + '.sha256')).write_text(
            digest + '  ' + self.archive.name + '\n', encoding='ascii')
        result = self.run_bootstrap('--harness', 'codex')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.base / 'escaped').exists())
        self.assertFalse((self.project / '.kkdesign-kit/installations/codex/state.json').exists())

    def test_old_python_and_non_loopback_transport_are_refused(self):
        directory = self.base / 'bin'
        directory.mkdir()
        fake = directory / 'python3'
        fake.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        fake.chmod(0o755)
        env = dict(self.env, PATH=str(directory) + os.pathsep + os.environ['PATH'])
        result = self.run_bootstrap('--harness', 'codex', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Python 3.9 or newer', result.stderr)
        for url in ('http://example.com', 'http://127.0.0.1:80@example.com'):
            with self.subTest(url=url):
                env = dict(self.env, KKDESIGN_BOOTSTRAP_TEST_BASE_URL=url)
                result = self.run_bootstrap('--harness', 'codex', env=env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('loopback', result.stderr)

    def test_missing_required_harness_is_actionable(self):
        result = self.run_bootstrap('--scope', 'project')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--harness codex or claude-code', result.stderr)

    def test_missing_python_or_curl_stops_before_managed_install(self):
        directory = self.base / 'empty-bin'
        directory.mkdir()
        env = dict(self.env, PATH=str(directory))
        result = self.run_bootstrap('--harness', 'codex', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('python3 3.9 or newer is required', result.stderr)
        (directory / 'python3').symlink_to(sys.executable)
        result = self.run_bootstrap('--harness', 'codex', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('curl is required', result.stderr)
        self.assertFalse((self.project / '.kkdesign-kit/installations/codex/state.json').exists())

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'root bypasses write permissions')
    def test_unwritable_destination_stops_without_managed_partial_install(self):
        self.project.chmod(0o500)
        try:
            result = self.run_bootstrap('--harness', 'codex')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('writable directory', result.stderr)
            self.assertFalse((self.project / '.kkdesign-kit').exists())
        finally:
            self.project.chmod(0o700)

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'root bypasses write permissions')
    def test_project_bootstrap_requires_writable_private_home(self):
        self.home.chmod(0o500)
        try:
            result = self.run_bootstrap('--harness', 'codex')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('writable user home', result.stderr)
            self.assertFalse((self.project / '.kkdesign-kit').exists())
        finally:
            self.home.chmod(0o700)


if __name__ == '__main__':
    unittest.main()
