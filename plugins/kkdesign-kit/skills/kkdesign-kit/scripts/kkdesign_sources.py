#!/usr/bin/env python3
"""Read-only, DS-neutral adapters for local, Git and Figma sources."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlsplit
from urllib.request import Request, urlopen

CATEGORIES = ('tokens', 'styles', 'components', 'variants', 'modes')
_SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
_SHA256 = re.compile(r'^[0-9a-f]{64}$')
_MAX_RESPONSE = 10 * 1024 * 1024
_TIMEOUT = 8
_SECRET_KEY = re.compile(
    r'^(?:(?:figma[_-]?)?(?:access|refresh)[_-]?token|token|secret|client[_-]?secret|'
    r'password|passwd|credentials?|authorization|api[_-]?key|access[_-]?key|private[_-]?key)$', re.I)
_ABSOLUTE_PATH = re.compile(r'^(?:/(?:Users|home|private|tmp|var|Volumes)/|[A-Za-z]:[\\\\/]|~[/\\\\])', re.I)



def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _safe_relative(value, label):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError(label + ' must be a non-empty relative POSIX path')
    path = PurePosixPath(value)
    if (path.is_absolute() or re.match(r'^[A-Za-z]:', value) or
            any(part in ('.', '..') for part in value.split('/'))):
        raise ValueError(label + ' must not be absolute or contain traversal')
    return path


def _local_root(base, location):
    relative = _safe_relative(location, 'Local source location')
    base = Path(base).resolve()
    candidate = base.joinpath(*relative.parts)
    current = base
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Local source contains a symlink: ' + location)
    resolved = candidate.resolve()
    if not resolved.is_relative_to(base):
        raise ValueError('Local source escapes config directory: ' + location)
    if not resolved.exists() or not resolved.is_dir():
        raise ValueError('Local source directory is unavailable: ' + location)
    return resolved


def _read_file(root, filename):
    path = root / filename
    if path.is_symlink():
        raise ValueError('Source file is a symlink: ' + filename)
    if not path.is_file():
        return None
    if path.stat().st_size > _MAX_RESPONSE:
        raise ValueError('Source file exceeds 10 MiB limit: ' + filename)
    return path.read_bytes()


def _asset(category, identifier, name, source_id, data):
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError('Asset id must be a non-empty string in ' + category)
    if not isinstance(name, str) or not name.strip():
        raise ValueError('Asset name must be a non-empty string in ' + category)
    if not isinstance(data, dict):
        raise ValueError('Asset data must be a JSON object in ' + category)
    _safe_data(identifier, 'asset.id')
    _safe_data(name, 'asset.name')
    _safe_data(data)
    return {'id': identifier, 'name': name, 'sourceId': source_id, 'data': data}


def _safe_data(value, path='data'):
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or _SECRET_KEY.search(key):
                raise ValueError('Credential-like data key rejected at ' + path)
            _safe_data(child, path + '.' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _safe_data(child, path + '[' + str(index) + ']')
    elif isinstance(value, str):
        if _ABSOLUTE_PATH.match(value):
            raise ValueError('Absolute machine path rejected at ' + path)
        parsed = urlsplit(value)
        if parsed.username or parsed.password or (
                parsed.scheme and any(_SECRET_KEY.fullmatch(key) for key, _ in parse_qsl(parsed.query))):
            raise ValueError('Credential-bearing URL rejected at ' + path)


def _canonical_doc(doc, source_id):
    if not isinstance(doc, dict) or doc.get('schemaVersion') != '1.0.0':
        raise ValueError('ds.json must be an object with schemaVersion "1.0.0"')
    assets = {key: [] for key in CATEGORIES}
    for category in CATEGORIES:
        rows = doc.get(category, [])
        if not isinstance(rows, list):
            raise ValueError('ds.json category must be an array: ' + category)
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(('id', 'name', 'data')) - row.keys():
                raise ValueError('Each ds.json asset requires id, name and data')
            item = _asset(category, row['id'], row['name'], source_id, row['data'])
            if item['id'] in seen:
                raise ValueError('Duplicate asset id in ' + category + ': ' + item['id'])
            seen.add(item['id'])
            assets[category].append(item)
    return assets


def _dtcg_flatten(value, source_id):
    assets = {key: [] for key in CATEGORIES}
    seen_ids = set()

    def visit(node, path, inherited_type=None):
        if not isinstance(node, dict):
            return
        inherited_type = node.get('$type', inherited_type)
        if '$value' in node:
            if not path:
                raise ValueError('DTCG root cannot itself be a token')
            if not inherited_type:
                raise ValueError('DTCG token has no inherited or explicit $type: ' + '.'.join(path))
            identity = '.'.join(path)
            if identity in seen_ids:
                raise ValueError('DTCG flattened token identity collision: ' + identity)
            seen_ids.add(identity)
            token_data = {'$type': inherited_type, '$value': node['$value']}
            if '$description' in node:
                token_data['$description'] = node['$description']
            if '$extensions' in node:
                token_data['$extensions'] = node['$extensions']
            assets['tokens'].append(_asset('tokens', identity, path[-1], source_id, token_data))
            return
        for key, child in node.items():
            if not key.startswith('$'):
                visit(child, path + [key], inherited_type)

    if not isinstance(value, dict):
        raise ValueError('tokens.json must contain a JSON object')
    visit(value, [])
    modes = value.get('$modes')
    if modes is not None:
        if not isinstance(modes, dict):
            raise ValueError('DTCG $modes must be an object')
        for mode_id, mode_value in modes.items():
            assets['modes'].append(_asset('modes', str(mode_id), str(mode_id), source_id,
                                          {'value': mode_value}))
    return assets


def _merge_file_payload(ds_raw, tokens_raw, source_id):
    assets = {key: [] for key in CATEGORIES}
    content_parts = []
    if ds_raw is not None:
        content_parts.append(('ds.json', ds_raw))
        try:
            assets = _canonical_doc(json.loads(ds_raw.decode('utf-8')), source_id)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError('Invalid ds.json: ' + str(exc))
    if tokens_raw is not None:
        content_parts.append(('tokens.json', tokens_raw))
        try:
            token_assets = _dtcg_flatten(json.loads(tokens_raw.decode('utf-8')), source_id)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError('Invalid tokens.json: ' + str(exc))
        for category in CATEGORIES:
            if category == 'tokens' and assets[category]:
                raise ValueError('Use either ds.json or tokens.json for tokens, not both')
            assets[category].extend(token_assets[category])
    # hash bytes and names with length framing, independent of discovery time.
    digest = hashlib.sha256()
    for filename, raw in content_parts:
        digest.update(filename.encode('utf-8') + b'\0' + raw + b'\0')
    return assets, digest.hexdigest()


def _coverage(assets, declared=None):
    return {category: ('undeclared' if declared is not None and category not in declared else
                       'available' if assets[category] else 'empty') for category in CATEGORIES}


def _local_source(declaration, base):
    root = _local_root(base, declaration['location'])
    ds_raw = _read_file(root, 'ds.json')
    tokens_raw = _read_file(root, 'tokens.json')
    if ds_raw is None and tokens_raw is None:
        raise ValueError('Source directory must contain ds.json or tokens.json')
    assets, digest = _merge_file_payload(ds_raw, tokens_raw, declaration['id'])
    declared = set()
    if ds_raw is not None:
        declared.update(key for key in CATEGORIES
                        if key in json.loads(ds_raw.decode('utf-8')))
    if tokens_raw is not None:
        token_doc = json.loads(tokens_raw.decode('utf-8'))
        declared.add('tokens')
        if '$modes' in token_doc:
            declared.add('modes')
    return assets, digest, 'local:' + digest[:16], [], _coverage(assets, declared)


def _git_source(declaration, base):
    root = _local_root(base, declaration['location'])
    ref = declaration.get('ref', 'HEAD')
    if not isinstance(ref, str) or not ref or ref.startswith('-') or '\x00' in ref:
        raise ValueError('Git ref must be a non-empty revision name')
    subdir = declaration.get('subdir', '.')
    if subdir == '.':
        prefix = ''
    else:
        prefix = str(_safe_relative(subdir, 'Git subdir')) + '/'
    git_env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    revision_result = subprocess.run(
        ['git', '-C', str(root), 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=15, env=git_env)
    if revision_result.returncode:
        raise ValueError('Git ref is unavailable')
    revision = revision_result.stdout.decode('ascii', 'replace').strip()
    if not re.fullmatch(r'[0-9a-fA-F]{40,64}', revision):
        raise ValueError('Git ref did not resolve to a commit')
    found = []
    for filename in ('ds.json', 'tokens.json'):
        command = ['git', '-C', str(root), 'show', revision + ':' + prefix + filename]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                check=False, timeout=15, env=git_env)
        if result.returncode == 0:
            if len(result.stdout) > _MAX_RESPONSE:
                raise ValueError('Committed source file exceeds 10 MiB limit: ' + filename)
            found.append((filename, result.stdout))
    if not found:
        raise ValueError('Git ref has no supported ds.json or tokens.json at requested subdir')
    raw = dict(found)
    assets, digest = _merge_file_payload(raw.get('ds.json'), raw.get('tokens.json'), declaration['id'])
    declared = set()
    if raw.get('ds.json') is not None:
        declared.update(category for category in CATEGORIES
                        if category in json.loads(raw['ds.json'].decode('utf-8')))
    if raw.get('tokens.json') is not None:
        token_doc = json.loads(raw['tokens.json'].decode('utf-8'))
        declared.add('tokens')
        if '$modes' in token_doc:
            declared.add('modes')
    return assets, digest, revision, [], _coverage(assets, declared)


def _figma_capture(declaration, base):
    root = Path(base).resolve()
    relative = _safe_relative(declaration.get('capture'), 'Figma capture path')
    path = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Figma capture path contains a symlink')
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('Figma capture file is unavailable inside config directory')
    if path.stat().st_size > _MAX_RESPONSE:
        raise ValueError('Figma capture exceeds 10 MiB limit')
    raw = path.read_bytes()
    try:
        capture = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid Figma capture JSON: ' + str(exc))
    if not isinstance(capture, dict) or capture.get('schemaVersion') != '1.0.0' or capture.get('kind') != 'figma-capture':
        raise ValueError('Capture must have schemaVersion 1.0.0 and kind figma-capture')
    expected_key = urlsplit(declaration['location']).path.split('/')[2]
    if capture.get('fileKey') != expected_key:
        raise ValueError('Figma capture fileKey does not match the declared source')
    assets = {key: [] for key in CATEGORIES}
    def native_rows(key, category, id_keys):
        rows = capture.get(key, [])
        if not isinstance(rows, list):
            raise ValueError('Figma capture ' + key + ' must be an array')
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError('Figma capture ' + key + ' records must be objects')
            identity = next((row.get(field) for field in id_keys
                             if isinstance(row.get(field), str) and row[field]), None)
            name = row.get('name')
            if identity is None or not isinstance(name, str) or not name:
                raise ValueError('Figma capture ' + key + ' record requires its native id and name')
            allowed = ('key', 'node_id', 'nodeId', 'id', 'name', 'description', 'component_set_id',
                       'componentSetId', 'containing_frame', 'containingFrame', 'containing_page',
                       'containingPage', 'style_type', 'styleType', 'file_key', 'fileKey',
                       'componentPropertyDefinitions', 'variantProperties', 'componentProperties',
                       'paints', 'textStyle', 'effects', 'grids')
            safe_data = {field: row[field] for field in allowed if field in row}
            assets[category].append(_asset(category, identity, name, declaration['id'], safe_data))

    native_rows('components', 'components', ('node_id', 'nodeId', 'id', 'key'))
    native_rows('componentSets', 'variants', ('node_id', 'nodeId', 'id', 'key'))
    native_rows('styles', 'styles', ('key', 'node_id', 'nodeId', 'id'))
    def capture_nodes(node):
        if not isinstance(node, dict):
            raise ValueError('Figma capture document nodes must be objects')
        category = {'COMPONENT': 'components', 'COMPONENT_SET': 'variants'}.get(node.get('type'))
        if category:
            identity = node.get('id')
            if not identity or not node.get('name'):
                raise ValueError('Figma capture component requires native id and name')
            data = {key: node[key] for key in (
                'type', 'componentPropertyDefinitions', 'variantProperties', 'componentProperties')
                if key in node}
            _safe_data(data)
            existing = next((row for row in assets[category] if row['id'] == identity), None)
            if existing:
                existing['data'].update(data)
            else:
                assets[category].append(_asset(category, identity, node['name'], declaration['id'], data))
        for child in node.get('children', []):
            capture_nodes(child)

    capture_nodes(capture.get('document', {}))
    variables = capture.get('variables')
    limitations = capture.get('limitations', [])
    if not isinstance(limitations, list):
        raise ValueError('Figma capture limitations must be an array')
    limitations = list(limitations)
    if any(not isinstance(value, str) for value in limitations):
        raise ValueError('Figma capture limitations must be strings')
    if variables is None:
        coverage_tokens = coverage_modes = 'unavailable'
        limitations.append('Variables unavailable in supplied Figma capture.')
    else:
        if not isinstance(variables, dict):
            raise ValueError('Figma capture variables must be an object')
        meta = variables.get('meta', variables)
        if not isinstance(meta, dict):
            raise ValueError('Figma capture variables metadata must be an object')
        collections = meta.get('variableCollections', {})
        variable_rows = meta.get('variables', {})
        collection_rows = list(collections.values()) if isinstance(collections, dict) else collections
        variable_rows = list(variable_rows.values()) if isinstance(variable_rows, dict) else variable_rows
        if not isinstance(collection_rows, list) or not isinstance(variable_rows, list):
            raise ValueError('Figma capture variable collections and variables must be arrays or objects')
        for collection in collection_rows:
            if isinstance(collection, dict):
                for mode in collection.get('modes', []):
                    if isinstance(mode, dict):
                        mode_id = mode.get('modeId') or mode.get('id')
                        if mode_id and mode.get('name'):
                            assets['modes'].append(_asset(
                                'modes', collection['id'] + '/' + mode_id, mode['name'], declaration['id'],
                                {'collectionId': collection['id'], 'modeId': mode_id}))
        for variable in variable_rows:
            if isinstance(variable, dict) and variable.get('id') and variable.get('name'):
                assets['tokens'].append(_asset('tokens', variable['id'], variable['name'], declaration['id'],
                                               {key: variable[key] for key in (
                                                   'key', 'variableCollectionId', 'resolvedType',
                                                   'valuesByMode', 'scopes') if key in variable}))
        coverage_tokens = 'available'
        coverage_modes = 'available'
    counts = capture.get('captureCounts', {})
    if not isinstance(counts, dict):
        raise ValueError('Figma capture captureCounts must be an object')
    categories = {'styles': counts.get('styles'), 'tokens': counts.get('variables')}
    partial_styles = False
    for category, count in categories.items():
        if isinstance(count, dict) and isinstance(count.get('total'), int) and isinstance(count.get('returned'), int):
            if count['returned'] < count['total']:
                if category == 'tokens':
                    coverage_tokens = 'partial'
                else:
                    partial_styles = True
                limitations.append('Figma capture contains a partial ' + category + ' inventory.')
    missing_nodes = capture.get('missingNodeIds', [])
    if missing_nodes:
        if not isinstance(missing_nodes, list):
            raise ValueError('Figma capture missingNodeIds must be an array')
        limitations.append('Some requested Figma nodes were unavailable in the capture.')
    unavailable = capture.get('unavailableProperties', [])
    if unavailable:
        limitations.append('Some Figma properties were unavailable in the capture.')
    revision = capture.get('version')
    limitations.extend([] if revision else ['Figma capture has no version; content hash is the available revision evidence.'])
    declared = {category for category in ('components', 'styles') if category in capture}
    if 'componentSets' in capture:
        declared.add('variants')
    if variables is not None:
        declared.update(('tokens', 'modes'))
    coverage = _coverage(assets, declared)
    if variables is None:
        coverage['tokens'] = coverage['modes'] = 'unavailable'
    elif coverage_tokens == 'partial':
        coverage['tokens'] = 'partial'
    if partial_styles:
        coverage['styles'] = 'partial'
    if capture.get('truncatedValues'):
        limitations.append('Figma capture omitted values exceeding its serialization budget.')
    if any('subtree' in value.lower() for value in limitations):
        coverage['components'] = coverage['variants'] = 'partial'
    if coverage_tokens == 'partial':
        coverage['modes'] = 'partial'
    if missing_nodes:
        coverage['components'] = 'partial'
    if unavailable:
        for category in CATEGORIES:
            if assets[category] and coverage[category] == 'available':
                coverage[category] = 'partial'
    return assets, _hash(raw), str(revision) if revision else 'unknown', limitations, coverage


def _figma(declaration, base):
    if declaration.get('capture') is not None:
        return _figma_capture(declaration, base)
    return _figma_source(declaration)

def _figma_source(declaration):
    from urllib.parse import urlencode
    file_key = urlsplit(declaration['location']).path.split('/')[2]
    token = os.environ.get('FIGMA_ACCESS_TOKEN')
    if not token:
        raise ValueError('FIGMA_ACCESS_TOKEN is required to read Figma sources')
    node_ids = declaration.get('nodeIds')
    if node_ids is not None and (
            not isinstance(node_ids, list) or not node_ids or
            any(not isinstance(item, str) or not item for item in node_ids)):
        raise ValueError('nodeIds must be a non-empty array of native node IDs')
    headers = {'X-Figma-Token': token, 'Accept': 'application/json'}

    def get(endpoint):
        request = Request('https://api.figma.com/v1/' + endpoint, headers=headers)
        try:
            with urlopen(request, timeout=_TIMEOUT) as response:
                raw = response.read(_MAX_RESPONSE + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ValueError('Figma API request failed: ' + exc.__class__.__name__)
        if len(raw) > _MAX_RESPONSE:
            raise ValueError('Figma API response exceeds 10 MiB limit')
        try:
            document = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError('Figma API returned invalid JSON')
        if not isinstance(document, dict) or document.get('error'):
            raise ValueError('Figma API returned an unsuccessful document')
        return document, raw

    endpoint = 'files/' + file_key
    if node_ids:
        endpoint += '?' + urlencode({'ids': ','.join(node_ids)})
    file_doc, file_raw = get(endpoint)
    assets = {key: [] for key in CATEGORIES}
    document = file_doc.get('document')
    if not isinstance(document, dict):
        raise ValueError('Figma API file response lacks a document')
    for native_name, category in (('components', 'components'), ('componentSets', 'variants'),
                                  ('styles', 'styles')):
        rows = file_doc.get(native_name, {})
        if not isinstance(rows, dict):
            raise ValueError('Figma API ' + native_name + ' must be a native metadata map')
        for identity, row in rows.items():
            if not isinstance(row, dict):
                raise ValueError('Figma API metadata records must be objects')
            safe = {key: row[key] for key in (
                'key', 'name', 'description', 'remote', 'componentSetId', 'styleType')
                if key in row}
            assets[category].append(_asset(category, identity, row.get('name'), declaration['id'], safe))

    def visit(node):
        if not isinstance(node, dict):
            raise ValueError('Figma document nodes must be objects')
        category = {'COMPONENT': 'components', 'COMPONENT_SET': 'variants'}.get(node.get('type'))
        if category:
            data = {key: node[key] for key in (
                'type', 'description', 'componentPropertyDefinitions',
                'variantProperties', 'componentProperties') if key in node}
            _safe_data(data)
            existing = next((row for row in assets[category] if row['id'] == node.get('id')), None)
            if existing:
                existing['data'].update(data)
            else:
                assets[category].append(_asset(
                    category, node.get('id'), node.get('name'), declaration['id'], data))
        for child in node.get('children', []):
            visit(child)

    visit(document)
    limitations = [
        'File metadata and observed document subtrees are not an exhaustive published library inventory.',
        'Styles are native metadata; resolved style definitions and live imports/renders were not verified.']
    if node_ids:
        limitations.append('Document capture is limited to requested nodes and API-provided ancestors/dependencies.')
    try:
        variables_doc, variables_raw = get('files/' + file_key + '/variables/local')
    except ValueError as exc:
        limitations.append('Variables unavailable: ' + str(exc))
        variables_raw = b''
        variables_doc = {}
    meta = variables_doc.get('meta', {})
    if not isinstance(meta, dict):
        raise ValueError('Figma variable metadata must be an object')
    for collection in meta.get('variableCollections', {}).values():
        for mode in collection.get('modes', []):
            assets['modes'].append(_asset(
                'modes', collection['id'] + '/' + mode['modeId'], mode.get('name'), declaration['id'],
                {'collectionId': collection['id'], 'modeId': mode['modeId']}))
    for variable in meta.get('variables', {}).values():
        assets['tokens'].append(_asset(
            'tokens', variable.get('id'), variable.get('name'), declaration['id'],
            {key: variable[key] for key in (
                'key', 'variableCollectionId', 'resolvedType', 'valuesByMode', 'scopes')
             if key in variable}))
    content_hash = hashlib.sha256(file_raw + b'\0' + variables_raw).hexdigest()
    revision = file_doc.get('version') or 'unknown'
    coverage = _coverage(assets)
    for category in ('components', 'variants', 'styles'):
        coverage[category] = 'partial'
    if not variables_raw:
        coverage['tokens'] = coverage['modes'] = 'unavailable'
    return assets, content_hash, str(revision), limitations, coverage


def _validate_declaration(declaration, index):
    if not isinstance(declaration, dict):
        raise ValueError('Source declaration ' + str(index) + ' must be an object')
    source_id = declaration.get('id')
    if not isinstance(source_id, str) or not _SLUG.fullmatch(source_id):
        raise ValueError('Source id must be a lowercase slug')
    provider = declaration.get('provider')
    if provider not in ('local', 'git', 'figma'):
        raise ValueError('Unsupported source provider for ' + source_id)
    location = declaration.get('location')
    if not isinstance(location, str) or not location:
        raise ValueError('Source location must be a non-empty string for ' + source_id)
    if provider == 'figma':
        parsed = urlsplit(location)
        parts = [part for part in parsed.path.split('/') if part]
        if (parsed.scheme != 'https' or parsed.hostname != 'www.figma.com' or
                parsed.username or parsed.password or parsed.port not in (None, 443) or
                any(_SECRET_KEY.fullmatch(key) for key, _ in parse_qsl(parsed.query)) or
                len(parts) < 3 or parts[0] not in ('design', 'file') or
                not re.fullmatch(r'[A-Za-z0-9_-]+', parts[1])):
            raise ValueError('Figma location must be a credential-free HTTPS design/file URL')
        if 'capture' in declaration:
            _safe_relative(declaration['capture'], 'Figma capture path')
    return source_id, provider


def scan_sources(config, base):
    """Scan declared sources in order; later source identities override earlier ones."""
    if not isinstance(config, dict) or not isinstance(config.get('sources'), list):
        raise ValueError('Source config must contain a sources array')
    if not config['sources']:
        raise ValueError('Source config must declare at least one source')
    snapshots = []
    merged = {key: [] for key in CATEGORIES}
    positions = {key: {} for key in CATEGORIES}
    overrides = []
    seen_source_ids = set()
    for index, declaration in enumerate(config['sources']):
        source_id, provider = _validate_declaration(declaration, index)
        if source_id in seen_source_ids:
            raise ValueError('Duplicate source id: ' + source_id)
        seen_source_ids.add(source_id)
        if provider == 'local':
            assets, content_hash, revision, limitations, coverage = _local_source(declaration, base)
        elif provider == 'git':
            assets, content_hash, revision, limitations, coverage = _git_source(declaration, base)
        else:
            assets, content_hash, revision, limitations, coverage = _figma(declaration, base)
        location = declaration['location']
        if provider == 'figma' and urlsplit(location).scheme:
            parsed = urlsplit(location)
            location = parsed.scheme + '://' + parsed.netloc + parsed.path
        snapshot = {'id': source_id, 'provider': provider, 'location': location,
                    'revision': revision, 'contentHash': content_hash,
                    'capturedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'coverage': coverage, 'limitations': limitations, 'assets': assets}
        if provider == 'git':
            snapshot['selection'] = {'subdir': declaration.get('subdir', '.')}
        elif provider == 'figma':
            snapshot['transport'] = 'plugin-capture' if declaration.get('capture') else 'rest'
            if declaration.get('nodeIds') is not None:
                node_ids = declaration['nodeIds']
                if (not isinstance(node_ids, list) or not node_ids or
                        any(not isinstance(value, str) or not value for value in node_ids)):
                    raise ValueError('nodeIds must be a non-empty array of native node IDs')
                snapshot['selection'] = {'nodeIds': sorted(set(node_ids))}
        snapshots.append(snapshot)
        for category in CATEGORIES:
            for asset in assets[category]:
                identity = asset['id']
                if identity in positions[category]:
                    old = merged[category][positions[category][identity]]
                    overrides.append({'category': category, 'id': identity,
                                      'fromSourceId': old['sourceId'], 'toSourceId': source_id})
                    merged[category][positions[category][identity]] = asset
                else:
                    positions[category][identity] = len(merged[category])
                    merged[category].append(asset)
    return {'schemaVersion': '1.0.0', 'kind': 'source-registry', 'sources': snapshots,
            'assets': merged, 'precedence': 'later-source-wins', 'overrides': overrides}


def validate_registry(registry):
    """Return integrity diagnostics, including ordered merge and provenance checks."""
    errors = []
    if not isinstance(registry, dict) or registry.get('schemaVersion') != '1.0.0' or registry.get('kind') != 'source-registry':
        return ['Registry must have schemaVersion 1.0.0 and kind source-registry']
    sources = registry.get('sources')
    assets = registry.get('assets')
    if not isinstance(sources, list) or not sources:
        errors.append('Registry sources must be a non-empty array')
        sources = []
    if not isinstance(assets, dict):
        return errors + ['Registry assets must be an object']
    source_ids = set()
    positions = {category: {} for category in CATEGORIES}
    expected_assets = {category: [] for category in CATEGORIES}
    expected_overrides = []
    allowed_coverage = {'available', 'empty', 'partial', 'unavailable', 'undeclared'}
    for source in sources:
        if not isinstance(source, dict):
            errors.append('Every source snapshot must be an object')
            continue
        source_id = source.get('id')
        if not isinstance(source_id, str) or not _SLUG.fullmatch(source_id):
            errors.append('Every source requires a valid slug id')
            continue
        if source_id in source_ids:
            errors.append('Duplicate source id: ' + source_id)
        source_ids.add(source_id)
        provider = source.get('provider')
        if provider not in ('local', 'git', 'figma'):
            errors.append('Unsupported provider for source ' + source_id)
        if not isinstance(source.get('location'), str) or not source['location']:
            errors.append('Invalid location for source ' + source_id)
        if not isinstance(source.get('revision'), str) or not source['revision']:
            errors.append('Invalid revision for source ' + source_id)
        if not isinstance(source.get('contentHash'), str) or not _SHA256.fullmatch(source['contentHash']):
            errors.append('Invalid contentHash for source ' + source_id)
        captured_at = source.get('capturedAt')
        if not isinstance(captured_at, str):
            errors.append('Invalid capturedAt for source ' + source_id)
        else:
            try:
                parsed_time = datetime.fromisoformat(captured_at.replace('Z', '+00:00'))
                if parsed_time.tzinfo is None or parsed_time.utcoffset() != timezone.utc.utcoffset(parsed_time):
                    errors.append('Invalid capturedAt for source ' + source_id)
            except ValueError:
                errors.append('Invalid capturedAt for source ' + source_id)
        if not isinstance(source.get('limitations'), list) or any(not isinstance(item, str) for item in source.get('limitations', [])):
            errors.append('Invalid limitations for source ' + source_id)
        coverage = source.get('coverage')
        if not isinstance(coverage, dict) or any(coverage.get(cat) not in allowed_coverage for cat in CATEGORIES):
            errors.append('Incomplete or invalid coverage for source ' + source_id)
            coverage = {}
        source_assets = source.get('assets')
        if not isinstance(source_assets, dict):
            errors.append('Invalid source assets for ' + source_id)
            continue
        for category in CATEGORIES:
            rows = source_assets.get(category)
            if not isinstance(rows, list):
                errors.append('Source assets.' + category + ' must be an array for ' + source_id)
                continue
            status = coverage.get(category)
            if status in ('empty', 'undeclared', 'unavailable') and rows:
                errors.append('Coverage conflicts with source assets for ' + category + ' in ' + source_id)
            if status == 'available' and not rows:
                errors.append('Available coverage has no source assets for ' + category + ' in ' + source_id)
            if status in ('partial', 'unavailable') and not source.get('limitations'):
                errors.append('Incomplete coverage lacks a limitation for ' + category + ' in ' + source_id)
            seen = set()
            for row in rows:
                if not isinstance(row, dict):
                    errors.append('Invalid source asset in ' + category + ' for ' + source_id)
                    continue
                identity = row.get('id')
                if not isinstance(identity, str) or not identity:
                    errors.append('Invalid source asset id in ' + category + ' for ' + source_id)
                    continue
                if identity in seen:
                    errors.append('Duplicate source asset id in ' + category + ': ' + identity)
                seen.add(identity)
                if row.get('sourceId') != source_id:
                    errors.append('Source asset ownership mismatch for ' + category + ' asset ' + identity)
                if not isinstance(row.get('name'), str) or not row['name'] or not isinstance(row.get('data'), dict):
                    errors.append('Invalid normalized source asset in ' + category + ': ' + identity)
                    continue
                try:
                    _safe_data(row['data'])
                except ValueError as exc:
                    errors.append(str(exc))
                if identity in positions[category]:
                    old = expected_assets[category][positions[category][identity]]
                    expected_overrides.append({'category': category, 'id': identity,
                                               'fromSourceId': old['sourceId'], 'toSourceId': source_id})
                    expected_assets[category][positions[category][identity]] = row
                else:
                    positions[category][identity] = len(expected_assets[category])
                    expected_assets[category].append(row)
    for category in CATEGORIES:
        rows = assets.get(category)
        if not isinstance(rows, list):
            errors.append('Registry assets.' + category + ' must be an array')
            continue
        ids = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row.get('id'):
                errors.append('Invalid asset id in ' + category)
                continue
            if row['id'] in ids:
                errors.append('Duplicate asset id in ' + category + ': ' + row['id'])
            ids.add(row['id'])
            if row.get('sourceId') not in source_ids:
                errors.append('Unknown sourceId for ' + category + ' asset ' + row['id'])
            if not isinstance(row.get('name'), str) or not row['name'] or not isinstance(row.get('data'), dict):
                errors.append('Invalid normalized asset in ' + category + ': ' + row['id'])
                continue
            try:
                _safe_data(row['data'])
            except ValueError as exc:
                errors.append(str(exc))
        if rows != expected_assets[category]:
            errors.append('Merged assets.' + category + ' do not match ordered source snapshots')
    if registry.get('precedence') != 'later-source-wins':
        errors.append('Invalid precedence')
    if registry.get('overrides') != expected_overrides:
        errors.append('Overrides do not match ordered source snapshots')
    return errors
