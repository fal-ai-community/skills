#!/usr/bin/env python3
"""Prepare local Registry, Gemini and OpenClaw bundles. Never install or publish."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def load_packages():
    spec = importlib.util.spec_from_file_location('canonical_packages', ROOT / 'scripts/build-packages.py')
    packages = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packages)
    return packages


def build(output, source_ref=None):
    """Export complete canonical skills once per client, with source/file hashes."""
    output = Path(output).resolve()
    if output == ROOT or output.is_relative_to(ROOT) or output in ROOT.parents:
        raise ValueError('Distribution output must be outside the source checkout')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('Distribution output must be absent or an empty directory')
    ref = source_ref or subprocess.check_output(
        ['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}', ref):
        raise ValueError('Source ref must be a full Git commit SHA')

    # Reuse the established package builder so references, scripts and assets
    # retain the same semantics. Nothing invokes a client, network or publisher.
    with tempfile.TemporaryDirectory(prefix='fal-distribution-') as tmp:
        staging = Path(tmp) / 'staging'
        load_packages().build(staging, 'claude', ref)
        prepared = Path(tmp) / 'prepared'
        shutil.copytree(ROOT / 'distribution', prepared)
        for client in ['gemini', 'openclaw']:
            destination = prepared / client
            shutil.copytree(staging / 'skills', destination / 'skills')
            shutil.copy2(ROOT / 'LICENSE', destination / 'LICENSE')
            shutil.copy2(staging / 'skills-source.lock.json', destination / 'skills-source.lock.json')
            lock = json.loads((destination / 'skills-source.lock.json').read_text(encoding='utf-8'))
            lock['profile'] = client
            (destination / 'skills-source.lock.json').write_text(
                json.dumps(lock, indent=2) + '\n', encoding='utf-8', newline='\n')
        hashes = {
            path.relative_to(prepared).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(prepared.rglob('*')) if path.is_file()
        }
        lock = {
            'repository': 'https://github.com/fal-ai-community/skills',
            'commit': ref,
            'files': hashes,
            'publication': 'not performed',
        }
        (prepared / 'distribution.lock.json').write_text(
            json.dumps(lock, indent=2) + '\n', encoding='utf-8', newline='\n')
        shutil.copytree(prepared, output, dirs_exist_ok=True)
    return lock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    lock = build(args.output)
    print(f'Prepared {len(lock["files"])} files at {args.output.resolve()}; nothing published')


if __name__ == '__main__':
    main()
