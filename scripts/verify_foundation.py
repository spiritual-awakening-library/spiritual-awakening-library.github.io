"""Phase 0.1: dependency-free structural validation for the public repository.

This deliberately does NOT claim book-text completeness, translation accuracy,
legal clearance, or app build success. Python 3.12+ on Windows and Linux.
"""
from __future__ import annotations

import csv
import io
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = [
    'book_id', 'entry_id', 'entry_kind', 'order', 'original_title',
    'printed_page', 'pdf_page', 'language', 'source_status',
    'translation_status', 'review_notes',
]
REQUIRED = [
    'docs/architecture/architecture-v1.1.md',
    'docs/editorial/source-inventory-protocol.md',
    'docs/editorial/translation-policy-v1.0.md',
    'docs/milestones/2026-11-02-phase0-foundation.md',
    'data/chapter-inventory-SEED-INCOMPLETE.csv',
]
FORBIDDEN_NAMES = {'.env', '.env.local', '.env.production', '.env.development',
                   '.env.test', '.npmrc', 'id_rsa', 'id_ed25519'}
FORBIDDEN_PARTS = {'node_modules', '.next', '.git', '__pycache__', '.zscripts', '.venv'}
SECRET_PATTERNS = [
    ('GitHub token', re.compile(r'gh[pousr]_[A-Za-z0-9_]{30,}')),
    ('GitHub fine-grained token', re.compile(r'github_pat_[A-Za-z0-9_]{30,}')),
    ('OpenAI key', re.compile(r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}')),
    ('Private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
]

def fail(message: str) -> None:
    raise ValueError(message)

def tracked_files() -> list[str]:
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, check=True, capture_output=True)
    return [x.decode('utf-8') for x in result.stdout.split(b'\0') if x]

def validate() -> None:
    paths = tracked_files()
    if len(paths) != len(set(paths)):
        fail('Duplicate tracked paths')
    for relative in REQUIRED:
        if relative not in paths:
            fail(f'Missing tracked foundation file: {relative}')
    for name in paths:
        normalized = PurePosixPath(name.replace('\\', '/'))
        if normalized.name in FORBIDDEN_NAMES or normalized.name.startswith('.env.'):
            fail(f'Forbidden tracked credential/config file: {name}')
        if set(normalized.parts) & FORBIDDEN_PARTS:
            fail(f'Forbidden tracked artifact directory: {name}')
        path = ROOT / name
        if not path.is_file():
            fail(f'Tracked path unavailable: {name}')
        if path.stat().st_size > 2 * 1024 * 1024:
            continue  # Binary or large approved files require separate review.
        try:
            body = path.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(body):
                fail(f'Possible {label} in {name}; review before publishing')

    csv_file = ROOT / 'data/chapter-inventory-SEED-INCOMPLETE.csv'
    text = csv_file.read_text(encoding='utf-8-sig')
    reader = csv.DictReader(io.StringIO(text), strict=True)
    if reader.fieldnames != EXPECTED_COLUMNS:
        fail(f'CSV columns differ from expected Phase 0 schema: {reader.fieldnames}')
    seen: set[tuple[str, str, str]] = set()
    count = 0
    for row in reader:
        count += 1
        if None in row or any(value is None for value in row.values()):
            fail(f'Malformed CSV row {count}')
        book, entry, language = (row[k].strip() for k in ('book_id', 'entry_id', 'language'))
        if book not in {'book-1', 'book-2'}:
            fail(f'Unknown book ID at row {count}')
        if not entry or not row['original_title'].strip():
            fail(f'Missing entry ID or title at row {count}')
        if language not in {'zh-TW', 'en'}:
            fail(f'Invalid language at row {count}')
        identity = (book, entry, language)
        if identity in seen:
            fail(f'Duplicate entry identity: {identity}')
        seen.add(identity)
        for column in ('order', 'pdf_page'):
            value = row[column].strip()
            if value and (not value.isdecimal() or int(value) < 1):
                fail(f'Invalid {column} at row {count}')
    if count == 0:
        fail('Inventory contains no rows')
    print(f'PASS: {len(paths)} tracked files checked; {count} seed entries structurally valid.')
    print('LIMITATION: Not a complete chapter inventory, translation review, or full security audit.')

if __name__ == '__main__':
    try:
        validate()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
