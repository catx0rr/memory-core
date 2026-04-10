#!/usr/bin/env python3
"""
memory-core: memory_state — count MEMORY.md metrics

Counts lines, sections, list entries, and section breakdown
in MEMORY.md for status reporting.

Usage:
    python3 memory_state.py
    python3 memory_state.py --memory-file ~/.openclaw/workspace/MEMORY.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MEMORY = os.path.expanduser('~/.openclaw/workspace/MEMORY.md')


def count_state(memory_path: str) -> dict:
    """Count MEMORY.md structure and content metrics."""
    now = datetime.now(tz=timezone.utc).isoformat()
    path = Path(memory_path)

    if not path.exists():
        return {
            'timestamp': now,
            'error': f'MEMORY.md not found: {memory_path}',
            'exists': False,
        }

    content = path.read_text(encoding='utf-8', errors='replace')
    lines = content.split('\n')

    # Count sections (## and ### headers)
    h2_sections = [l.strip() for l in lines if l.startswith('## ')]
    h3_sections = [l.strip() for l in lines if l.startswith('### ')]

    # Count list entries (lines starting with - or *)
    list_entries = [l for l in lines if re.match(r'^\s*[-*]\s+\S', l)]

    # Non-empty, non-header, non-list lines (prose)
    prose_lines = [l for l in lines
                   if l.strip()
                   and not l.startswith('#')
                   and not re.match(r'^\s*[-*]\s', l)
                   and not l.startswith('>')
                   and not l.startswith('```')]

    # Find last updated date if present
    updated_match = re.search(
        r'[Ll]ast updated[:\s]*(\d{4}-\d{2}-\d{2})', content
    )
    last_updated = updated_match.group(1) if updated_match else None

    # Section breakdown
    section_breakdown = {}
    current_section = '(top-level)'
    section_items = {current_section: 0}
    for line in lines:
        if line.startswith('## '):
            current_section = line.strip('# ').strip()
            section_items[current_section] = 0
        elif re.match(r'^\s*[-*]\s+\S', line):
            section_items[current_section] = section_items.get(current_section, 0) + 1

    # Remove empty sections
    section_breakdown = {k: v for k, v in section_items.items() if v > 0}

    return {
        'timestamp': now,
        'exists': True,
        'path': memory_path,
        'size_bytes': path.stat().st_size,
        'modified': datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).isoformat(),
        'total_lines': len(lines),
        'h2_sections': len(h2_sections),
        'h3_sections': len(h3_sections),
        'list_entries': len(list_entries),
        'prose_lines': len(prose_lines),
        'last_updated_date': last_updated,
        'section_breakdown': section_breakdown,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Memory-Core: Count MEMORY.md state'
    )
    parser.add_argument(
        '--memory-file', default=DEFAULT_MEMORY,
        help=f'Path to MEMORY.md (default: {DEFAULT_MEMORY})'
    )
    args = parser.parse_args()

    result = count_state(args.memory_file)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 1 if 'error' in result else 0


if __name__ == '__main__':
    sys.exit(main())
