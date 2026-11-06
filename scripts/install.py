#!/usr/bin/env python3
"""Install complete skill folders locally; never overwrite existing skills."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def install(destination, names=None):
    destination = Path(destination).expanduser().resolve()
    index = json.loads((ROOT / 'skills/index.json').read_text(encoding='utf-8'))
    entries = index['skills']
    if names:
        unknown = set(names) - {s['name'] for s in entries}
        if unknown: raise ValueError('Unknown skills: ' + ', '.join(sorted(unknown)))
        entries = [s for s in entries if s['name'] in names]
    if any((destination / s['name']).exists() or (destination / s['name']).is_symlink() for s in entries):
        raise ValueError('A selected skill already exists. Choose an empty destination; existing skills were preserved.')
    # Verify every selected byte before writing anything to the destination.
    for s in entries:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', s['name']):
            raise ValueError('Unsafe skill name')
        folder = ROOT / 'skills' / s['name']
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()
                  and not any(v in {'__pycache__', 'node_modules', '.DS_Store'} for v in p.relative_to(folder).parts)}
        if actual != {f['path'] for f in s['files']}:
            raise ValueError('Unindexed or missing skill file')
        for f in s['files']:
            rel = Path(f['path'])
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('Unsafe registry path')
            src = ROOT / 'skills' / s['name'] / rel
            if not src.resolve().is_relative_to((ROOT / 'skills').resolve()):
                raise ValueError('External source symlink')
            data = src.read_bytes()
            if len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != f['sha256']:
                raise ValueError(f'Integrity mismatch: {src}')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fal-install-', dir=destination) as scratch:
        for s in entries:
            shutil.copytree(ROOT / 'skills' / s['name'], Path(scratch) / s['name'],
                            ignore=shutil.ignore_patterns('__pycache__', 'node_modules', '.DS_Store'))
        for s in entries:
            target = destination / s['name']
            if target.exists() or target.is_symlink(): raise ValueError(f'Concurrent install at {target}')
            (Path(scratch) / s['name']).rename(target)
    return [s['name'] for s in entries]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--agent', choices=['codex', 'claude', 'cursor'], required=True)
    p.add_argument('--destination', type=Path, help='Override project skill destination (also useful for validation)')
    p.add_argument('--skill', action='append', help='Install selected skills; default installs the complete bundle')
    a = p.parse_args()
    dest = a.destination or Path({'codex': '.agents/skills', 'claude': '.claude/skills', 'cursor': '.cursor/skills'}[a.agent])
    try:
        result = install(dest, a.skill)
        print(f'Installed {len(result)} skills in {dest}. Restart the agent to refresh discovery.')
    except (ValueError, OSError) as error: p.exit(1, str(error) + '\n')


if __name__ == '__main__': main()
