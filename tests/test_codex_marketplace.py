"""Consumer regression coverage for the distributable Codex package."""
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
import build_codex_marketplace as marketplace
import kkdesign_install as kit


class CodexMarketplaceTests(unittest.TestCase):
    def test_relocated_payload_integrity_and_fail_closed_execution(self):
        with tempfile.TemporaryDirectory(prefix='codex package spaces ') as temp:
            base = Path(temp).resolve()
            first, second = base / 'one.zip', base / 'two.zip'
            marketplace.package(ROOT, first)
            marketplace.package(ROOT, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                archive.extractall(base / 'cache')
            catalog_root = base / 'cache/kkdesign-codex-marketplace'
            catalog = kit.read_json(catalog_root / '.agents/plugins/marketplace.json')
            plugin = catalog_root / catalog['plugins'][0]['source']['path']
            skill = plugin / 'skills/kkdesign-kit'
            version = kit.read_json(ROOT / 'manifest.json')['version']
            self.assertEqual(kit.read_json(plugin / '.codex-plugin/plugin.json')['version'], version)
            result = subprocess.run([sys.executable, '-I', '-B',
                                     str(skill / 'scripts/kkdesign_install.py'),
                                     'verify', '--source', str(skill)], cwd=base,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            before = kit.hashes(plugin)
            destination = base / 'must not exist'
            result = subprocess.run([sys.executable, '-I', '-B',
                                     str(skill / 'scripts/kkdesign_run.py'), '--package-root', str(skill),
                                     'materialize_example', '--output', str(destination)],
                                    cwd=base, env=dict(os.environ, HOME=str(base), USERPROFILE=str(base)),
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(destination.exists())
            self.assertEqual(kit.hashes(plugin), before)
            (skill / 'references/commands.md').write_text('tampered')
            with self.assertRaises(ValueError):
                kit.verify(skill)

    def test_rejects_version_drift_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source = base / 'source'
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '.hoangsa', '__pycache__'))
            descriptor = source / 'packaging/codex/.codex-plugin/plugin.json'
            value = kit.read_json(descriptor)
            value['version'] = 'wrong-version'
            kit.write_json(descriptor, value)
            with self.assertRaises(ValueError):
                marketplace.package(source, base / 'bad.zip')
            self.assertFalse((base / 'bad.zip').exists())
            output = base / 'existing.zip'
            output.write_bytes(b'preserved')
            with self.assertRaises(FileExistsError):
                marketplace.package(ROOT, output)
            self.assertEqual(output.read_bytes(), b'preserved')
            with self.assertRaises(ValueError):
                marketplace.package(ROOT, ROOT / 'forbidden.zip')


if __name__ == '__main__':
    unittest.main()
