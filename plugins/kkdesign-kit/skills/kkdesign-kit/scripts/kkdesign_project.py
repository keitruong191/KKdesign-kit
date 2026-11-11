#!/usr/bin/env python3
"""Reviewable, recoverable project lifecycle for KKdesign-kit Stage-A."""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
import uuid
from urllib.parse import parse_qsl, unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from kkdesign_core import _validate_web_artifacts, build_lesson_index, load, local_path, validate_foundation

CATEGORIES = ('tokens', 'styles', 'components', 'variants', 'modes')
PLATFORMS = {'web', 'macos', 'ios', 'android', 'windows', 'adaptive'}
STATUS = {'confirmed', 'observed', 'inferred', 'open', 'superseded'}


def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _safe_rel(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or any(part in ('..', '.') for part in p.parts) or '\\' in value:
        raise ValueError('Unsafe project-relative path: ' + str(value))
    return p.as_posix()


def _no_symlink(path, boundary):
    boundary = Path(boundary).absolute()
    path = Path(path).absolute()
    try:
        rel = path.relative_to(boundary)
    except ValueError:
        raise ValueError('Path escapes project: ' + str(path))
    cursor = boundary
    if cursor.is_symlink():
        raise ValueError('Symlink boundary is not allowed: ' + str(cursor))
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink path is not allowed: ' + str(cursor))
    return path


def _source_scan(config_path):
    config_path = Path(config_path).absolute()
    if config_path.is_symlink():
        raise ValueError('Source configuration must not be a symlink')
    config = load(config_path)
    if not isinstance(config, dict) or not isinstance(config.get('sources'), list):
        raise ValueError('Source config must contain a sources array')
    from kkdesign_sources import scan_sources
    return scan_sources(config, config_path.parent)




def _credential_query(query):
    return any(re.search(r'(?:token|auth|secret|credential|password|api.?key)', key, re.I)
               for key, _ in parse_qsl(query, keep_blank_values=True))


def _validate_context_safety(value, key=''):
    if isinstance(value, dict):
        for child_key, child in value.items():
            if re.fullmatch(
                    r'(?:(?:figma[_-]?)?(?:access|refresh)[_-]?token|token|secret|client[_-]?secret|'
                    r'password|passwd|credentials?|authorization|api[_-]?key|private[_-]?key)',
                    str(child_key), re.I):
                raise ValueError('Context contains a forbidden credential field')
            _validate_context_safety(child, str(child_key))
    elif isinstance(value, list):
        for child in value:
            _validate_context_safety(child, key)
    elif isinstance(value, str):
        if value.startswith(('/', '\\\\')) or re.match(r'^[A-Za-z]:[\\\\/]', value):
            raise ValueError('Context must not contain machine-specific absolute paths')
        for match in re.findall(r'https?://[^\s]+', value):
            parsed = urlsplit(match)
            if parsed.username or parsed.password or _credential_query(parsed.query):
                raise ValueError('Context URLs must not contain credentials')


def _profile_location(project, location):
    parsed = urlsplit(str(location))
    if parsed.scheme:
        if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or _credential_query(parsed.query):
            raise ValueError('Profile source URLs must be credential-free HTTPS URLs')
        return parsed.scheme + '://' + parsed.netloc + parsed.path + (('?' + parsed.query) if parsed.query else '') + (('#' + parsed.fragment) if parsed.fragment else '')
    relative = _safe_rel(str(location))
    _no_symlink(Path(project) / relative, project)
    return relative



def _validate_context_schema(context):
    allowed = {'product', 'sources', 'requirements', 'visualReferences', 'runtimeConstraints', 'lessons'}
    if not isinstance(context, dict) or set(context) - allowed:
        raise ValueError('Context must use only the supported project context fields')
    product = context.get('product', {})
    if not isinstance(product, dict) or set(product) - {'name', 'platforms'}:
        raise ValueError('Context product supports only name and platforms')
    if 'name' in product and product['name'] is not None and not isinstance(product['name'], str):
        raise ValueError('Context product.name must be a string or null')
    platforms = product.get('platforms', [])
    if not isinstance(platforms, list) or any(p not in PLATFORMS for p in platforms) or len(platforms) != len(set(platforms)):
        raise ValueError('Context product.platforms must be a unique array of Stage-A platform names')
    sources = context.get('sources', [])
    if not isinstance(sources, list):
        raise ValueError('Context sources must be an array')
    for source in sources:
        if (not isinstance(source, dict) or set(source) - {'id', 'location', 'revision', 'observedAt'}
                or not isinstance(source.get('id'), str) or not source['id']
                or not isinstance(source.get('location'), str) or not source['location']):
            raise ValueError('Context sources require string id and location and support revision/observedAt')
    decision_fields = {'id', 'topic', 'value', 'location', 'sourceId', 'status', 'scope', 'platforms',
                       'sourceIds', 'recheckWhen', 'surface', 'surfaceId', 'task', 'taskId', 'revision', 'observedAt'}
    for key in ('requirements', 'visualReferences', 'runtimeConstraints', 'lessons'):
        values = context.get(key, [])
        if not isinstance(values, list):
            raise ValueError('Context ' + key + ' must be an array')
        for item in values:
            if not isinstance(item, dict) or set(item) - decision_fields or not isinstance(item.get('id'), str) or not item['id']:
                raise ValueError('Context ' + key + ' entries require an id and supported decision fields')
            if item.get('status', 'open') not in STATUS:
                raise ValueError('Context decision status must be confirmed, observed, inferred, open, or superseded')
            applies_to = item.get('platforms')
            if applies_to is not None and (not isinstance(applies_to, list) or any(p not in PLATFORMS for p in applies_to)):
                raise ValueError('Context decision platforms must use Stage-A platform names')
            if key == 'visualReferences' and (not isinstance(item.get('location'), str) or not item['location']):
                raise ValueError('Context visualReferences require a location')
            if item.get('sourceId') is not None and not isinstance(item['sourceId'], str):
                raise ValueError('Context sourceId must be a string')
            source_ids = item.get('sourceIds', [])
            if not isinstance(source_ids, list) or any(not isinstance(x, str) for x in source_ids):
                raise ValueError('Context decision sourceIds must be an array of source IDs')

def _context_decisions(context, platform):
    if context is None:
        return []
    if not isinstance(context, dict):
        raise ValueError('Context JSON must be an object')
    decisions = []
    names = ('requirements', 'visualReferences', 'runtimeConstraints', 'lessons')
    for key in names:
        values = context.get(key, [])
        if not isinstance(values, list):
            raise ValueError('Context ' + key + ' must be an array')
        for pos, item in enumerate(values):
            if not isinstance(item, dict):
                raise ValueError('Context ' + key + ' entries must be objects')
            status = item.get('status', 'open')
            if status not in STATUS:
                raise ValueError('Unsupported context decision status: ' + str(status))
            platforms = item.get('platforms')
            if platforms is not None and (not isinstance(platforms, list) or any(p not in PLATFORMS for p in platforms)):
                raise ValueError(key + ' platforms must use Stage-A platform names')
            if platforms is not None and platform not in platforms:
                continue
            applicable = (context.get('product') or {}).get('platforms', []) if isinstance(context.get('product'), dict) else []
            if platforms is None and len(applicable) > 1:
                status = 'open'
            raw_topic = str(item.get('topic') or item['id'])
            topic = {'requirements': 'Requirement — ', 'visualReferences': 'Visual reference — ',
                     'runtimeConstraints': 'Runtime constraint — ', 'lessons': 'Scoped lesson — '}[key] + raw_topic
            modes = {'operate', 'read', 'persuade', 'experience'}
            is_mode = raw_topic.lower() in modes or (
                raw_topic.lower() in {'mode', 'surface-mode', 'surface mode', 'task-mode', 'task mode'}
                and isinstance(item.get('value'), str) and item['value'].lower() in modes)
            if is_mode:
                locator = item.get('surface') or item.get('surfaceId') or item.get('task') or item.get('taskId')
                if not locator:
                    raise ValueError('Surface/task modes require an explicit surface or task locator')
                scope = 'Surface/task ' + str(locator) + ': ' + str(item.get('scope') or 'scoped mode')
            else:
                scope = str(item.get('scope') or ('Platform: ' + platform if platforms else 'Open platform scope; confirm applicability.'))
            sid = re.sub(r'[^a-z0-9]+', '-', str(item.get('id') or topic.lower())).strip('-') or key + '-' + str(pos + 1)
            source_ids = list(item.get('sourceIds', []))
            value = item.get('value')
            if key == 'visualReferences':
                location = item.get('location')
                if not location:
                    raise ValueError('Visual references require a credential-free location')
                source_id = str(item.get('sourceId') or ('visual-' + sid))
                source_ids = source_ids or [source_id]
                value = {'location': str(location), 'designation': 'visual reference; not a product requirement'}
            decisions.append({'id': sid, 'topic': topic, 'value': value, 'status': status,
                              'scope': scope, 'sourceIds': source_ids,
                              'recheckWhen': str(item.get('recheckWhen') or 'When requirements, implementation, or target platform changes.')})
    return decisions


def _profile(context, product, platform, registry=None):
    if context is not None:
        _validate_context_schema(context)
    product_info = (context or {}).get('product', {})
    profile_id = 'product-' + platform
    project = Path(product).parent
    product_source = {'id': 'product-context', 'location': 'PRODUCT.md', 'revision': None,
                      'observedAt': dt.date.today().isoformat(),
                      'note': 'Existing context reference; raw text is not owner approval.'}
    product_path = project / 'PRODUCT.md'
    if product_path.is_file():
        _no_symlink(product_path, project)
        product_source['sha256'] = _hash(product_path.read_bytes())
    sources = [product_source]
    for source in (context or {}).get('sources', []):
        location = _profile_location(project, source['location'])
        entry = {'id': source['id'], 'location': location, 'revision': source.get('revision'),
                 'observedAt': str(source.get('observedAt') or dt.date.today().isoformat())}
        target = project / location if not urlsplit(location).scheme else None
        if target and target.is_file():
            entry['sha256'] = _hash(target.read_bytes())
        sources.append(entry)
    for item in (context or {}).get('visualReferences', []):
        sid = re.sub(r'[^a-z0-9]+', '-', str(item['id'])).strip('-') or 'visual-reference'
        source_id = str(item.get('sourceId') or ('visual-' + sid))
        if source_id not in {source['id'] for source in sources}:
            sources.append({'id': source_id, 'location': _profile_location(project, item['location']),
                            'revision': item.get('revision'), 'observedAt': str(item.get('observedAt') or dt.date.today().isoformat()),
                            'note': 'Designated visual reference; not product requirement evidence.'})
    decisions = _context_decisions(context, platform)
    if not decisions:
        decisions.append({'id': 'product-purpose', 'topic': 'Product requirements', 'value': None,
                          'status': 'open', 'scope': 'No confirmed product or platform rules supplied.',
                          'sourceIds': ['product-context'], 'recheckWhen': 'When an owner confirms product requirements and applicability.'})
    if registry is not None:
        sources.append({'id': 'design-system', 'location': 'design/sources.json', 'revision': None,
                        'observedAt': dt.date.today().isoformat(),
                        'note': 'Design-system identity and assets are not product capability evidence.'})
        decisions.append({'id': 'design-system-identity', 'topic': 'Design-system identity',
                          'value': [{'id': item['id'], 'provider': item['provider'], 'location': item['location'],
                                     'revision': item['revision'], 'selection': item.get('selection')} for item in registry.get('sources', [])],
                          'status': 'observed', 'scope': 'Design-system source identity for platform ' + platform,
                          'sourceIds': ['design-system'], 'recheckWhen': 'When the source registry or selected design system changes.'})
    source_ids = [source['id'] for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError('Context source IDs must be unique within a product profile')
    decision_ids = [decision['id'] for decision in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError('Context decision IDs must be unique within a product profile')
    available_sources = set(source_ids)
    for decision in decisions:
        unknown = set(decision['sourceIds']) - available_sources
        if unknown:
            raise ValueError('Decision ' + decision['id'] + ' references undeclared source IDs: ' + ', '.join(sorted(unknown)))
    return {'$schema': '../schemas/product-profile.schema.json', 'schemaVersion': '1.0.0',
            'kind': 'product-profile', 'id': profile_id,
            'product': str(product_info.get('name') or 'Unspecified product'),
            'platform': platform, 'status': 'draft', 'scope': 'Scoped draft; DS source data does not establish product behavior.',
            'sources': sources, 'decisions': decisions}



def _build_files(project, registry, context, platforms):
    files = {}
    product = project / 'PRODUCT.md'
    if not product.exists():
        files['PRODUCT.md'] = ('# Product context\n\nAdd approved product purpose, users, requirements, platform scope, and implementation/runtime constraints. Source observations are not approval.\n').encode()
    for name in ('task.schema.json', 'task-evidence.schema.json', 'lesson-index.schema.json', 'product-profile.schema.json', 'source-registry.schema.json'):
        schema_path = ROOT / 'schemas' / name
        if schema_path.is_file():
            files['design/schemas/' + name] = schema_path.read_bytes()
    if not (project / 'DESIGN.md').exists():
        files['DESIGN.md'] = ('# Project design guide\n\nRead [product context](PRODUCT.md), the [source registry](design/sources.json), '
            '[lessons](design/LESSON.md), and the scoped profile for the task platform before designing. Copy [task template](design/task-template.json).\n\n'
            'Source capabilities and limitations are recorded in the registry. Source data does not establish product requirements. Keep decisions scoped; confirm open decisions before relying on them. Offline foundation validation is not live import, render, or runtime verification.\n').encode()
    files['design/task-template.json'] = (ROOT / 'templates/task.json').read_bytes()
    lesson = ('# Design lessons\n\n<a id="DL-001"></a>\n### DL-001 · Confirm scope before applying a lesson\n\n'
              '<!-- kkdesign-lesson {\"id\":\"DL-001\",\"status\":\"active\",\"platforms\":[\"any\"],\"tags\":[\"scope\"],\"appliesWhen\":\"Before applying guidance to a design task.\",\"evidence\":[\"../PRODUCT.md\"],\"originTask\":null} -->\n\n'
              'Treat lessons as scoped guidance, not universal product requirements. Confirm the target platform, surface, and task applicability.\n\n'
              '**Verification:** Record the selected lesson and task-specific evidence; leave unsupported applicability open.\n').encode()
    if not (project / 'design/LESSON.md').exists():
        files['design/LESSON.md'] = lesson
    files['design/sources.json'] = _json_bytes(registry)
    current_lessons = project / 'design/LESSON.md'
    if current_lessons.exists():
        try:
            index = build_lesson_index(current_lessons.parent)
        except Exception as exc:
            raise ValueError('Cannot regenerate lesson index from existing history: ' + str(exc))
    else:
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory) / 'design'; d.mkdir(); (d / 'LESSON.md').write_bytes(lesson)
            index = build_lesson_index(d)
    files['design/lessons-index.json'] = _json_bytes({'$schema': 'schemas/lesson-index.schema.json', **index})
    for platform in platforms:
        profile_path = project / 'design/profiles' / (platform + '.json')
        if not profile_path.exists():
            files['design/profiles/' + platform + '.json'] = _json_bytes(_profile(context, project / 'PRODUCT.md', platform, registry))
    return files


def _read_old_registry(project):
    path = project / 'design/sources.json'
    if path.is_symlink():
        raise ValueError('Existing source registry must not be a symlink')
    return load(path) if path.is_file() else None


def _design_contract_paths(design):
    for directory, directories, files in os.walk(design):
        if Path(directory) == design:
            directories[:] = [name for name in directories if name != 'prototypes']
        for name in directories + files:
            yield Path(directory) / name


def _asset_diff(old, new, project):
    delta = {}
    old_assets, new_assets = old.get('assets', {}), new.get('assets', {})
    refs = []
    searchable = []
    design = Path(project) / 'design'
    if design.exists():
        for path in _design_contract_paths(design):
            if path.is_file():
                _no_symlink(path, project)
                if path.name != 'sources.json':
                    try:
                        searchable.append((path.relative_to(project).as_posix(), path.read_text(encoding='utf-8')))
                    except UnicodeDecodeError:
                        continue
    for category in CATEGORIES:
        a = {x['id']: x for x in old_assets.get(category, [])}
        b = {x['id']: x for x in new_assets.get(category, [])}
        added = sorted(set(b) - set(a)); removed = sorted(set(a) - set(b))
        changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
        delta[category] = {'added': added, 'removed': removed, 'changed': changed}
        for identifier in removed + changed:
            files = [name for name, text in searchable if identifier in text]
            refs.append({'category': category, 'id': identifier, 'files': files,
                         'reason': 'removed or changed source asset; review listed references'})
    return delta, refs


def _preserved_inventory(project):
    project = Path(project).absolute()
    preserved = []
    for rel in ('PRODUCT.md', 'DESIGN.md', 'design/LESSON.md'):
        path = project / rel
        if path.is_file():
            _no_symlink(path, project)
            preserved.append({'path': rel, 'sha256': _hash(path.read_bytes())})
    for relative in ('design/profiles', 'design/tasks'):
        root = project / relative
        if not root.exists():
            continue
        _no_symlink(root, project)
        for path in sorted(root.rglob('*')):
            _no_symlink(path, project)
            if path.is_file():
                preserved.append({'path': path.relative_to(project).as_posix(),
                                  'sha256': _hash(path.read_bytes())})
    return preserved


def _stable_snapshot(registry, previous):
    """Retain capture metadata for unchanged source content; capturedAt is not identity."""
    prior = {item.get('id'): item for item in (previous or {}).get('sources', [])}
    result = copy.deepcopy(registry)
    for item in result.get('sources', []):
        old = prior.get(item.get('id'))
        if old and old.get('contentHash') == item.get('contentHash') and old.get('location') == item.get('location'):
            item['capturedAt'] = old.get('capturedAt', item.get('capturedAt'))
    return result


def _comparable_snapshot(item):
    return {key: value for key, value in item.items() if key != 'capturedAt'}



def _migration_required(before, after):
    return before is not None and (
        after is None or before.get('location') != after.get('location')
        or before.get('provider') != after.get('provider')
        or before.get('selection') != after.get('selection'))

def _plan(project, config_path, context_path=None, migration=None, refresh=False):
    project = Path(project).absolute()
    project.mkdir(parents=True, exist_ok=True)
    _no_symlink(project, project.parent)
    for relative in ('PRODUCT.md', 'DESIGN.md', 'design', '.kkdesign-kit'):
        _no_symlink(project / relative, project)
    control = project / '.kkdesign-kit/project'
    _no_symlink(control, project)
    registry = _source_scan(config_path)
    old_registry = _read_old_registry(project)
    registry = _stable_snapshot(registry, old_registry)
    source_changes = []
    if old_registry:
        old_by_id = {s['id']: s for s in old_registry.get('sources', [])}
        new_by_id = {s['id']: s for s in registry.get('sources', [])}
        for sid in sorted(set(old_by_id) | set(new_by_id)):
            before, after = old_by_id.get(sid), new_by_id.get(sid)
            if before is None or after is None or _comparable_snapshot(before) != _comparable_snapshot(after):
                source_changes.append({'id': sid, 'before': before, 'after': after})
                if _migration_required(before, after) and not migration:
                    raise ValueError('Source relocation, replacement, or removal requires --migration REASON for ' + sid)
    elif refresh:
        raise ValueError('Cannot refresh: no existing source registry; initialize first')
    if migration and not str(migration).strip():
        raise ValueError('Migration reason must not be empty')
    if migration:
        _validate_context_safety({'migrationReason': migration})
    context = load(context_path) if context_path else None
    if context is not None:
        _validate_context_schema(context)
        _validate_context_safety(context)
    product_obj = (context or {}).get('product', {})
    platforms = product_obj.get('platforms', []) if isinstance(product_obj, dict) else []
    platforms = platforms or ['adaptive']
    if not isinstance(platforms, list) or any(p not in PLATFORMS for p in platforms):
        raise ValueError('Context product.platforms must contain valid Stage-A platforms')
    files = _build_files(project, registry, context, platforms)
    old_assets = old_registry or {'assets': {k: [] for k in CATEGORIES}}
    asset_changes, affected = _asset_diff(old_assets, registry, project)
    plan_id = uuid.uuid4().hex
    states = {}
    changes = []
    managed_path = control / 'managed.json'
    if managed_path.exists():
        _no_symlink(managed_path, project)
        managed = load(managed_path)
    else:
        managed = {}
    for rel, data in sorted(files.items()):
        rel = _safe_rel(rel)
        path = _no_symlink(project / rel, project)
        before = path.read_bytes() if path.is_file() else None
        precondition = _hash(before) if before is not None else None
        if rel in {'PRODUCT.md', 'DESIGN.md', 'design/LESSON.md'} and before is not None:
            state = 'preserve'
        elif before == data:
            state = 'unchanged'
        elif before is None:
            state = 'add'
        else:
            state = 'update' if managed.get(rel) == precondition else 'conflict'
        states[rel] = {'beforeHash': precondition, 'afterHash': _hash(data), 'content': data.decode('utf-8'), 'state': state}
        changes.append({'path': rel, 'action': state, 'beforeHash': precondition, 'afterHash': _hash(data),
                        'diff': _unified(rel, before or b'', data) if state not in ('preserve', 'unchanged') else ''})
    preserved = _preserved_inventory(project)
    candidate_errors = _validate_candidate(project, states)
    plan = {'schemaVersion': '1.0.0', 'kind': 'project-plan', 'id': plan_id,
            'createdAt': utcnow(), 'project': '.', 'operation': 'refresh' if refresh else 'init',
            'status': 'review-required', 'migration': {'reason': migration, 'sources': source_changes} if migration else None,
            'sourceChanges': source_changes, 'assetChanges': asset_changes, 'affectedReferences': affected,
            'changes': changes, 'conflicts': [x for x in changes if x['action'] == 'conflict'],
            'preserved': preserved, 'candidateErrors': candidate_errors, 'files': states,
            'contextSchema': 'Context JSON schema 1.0.0; see project lifecycle contract.'}
    _no_symlink(control, project)
    control.mkdir(parents=True, exist_ok=True)
    plans_dir = control / 'plans'
    _no_symlink(plans_dir, project)
    plans_dir.mkdir(exist_ok=True)
    plan_path = plans_dir / (plan_id + '.json')
    _no_symlink(plan_path, project)
    _durable_json(plan_path, plan)
    return {'id': plan_id, 'status': plan['status'], 'operation': plan['operation'], 'changes': changes,
            'sourceChanges': source_changes, 'assetChanges': asset_changes, 'affectedReferences': affected,
            'conflicts': plan['conflicts'], 'preserved': preserved, 'candidateErrors': candidate_errors,
            'planPath': '.kkdesign-kit/project/plans/' + plan_id + '.json'}


def _unified(name, before, after):
    import difflib
    try:
        old = before.decode('utf-8').splitlines(True); new = after.decode('utf-8').splitlines(True)
    except UnicodeDecodeError:
        return 'Binary content changed (' + str(len(before)) + ' -> ' + str(len(after)) + ' bytes)'
    return ''.join(difflib.unified_diff(old, new, fromfile='a/' + name, tofile='b/' + name))

def _validate_candidate(project, files):
    project = Path(project).resolve()
    with tempfile.TemporaryDirectory(prefix='kkdesign-candidate-') as directory:
        candidate = (Path(directory) / 'project').resolve()
        candidate.mkdir()
        design = project / 'design'
        if design.exists():
            _no_symlink(design, project)
            for path in _design_contract_paths(design):
                _no_symlink(path, project)
            shutil.copytree(design, candidate / 'design',
                            ignore=lambda directory, names: ['prototypes'] if Path(directory) == design else [])
        for name in ('PRODUCT.md', 'DESIGN.md'):
            source = project / name
            if source.exists():
                _no_symlink(source, project)
                shutil.copy2(source, candidate / name)
        for rel, record in files.items():
            target = candidate / _safe_rel(rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(record['content'].encode('utf-8'))
        references = []
        artifact_errors = []
        for path in (candidate / 'design/profiles').glob('*.json'):
            try:
                profile = load(path)
                references.extend((Path('.'), source['location']) for source in profile.get('sources', []))
            except (ValueError, KeyError, TypeError, AttributeError):
                pass  # The foundation validator reports malformed records.
        try:
            index = load(candidate / 'design/lessons-index.json')
            references.extend((Path('design'), ref) for lesson in index.get('lessons', [])
                              for ref in lesson.get('evidence', []))
        except (ValueError, OSError, TypeError, AttributeError):
            pass
        for path in (candidate / 'design/tasks').rglob('*.json'):
            try:
                document = load(path)
                if document.get('delivery') in ('html_prototype', 'react_prototype'):
                    delivered = document.get('status') in ('design_delivered', 'design_verified_review_pending')
                    artifact_errors.extend(str(path.relative_to(candidate)) + ': ' + issue for issue in
                                           _validate_web_artifacts(project, document, require_delivery=delivered))
                    for artifact in document.get('handoff', {}).get('artifacts', []):
                        references.extend((Path('.'), artifact.get(field)) for field in ('entry', 'instructions'))
                        references.append((Path('.'), artifact.get('launch', {}).get('cwd')))
                refs = document.get('record', {}).get('references', [])
                refs += [ref for entry in document.get('lessonReview', {}).get('entries', [])
                         for ref in entry.get('evidence', [])]
                references.extend((path.parent.relative_to(candidate), ref) for ref in refs)
            except (ValueError, TypeError, AttributeError):
                pass
        for relative in ('DESIGN.md', 'design/LESSON.md'):
            path = candidate / relative
            if path.is_file():
                references.extend((path.parent.relative_to(candidate), ref)
                                  for ref in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')))
        for base, reference in references:
            if not isinstance(reference, str):
                continue
            parsed = urlsplit(reference)
            if parsed.scheme or not parsed.path:
                continue
            destination = (candidate / base / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(candidate) or destination.exists():
                continue
            try:
                source = local_path(project / base, reference, project)
            except (ValueError, OSError):
                continue
            if source is None:
                continue
            _no_symlink(project / base / unquote(parsed.path), project)
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            elif source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
        result = validate_project(candidate)
        return [error.replace(str(candidate), '<PROJECT>').replace(str(project), '<PROJECT>')
                for error in artifact_errors + result['errors']]


def _validate_plan_integrity(project, plan, plan_id):
    project = Path(project).absolute()
    if plan.get('schemaVersion') != '1.0.0' or plan.get('kind') != 'project-plan' or plan.get('id') != plan_id:
        raise ValueError('Malformed or mismatched project plan')
    if plan.get('operation') not in ('init', 'refresh') or not isinstance(plan.get('files'), dict):
        raise ValueError('Malformed project plan file map')
    allowed_exact = {'PRODUCT.md', 'DESIGN.md', 'design/sources.json', 'design/LESSON.md',
                     'design/lessons-index.json', 'design/task-template.json'}
    allowed_schemas = {'design/schemas/' + name for name in
                       ('task.schema.json', 'task-evidence.schema.json', 'lesson-index.schema.json',
                        'product-profile.schema.json', 'source-registry.schema.json')}
    managed_path = project / '.kkdesign-kit/project/managed.json'
    _no_symlink(managed_path, project)
    managed = load(managed_path) if managed_path.is_file() else {}
    normalized, changes = {}, []
    if plan.get('preserved') != _preserved_inventory(project):
        raise ValueError('Preserved product/profile/lesson/task inputs changed after plan review')
    for rel, record in plan['files'].items():
        rel = _safe_rel(rel)
        profile = re.fullmatch(r'design/profiles/(web|macos|ios|android|windows|adaptive)\.json', rel)
        if rel not in allowed_exact and rel not in allowed_schemas and not profile:
            raise ValueError('Plan contains a path outside lifecycle ownership: ' + rel)
        if not isinstance(record, dict) or not isinstance(record.get('content'), str):
            raise ValueError('Malformed plan file record: ' + rel)
        content = record['content'].encode('utf-8')
        after_hash = _hash(content)
        if record.get('afterHash') != after_hash:
            raise ValueError('Plan content hash mismatch: ' + rel)
        before_hash = record.get('beforeHash')
        if before_hash is not None and not re.fullmatch(r'[0-9a-f]{64}', str(before_hash)):
            raise ValueError('Invalid beforeHash in plan: ' + rel)
        path = _no_symlink(project / rel, project)
        current = path.read_bytes() if path.is_file() else None
        current_hash = _hash(current) if current is not None else None
        if current_hash != before_hash:
            raise ValueError('Stale plan precondition failed for ' + rel)
        action = record.get('state')
        if action not in ('add', 'update', 'unchanged', 'conflict'):
            raise ValueError('Invalid planned action for ' + rel)
        if (action == 'add' and before_hash is not None) or (action == 'unchanged' and before_hash != after_hash):
            raise ValueError('Inconsistent plan action/precondition for ' + rel)
        if action == 'update' and (before_hash is None or before_hash == after_hash or managed.get(rel) != before_hash):
            raise ValueError('Plan update is not authorized by managed-file history: ' + rel)
        if action == 'conflict' and (before_hash is None or before_hash == after_hash or managed.get(rel) == before_hash):
            raise ValueError('Inconsistent conflict state in plan: ' + rel)
        if rel.endswith('.json'):
            try:
                document = json.loads(content.decode('utf-8'))
                _validate_context_safety(document)
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError('Planned JSON is malformed: ' + rel)
        normalized[rel] = record
        changes.append({'path': rel, 'action': action, 'beforeHash': before_hash, 'afterHash': after_hash,
                        'diff': _unified(rel, current or b'', content) if action not in ('unchanged',) else ''})
    if 'design/sources.json' not in normalized:
        raise ValueError('Plan does not include its source registry')
    announced = {item.get('path'): item for item in plan.get('changes', []) if isinstance(item, dict)}
    if set(announced) != set(normalized):
        raise ValueError('Plan change summary does not match its file map')
    for item in changes:
        summary = announced[item['path']]
        if any(summary.get(key) != item[key] for key in ('action', 'beforeHash', 'afterHash', 'diff')):
            raise ValueError('Plan change summary mismatch: ' + item['path'])
    expected_conflicts = [item for item in changes if item['action'] == 'conflict']
    if plan.get('conflicts') != expected_conflicts:
        raise ValueError('Plan conflicts do not match its file map')
    try:
        registry = json.loads(normalized['design/sources.json']['content'])
        from kkdesign_sources import validate_registry
        registry_errors = validate_registry(registry)
        schema_path = ROOT / 'schemas/source-registry.schema.json'
        if schema_path.is_file():
            from kkdesign_core import schema_errors
            registry_errors.extend(schema_errors(registry, schema_path))
        if registry_errors:
            raise ValueError('Invalid planned registry: ' + '; '.join(registry_errors))
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Malformed planned registry: ' + str(exc))
    current_registry = _read_old_registry(project)
    expected_source_changes = []
    if current_registry:
        old_sources = {item['id']: item for item in current_registry.get('sources', [])}
        new_sources = {item['id']: item for item in registry.get('sources', [])}
        for sid in sorted(set(old_sources) | set(new_sources)):
            before, after = old_sources.get(sid), new_sources.get(sid)
            if before is None or after is None or _comparable_snapshot(before) != _comparable_snapshot(after):
                expected_source_changes.append({'id': sid, 'before': before, 'after': after})
                if _migration_required(before, after):
                    migration = plan.get('migration') or {}
                    if not str(migration.get('reason') or '').strip():
                        raise ValueError('Plan omits required source migration reason')
    if plan.get('sourceChanges') != expected_source_changes:
        raise ValueError('Plan source changes do not match its registry')
    old = current_registry or {'assets': {category: [] for category in CATEGORIES}}
    asset_changes, refs = _asset_diff(old, registry, project)
    if plan.get('assetChanges') != asset_changes or plan.get('affectedReferences') != refs:
        raise ValueError('Plan asset deltas/references do not match its registry')
    candidate_errors = _validate_candidate(project, normalized)
    if candidate_errors:
        raise ValueError('Candidate foundation validation failed: ' + '; '.join(candidate_errors))
    return normalized

def inspect_plan(project, plan_id):
    plan = load(_plan_path(project, plan_id))
    return plan


def _plan_path(project, plan_id):
    if not re.fullmatch(r'[a-f0-9]{32}', str(plan_id)):
        raise ValueError('Invalid plan ID')
    path = Path(project).absolute() / '.kkdesign-kit/project/plans' / (plan_id + '.json')
    _no_symlink(path, Path(project).absolute())
    if not path.is_file():
        raise ValueError('Unknown plan ID: ' + str(plan_id))
    return path


def _durable_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    with temp.open('xb') as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    if os.name != 'nt':
        fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _owner_alive(pid):
    if pid <= 0:
        raise ValueError('Lifecycle lock has an invalid process owner')
    if os.name != 'nt':
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True
    # os.kill(pid, 0) terminates processes on Windows; query a handle instead.
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:
            return False
        raise OSError('Lifecycle lock owner cannot be queried')
    try:
        status = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(status)):
            raise OSError('Lifecycle lock owner status is unavailable')
        return status.value == 259
    finally:
        kernel.CloseHandle(handle)


def _acquire_lock(project):
    project = Path(project).absolute()
    parent = project / '.kkdesign-kit/project'
    _no_symlink(parent, project)
    parent.mkdir(parents=True, exist_ok=True)
    lock = parent / 'lock'
    _no_symlink(lock, project)
    try:
        with lock.open('xb') as stream:
            stream.write((str(os.getpid()) + '\n').encode('ascii'))
            stream.flush()
            os.fsync(stream.fileno())
        return lock
    except FileExistsError:
        try:
            owner = int(lock.read_text(encoding='ascii').strip())
            alive = _owner_alive(owner)
        except (ValueError, OSError):
            raise ValueError('Lifecycle lock exists; owner cannot be verified safely')
        if not alive:
            lock.unlink()
            return _acquire_lock(project)
        raise ValueError('Another lifecycle update is in progress')


def _release_lock(lock):
    try:
        if int(Path(lock).read_text(encoding='ascii').strip()) == os.getpid():
            Path(lock).unlink()
    except (OSError, ValueError):
        pass


def _validate_journal_entries(project, entries):
    if not isinstance(entries, list):
        raise ValueError('Malformed recovery journal entries')
    allowed_exact = {'PRODUCT.md', 'DESIGN.md', 'design/sources.json', 'design/LESSON.md',
                     'design/lessons-index.json', 'design/task-template.json',
                     '.kkdesign-kit/project/managed.json'}
    allowed_schemas = {'design/schemas/' + name for name in
                       ('task.schema.json', 'task-evidence.schema.json', 'lesson-index.schema.json',
                        'product-profile.schema.json', 'source-registry.schema.json')}
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
            raise ValueError('Malformed recovery journal file entry')
        rel = _safe_rel(entry['path'])
        profile = re.fullmatch(r'design/profiles/(web|macos|ios|android|windows|adaptive)\.json', rel)
        if rel not in allowed_exact and rel not in allowed_schemas and not profile:
            raise ValueError('Recovery journal path is outside lifecycle ownership')
        if rel in seen:
            raise ValueError('Duplicate recovery journal path')
        seen.add(rel)
        before_hash, after_hash, backup = entry.get('beforeHash'), entry.get('afterHash'), entry.get('backup')
        if before_hash is not None and not re.fullmatch(r'[0-9a-f]{64}', str(before_hash)):
            raise ValueError('Invalid recovery beforeHash')
        if after_hash is not None and not re.fullmatch(r'[0-9a-f]{64}', str(after_hash)):
            raise ValueError('Invalid recovery afterHash')
        if ((backup is None) != (before_hash is None) or
                (backup is not None and (not isinstance(backup, str) or
                 _hash(backup.encode('utf-8')) != before_hash))):
            raise ValueError('Recovery backup does not match its precondition hash')
        path = _no_symlink(Path(project) / rel, project)
        current = path.read_bytes() if path.is_file() else None
        current_hash = _hash(current) if current is not None else None
        if current_hash not in (before_hash, after_hash):
            raise ValueError('Recovery conflict: current file matches neither journal state: ' + rel)
def apply_plan(project, plan_id):
    project = Path(project).absolute()
    lock = _acquire_lock(project)
    try:
        plan_path = _plan_path(project, plan_id)
        plan = load(plan_path)
        if plan.get('status') != 'review-required':
            raise ValueError('Plan is not applicable: ' + str(plan.get('status')))
        if plan.get('conflicts'):
            raise ValueError('Unresolved plan conflicts: ' + ', '.join(item['path'] for item in plan['conflicts']))
        if plan.get('candidateErrors'):
            raise ValueError('Candidate foundation validation failed: ' + '; '.join(plan['candidateErrors']))
        recovery_root = project / '.kkdesign-kit/project/recovery'
        _no_symlink(recovery_root, project)
        if recovery_root.exists():
            for journal_path in recovery_root.glob('*.json'):
                if journal_path.is_symlink():
                    raise ValueError('Recovery journal path must not be a symlink')
                if load(journal_path).get('status') in ('applying', 'rollback-applying'):
                    raise ValueError('An interrupted update must be recovered before applying another plan')
        files = _validate_plan_integrity(project, plan, plan_id)
        for rel, record in files.items():
            path = _no_symlink(project / _safe_rel(rel), project)
            current = path.read_bytes() if path.is_file() else None
            if (_hash(current) if current is not None else None) != record['beforeHash']:
                raise ValueError('Stale plan precondition failed for ' + rel)
            if record['state'] == 'conflict':
                continue
        journal_dir = project / '.kkdesign-kit/project/recovery'
        journal_dir.mkdir(parents=True, exist_ok=True)
        journal = {'schemaVersion': '1.0.0', 'planId': plan_id, 'status': 'applying', 'entries': []}
        journal_path = journal_dir / (plan_id + '.json')
        for rel, record in files.items():
            if record['state'] in ('unchanged', 'conflict'):
                continue
            path = _no_symlink(project / _safe_rel(rel), project)
            old = path.read_bytes() if path.is_file() else None
            entry = {'path': rel, 'beforeHash': _hash(old) if old is not None else None,
                     'afterHash': record['afterHash'], 'backup': old.decode('utf-8') if old is not None else None,
                     'written': False}
            journal['entries'].append(entry)
            journal_path = journal_dir / (plan_id + '.json')
            _durable_json(journal_path, journal)
            path.parent.mkdir(parents=True, exist_ok=True)
            _no_symlink(path, project)
            temp = path.with_name(path.name + '.kkdesign-tmp-' + plan_id)
            with temp.open('xb') as stream:
                stream.write(record['content'].encode('utf-8')); stream.flush(); os.fsync(stream.fileno())
            os.replace(temp, path)
            entry['written'] = True
            _durable_json(journal_path, journal)
        managed_path = project / '.kkdesign-kit/project/managed.json'
        _no_symlink(managed_path, project)
        managed_old = managed_path.read_bytes() if managed_path.is_file() else None
        managed = json.loads(managed_old.decode('utf-8')) if managed_old else {}
        for rel, record in files.items():
            if record['state'] != 'conflict':
                managed[rel] = record['afterHash']
        managed_bytes = _json_bytes(managed)
        managed_rel = managed_path.relative_to(project).as_posix()
        managed_entry = {'path': managed_rel, 'beforeHash': _hash(managed_old) if managed_old is not None else None,
                         'afterHash': _hash(managed_bytes), 'backup': managed_old.decode('utf-8') if managed_old is not None else None,
                         'written': False}
        journal['entries'].append(managed_entry)
        _durable_json(journal_path, journal)
        _durable_json(managed_path, managed)
        managed_entry['written'] = True
        _durable_json(journal_path, journal)
        plan['status'] = 'applied'; _durable_json(plan_path, plan)
        journal['status'] = 'complete'; _durable_json(journal_path, journal)
        return {'status': 'applied', 'planId': plan_id, 'written': [e['path'] for e in journal['entries']],
                'conflicts': [c['path'] for c in plan.get('conflicts', [])]}
    except Exception:
        # Keep the durable journal for recover(); never hide a partial-write diagnostic.
        raise
    finally:
        _release_lock(lock)


def _atomic_restore(path, data):
    path = Path(path)
    if data is None:
        if path.exists():
            path.unlink()
        return
    temp = path.with_name(path.name + '.kkdesign-restore-' + uuid.uuid4().hex)
    with temp.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def recover(project, plan_id=None):
    project = Path(project).absolute()
    lock = _acquire_lock(project)
    restored = []
    try:
        root = project / '.kkdesign-kit/project/recovery'
        _no_symlink(root, project)
        if not root.exists():
            return {'status': 'clean', 'restored': []}
        if plan_id is not None and not re.fullmatch(r'[a-f0-9]{32}', str(plan_id)):
            raise ValueError('Invalid plan ID')
        paths = [root / (plan_id + '.json')] if plan_id else sorted(root.glob('*.json'))
        for jp in paths:
            _no_symlink(jp, project)
            if not jp.is_file():
                continue
            record = load(jp)
            if record.get('schemaVersion') != '1.0.0' or record.get('planId') != jp.stem:
                raise ValueError('Malformed or mismatched recovery journal')
            state = record.get('status')
            if state == 'rollback-applying':
                _validate_journal_entries(project, record.get('rollbackEntries'))
            elif state == 'applying':
                _validate_journal_entries(project, record.get('entries'))
            elif state in ('complete', 'rolled-back', 'recovered'):
                continue
            else:
                raise ValueError('Unknown recovery journal state')
            if state == 'rollback-applying':
                for entry in reversed(record.get('rollbackEntries', [])):
                    path = _no_symlink(project / _safe_rel(entry['path']), project)
                    current = path.read_bytes() if path.is_file() else None
                    current_hash = _hash(current) if current is not None else None
                    if current_hash == entry['afterHash']:
                        _atomic_restore(path, entry['backup'].encode('utf-8') if entry['backup'] is not None else None)
                        restored.append(entry['path'])
                    elif current_hash != entry['beforeHash']:
                        raise ValueError('Recovery conflict during rollback: ' + entry['path'])
                record['status'] = 'complete'
                _durable_json(jp, record)
                continue
            if state != 'applying':
                raise ValueError('Unknown recovery journal state: ' + str(state))
            for entry in reversed(record.get('entries', [])):
                path = _no_symlink(project / _safe_rel(entry['path']), project)
                current = path.read_bytes() if path.is_file() else None
                current_hash = _hash(current) if current is not None else None
                if current_hash == entry['afterHash']:
                    _atomic_restore(path, entry['backup'].encode('utf-8') if entry['backup'] is not None else None)
                    restored.append(entry['path'])
                elif current_hash != entry['beforeHash']:
                    raise ValueError('Recovery conflict: current file differs from both journal states: ' + entry['path'])
                temp = path.with_name(path.name + '.kkdesign-tmp-' + record['planId'])
                _no_symlink(temp, project)
                if temp.exists():
                    temp.unlink()
            record['status'] = 'recovered'
            _durable_json(jp, record)
            plan_path = _plan_path(project, record['planId'])
            plan = load(plan_path)
            if plan.get('status') == 'applied':
                plan['status'] = 'recovered'
                _durable_json(plan_path, plan)
        return {'status': 'recovered', 'restored': restored}
    finally:
        _release_lock(lock)

def rollback(project, plan_id=None):
    project = Path(project).absolute()
    lock = _acquire_lock(project)
    try:
        root = project / '.kkdesign-kit/project/recovery'
        _no_symlink(root, project)
        if plan_id is None:
            candidates = []
            if root.exists():
                for item in root.glob('*.json'):
                    _no_symlink(item, project)
                    journal = load(item)
                    if journal.get('status') == 'complete':
                        plan_path = _plan_path(project, journal['planId'])
                        candidates.append((load(plan_path).get('createdAt', ''), journal['planId']))
            if not candidates:
                raise ValueError('No applied plan is available to roll back')
            plan_id = max(candidates)[1]
        if not re.fullmatch(r'[a-f0-9]{32}', str(plan_id)):
            raise ValueError('Invalid plan ID')
        jp = root / (str(plan_id) + '.json')
        _no_symlink(jp, project)
        if not jp.is_file():
            raise ValueError('No recovery history for plan: ' + str(plan_id))
        record = load(jp)
        if record.get('schemaVersion') != '1.0.0' or record.get('planId') != str(plan_id):
            raise ValueError('Malformed or mismatched rollback journal')
        if record.get('status') != 'complete':
            raise ValueError('Plan cannot be rolled back from state ' + str(record.get('status')))
        _validate_journal_entries(project, record.get('entries'))
        rollback_entries = []
        for entry in record.get('entries', []):
            path = _no_symlink(project / _safe_rel(entry['path']), project)
            current = path.read_bytes() if path.is_file() else None
            current_hash = _hash(current) if current is not None else None
            if current_hash != entry['afterHash']:
                raise ValueError('Rollback precondition failed for ' + entry['path'])
            rollback_entries.append({'path': entry['path'], 'beforeHash': current_hash,
                                     'afterHash': entry['beforeHash'], 'backup': current.decode('utf-8') if current is not None else None})
        record['status'] = 'rollback-applying'
        record['rollbackEntries'] = rollback_entries
        _durable_json(jp, record)
        for entry in reversed(record['entries']):
            path = _no_symlink(project / _safe_rel(entry['path']), project)
            _atomic_restore(path, entry['backup'].encode('utf-8') if entry['backup'] is not None else None)
        record['status'] = 'rolled-back'
        _durable_json(jp, record)
        plan_path = _plan_path(project, plan_id)
        plan = load(plan_path); plan['status'] = 'rolled-back'; _durable_json(plan_path, plan)
        return {'status': 'rolled-back', 'planId': plan_id, 'restored': [entry['path'] for entry in rollback_entries]}
    finally:
        _release_lock(lock)


def validate_project(project):
    project = Path(project).absolute()
    design = project / 'design'
    _no_symlink(design, project)
    result = validate_foundation(design)
    registry_path = design / 'sources.json'
    _no_symlink(registry_path, project)
    if registry_path.is_file():
        try:
            from kkdesign_core import schema_errors
            from kkdesign_sources import validate_registry
            registry = load(registry_path)
            schema_path = ROOT / 'schemas/source-registry.schema.json'
            registry_errors = schema_errors(registry, schema_path) if schema_path.is_file() else ['Bundled source-registry.schema.json is missing']
            registry_errors.extend(validate_registry(registry))
        except Exception as exc:
            registry_errors = [str(exc)]
        result['registryErrors'] = registry_errors
        result['errors'].extend('source registry: ' + e for e in registry_errors)
        result['status'] = 'fail' if result['errors'] else 'pass'
    else:
        result['errors'].append('Missing design/sources.json')
        result['status'] = 'fail'
    return result



def init_project(project, sources, context=None):
    """Stage an initialization plan; writes to the project only when apply_plan is called."""
    return _plan(project, sources, context, refresh=False)


def refresh_project(project, sources, context=None, migration=None):
    """Stage a refresh plan without mutating the current valid workspace."""
    return _plan(project, sources, context, migration=migration, refresh=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'refresh'):
        p = sub.add_parser(name); p.add_argument('--project', required=True); p.add_argument('--sources', required=True)
        p.add_argument('--context');
        if name == 'refresh': p.add_argument('--migration')
    p = sub.add_parser('apply'); p.add_argument('--project', required=True); p.add_argument('--plan', required=True)
    p = sub.add_parser('plan'); p.add_argument('--project', required=True); p.add_argument('--plan', required=True)
    for name in ('recover', 'rollback', 'validate'):
        p = sub.add_parser(name); p.add_argument('--project', required=True)
        if name in ('recover', 'rollback'): p.add_argument('--plan')
    args = parser.parse_args(argv)
    try:
        if args.command in ('init', 'refresh'):
            result = _plan(args.project, args.sources, args.context, getattr(args, 'migration', None), args.command == 'refresh')
        elif args.command == 'plan': result = inspect_plan(args.project, args.plan)
        elif args.command == 'apply': result = apply_plan(args.project, args.plan)
        elif args.command == 'recover': result = recover(args.project, args.plan)
        elif args.command == 'rollback': result = rollback(args.project, args.plan)
        else: result = validate_project(args.project)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get('status') == 'fail' or 'error' in result else 0
    except (ValueError, OSError, KeyError, TypeError, ImportError, AttributeError) as exc:
        print(json.dumps({'status': 'error', 'diagnostic': str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
