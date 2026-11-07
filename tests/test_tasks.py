import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_task as tasks
from materialize_example import materialize


class DesignTaskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = materialize(Path(self.temp.name) / 'project')
        self.record_path = Path(self.temp.name) / 'task.json'
        self.record = json.loads((self.project / 'design/task-template.json').read_text(encoding='utf-8'))
        self.record.update({
            'kind': 'design-task', 'status': 'in_progress', 'taskId': 'settings-review',
            'objective': 'Record a synthetic settings design task.', 'product': 'Synthetic product',
            'platform': 'web', 'productProfileId': 'example-web',
            'target': {'destination': 'design-file://synthetic/settings'},
            'designPlan': {
                'recipeId': None, 'platformProfileId': 'web',
                'layoutDecisions': [{'decision': 'Inspect existing component and semantic bindings before reuse.'}],
                'stateDispositions': [{'state': 'default', 'disposition': 'planned'}],
                'accessibilityChecks': [], 'referenceExamples': [], 'policyOverrides': []
            },
            'lessonReview': {
                'status': 'reviewed', 'sourceHash': json.loads(
                    (self.project / 'design/lessons-index.json').read_text(encoding='utf-8'))['sourceHash'],
                'entries': [{'lessonId': 'DL-001', 'decision': 'apply',
                             'reason': 'Inspect reference instances before choosing a component.',
                             'verification': 'pending', 'evidence': []}]
            }
        })
        self.record_path.write_text(json.dumps(self.record), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def begin(self):
        return tasks.begin(self.project, self.record_path)

    def test_begin_rejects_stale_review_before_creating_task(self):
        self.record['lessonReview']['sourceHash'] = '0' * 64
        self.record_path.write_text(json.dumps(self.record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'current lesson review'):
            self.begin()
        self.assertFalse((self.project / 'design/tasks/settings-review').exists())

    def test_begin_requires_resolved_pre_mutation_design_decisions(self):
        self.record['designPlan']['layoutDecisions'] = []
        self.record_path.write_text(json.dumps(self.record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'layout'):
            self.begin()
        self.assertFalse((self.project / 'design/tasks/settings-review').exists())

    def test_begin_rejects_preexisting_pass_claims_before_mutation(self):
        self.record['lessonReview']['entries'][0].update(
            verification='pass', evidence=['../../LESSON.md'])
        self.record_path.write_text(json.dumps(self.record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'verification pending'):
            self.begin()
        self.assertFalse((self.project / 'design/tasks/settings-review').exists())

    def test_begin_rejects_a_stale_canonical_lesson_index(self):
        source = self.project / 'design/LESSON.md'
        source.write_text(source.read_text() + '\nChanged canonical advice.\n')
        with self.assertRaisesRegex(ValueError, 'index is stale'):
            self.begin()
        self.assertFalse((self.project / 'design/tasks/settings-review').exists())

    def test_begin_never_overwrites_existing_task(self):
        self.begin()
        task_path = self.project / 'design/tasks/settings-review/task.json'
        original = task_path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            self.begin()
        self.assertEqual(task_path.read_bytes(), original)

    def test_evidence_is_wrapped_and_check_detects_payload_tampering(self):
        self.begin()
        payload_path = Path(self.temp.name) / 'payload.json'
        payload_path.write_text(json.dumps({'observation': 'synthetic fixture only', 'live': False}), encoding='utf-8')
        capture = self.project / 'design/tasks/settings-review/capture.txt'
        capture.write_text('synthetic fixture reference', encoding='utf-8')
        result = tasks.add_evidence(self.project, 'settings-review', 'snapshot',
                                    'Synthetic fixture readback; not live Figma evidence.', payload_path, ['capture.txt'])
        evidence_path = self.project / result['evidence']
        wrapper = json.loads(evidence_path.read_text(encoding='utf-8'))
        self.assertEqual(wrapper['kind'], 'task-evidence')
        self.assertEqual(wrapper['record']['taskId'], 'settings-review')
        self.assertEqual(tasks.check_task(self.project, 'settings-review')['evidenceRecords'], 1)
        wrapper['observation'] = 'altered'
        evidence_path.write_text(json.dumps(wrapper), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'payload hash mismatch'):
            tasks.check_task(self.project, 'settings-review')

    def test_evidence_rejects_references_outside_project(self):
        self.begin()
        payload_path = Path(self.temp.name) / 'payload.json'
        payload_path.write_text(json.dumps({'observed': 'fixture'}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'missing or escapes'):
            tasks.add_evidence(self.project, 'settings-review', 'audit', 'Fixture evidence', payload_path, ['../../outside.txt'])
        self.assertEqual(list((self.project / 'design/tasks/settings-review').glob('evidence-*.json')), [])

    def test_evidence_cannot_override_its_integrity_wrapper(self):
        self.begin()
        payload_path = Path(self.temp.name) / 'payload.json'
        payload_path.write_text(json.dumps({'record': {'taskId': 'unrelated'}}))
        with self.assertRaisesRegex(ValueError, 'wrapper contract fields'):
            tasks.add_evidence(self.project, 'settings-review', 'audit',
                               'Untrusted payload', payload_path, [])
        self.assertEqual(list((self.project / 'design/tasks/settings-review').glob('evidence-*.json')), [])

    def test_handoff_requires_integrity_checked_evidence_and_complete_delivery_mapping(self):
        self.begin()
        payload_path = Path(self.temp.name) / 'payload.json'
        payload_path.write_text(json.dumps({'observation': 'synthetic fixture only'}), encoding='utf-8')
        tasks.add_evidence(self.project, 'settings-review', 'audit', 'Synthetic evidence only.', payload_path, [])
        handoff_path = Path(self.temp.name) / 'handoff.json'
        handoff = {'frameLinks': ['https://figma.example.invalid/file/synthetic'],
                   'createdNodeIds': [], 'modifiedNodeIds': [], 'checks': [], 'remainingGaps': []}
        handoff_path.write_text(json.dumps(handoff), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Delivery requires checks'):
            tasks.update_handoff(self.project, 'settings-review', handoff_path, 'design_delivered')
        unchanged = json.loads((self.project / 'design/tasks/settings-review/task.json').read_text(encoding='utf-8'))
        self.assertEqual(unchanged['status'], 'in_progress')
        handoff['checks'] = [{'requirement': 'synthetic', 'evidence': ['evidence-0001.json']}]
        handoff['requirementStateMapping'] = [{'requirement': 'synthetic', 'state': 'default',
                                                'evidence': ['evidence-0001.json']}]
        handoff_path.write_text(json.dumps(handoff), encoding='utf-8')
        result = tasks.update_handoff(self.project, 'settings-review', handoff_path, 'design_delivered')
        self.assertEqual(result['taskStatus'], 'design_delivered')
        self.assertEqual(tasks.check_task(self.project, 'settings-review')['evidenceRecords'], 1)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is optional for the Plugin API helper regression test')
    def test_prototype_duplicate_ignores_native_serialization_defaults(self):
        helper = (ROOT / 'scripts/figma_prototype.js').read_text(encoding='utf-8')
        script = r"""
const {applyPrototypeGraph} = await import('data:text/javascript;base64,' +
  Buffer.from(__HELPER__).toString('base64'));
let writes = 0;
const node = {
  reactions: [{trigger:{type:'ON_CLICK'}, actions:[{type:'NODE', destinationId:'target',
    navigation:'NAVIGATE', transition:null, resetVideoPosition:false}]}],
  async setReactionsAsync(next) { writes++; this.reactions = next; }
};
const figma = {async getNodeByIdAsync(id) { return id === 'source' ? node : {}; }};
let rejected = false;
try {
  await applyPrototypeGraph(figma, {edges:[{from:'source',to:'target',
    navigation:'NAVIGATE',trigger:{type:'ON_CLICK'},transition:null}]}, true);
} catch (error) { rejected = /already exists/.test(String(error)); }
if (!rejected || writes !== 0 || node.reactions.length !== 1)
  throw new Error('Native-default duplicate changed the existing graph');
"""
        result = subprocess.run(
            ['node', '--input-type=module', '-e', script.replace('__HELPER__', json.dumps(helper))],
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is optional for the Plugin API helper regression test')
    def test_prototype_helper_rejects_timeout_and_transition_readback_mismatch(self):
        helper = (ROOT / 'scripts/figma_prototype.js').read_text(encoding='utf-8')
        script = r"""
const source = __HELPER__;
const {applyPrototypeGraph} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const original = [{trigger:{type:'ON_CLICK'}, actions:[{type:'BACK'}]}];
const graph = {edges:[{from:'source',to:'target',navigation:'NAVIGATE',
  trigger:{type:'AFTER_TIMEOUT',timeout:500},
  transition:{type:'DISSOLVE',duration:0.25,easing:{type:'EASE_OUT'}}}]};
for (const mismatch of ['timeout','transition']) {
  const node = {reactions:JSON.parse(JSON.stringify(original)), async setReactionsAsync(next) {
    this.reactions = JSON.parse(JSON.stringify(next));
    if (this.reactions.length > original.length) {
      const edge = this.reactions[this.reactions.length - 1];
      if (mismatch === 'timeout') edge.trigger.timeout = 501;
      else edge.actions[0].transition.duration = 0.5;
    }
  }};
  const figma = {async getNodeByIdAsync(id) {
    if (id === 'source') return node;
    if (id === 'target') return {reactions:[], async setReactionsAsync() {}};
    return null;
  }};
  let rejected = false;
  try { await applyPrototypeGraph(figma, graph, true); }
  catch (error) { rejected = /readback mismatch/.test(String(error)); }
  if (!rejected) throw new Error(mismatch + ' mismatch was not rejected');
  if (JSON.stringify(node.reactions) !== JSON.stringify(original)) throw new Error(mismatch + ' rollback lost original reactions');
}
"""
        script = script.replace('__HELPER__', json.dumps(helper))
        result = subprocess.run(['node', '--input-type=module', '-e', script],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
