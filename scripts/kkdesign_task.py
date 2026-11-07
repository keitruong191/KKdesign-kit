#!/usr/bin/env python3
"""Record scoped design tasks and evidence without executing design tools."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, unquote, urlsplit

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from kkdesign_core import build_lesson_index, load, schema_errors

TASK_SCHEMA = ROOT / 'schemas/task.schema.json'
EVIDENCE_SCHEMA = ROOT / 'schemas/task-evidence.schema.json'
PLATFORMS = {'web', 'macos', 'ios', 'android', 'windows', 'adaptive'}
EVIDENCE_TYPES = {'snapshot', 'audit', 'style-review', 'correction'}



def _canonical_hash(value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def _safe_task_id(task_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', task_id) or task_id in ('.', '..'):
        raise ValueError('task ID must be a simple project-local name')
    return task_id


def _project_paths(project):
    project = Path(project).resolve()
    design = project / 'design'
    for path in (design, design / 'tasks', design / 'profiles', design / 'lessons-index.json'):
        if path.is_symlink():
            raise ValueError('Project design path must not be a symlink: ' + str(path))
    if not design.is_dir() or not (design / 'tasks').is_dir():
        raise ValueError('Project design kit is not initialized: ' + str(design))
    return project, design


def _payload_from_evidence(document):
    return {key: value for key, value in document.items()
            if key not in ('$schema', 'schemaVersion', 'kind', 'record')}


def check_task(project, task_id):
    project, design = _project_paths(project)
    task_dir, _, task = _task_record(design, task_id)
    evidence_names = set()
    for path in sorted(item for item in task_dir.glob('*.json') if item.name != 'task.json'):
        if path.is_symlink() or not path.is_file():
            raise ValueError('Evidence path is missing or unsafe: ' + str(path))
        document = load(path)
        issues = schema_errors(document, EVIDENCE_SCHEMA)
        if issues:
            raise ValueError(str(path.name) + ': ' + '; '.join(issues))
        record = document['record']
        if record['taskId'] != task_id:
            raise ValueError(str(path.name) + ': evidence taskId mismatch')
        if record['payloadSha256'] != _canonical_hash(_payload_from_evidence(document)):
            raise ValueError(str(path.name) + ': evidence payload hash mismatch')
        _reference_check(task_dir, record['references'], project)
        evidence_names.add(path.name)
    for check in task.get('handoff', {}).get('checks', []):
        cited = check.get('evidence') if isinstance(check, dict) else None
        if not isinstance(cited, list) or not cited or any(name not in evidence_names for name in cited):
            raise ValueError('Handoff checks must cite existing task evidence')
    return {'status': 'checked', 'taskId': task_id, 'evidenceRecords': len(evidence_names),
            'scope': 'Offline record/schema/reference integrity only; not live behavior or approval.'}


def _validate_record(record, design, task_id):
    issues = schema_errors(record, TASK_SCHEMA)
    if issues:
        raise ValueError('Invalid task record: ' + '; '.join(issues))
    if record['kind'] != 'design-task' or record['taskId'] != task_id:
        raise ValueError('Task record kind and taskId must match the requested task')
    if record['status'] != 'in_progress':
        raise ValueError('A new task must start in_progress')
    if record['platform'] not in PLATFORMS:
        raise ValueError('Unsupported task platform: ' + str(record['platform']))
    profile_id = record['productProfileId']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', profile_id):
        raise ValueError('Invalid project-local product profile ID')
    profile_path = design / 'profiles' / (profile_id + '.json')
    if not profile_path.is_file() or profile_path.is_symlink():
        raise ValueError('Task product profile is missing or unsafe: ' + profile_id)
    profile = load(profile_path)
    if profile.get('platform') not in ('adaptive', record['platform']):
        raise ValueError('Task platform does not match its product profile')
    index_path = design / 'lessons-index.json'
    index = load(index_path)
    generated = build_lesson_index(design)
    if {key: value for key, value in index.items() if key != '$schema'} != generated:
        raise ValueError('Lesson index is stale; regenerate it before beginning the task')
    review = record['lessonReview']
    if review.get('status') != 'reviewed' or review.get('sourceHash') != index.get('sourceHash'):
        raise ValueError('Complete a current lesson review before beginning mutation')
    available = {item.get('id'): item for item in index.get('lessons', [])}
    decisions = review.get('entries', [])
    if not decisions:
        raise ValueError('Pre-task lesson review must record a decision for applicable lessons')
    applicable = {lesson_id for lesson_id, lesson in available.items()
                  if lesson.get('status') == 'active' and
                  ('any' in lesson.get('platforms', []) or record['platform'] in lesson.get('platforms', []))}
    ids = set()
    for decision in decisions:
        lesson_id = decision['lessonId']
        lesson = available.get(lesson_id)
        if lesson is None or lesson_id in ids:
            raise ValueError('Lesson review contains an unknown or repeated lesson: ' + lesson_id)
        ids.add(lesson_id)
        if decision['decision'] == 'apply' and decision['verification'] != 'pending':
            raise ValueError('Pre-task lesson decisions must leave verification pending: ' + lesson_id)
        if decision['decision'] == 'not-applicable' and decision['verification'] != 'not-applicable':
            raise ValueError('Inapplicable lesson decisions must use not-applicable verification: ' + lesson_id)
        if decision['decision'] == 'apply':
            if lesson['status'] != 'active' or ('any' not in lesson['platforms'] and record['platform'] not in lesson['platforms']):
                raise ValueError('Cannot apply inactive or platform-inapplicable lesson: ' + lesson_id)
    if applicable - ids:
        raise ValueError('Pre-task lesson review omits applicable lessons: ' + ', '.join(sorted(applicable - ids)))
    destination = record['target'].get('fileKey') or record['target'].get('destination')
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError('Resolve target.fileKey or target.destination before beginning')
    states = record.get('states')
    if not isinstance(states, dict) or not isinstance(states.get('required'), list) or not isinstance(states.get('notApplicable'), list):
        raise ValueError('Resolve required and inapplicable states before beginning')
    plan = record['designPlan']
    if not isinstance(plan.get('layoutDecisions'), list) or not plan['layoutDecisions']:
        raise ValueError('Record component/layout/binding and scoped fallback decisions before beginning')
    if not isinstance(plan.get('stateDispositions'), list):
        raise ValueError('Record state dispositions in designPlan before beginning')
    if not isinstance(plan.get('referenceExamples'), list):
        raise ValueError('Record inspected reference instances, or an explicit empty list, before beginning')
    return record


def begin(project, record_file):
    project, design = _project_paths(project)
    record = load(record_file)
    if not isinstance(record, dict):
        raise ValueError('Task record must be a JSON object')
    record['$schema'] = '../../schemas/task.schema.json'
    task_id = _safe_task_id(str(record.get('taskId', '')))
    _validate_record(record, design, task_id)
    task_dir = design / 'tasks' / task_id
    if task_dir.exists() or task_dir.is_symlink():
        raise ValueError('Task already exists; refusing to overwrite: ' + task_id)
    task_dir.mkdir()
    try:
        path = task_dir / 'task.json'
        with path.open('x', encoding='utf-8') as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    except Exception:
        try:
            path.unlink()
            task_dir.rmdir()
        except OSError:
            pass
        raise
    return {'status': 'begun', 'taskId': task_id, 'record': str(path.relative_to(project))}


def _task_record(design, task_id):
    task_id = _safe_task_id(task_id)
    task_dir = design / 'tasks' / task_id
    if task_dir.is_symlink() or not task_dir.is_dir():
        raise ValueError('Unknown or unsafe task: ' + task_id)
    path = task_dir / 'task.json'
    if path.is_symlink() or not path.is_file():
        raise ValueError('Task record is missing or unsafe: ' + task_id)
    task = load(path)
    issues = schema_errors(task, TASK_SCHEMA)
    if issues:
        raise ValueError('Invalid task record: ' + '; '.join(issues))
    if task.get('taskId') != task_id or task.get('kind') != 'design-task':
        raise ValueError('Task record identity differs from its directory')
    return task_dir, path, task


def _reference_check(task_dir, references, project):
    if not isinstance(references, list) or any(not isinstance(ref, str) or not ref for ref in references):
        raise ValueError('Evidence references must be a list of nonempty strings')
    for reference in references:
        parsed = urlsplit(reference)
        credential_query = any(re.search(r'(?:token|auth|secret|credential|password|api.?key)', key, re.I)
                               for key, _ in parse_qsl(parsed.query, keep_blank_values=True))
        if parsed.scheme:
            if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or credential_query:
                raise ValueError('Remote evidence references must be credential-free HTTPS URLs')
            continue
        if parsed.netloc or Path(unquote(parsed.path)).is_absolute() or not parsed.path:
            raise ValueError('Evidence references must be project-relative paths or HTTPS URLs')
        resolved = (task_dir / unquote(parsed.path)).resolve()
        if not resolved.is_relative_to(project.resolve()) or not resolved.exists():
            raise ValueError('Evidence reference is missing or escapes the project: ' + reference)


def add_evidence(project, task_id, evidence_type, description, payload_file, references, historical_status='historical'):
    project, design = _project_paths(project)
    task_dir, _, task = _task_record(design, task_id)
    if evidence_type not in EVIDENCE_TYPES:
        raise ValueError('Unsupported evidence type: ' + evidence_type)
    if historical_status not in ('current', 'superseded', 'historical'):
        raise ValueError('Unsupported historical evidence status: ' + historical_status)
    if not description.strip():
        raise ValueError('Evidence description must not be empty')
    payload = load(payload_file)
    if not isinstance(payload, dict):
        raise ValueError('Evidence payload must be a JSON object')
    if set(payload) & {'$schema', 'schemaVersion', 'kind', 'record'}:
        raise ValueError('Evidence payload must not replace wrapper contract fields')
    _reference_check(task_dir, references, project)
    existing = sorted(task_dir.glob('evidence-*.json'))
    numbers = []
    for path in existing:
        if path.is_symlink():
            raise ValueError('Evidence path must not be a symlink: ' + str(path))
        match = re.fullmatch(r'evidence-(\d{4,})\.json', path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    path = task_dir / ('evidence-%04d.json' % number)
    wrapper = {'$schema': '../../schemas/task-evidence.schema.json', 'schemaVersion': '1.0.0',
               'kind': 'task-evidence', 'record': {
                   'taskId': task['taskId'], 'evidenceType': evidence_type,
                   'historicalStatus': historical_status, 'description': description.strip(),
                   'payloadSha256': _canonical_hash(payload), 'references': references},
               **payload}
    issues = schema_errors(wrapper, EVIDENCE_SCHEMA)
    if issues:
        raise ValueError('Invalid wrapped task evidence: ' + '; '.join(issues))
    with path.open('x', encoding='utf-8') as stream:
        json.dump(wrapper, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return {'status': 'recorded', 'taskId': task_id, 'evidence': str(path.relative_to(project))}


def update_handoff(project, task_id, handoff_file, status):
    project, design = _project_paths(project)
    task_dir, task_path, task = _task_record(design, task_id)
    if status not in ('in_progress', 'design_delivered', 'design_verified_review_pending'):
        raise ValueError('Unsupported handoff status')
    handoff = load(handoff_file)
    if not isinstance(handoff, dict):
        raise ValueError('Handoff must be a JSON object')
    for key in ('frameLinks', 'createdNodeIds', 'modifiedNodeIds', 'checks', 'remainingGaps'):
        if key not in handoff:
            raise ValueError('Handoff must include ' + key)
        if not isinstance(handoff[key], list):
            raise ValueError('Handoff field must be an array: ' + key)
    evidence = check_task(project, task_id)
    evidence_ids = {path.name for path in task_dir.glob('evidence-*.json')
                    if path.is_file() and not path.is_symlink()}
    for check in handoff['checks']:
        if not isinstance(check, dict) or not isinstance(check.get('evidence'), list) or not check['evidence']:
            raise ValueError('Each handoff check must cite task evidence; no check result is inferred')
        if any(cited not in evidence_ids for cited in check['evidence']):
            raise ValueError('Handoff check cites missing task evidence')
    if status != 'in_progress':
        mapping = handoff.get('requirementStateMapping')
        blocked = handoff.get('blockedDisposition')
        if not handoff['checks'] or evidence['evidenceRecords'] == 0:
            raise ValueError('Delivery requires checks backed by valid task evidence')
        if not handoff['frameLinks'] and not (isinstance(blocked, str) and blocked.strip()):
            raise ValueError('Delivery requires direct frame links or an explicit blockedDisposition')
        if not mapping and not (isinstance(blocked, str) and blocked.strip()):
            raise ValueError('Delivery requires requirementStateMapping or an explicit blockedDisposition')
        if not isinstance(mapping, list) and mapping is not None:
            raise ValueError('requirementStateMapping must be an array')
    task['handoff'] = handoff
    task['status'] = status
    issues = schema_errors(task, TASK_SCHEMA)
    if issues:
        raise ValueError('Invalid updated task record: ' + '; '.join(issues))
    temp = task_path.with_name(task_path.name + '.tmp')
    with temp.open('x', encoding='utf-8') as stream:
        json.dump(task, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    try:
        temp.replace(task_path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    return {'status': 'updated', 'taskId': task_id, 'taskStatus': status}




def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('begin', help='Create a task record after preflight decisions are resolved')
    p.add_argument('--project', required=True); p.add_argument('--record', required=True)
    p = sub.add_parser('evidence', help='Append an authentic, wrapped evidence record')
    p.add_argument('--project', required=True); p.add_argument('--task-id', required=True)
    p.add_argument('--type', required=True, choices=sorted(EVIDENCE_TYPES)); p.add_argument('--description', required=True)
    p.add_argument('--payload', required=True); p.add_argument('--reference', action='append', default=[])
    p.add_argument('--historical-status', choices=('current', 'superseded', 'historical'), default='historical')
    p = sub.add_parser('handoff', help='Record evidence-linked handoff; never invent results')
    p.add_argument('--project', required=True); p.add_argument('--task-id', required=True)
    p.add_argument('--record', required=True); p.add_argument('--status', default='in_progress')
    p = sub.add_parser('check', help='Check task and wrapped evidence integrity only')
    p.add_argument('--project', required=True); p.add_argument('--task-id', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'begin':
            result = begin(args.project, args.record)
        elif args.command == 'evidence':
            result = add_evidence(args.project, args.task_id, args.type, args.description,
                                  args.payload, args.reference, args.historical_status)
        elif args.command == 'handoff':
            result = update_handoff(args.project, args.task_id, args.record, args.status)
        else:
            result = check_task(args.project, args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'error', 'diagnostic': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
