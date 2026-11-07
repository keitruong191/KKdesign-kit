import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kkdesign_review as review


class ReviewReadbackTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / 'examples/review/flawed-design.json').read_text(encoding='utf-8'))

    def test_flawed_fixture_reports_each_seeded_objective_discrepancy(self):
        result = review.analyze(self.fixture)
        self.assertEqual(result['assessment'], 'evidence-only')
        self.assertEqual(result['approval'], 'not-assessed')
        self.assertEqual(
            [finding['evidence']['kind'] for finding in result['findings']],
            ['recorded-reference-metadata', 'recorded-instance-overrides',
             'recorded-text-style-binding', 'recorded-layout-measurements',
             'recorded-contrast-measurement'])
        self.assertEqual(
            [finding['location'] for finding in result['findings']],
            ['Settings/Notifications/Reference', 'Settings/Notifications/SaveButton',
             'Settings/Notifications/Heading', 'Settings/Notifications/PreferenceDescription',
             'Settings/Notifications/DisabledHint'])

    def test_empty_supported_records_are_not_a_pass(self):
        empty = {'schemaVersion': '1.0.0', 'kind': 'design-review-record',
                 'scope': {}, 'records': {}}
        result = review.analyze(empty)
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['assessment'], 'evidence-only')
        self.assertEqual(result['approval'], 'not-assessed')

    def test_missing_platform_metadata_is_unassessed_not_a_mismatch(self):
        record = {'schemaVersion': '1.0.0', 'kind': 'design-review-record', 'scope': {},
                  'records': {'references': [{'location': 'unknown-platform'}]}}
        result = review.analyze(record)
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['unassessed'][0]['location'], 'unknown-platform')

    def test_rejects_malformed_category_rows(self):
        record = {'schemaVersion': '1.0.0', 'kind': 'design-review-record', 'scope': {},
                  'records': {'references': ['not-object']}}
        with self.assertRaisesRegex(ValueError, 'array of objects'):
            review.analyze(record)

    def test_rejects_non_review_input(self):
        with self.assertRaisesRegex(ValueError, 'design-review-record'):
            review.analyze({'kind': 'task-evidence', 'schemaVersion': '1.0.0'})

    def test_layout_numeric_checks_ignore_booleans(self):
        record = {'schemaVersion': '1.0.0', 'kind': 'design-review-record',
                  'scope': {}, 'records': {'contentBounds': [
                      {'location': 'boolean-measurement', 'contentHeight': True, 'availableHeight': 0}]}}
        self.assertEqual(review.analyze(record)['findings'], [])


if __name__ == '__main__':
    unittest.main()
