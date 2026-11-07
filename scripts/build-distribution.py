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
TEMPLATES = (
    'distribution/registry/server.json',
    'distribution/gemini/gemini-extension.json',
    'distribution/gemini/GEMINI.md',
    'distribution/openclaw/mcp.config.json',
    'distribution/openclaw/.claude-plugin/plugin.json',
    'distribution/openclaw/.mcp.json',
    'distribution/openclaw/package.json',
    'distribution/openclaw/README.md',
)
REQUIRED_INPUTS = (*TEMPLATES, 'LICENSE', 'scripts/build-packages.py',
                   'scripts/build-skills-index.py')


def git(*args):
    return subprocess.check_output(
        ['git', '--no-replace-objects', '-C', str(ROOT), *args], stderr=subprocess.PIPE)


def resolve_commit(source_ref):
    if source_ref is not None and not re.fullmatch(r'[0-9a-f]{40}', source_ref):
        raise ValueError('Source ref must be a full Git commit SHA')
    ref = source_ref or git('rev-parse', 'HEAD').decode().strip()
    try:
        object_type = git('cat-file', '-t', ref).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError('Source commit does not exist locally') from exc
    if object_type != 'commit':
        raise ValueError('Source ref must identify a commit object')
    return ref


def snapshot_inputs(ref, destination):
    """Materialize allowlisted Git blobs, never files from the working tree."""
    records = git('ls-tree', '-r', '-z', ref, '--', *REQUIRED_INPUTS, 'skills/').split(b'\0')
    entries = []
    for record in filter(None, records):
        metadata, raw_path = record.split(b'\t', 1)
        mode, object_type, oid = metadata.decode('ascii').split()
        relative = raw_path.decode('utf-8')
        if mode not in {'100644', '100755'} or object_type != 'blob':
            raise ValueError(f'Export input must be a regular Git file: {relative}')
        parts = relative.split('/')
        if any(part in {'', '.', '..'} for part in parts) or '\\' in relative or ':' in relative:
            raise ValueError(f'Unsafe export path: {relative}')
        entries.append((relative, mode, oid))
    names = {relative for relative, _, _ in entries}
    missing = set(REQUIRED_INPUTS) - names
    if missing or not any(name.startswith('skills/') for name in names):
        raise ValueError(f'Source commit lacks required export inputs: {sorted(missing)}')
    # Validate every mode and path before reading any blob or writing a file.
    for relative, mode, oid in entries:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git('cat-file', 'blob', oid))
        path.chmod(0o755 if mode == '100755' else 0o644)


def load_packages(source):
    spec = importlib.util.spec_from_file_location('canonical_packages', source / 'scripts/build-packages.py')
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
    ref = resolve_commit(source_ref)

    # Reuse the established package builder so references, scripts and assets
    # retain the same semantics. Nothing invokes a client, network or publisher.
    with tempfile.TemporaryDirectory(prefix='fal-distribution-') as tmp:
        source = Path(tmp) / 'source'
        snapshot_inputs(ref, source)
        staging = Path(tmp) / 'staging'
        load_packages(source).build(staging, 'claude', ref)
        prepared = Path(tmp) / 'prepared'
        shutil.copytree(source / 'distribution', prepared)
        for client in ['gemini', 'openclaw']:
            destination = prepared / client
            shutil.copytree(staging / 'skills', destination / 'skills')
            shutil.copy2(source / 'LICENSE', destination / 'LICENSE')
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
    parser.add_argument('--source-ref', help='Full local commit SHA (defaults to HEAD)')
    args = parser.parse_args()
    lock = build(args.output, args.source_ref)
    print(f'Prepared {len(lock["files"])} files at {args.output.resolve()}; nothing published')


if __name__ == '__main__':
    main()
