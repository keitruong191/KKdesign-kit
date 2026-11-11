#!/usr/bin/env python3
"""Capture design feedback and author canonical lessons without fabricating verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from kkdesign_core import build_lesson_index, local_path, schema_errors
from kkdesign_install import no_links

PLATFORMS = {'any', 'web', 'macos', 'ios', 'android', 'windows'}
LESSON = re.compile(r'^### (DL-\d{3}) · (.+)$', re.M)
META = re.compile(r'<!-- kkdesign-lesson (\{[^\n]+\}) -->')


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _required(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be a non-empty string')
    return value.strip()


def _evidence(design, refs):
    if not refs:
        raise ValueError('At least one evidence reference is required')
    for ref in refs:
        _required(ref, 'Evidence reference')
        if local_path(design, ref, design.parent) is None:
            raise ValueError('Learning requires preserved project-local evidence: ' + ref)
    return list(dict.fromkeys(refs))


def _load_feedback(path):
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, list):
        raise ValueError('feedback.json must contain an array')
    ids = set()
    for record in value:
        if not isinstance(record, dict) or not isinstance(record.get('id'), str):
            raise ValueError('Malformed feedback record')
        if record['id'] in ids:
            raise ValueError('Duplicate feedback ID: ' + record['id'])
        ids.add(record['id'])
    return value


def _lock(design):
    lock = design / '.kkdesign-learn.lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('Another learn operation is in progress (lock: ' + str(lock) + ')')
    (lock / 'owner').write_text(str(os.getpid()), encoding='ascii')
    return lock


def _atomic_write(path, data):
    no_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _commit(design, replacements, expected):
    """Write a validated file set, rolling back on an ordinary write failure."""
    for path in set(replacements) | set(expected):
        no_links(path)
        if not path.resolve().is_relative_to(design):
            raise ValueError('Learning write path escapes design directory: ' + str(path))
    lock = _lock(design)
    originals = {}
    try:
        for path, prior in expected.items():
            current = path.read_bytes() if path.exists() else None
            if current != prior:
                raise ValueError('Learning files changed while preparing update: ' + str(path))
        originals = {path: path.read_bytes() if path.exists() else None for path in replacements}
        try:
            for path, content in replacements.items():
                _atomic_write(path, content)
        except Exception:
            for path, content in originals.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    _atomic_write(path, content)
            raise
    finally:
        try:
            (lock / 'owner').unlink(missing_ok=True)
            lock.rmdir()
        except OSError:
            pass



def _checked_index(design, source_bytes):
    with tempfile.TemporaryDirectory() as temp:
        staged = Path(temp) / 'design'
        staged.mkdir()
        (staged / 'LESSON.md').write_bytes(source_bytes)
        index = build_lesson_index(staged)
    document = {'$schema': 'schemas/lesson-index.schema.json', **index}
    issues = schema_errors(document, Path(design) / 'schemas/lesson-index.schema.json')
    if issues:
        raise ValueError('Generated lesson index is invalid: ' + '; '.join(issues))
    return index


def _history_snapshot(design, source_bytes):
    """Return immutable pre-change snapshots keyed by their canonical source hash."""
    index = _checked_index(design, source_bytes)
    history = design / 'lesson-history' / index['sourceHash']
    source_path = history / 'LESSON.md'
    index_path = history / 'lessons-index.json'
    source_data = source_bytes
    index_data = _json_bytes({'$schema': 'schemas/lesson-index.schema.json', **index})
    expected = {}
    for path, data in ((source_path, source_data), (index_path, index_data)):
        no_links(path)
        if not path.resolve().is_relative_to(design):
            raise ValueError('Historical lesson path escapes design directory: ' + str(path))
        existing = path.read_bytes() if path.exists() else None
        if existing is not None and existing != data:
            raise ValueError('Conflicting historical lesson snapshot: ' + str(path))
        expected[path] = existing
    return {source_path: source_data, index_path: index_data}, expected

def _feedback_identity(content, evidence, scope, origin):
    body = {'content': content, 'evidence': evidence, 'scope': scope, 'origin': origin}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def capture_feedback(design, content, evidence, scope, origin):
    design = Path(design).resolve()
    path = design / 'feedback.json'
    content = _required(content, 'Feedback')
    scope = _required(scope, 'Scope')
    if scope not in PLATFORMS:
        raise ValueError('Scope must be one of: ' + ', '.join(sorted(PLATFORMS)))
    origin = _required(origin, 'Origin')
    evidence = _evidence(design, evidence)
    original = path.read_bytes() if path.exists() else None
    records = _load_feedback(path)
    fingerprint = _feedback_identity(content, evidence, scope, origin)
    for record in records:
        if record.get('fingerprint') == fingerprint:
            return {'status': 'duplicate', 'id': record['id'], 'changed': False}
    numbers = [int(match.group(1)) for row in records
               if (match := re.fullmatch(r'FB-(\d+)', str(row.get('id', ''))))]
    feedback_id = 'FB-' + str(max(numbers, default=0) + 1).zfill(3)
    record = {'id': feedback_id, 'kind': 'direct-feedback', 'content': content,
              'evidence': evidence, 'scope': scope, 'origin': origin,
              'fingerprint': fingerprint}
    records.append(record)
    _commit(design, {path: _json_bytes(records)}, {path: original})
    return {'status': 'captured', 'id': feedback_id, 'changed': True}


def _next_id(text):
    ids = [int(match[0][3:]) for match in LESSON.findall(text)]
    number = max(ids, default=0) + 1
    if number > 999:
        raise ValueError('DL-NNN lesson ID space is exhausted')
    return 'DL-' + str(number).zfill(3)


def _existing_authored_lesson(text, metadata, title, body, verification):
    text = text.replace('\r\n', '\n')
    expected_advice = ('\n\n' + body + '\n\n**Verification:** ' + verification + '\n').replace('\r\n', '\n')
    headings = list(LESSON.finditer(text))
    lifecycle_fields = {'id', 'status', 'supersededBy'}
    comparable = {key: value for key, value in metadata.items() if key not in lifecycle_fields}
    for position, match in enumerate(headings):
        end = headings[position + 1].start() if position + 1 < len(headings) else len(text)
        section = text[match.start():end]
        if position + 1 < len(headings):
            next_anchor = '\n<a id="' + headings[position + 1].group(1) + '"></a>\n'
            section = section.removesuffix(next_anchor)
        blocks = list(META.finditer(section))
        if len(blocks) != 1:
            continue
        existing = json.loads(blocks[0].group(1))
        existing_comparable = {key: value for key, value in existing.items() if key not in lifecycle_fields}
        advice = section[blocks[0].end():]
        if existing_comparable == comparable and match.group(2) == title and advice == expected_advice:
            return match.group(1)
    return None


def author_lesson(design, title, body, verification, evidence, scope, tags,
                  applies_when, origin_task=None, feedback_id=None):
    design = Path(design).resolve()
    source = design / 'LESSON.md'
    index_path = design / 'lessons-index.json'
    original = source.read_bytes()
    source_text = original.decode('utf-8')
    title, body = _required(title, 'Title'), _required(body, 'Lesson body')
    if '\n' in title or '\r' in title:
        raise ValueError('Title must be a single line')
    verification = _required(verification, 'Verification')
    scope = _required(scope, 'Scope')
    if scope not in PLATFORMS:
        raise ValueError('Scope must be one of: ' + ', '.join(sorted(PLATFORMS)))
    applies_when = _required(applies_when, 'Applies-when condition')
    evidence = _evidence(design, evidence)
    if origin_task is not None:
        origin_task = _required(origin_task, 'Origin task')
    if feedback_id is not None:
        feedback_id = _required(feedback_id, 'Feedback ID')
    tags = list(dict.fromkeys(_required(tag, 'Tag') for tag in tags))
    if not tags:
        raise ValueError('At least one tag is required')
    feedback_path = design / 'feedback.json'
    feedback_original = feedback_path.read_bytes() if feedback_path.exists() else None
    feedback_ids = {record['id'] for record in _load_feedback(feedback_path)}
    if feedback_id and feedback_id not in feedback_ids:
        raise ValueError('Unknown feedback ID: ' + feedback_id)
    meta = {'kind': 'inferred', 'status': 'active',
            'platforms': [scope], 'tags': tags, 'appliesWhen': applies_when,
            'evidence': evidence, 'originTask': origin_task}
    if feedback_id:
        meta['originFeedback'] = feedback_id
    if not origin_task and not feedback_id:
        raise ValueError('An inferred lesson requires --origin-task or --feedback-id')
    duplicate = _existing_authored_lesson(source_text, meta, title, body, verification)
    if duplicate:
        return {'status': 'duplicate', 'id': duplicate, 'changed': False}
    lesson_id = _next_id(source_text)
    meta = {'id': lesson_id, **meta}
    section = ('\n<a id="' + lesson_id + '"></a>\n### ' + lesson_id + ' · ' + title +
               '\n\n<!-- kkdesign-lesson ' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) +
               ' -->\n\n' + body + '\n\n**Verification:** ' + verification + '\n')
    new_source = original + section.encode('utf-8')
    index = _checked_index(design, new_source)
    index_data = {'$schema': 'schemas/lesson-index.schema.json', **index}
    history_replacements, history_expected = _history_snapshot(design, original)
    replacements = dict(history_replacements)
    replacements.update({source: new_source, index_path: _json_bytes(index_data)})
    expected = {source: original, index_path: index_path.read_bytes() if index_path.exists() else None,
                feedback_path: feedback_original}
    expected.update(history_expected)
    _commit(design, replacements, expected)
    return {'status': 'authored', 'id': lesson_id, 'sourceHash': index['sourceHash'], 'changed': True}


def supersede_lesson(design, lesson_id, replacement_id):
    design = Path(design).resolve()
    source = design / 'LESSON.md'
    index_path = design / 'lessons-index.json'
    original = source.read_bytes()
    text = original.decode('utf-8')
    headings = list(LESSON.finditer(text))
    positions = {match.group(1): match for match in headings}
    if lesson_id not in positions or replacement_id not in positions:
        raise ValueError('Both lesson IDs must already exist')
    if lesson_id == replacement_id:
        raise ValueError('A lesson cannot supersede itself')
    start = positions[lesson_id].start()
    end = next((match.start() for match in headings if match.start() > start), len(text))
    section = text[start:end]
    metas = list(META.finditer(section))
    if len(metas) != 1:
        raise ValueError('Exactly one metadata block required: ' + lesson_id)
    metadata = json.loads(metas[0].group(1))
    if metadata.get('status') == 'superseded':
        if metadata.get('supersededBy') == replacement_id:
            return {'status': 'duplicate', 'id': lesson_id, 'changed': False}
        raise ValueError('Lesson is already superseded; supersession is explicit and immutable')
    if metadata.get('status') != 'active':
        raise ValueError('Only an active lesson can be superseded')
    replacement_match = positions[replacement_id]
    replacement_end = next((match.start() for match in headings
                            if match.start() > replacement_match.start()), len(text))
    replacement_section = text[replacement_match.start():replacement_end]
    replacement_meta = META.findall(replacement_section)
    if len(replacement_meta) != 1 or json.loads(replacement_meta[0]).get('status') != 'active':
        raise ValueError('Replacement lesson must have active canonical metadata')
    metadata['status'] = 'superseded'
    metadata['supersededBy'] = replacement_id
    changed_section = section[:metas[0].start()] + '<!-- kkdesign-lesson ' + json.dumps(
        metadata, ensure_ascii=False, separators=(',', ':')) + ' -->' + section[metas[0].end():]
    updated = text[:start] + changed_section + text[end:]
    index = _checked_index(design, updated.encode('utf-8'))
    history_replacements, history_expected = _history_snapshot(design, original)
    replacements = dict(history_replacements)
    replacements.update({source: updated.encode('utf-8'),
                         index_path: _json_bytes({'$schema': 'schemas/lesson-index.schema.json', **index})})
    expected = {source: original, index_path: index_path.read_bytes() if index_path.exists() else None}
    expected.update(history_expected)
    _commit(design, replacements, expected)
    return {'status': 'superseded', 'id': lesson_id, 'supersededBy': replacement_id,
            'sourceHash': index['sourceHash'], 'changed': True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    feedback = subs.add_parser('feedback', help='capture direct feedback separately from lessons')
    feedback.add_argument('--design', type=Path, required=True)
    feedback.add_argument('--content', required=True)
    feedback.add_argument('--evidence', action='append', required=True)
    feedback.add_argument('--scope', required=True)
    feedback.add_argument('--origin', required=True)
    author = subs.add_parser('author', help='derive an inferred lesson from evidence')
    author.add_argument('--design', type=Path, required=True)
    author.add_argument('--title', required=True)
    author.add_argument('--body', required=True)
    author.add_argument('--verification', required=True)
    author.add_argument('--evidence', action='append', required=True)
    author.add_argument('--scope', required=True, choices=sorted(PLATFORMS))
    author.add_argument('--tag', action='append', required=True)
    author.add_argument('--applies-when', required=True)
    author.add_argument('--origin-task')
    author.add_argument('--feedback-id')
    supersede = subs.add_parser('supersede', help='mark a lesson superseded by an existing lesson')
    supersede.add_argument('--design', type=Path, required=True)
    supersede.add_argument('--id', required=True)
    supersede.add_argument('--by', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'feedback':
            result = capture_feedback(args.design, args.content, args.evidence, args.scope, args.origin)
        elif args.command == 'author':
            result = author_lesson(args.design, args.title, args.body, args.verification,
                                   args.evidence, args.scope, args.tag, args.applies_when,
                                   args.origin_task, args.feedback_id)
        else:
            result = supersede_lesson(args.design, args.id, args.by)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print('learn: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
