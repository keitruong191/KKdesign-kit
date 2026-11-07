#!/usr/bin/env python3
"""Portable Stage-A contracts. Does not call an agent, Figma, Git, or memory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

VERSION = '0.1.0a1'
LESSON_HEADING = re.compile(r'^### (DL-\d{3}) · (.+)$', re.M)
LESSON_META = re.compile(r'<!-- kkdesign-lesson (\{[^\n]+\}) -->')
KINDS = {'task-template': 'task', 'design-task': 'task',
         'task-evidence': 'task-evidence', 'lesson-index': 'lesson-index',
         'product-profile': 'product-profile'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def local_path(base, reference, boundary):
    """Resolve a local reference without escaping the project (including symlinks)."""
    parsed = urlsplit(reference)
    if parsed.scheme:
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError('Only HTTPS remote evidence is supported: ' + reference)
        return None
    if parsed.netloc or not parsed.path or Path(unquote(parsed.path)).is_absolute():
        raise ValueError('Expected project-relative evidence: ' + reference)
    target = (base / unquote(parsed.path)).resolve()
    if not target.is_relative_to(boundary.resolve()):
        raise ValueError('Reference escapes project: ' + reference)
    if not target.exists():
        raise ValueError('Missing reference: ' + reference)
    return target


def build_lesson_index(design):
    design = Path(design).resolve()
    source = design / 'LESSON.md'
    raw = source.read_bytes()
    text = raw.decode('utf-8')
    headings = list(LESSON_HEADING.finditer(text))
    entries = []
    seen = set()
    for pos, match in enumerate(headings):
        lesson_id, title = match.groups()
        if lesson_id in seen:
            raise ValueError('Duplicate lesson ID: ' + lesson_id)
        seen.add(lesson_id)
        end = headings[pos + 1].start() if pos + 1 < len(headings) else len(text)
        section = text[match.start():end]
        meta = LESSON_META.findall(section)
        if len(meta) != 1:
            raise ValueError('Exactly one metadata block required: ' + lesson_id)
        record = json.loads(meta[0])
        if record.get('id') != lesson_id:
            raise ValueError('Lesson metadata ID mismatch: ' + lesson_id)
        if '<a id="' + lesson_id + '"></a>' not in text[max(0, match.start()-100):match.start()]:
            raise ValueError('Missing explicit lesson anchor: ' + lesson_id)
        if not re.search(r'\*\*(?:Verification|Kiểm chứng):\*\*', section):
            raise ValueError('Missing verification instructions: ' + lesson_id)
        entries.append(dict(record, title=title, anchor=lesson_id,
                            sectionHash=digest(section.encode('utf-8'))))
    if not entries:
        raise ValueError('LESSON.md has no machine-addressable lessons')
    return {'schemaVersion': '1.0.0', 'kind': 'lesson-index',
            'source': 'LESSON.md', 'sourceHash': digest(raw), 'lessons': entries}


def schema_errors(document, schema_file):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = load(schema_file)
    Draft202012Validator.check_schema(schema)
    # Contracts are self-contained; never fetch schema references over the network.
    def walk(value):
        if isinstance(value, dict):
            if '$ref' in value and not value['$ref'].startswith('#/'):
                raise ValueError('Schema has non-local $ref: ' + str(schema_file))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [('/'.join(map(str, error.path)) or '$') + ': ' + error.message
            for error in validator.iter_errors(document)]


def validate_foundation(design, schemas=None):
    design = Path(design).resolve()
    boundary = design.parent
    schemas = Path(schemas).resolve() if schemas else design / 'schemas'
    errors, warnings = [], []
    lessons = {}
    profiles = {}
    checked = []

    def problem(label, operation):
        try:
            return operation()
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append(label + ': ' + str(exc))
            return None

    def check_ref(base, ref):
        return problem(str(base), lambda: local_path(base, ref, boundary))

    def check_document(path, family):
        document = problem(str(path), lambda: load(path))
        if not isinstance(document, dict):
            errors.append(str(path) + ': document must be an object')
            return None
        expected_schema = schemas / (family + '.schema.json')
        claimed_schema = document.get('$schema')
        if not claimed_schema:
            errors.append(str(path) + ': missing $schema')
        else:
            actual = problem(str(path), lambda: local_path(path.parent, claimed_schema, boundary))
            if actual != expected_schema.resolve():
                errors.append(str(path) + ': incorrect schema for ' + family)
        issues = problem(str(path), lambda: schema_errors(document, expected_schema))
        errors.extend(str(path) + ':' + issue for issue in (issues or []))
        checked.append(str(path.relative_to(design)))
        if issues is None or issues:
            return None
        return document

    index_path = design / 'lessons-index.json'
    index = check_document(index_path, 'lesson-index')
    generated = problem('LESSON.md', lambda: build_lesson_index(design))
    if generated and index:
        comparable = {k: v for k, v in index.items() if k != '$schema'}
        if comparable != generated:
            errors.append('lessons-index.json: stale index; rebuild from LESSON.md')
        for item in generated['lessons']:
            lessons[item['id']] = item
            for ref in item.get('evidence', []):
                check_ref(design, ref)

    for path in sorted((design / 'profiles').glob('*.json')):
        profile = check_document(path, 'product-profile')
        if not profile:
            continue
        pid = profile.get('id')
        if pid in profiles:
            errors.append('Duplicate product profile ID: ' + str(pid))
        profiles[pid] = profile
        sources = {s.get('id'): s for s in profile.get('sources', [])}
        if len(sources) != len(profile.get('sources', [])):
            errors.append(str(path) + ': duplicate source IDs')
        for source in sources.values():
            target = check_ref(boundary, source.get('location', ''))
            if target and source.get('sha256') and target.is_file():
                if digest(target.read_bytes()) != source['sha256']:
                    errors.append(str(path) + ': stale source ' + source['id'])
        ids = set()
        for decision in profile.get('decisions', []):
            if decision.get('id') in ids:
                errors.append(str(path) + ': duplicate decision ID')
            ids.add(decision.get('id'))
            for sid in decision.get('sourceIds', []):
                if sid not in sources:
                    errors.append(str(path) + ': unknown source ' + sid)
            if decision.get('status') in ('confirmed', 'observed') and not decision.get('sourceIds'):
                errors.append(str(path) + ': confirmed/observed decision lacks evidence')

    historical_lessons = {}

    def task_lessons(source_hash):
        """Resolve a pinned source without rewriting the task's historical claims."""
        if index and source_hash == index.get('sourceHash'):
            return lessons
        if not isinstance(source_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', source_hash):
            return None
        if source_hash in historical_lessons:
            return historical_lessons[source_hash]
        snapshot = design / 'lesson-history' / source_hash
        try:
            source_path = local_path(design, 'lesson-history/' + source_hash + '/LESSON.md', boundary)
            index_path = local_path(design, 'lesson-history/' + source_hash + '/lessons-index.json', boundary)
            if digest(source_path.read_bytes()) != source_hash:
                raise ValueError('historical lesson source hash mismatch')
            saved = load(index_path)
            if schema_errors(saved, schemas / 'lesson-index.schema.json'):
                raise ValueError('invalid historical lesson index')
            generated = build_lesson_index(snapshot)
            if {k: v for k, v in saved.items() if k != '$schema'} != generated:
                raise ValueError('historical lesson index mismatch')
            result = {item['id']: item for item in generated['lessons']}
        except (ValueError, OSError, KeyError, TypeError):
            result = None
        historical_lessons[source_hash] = result
        return result

    paths = [design / 'task-template.json'] + sorted((design / 'tasks').rglob('*.json'))
    for path in paths:
        family = 'task' if path.name in ('task-template.json', 'task.json') else 'task-evidence'
        doc = check_document(path, family)
        if not doc:
            continue
        if family == 'task-evidence':
            record = doc.get('record', {})
            tid = record.get('taskId')
            if tid != path.parent.name:
                errors.append(str(path) + ': record.taskId differs from directory')
            if not (path.parent / 'task.json').is_file():
                errors.append(str(path) + ': evidence has no task.json')
            payload = {k: v for k, v in doc.items() if k not in ('$schema', 'schemaVersion', 'kind', 'record')}
            payload_hash = digest(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
            if payload_hash != record.get('payloadSha256'):
                errors.append(str(path) + ': evidence payload hash mismatch')
            for ref in record.get('references', []):
                check_ref(path.parent, ref)
            continue
        review = doc.get('lessonReview', {})
        status = review.get('status')
        entries = review.get('entries', [])
        if path.name == 'task-template.json':
            if doc.get('kind') != 'task-template' or doc.get('status') != 'template':
                errors.append('Shared task-template.json contains an active task')
            if status != 'pending' or entries:
                errors.append('Shared template must have a pending, empty lessonReview')
        else:
            if doc.get('kind') != 'design-task' or doc.get('status') == 'template':
                errors.append(str(path) + ': active task has template identity')
            if doc.get('taskId') != path.parent.name:
                errors.append(str(path) + ': taskId differs from directory')
            if doc.get('productProfileId') not in profiles:
                errors.append(str(path) + ': unknown productProfileId')
            else:
                profile_platform = profiles[doc['productProfileId']]['platform']
                if profile_platform not in ('adaptive', str(doc.get('platform')).lower()):
                    errors.append(str(path) + ': product profile platform mismatch')
            if doc.get('status') in ('design_delivered', 'design_verified_review_pending', 'complete', 'done', 'delivered') and status == 'pending':
                errors.append(str(path) + ': delivered task still has pending lesson review')
            if status == 'retrospective':
                warnings.append(str(path.relative_to(design)) + ': retrospective mapping is not proof of pre-task reading')
        reviewed_lessons = lessons
        if status in ('reviewed', 'retrospective', 'not-applicable'):
            reviewed_lessons = task_lessons(review.get('sourceHash'))
            if reviewed_lessons is None:
                errors.append(str(path) + ': lessonReview sourceHash is stale or historical snapshot is invalid')
                reviewed_lessons = lessons
            elif index and review.get('sourceHash') != index.get('sourceHash'):
                warnings.append(str(path.relative_to(design)) + ': historical lesson source verified; not proof of prior reading or a new pass')
        if status == 'reviewed' and not entries:
            errors.append(str(path) + ': reviewed task has no lesson decisions')
        if status in ('retrospective', 'not-applicable') and not review.get('reason'):
            errors.append(str(path) + ': lessonReview requires a reason')
        used = set()
        for entry in entries:
            lid = entry.get('lessonId')
            if lid in used:
                errors.append(str(path) + ': duplicate lesson decision ' + str(lid))
            used.add(lid)
            if lid not in reviewed_lessons:
                errors.append(str(path) + ': unknown lesson ID ' + str(lid))
            elif reviewed_lessons[lid].get('status') != 'active' and entry.get('decision') == 'apply':
                errors.append(str(path) + ': applying inactive lesson ' + str(lid))
            elif entry.get('decision') == 'apply':
                platforms = reviewed_lessons[lid].get('platforms', [])
                if 'any' not in platforms and str(doc.get('platform')).lower() not in platforms:
                    errors.append(str(path) + ': lesson platform mismatch ' + str(lid))
            if entry.get('verification') in ('pass', 'evidence-mapped') and not entry.get('evidence'):
                errors.append(str(path) + ': verification claim lacks evidence ' + str(lid))
            if entry.get('decision') == 'not-applicable' and entry.get('verification') != 'not-applicable':
                errors.append(str(path) + ': inapplicable lesson must not claim verification ' + str(lid))
            if status == 'retrospective' and entry.get('verification') == 'pass':
                errors.append(str(path) + ': retrospective mapping cannot declare new pass results')
            for ref in entry.get('evidence', []):
                check_ref(path.parent, ref)

    # Validate the entry guide and lesson references, including explicit lesson anchors.
    for path in [boundary / 'DESIGN.md', design / 'LESSON.md']:
        text = problem(str(path), lambda: path.read_text(encoding='utf-8'))
        if text is None:
            continue
        for reference in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
            if reference.startswith(('https://', '#')):
                continue
            target = check_ref(path.parent, reference)
            fragment = urlsplit(reference).fragment
            if target and target.name == 'LESSON.md' and fragment:
                if fragment not in lessons:
                    errors.append(str(path) + ': unknown lesson anchor ' + fragment)
    return {'status': 'fail' if errors else 'pass', 'version': VERSION,
            'checkedFiles': checked, 'lessons': len(lessons), 'profiles': len(profiles),
            'errors': errors, 'warnings': warnings,
            'scope': 'Offline contract integrity; not fresh Figma/runtime evidence or approval.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'lessons-index'])
    parser.add_argument('--design', required=True, type=Path)
    parser.add_argument('--schemas', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'lessons-index':
            data = build_lesson_index(args.design)
            data = {'$schema': 'schemas/lesson-index.schema.json', **data}
            issues = schema_errors(data, (args.schemas or args.design / 'schemas') / 'lesson-index.schema.json')
            if issues:
                raise ValueError('; '.join(issues))
            save(args.design / 'lessons-index.json', data)
            print(json.dumps({'status': 'generated', 'lessons': len(data['lessons'])}))
            return 0
        result = validate_foundation(args.design, args.schemas)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(result['status'] != 'pass')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'fail', 'errors': [str(exc)]}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
