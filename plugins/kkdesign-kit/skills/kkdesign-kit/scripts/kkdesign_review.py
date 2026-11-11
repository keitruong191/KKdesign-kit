#!/usr/bin/env python3
"""Read structured review records and report objective discrepancies only."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def _finding(location, severity, impact, evidence, recommendation, verification, verification_status):
    return {
        'location': location,
        'severity': severity,
        'userImpact': impact,
        'evidence': evidence,
        'recommendation': recommendation,
        'verificationStatus': verification_status,
        'verification': verification,
    }


def analyze(document):
    """Read a structured evidence record and report objective discrepancies only."""
    if not isinstance(document, dict) or document.get('kind') != 'design-review-record':
        raise ValueError('Input must be a design-review-record JSON object')
    if document.get('schemaVersion') != '1.0.0':
        raise ValueError('Unsupported review record schemaVersion')
    scope = document.get('scope')
    records = document.get('records')
    if not isinstance(scope, dict) or not isinstance(records, dict):
        raise ValueError('Review record requires scope and records objects')
    categories = {'references', 'instances', 'textStyles', 'contentBounds', 'contrast'}
    if set(records) - categories:
        raise ValueError('Review record contains an unsupported records category')
    for category, rows in records.items():
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError('Review record category ' + category + ' must be an array of objects')
    verification_status = 'evidence-only' if scope.get('evidenceType') == 'synthetic-record' else 'not-verified'
    findings = []
    unassessed = []
    for item in records.get('references', []):
        intended = item.get('intendedPlatform')
        reference_platform = item.get('referencePlatform')
        if (not isinstance(intended, str) or not intended
                or not isinstance(reference_platform, str) or not reference_platform):
            unassessed.append({'location': item.get('location', 'unknown'),
                               'reason': 'Reference platform comparison requires non-empty intendedPlatform and referencePlatform strings.'})
            continue
        if intended != reference_platform:
            findings.append(_finding(
                item.get('location', 'unknown'), 'P2',
                'A reference from another platform can lead to inappropriate navigation, controls, or layout for the intended platform.',
                {'kind': 'recorded-reference-metadata', 'referenceId': item.get('referenceId'),
                 'intendedPlatform': intended, 'referencePlatform': reference_platform,
                 'detail': item.get('evidence')},
                'Use an approved reference for the intended platform or record an explicit rationale for the divergence.',
                'Review the approved ' + intended + ' reference and compare the actual target on ' + intended +
                '; confirm platform-specific behavior in the running app.',
                verification_status
            ))

    for item in records.get('instances', []):
        overrides = item.get('overrides', [])
        if overrides:
            findings.append(_finding(
                item.get('location', 'unknown'), 'P2',
                'A local component override can drift from canonical design-system styling and make later updates inconsistent.',
                {'kind': 'recorded-instance-overrides', 'component': item.get('component'),
                 'variant': item.get('variant'), 'overrides': overrides, 'detail': item.get('evidence')},
                'Confirm each override is intentional; use the canonical component property or variant when it is not.',
                'Inspect the target instance and canonical component in the design source; verify intended appearance and binding after any correction.',
                verification_status
            ))

    for item in records.get('textStyles', []):
        if item.get('expectedBinding') and item.get('actualBinding') != item.get('expectedBinding'):
            findings.append(_finding(
                item.get('location', 'unknown'), 'P2',
                'Unbound or mismatched typography may become inconsistent and fail to track approved type-system changes.',
                {'kind': 'recorded-text-style-binding', 'expectedBinding': item.get('expectedBinding'),
                 'actualBinding': item.get('actualBinding'), 'detail': item.get('evidence')},
                'Restore the approved text-style binding if the detachment was not intentional.',
                'Inspect the actual layer binding against the canonical text style; verify the style remains attached to the intended text layer.',
                verification_status
            ))

    for item in records.get('contentBounds', []):
        content_height = item.get('contentHeight')
        available_height = item.get('availableHeight')
        if (isinstance(content_height, (int, float)) and not isinstance(content_height, bool)
                and isinstance(available_height, (int, float)) and not isinstance(available_height, bool)
                and content_height > available_height):
            findings.append(_finding(
                item.get('location', 'unknown'), 'P1',
                'Content exceeds the recorded available region; users may lose access to text or controls in this long-content case.',
                {'kind': 'recorded-layout-measurements', 'contentHeight': content_height,
                 'availableHeight': available_height, 'contentCase': item.get('contentCase'),
                 'detail': item.get('evidence')},
                'Provide sufficient layout growth or an intentional scroll path so the complete content and related actions remain reachable.',
                'Render the long/localized content on the intended platform and verify there is no clipping and all content and actions are reachable.',
                verification_status
            ))

    for item in records.get('contrast', []):
        ratio = item.get('ratio')
        required = item.get('requiredRatio')
        if (isinstance(ratio, (int, float)) and not isinstance(ratio, bool)
                and isinstance(required, (int, float)) and not isinstance(required, bool)
                and ratio < required):
            findings.append(_finding(
                item.get('location', 'unknown'), 'P1',
                'The recorded contrast ratio is below the supplied requirement, which can make this text difficult to perceive.',
                {'kind': 'recorded-contrast-measurement', 'foreground': item.get('foreground'),
                 'background': item.get('background'), 'ratio': ratio, 'requiredRatio': required,
                 'textClass': item.get('textClass'), 'mode': item.get('mode'), 'detail': item.get('evidence')},
                'Choose colors that meet the applicable contrast requirement while preserving the intended visual hierarchy.',
                'Measure the actual foreground/background colors in the rendered target for every applicable mode and verify against the correct criterion.',
                verification_status
            ))

    return {
        'schemaVersion': '1.0.0',
        'kind': 'design-review-evidence-readback',
        'assessment': 'evidence-only',
        'approval': 'not-assessed',
        'scope': scope,
        'findings': findings,
        'unassessed': unassessed,
        'limitations': [
            'This helper reports only discrepancies explicitly represented in the input records; it does not perform visual or UX review.',
            'A record or fixture is not proof of a live Figma canvas, source implementation, native rendering, runtime behavior, accessibility, performance, or human approval.',
            'Finding absence means only that no supported recorded discrepancy was found; it is not a pass.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='path to a structured design-review-record JSON file')
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.input).read_text(encoding='utf-8'))
        result = analyze(document)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
