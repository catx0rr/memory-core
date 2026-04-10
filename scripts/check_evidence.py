#!/usr/bin/env python3
"""
memory-core: check_evidence — scan built-in dreaming evidence surfaces

Checks all locations where memory-core dreaming leaves evidence:
  - DREAMS.md / dreams.md (human-readable dream reports)
  - memory/.dreams/ (machine state, short-term recall tracking)
  - memory/dreaming/<phase>/ (optional phase reports)
  - MEMORY.md (recent promotions in tail)

Returns structured JSON for the status prompt to consume.

Usage:
    python3 check_evidence.py
    python3 check_evidence.py --workspace ~/.openclaw/workspace
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


DEFAULT_WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
PROMOTION_LOOKBACK_HOURS = 26  # slightly more than 24h to catch 3 AM runs


def check_dreams_md(workspace: Path) -> dict:
    """Check DREAMS.md or dreams.md for dream reports."""
    now = datetime.now(tz=timezone.utc)

    for name in ['DREAMS.md', 'dreams.md']:
        path = workspace / name
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='replace')
            lines = content.strip().split('\n')
            line_count = len(lines)

            # Count entries (headers starting with ## or ###)
            entries = [l for l in lines if l.startswith('## ')]
            entry_count = len(entries)

            # Find most recent timestamp-like pattern
            timestamps = re.findall(
                r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', content
            )
            latest = timestamps[-1] if timestamps else None

            # Find most recent date pattern
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', content)
            latest_date = dates[-1] if dates else None

            # Recency: was this file modified within the lookback window?
            mtime = datetime.fromtimestamp(
                path.stat().st_mtime, tz=timezone.utc
            )
            hours_since = (now - mtime).total_seconds() / 3600
            recent = hours_since <= PROMOTION_LOOKBACK_HOURS

            return {
                'found': True,
                'recent': recent,
                'filename': name,
                'lines': line_count,
                'entries': entry_count,
                'latest_timestamp': latest,
                'latest_date': latest_date,
                'size_bytes': path.stat().st_size,
                'modified': mtime.isoformat(),
                'hours_since_modified': round(hours_since, 1),
            }

    return {'found': False, 'recent': False, 'filename': None}


def check_dreams_dir(workspace: Path) -> dict:
    """Check memory/.dreams/ directory for tracking files."""
    now = datetime.now(tz=timezone.utc)
    dreams_dir = workspace / 'memory' / '.dreams'

    if not dreams_dir.exists():
        return {'found': False, 'recent': False, 'file_count': 0, 'files': []}

    files = sorted(dreams_dir.iterdir())
    file_info = []
    most_recent_mtime = None
    for f in files:
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if most_recent_mtime is None or mtime > most_recent_mtime:
                most_recent_mtime = mtime
            file_info.append({
                'name': f.name,
                'size_bytes': f.stat().st_size,
                'modified': mtime.isoformat(),
            })

    # Recency: was any file in .dreams/ modified within the lookback window?
    recent = False
    hours_since = None
    if most_recent_mtime:
        hours_since = (now - most_recent_mtime).total_seconds() / 3600
        recent = hours_since <= PROMOTION_LOOKBACK_HOURS

    # Check for short-term-recall.json specifically
    recall_file = dreams_dir / 'short-term-recall.json'
    recall_info = None
    if recall_file.exists():
        try:
            with open(recall_file, 'r') as rf:
                recall_data = json.loads(rf.read())
            candidates = recall_data if isinstance(recall_data, list) else \
                recall_data.get('candidates', recall_data.get('entries', []))
            recall_info = {
                'exists': True,
                'candidate_count': len(candidates),
                'size_bytes': recall_file.stat().st_size,
            }
        except (json.JSONDecodeError, IOError):
            recall_info = {'exists': True, 'error': 'could not parse'}

    return {
        'found': True,
        'recent': recent,
        'hours_since_most_recent': round(hours_since, 1) if hours_since is not None else None,
        'file_count': len(file_info),
        'files': file_info,
        'short_term_recall': recall_info,
    }


def check_phase_reports(workspace: Path) -> dict:
    """Check memory/dreaming/<phase>/ for optional phase reports."""
    now = datetime.now(tz=timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    dreaming_dir = workspace / 'memory' / 'dreaming'

    if not dreaming_dir.exists():
        return {'found': False, 'recent': False, 'phases': {}}

    phases = {}
    any_recent = False
    for phase_name in ['light', 'rem', 'deep']:
        phase_dir = dreaming_dir / phase_name
        if phase_dir.exists() and phase_dir.is_dir():
            reports = sorted(phase_dir.glob('*.md'))
            latest_name = reports[-1].name if reports else None
            # Check if latest report is from today or yesterday
            recent = False
            if latest_name:
                recent = today_str in latest_name or yesterday_str in latest_name
                if recent:
                    any_recent = True
            phases[phase_name] = {
                'report_count': len(reports),
                'latest': latest_name,
                'recent': recent,
            }

    return {
        'found': bool(phases),
        'recent': any_recent,
        'phases': phases,
    }


def check_memory_md_promotions(workspace: Path) -> dict:
    """Check tail of MEMORY.md for recent promotions."""
    memory_file = workspace / 'MEMORY.md'

    if not memory_file.exists():
        return {'found': False, 'error': 'MEMORY.md not found'}

    content = memory_file.read_text(encoding='utf-8', errors='replace')
    lines = content.strip().split('\n')

    # Check file modification time
    mtime = datetime.fromtimestamp(
        memory_file.stat().st_mtime, tz=timezone.utc
    )
    now = datetime.now(tz=timezone.utc)
    hours_since_modified = (now - mtime).total_seconds() / 3600

    # Look for promotion markers in last 50 lines
    tail = lines[-50:] if len(lines) > 50 else lines
    tail_text = '\n'.join(tail)

    promotion_patterns = [
        r'promoted',
        r'dream',
        r'consolidated',
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}',
    ]

    promotion_evidence = []
    for pattern in promotion_patterns:
        matches = re.findall(pattern, tail_text, re.IGNORECASE)
        if matches:
            promotion_evidence.append({
                'pattern': pattern,
                'count': len(matches),
            })

    # Check if modified within lookback window
    recently_modified = hours_since_modified <= PROMOTION_LOOKBACK_HOURS

    return {
        'found': True,
        'total_lines': len(lines),
        'size_bytes': memory_file.stat().st_size,
        'last_modified': mtime.isoformat(),
        'hours_since_modified': round(hours_since_modified, 1),
        'recently_modified': recently_modified,
        'promotion_evidence': promotion_evidence,
        'evidence_in_tail': bool(promotion_evidence),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Memory-Core: Check dreaming evidence surfaces'
    )
    parser.add_argument(
        '--workspace', default=DEFAULT_WORKSPACE,
        help=f'Workspace path (default: {DEFAULT_WORKSPACE})'
    )
    args = parser.parse_args()

    ws = Path(args.workspace)
    now = datetime.now(tz=timezone.utc).isoformat()

    if not ws.exists():
        print(json.dumps({
            'ok': False,
            'error': f'Workspace not found: {args.workspace}',
            'timestamp': now,
        }))
        return 1

    result = {
        'timestamp': now,
        'workspace': args.workspace,
        'dreams_md': check_dreams_md(ws),
        'dreams_dir': check_dreams_dir(ws),
        'phase_reports': check_phase_reports(ws),
        'memory_md': check_memory_md_promotions(ws),
    }

    # Summary judgment — requires RECENT evidence, not mere existence
    has_recent_evidence = (
        result['dreams_md'].get('recent', False)
        or result['dreams_dir'].get('recent', False)
        or result['phase_reports'].get('recent', False)
        or (result['memory_md'].get('recently_modified', False)
            and result['memory_md'].get('evidence_in_tail', False))
    )
    result['sweep_appears_active'] = has_recent_evidence
    result['ok'] = True

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
