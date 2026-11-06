#!/usr/bin/env python3
"""Create a synthetic offline test workspace, never overwrite an existing folder."""
import argparse
from pathlib import Path
import shutil
from kkdesign_core import build_lesson_index, save


def materialize(destination):
    repository = Path(__file__).resolve().parent.parent
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Destination already exists: ' + str(destination))
    shutil.copytree(repository / 'examples/minimal', destination)
    shutil.copytree(repository / 'schemas', destination / 'design/schemas')
    index = build_lesson_index(destination / 'design')
    save(destination / 'design/lessons-index.json', {'$schema': 'schemas/lesson-index.schema.json', **index})
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        print(materialize(args.output))
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')
