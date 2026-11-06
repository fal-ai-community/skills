#!/usr/bin/env python3
"""Build the portable, hash-verified skills registry; --check detects drift."""
import hashlib
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / 'skills'
INDEX_FILE = SKILLS_DIR / 'index.json'
IGNORED = {'__pycache__', 'node_modules', '.git', '.DS_Store'}


def parse_frontmatter(source):
    parts = source.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('Missing YAML frontmatter')
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError('Frontmatter must be a mapping')
    return data


def walk_files(folder):
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                  if p.is_file() and not any(v in IGNORED for v in p.relative_to(folder).parts))


def build_index(skills_dir=SKILLS_DIR):
    entries = []
    for folder in sorted(skills_dir.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        data = parse_frontmatter((folder / 'SKILL.md').read_text(encoding='utf-8'))
        name, desc = data.get('name'), data.get('description')
        if name != folder.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name or '') or len(name) > 64:
            raise ValueError(f'{folder}: invalid or mismatched name')
        if not isinstance(desc, str) or not 1 <= len(desc) <= 1024:
            raise ValueError(f'{folder}: description must be 1-1024 characters')
        files = []
        for rel in walk_files(folder):
            path = folder / rel
            if not path.resolve().is_relative_to(skills_dir.resolve()):
                raise ValueError(f'External symlink: {path}')
            content = path.read_bytes()
            files.append({'path': rel, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)})
        entries.append({'name': name, 'description': desc, 'files': files})
    return {'version': 1, 'skills': entries}


def main():
    serialized = json.dumps(build_index(), indent=2) + '\n'
    if '--check' in sys.argv:
        if not INDEX_FILE.exists() or INDEX_FILE.read_text(encoding='utf-8') != serialized:
            raise SystemExit('skills/index.json is stale; run python3 scripts/build-skills-index.py')
        print('skills/index.json is up to date')
    else:
        INDEX_FILE.write_text(serialized, encoding='utf-8', newline='\n')
        print(f'Indexed {len(json.loads(serialized)["skills"])} skills')


if __name__ == '__main__':
    main()
