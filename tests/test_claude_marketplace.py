import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_claude_marketplace as marketplace
import kkdesign_install as kit


class ClaudeMarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kkdesign marketplace spaces ')
        self.base = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def extract(self):
        output = self.base / 'marketplace.zip'
        marketplace.package(ROOT, output)
        with zipfile.ZipFile(output) as archive:
            archive.extractall(self.base / 'provider cache' / 'arbitrary version')
        return self.base / 'provider cache/arbitrary version/kkdesign-marketplace'

    def test_deterministic_artifact_and_relocated_verification(self):
        extracted = self.extract()
        second = self.base / 'second.zip'
        marketplace.package(ROOT, second)
        self.assertEqual((self.base / 'marketplace.zip').read_bytes(), second.read_bytes())
        catalog = kit.read_json(extracted / '.claude-plugin/marketplace.json')
        plugin = extracted / catalog['plugins'][0]['source']
        version = kit.read_json(ROOT / 'manifest.json')['version']
        descriptor = kit.read_json(plugin / '.claude-plugin/plugin.json')
        self.assertEqual(descriptor['version'], version)
        self.assertEqual(catalog['plugins'][0]['version'], version)
        # Run the extracted verifier in an unrelated CWD with isolated imports.
        result = subprocess.run([sys.executable, '-I', '-B',
                                 str(plugin / 'scripts/kkdesign_install.py'),
                                 'verify', '--source', str(plugin)],
                                cwd=self.base, env=dict(os.environ, HOME=str(self.base), USERPROFILE=str(self.base)),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'verified')
        (plugin / 'references/commands.md').write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            kit.verify(plugin)

    def test_plugin_launcher_refuses_to_execute_helper_or_create_standalone_state(self):
        plugin = self.extract() / 'plugins/kkdesign-kit'
        before = kit.hashes(plugin)
        output = self.base / 'must not be created'
        result = subprocess.run([sys.executable, '-B', str(plugin / 'scripts/kkdesign_run.py'), '--package-root', str(plugin),
                                 'materialize_example', '--output', str(output)],
                                cwd=self.base, env=dict(os.environ, HOME=str(self.base), USERPROFILE=str(self.base)),
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertEqual(kit.hashes(plugin), before)
        self.assertFalse((self.base / '.kkdesign-kit').exists())

    def test_no_overwrite_or_output_inside_source(self):
        archive = self.base / 'existing.zip'
        archive.write_bytes(b'keep this file')
        with self.assertRaises(FileExistsError):
            marketplace.package(ROOT, archive)
        self.assertEqual(archive.read_bytes(), b'keep this file')
        with self.assertRaises(ValueError):
            marketplace.package(ROOT, ROOT / 'forbidden.zip')
        self.assertFalse((ROOT / 'forbidden.zip').exists())

    def test_version_drift_and_unallowlisted_files_do_not_ship(self):
        source = self.base / 'source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
        (source / 'synthetic-private.json').write_text('not public')
        (source / 'scripts/not-a-public-helper.py').write_text('not public')
        output = self.base / 'allowlisted.zip'
        marketplace.package(source, output)
        with zipfile.ZipFile(output) as archive:
            self.assertFalse(any('synthetic-private' in name or 'not-a-public-helper' in name
                                 for name in archive.namelist()))
        descriptor = source / '.claude-plugin/plugin.json'
        value = kit.read_json(descriptor)
        value['version'] = 'wrong-version'
        kit.write_json(descriptor, value)
        with self.assertRaises(ValueError):
            marketplace.package(source, self.base / 'must-not-exist.zip')
        self.assertFalse((self.base / 'must-not-exist.zip').exists())


if __name__ == '__main__':
    unittest.main()
