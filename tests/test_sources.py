import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from io import BytesIO
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from kkdesign_sources import scan_sources, validate_registry


class SourceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def source(self, name, value):
        root = self.base / name
        root.mkdir(parents=True)
        (root / 'ds.json').write_text(json.dumps(value), encoding='utf-8')
        return {'id': name, 'provider': 'local', 'location': name}

    def document(self, color):
        return {'schemaVersion': '1.0.0', 'tokens': [
            {'id': 'color.brand', 'name': 'Brand', 'data': {'value': color}}],
            'styles': [], 'components': [], 'variants': [], 'modes': []}

    def test_local_sources_merge_in_order_and_record_overrides(self):
        first = self.source('base', self.document('#123456'))
        second = self.source('theme', self.document('#abcdef'))
        registry = scan_sources({'sources': [first, second]}, self.base)
        self.assertEqual(registry['assets']['tokens'][0]['data']['value'], '#abcdef')
        self.assertEqual(registry['overrides'], [{'category': 'tokens', 'id': 'color.brand',
                                                   'fromSourceId': 'base', 'toSourceId': 'theme'}])
        self.assertEqual(validate_registry(registry), [])
        self.assertNotIn(str(self.base), json.dumps(registry))

    def test_empty_category_is_distinct_from_empty_source_config(self):
        empty = self.source('empty', self.document('#000'))
        registry = scan_sources({'sources': [empty]}, self.base)
        self.assertEqual(registry['sources'][0]['coverage']['components'], 'empty')
        with self.assertRaisesRegex(ValueError, 'at least one source'):
            scan_sources({'sources': []}, self.base)

    def test_local_absolute_and_traversal_locations_are_rejected(self):
        for location in ('../outside', str(self.base / 'abs'), 'C:/outside'):
            with self.subTest(location=location), self.assertRaisesRegex(ValueError, 'relative|traversal|absolute'):
                scan_sources({'sources': [{'id': 'bad', 'provider': 'local', 'location': location}]}, self.base)

    def test_local_symlink_is_rejected(self):
        outside = self.base / 'outside'
        outside.mkdir()
        link = self.base / 'link'
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            scan_sources({'sources': [{'id': 'linked', 'provider': 'local', 'location': 'link'}]}, self.base)

    def test_invalid_ds_and_duplicate_ids_fail_with_diagnostics(self):
        root = self.base / 'bad'
        root.mkdir()
        (root / 'ds.json').write_text(json.dumps({'schemaVersion': '0.9.0'}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'schemaVersion'):
            scan_sources({'sources': [{'id': 'bad', 'provider': 'local', 'location': 'bad'}]}, self.base)
        valid = self.source('one', self.document('#000'))
        with self.assertRaisesRegex(ValueError, 'Duplicate source id'):
            scan_sources({'sources': [valid, {'id': 'one', 'provider': 'local', 'location': 'one'}]}, self.base)

    def test_dtcg_tokens_flatten_to_stable_paths_and_explicit_modes(self):
        root = self.base / 'dtcg'
        root.mkdir()
        (root / 'tokens.json').write_text(json.dumps({'$modes': {'dark': {'label': 'Dark'}},
                                                        'color': {'brand': {'$type': 'color', '$value': '#112233'}}}), encoding='utf-8')
        registry = scan_sources({'sources': [{'id': 'dtcg', 'provider': 'local', 'location': 'dtcg'}]}, self.base)
        self.assertEqual(registry['assets']['tokens'][0]['id'], 'color.brand')
        self.assertEqual(registry['assets']['modes'][0]['id'], 'dark')
        self.assertEqual(validate_registry(registry), [])

    def test_dtcg_inherited_types_and_dotted_identity_collisions(self):
        root = self.base / 'typed'
        root.mkdir()
        (root / 'tokens.json').write_text(json.dumps({'$type': 'dimension',
                                                        'space': {'small': {'$value': '4px'}}}), encoding='utf-8')
        registry = scan_sources({'sources': [{'id': 'typed', 'provider': 'local', 'location': 'typed'}]}, self.base)
        self.assertEqual(registry['assets']['tokens'][0]['data']['$type'], 'dimension')
        collision = self.base / 'collision'
        collision.mkdir()
        (collision / 'tokens.json').write_text(json.dumps({'a.b': {'$type': 'color', '$value': '#000'},
                                                            'a': {'b': {'$type': 'color', '$value': '#fff'}}}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'identity collision'):
            scan_sources({'sources': [{'id': 'collision', 'provider': 'local', 'location': 'collision'}]}, self.base)

    def test_asset_credentials_and_absolute_machine_paths_are_rejected(self):
        for index, data in enumerate(({'FIGMA_ACCESS_TOKEN': 'sample'},
                                      {'example': '/Users/test/private.json'})):
            name = 'unsafe-' + str(index)
            root = self.base / name
            root.mkdir()
            (root / 'ds.json').write_text(json.dumps({'schemaVersion': '1.0.0',
                                                       'tokens': [{'id': 'token', 'name': 'Synthetic', 'data': data}]}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Credential|Absolute'):
                scan_sources({'sources': [{'id': name, 'provider': 'local', 'location': name}]}, self.base)


    def test_figma_capture_is_supported_as_local_synthetic_input(self):
        capture = {'schemaVersion': '1.0.0', 'kind': 'figma-capture',
                   'fileKey': 'public-synthetic', 'document': {'id': '0:0'},
                   'components': [{'key': 'native-key', 'nodeId': '1:2', 'name': 'Button'}],
                   'componentSets': [], 'styles': [{'key': 'style-key', 'name': 'Text',
                                                      'styleType': 'TEXT', 'ignoredPrivateField': 'discard'}],
                   'variables': {'variables': [{'id': 'var-id', 'name': 'color/brand',
                                                'resolvedType': 'COLOR', 'valuesByMode': {'mode-id': '#2468AC'}}],
                                 'variableCollections': [{'id': 'collection', 'modes': [
                                     {'modeId': 'mode-id', 'name': 'Light'}]}]},
                   'captureCounts': {'styles': {'total': 10, 'returned': 1},
                                     'variables': {'total': 4, 'returned': 1}},
                   'missingNodeIds': ['synthetic-missing'], 'unavailableProperties': 1}
        (self.base / 'capture.json').write_text(json.dumps(capture), encoding='utf-8')
        registry = scan_sources({'sources': [{'id': 'figma-copy', 'provider': 'figma',
                                               'location': 'https://www.figma.com/design/public-synthetic/Library',
                                               'capture': 'capture.json'}]}, self.base)
        snapshot = registry['sources'][0]
        self.assertEqual(snapshot['revision'], 'unknown')
        self.assertEqual(registry['assets']['components'][0]['id'], '1:2')
        self.assertEqual(registry['assets']['tokens'][0]['id'], 'var-id')
        self.assertEqual(snapshot['coverage']['tokens'], 'partial')
        self.assertEqual(snapshot['coverage']['styles'], 'partial')
        self.assertTrue(snapshot['limitations'])
        self.assertNotIn('ignoredPrivateField', json.dumps(snapshot))
        self.assertEqual(validate_registry(registry), [])
        (self.base / 'other.json').write_text(json.dumps(dict(capture, fileKey='another-file')), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'fileKey'):
            scan_sources({'sources': [{'id': 'wrong', 'provider': 'figma',
                                       'location': 'https://www.figma.com/design/public-synthetic/Library',
                                       'capture': 'other.json'}]}, self.base)

    def test_figma_rest_preserves_native_variants_and_unavailable_variables(self):
        document = {
            'version': 'revision-one',
            'document': {'type': 'DOCUMENT', 'children': [
                {'type': 'COMPONENT_SET', 'id': '1:1', 'name': 'Button',
                 'componentPropertyDefinitions': {'Size': {'type': 'VARIANT', 'variantOptions': ['Small', 'Large']}},
                 'children': [{'type': 'COMPONENT', 'id': '1:2', 'name': 'Size=Small',
                               'variantProperties': {'Size': 'Small'}}]}]},
            'components': {'1:2': {'name': 'Size=Small', 'key': 'native-component-key'}},
            'componentSets': {'1:1': {'name': 'Button', 'key': 'native-set-key'}},
            'styles': {'2:1': {'name': 'Body', 'key': 'native-style-key', 'styleType': 'TEXT'}}
        }
        def response(request, timeout):
            if request.full_url.endswith('/variables/local'):
                raise HTTPError(request.full_url, 403, 'unavailable', {}, None)
            return BytesIO(json.dumps(document).encode())

        with patch.dict(os.environ, {'FIGMA_ACCESS_TOKEN': 'synthetic-not-a-credential'}):
            with patch('kkdesign_sources.urlopen', side_effect=response):
                registry = scan_sources({'sources': [{'id': 'figma', 'provider': 'figma',
                    'location': 'https://www.figma.com/design/public-synthetic/Library',
                    'nodeIds': ['1:1']}]}, self.base)
        components = registry['assets']['components']
        self.assertEqual(components[0]['data']['key'], 'native-component-key')
        self.assertEqual(components[0]['data']['variantProperties'], {'Size': 'Small'})
        self.assertEqual(registry['assets']['variants'][0]['data']['componentPropertyDefinitions']['Size']['variantOptions'],
                         ['Small', 'Large'])
        self.assertEqual(registry['sources'][0]['coverage']['tokens'], 'unavailable')
        self.assertEqual(registry['sources'][0]['revision'], 'revision-one')
        self.assertEqual(validate_registry(registry), [])

    def test_figma_capture_retains_style_values_and_collection_scoped_modes(self):
        capture = {'schemaVersion': '1.0.0', 'kind': 'figma-capture', 'fileKey': 'public-synthetic',
                   'document': {'type': 'DOCUMENT'}, 'components': [], 'componentSets': [],
                   'styles': [{'key': 'paint-key', 'name': 'Brand', 'paints': [{'type': 'SOLID', 'color': {'r': 0, 'g': 0, 'b': 1}}]}],
                   'variables': {'variables': [], 'variableCollections': [
                       {'id': 'collection-a', 'modes': [{'modeId': '1:0', 'name': 'Light'}]},
                       {'id': 'collection-b', 'modes': [{'modeId': '1:0', 'name': 'Light'}]}]}}
        (self.base / 'capture.json').write_text(json.dumps(capture), encoding='utf-8')
        registry = scan_sources({'sources': [{'id': 'figma', 'provider': 'figma',
            'location': 'https://www.figma.com/design/public-synthetic/Library', 'capture': 'capture.json'}]}, self.base)
        self.assertEqual(registry['assets']['styles'][0]['data']['paints'][0]['color']['b'], 1)
        self.assertEqual({mode['id'] for mode in registry['assets']['modes']}, {'collection-a/1:0', 'collection-b/1:0'})
        self.assertEqual(validate_registry(registry), [])

    def test_git_reads_committed_tree_without_checkout(self):
        repo = self.base / 'repo'
        repo.mkdir()
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'fixture@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Fixture'], check=True)
        (repo / 'ds.json').write_text(json.dumps(self.document('#334455')), encoding='utf-8')
        subprocess.run(['git', '-C', str(repo), 'add', 'ds.json'], check=True)
        subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'synthetic fixture'], check=True)
        revision = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], check=True,
                                  stdout=subprocess.PIPE, text=True).stdout.strip()
        (repo / 'ds.json').write_text('working tree must not be read', encoding='utf-8')
        registry = scan_sources({'sources': [{'id': 'git-source', 'provider': 'git', 'location': 'repo'}]}, self.base)
        self.assertEqual(registry['sources'][0]['revision'], revision)
        self.assertEqual(registry['assets']['tokens'][0]['data']['value'], '#334455')

    def test_figma_missing_token_fails_without_network(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'FIGMA_ACCESS_TOKEN'):
                scan_sources({'sources': [{'id': 'figma', 'provider': 'figma',
                                           'location': 'https://www.figma.com/design/abc123/Synthetic'}]}, self.base)

    def test_registry_validator_reports_bad_hash_source_and_merge_tampering(self):
        valid = self.source('valid', self.document('#000'))
        registry = scan_sources({'sources': [valid]}, self.base)
        registry = json.loads(json.dumps(registry))
        registry['sources'][0]['contentHash'] = 'bad'
        registry['assets']['tokens'][0]['data']['value'] = '#fff'
        errors = '\\n'.join(validate_registry(registry))
        self.assertIn('contentHash', errors)
        self.assertIn('Merged assets.tokens', errors)


if __name__ == '__main__':
    unittest.main()
