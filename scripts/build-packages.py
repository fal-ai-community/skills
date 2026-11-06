#!/usr/bin/env python3
"""Build complete client bundles from canonical skill folders, without publishing."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = '''\n## Client execution adapter\n\nThis package uses the connected fal MCP tools for generation. CLI commands in\nthis guide and its references illustrate endpoint inputs and dependencies;\ntranslate them into MCP calls instead of requiring a CLI installation.\nUse recommend_model for current choices unless the user names an endpoint.\nWhen it supplies next_call and input_contract, use those directly. Otherwise\ninspect the endpoint schema and matching price units before execution.\nUse run_model for bounded work; submit_job, check_job and get_job_result for\nqueued work. Save the request ID immediately and poll that same request.\nNever assume a hosted sandbox, asset library or renderer exists. Verify local\ncapabilities before composition. If a required capability is absent, deliver\nthe reviewed components and report the incomplete stage. Preserve the user's\nprovider, model, scope, budget and approval boundaries.\n\nThe `genmedia` skill remains an optional terminal fallback only.\n'''


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def build(output, profile, source_ref=None, codex_app_id=None):
    output = Path(output).resolve()
    if output == ROOT or output.is_relative_to(ROOT / 'skills') or output in ROOT.parents:
        raise ValueError('Output must not overwrite repository sources')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Build output must be empty')
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'skills', output / 'skills', ignore=shutil.ignore_patterns(
        '__pycache__', 'node_modules', '.DS_Store'), symlinks=False)
    if profile != 'cli':
        for path in (output / 'skills').glob('*/SKILL.md'):
            parts = path.read_text(encoding='utf-8').split('---', 2)
            path.write_text('---' + parts[1] + '---\n' + ADAPTER + parts[2], encoding='utf-8', newline='\n')
    spec = importlib.util.spec_from_file_location('registry', ROOT / 'scripts/build-skills-index.py')
    registry = importlib.util.module_from_spec(spec); spec.loader.exec_module(registry)
    index = registry.build_index(output / 'skills')
    dump(output / 'skills/index.json', index)
    manifest = {'name': 'fal-ai', 'version': '0.1.0',
                'description': 'Produce images, videos, audio and game assets with fal and focused creative workflows.',
                'author': {'name': 'fal.ai', 'url': 'https://fal.ai'},
                'homepage': 'https://fal.ai', 'repository': 'https://github.com/fal-ai-community/skills',
                'license': 'MIT'}
    portable = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', **manifest}
    dump(output / 'plugin.json', portable)
    mcp = {'mcpServers': {'fal': {'type': 'http', 'url': 'https://mcp.fal.ai/mcp-relay'}}}
    if profile in {'claude', 'cursor', 'grok'}:
        dump(output / 'mcp.json', mcp)
        dump(output / '.mcp.json', mcp)
    if profile == 'claude':
        dump(output / '.claude-plugin/plugin.json', {**manifest, 'skills': './skills/', 'mcpServers': './.mcp.json'})
    elif profile in {'cursor', 'grok'}:
        dump(output / '.cursor-plugin/plugin.json', {**manifest, 'skills': './skills/', 'mcpServers': './mcp.json'})
        if profile == 'grok':
            dump(output / '.grok-plugin/plugin.json', manifest)
    elif profile == 'codex':
        overlay = {**manifest, 'skills': './skills/'}
        if codex_app_id:
            dump(output / '.app.json', {'apps': {'fal-ai': {'id': codex_app_id}}})
            overlay['apps'] = './.app.json'
        dump(output / '.codex-plugin/plugin.json', overlay)
    for name in ['LICENSE']:
        if (ROOT / name).exists(): shutil.copy2(ROOT / name, output / name)
    ref = source_ref or subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    readme = (f'# fal.ai {profile} skill bundle\n\n'
              f'Generated from fal-ai-community/skills at `{ref}`.\n\n'
              'This bundle includes complete skill folders and supporting assets. '
              'See `skills-source.lock.json` for the source pin.\n\n'
              f'[Installation and host limits](https://github.com/fal-ai-community/skills/blob/{ref}/docs/install.md)\n\n'
              'Check renderer dependencies before local composition. Generation is billed '
              'to the connected fal account. No release or marketplace listing is published '
              'by this build.\n')
    (output / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
    digest = hashlib.sha256(json.dumps(index, sort_keys=True).encode()).hexdigest()
    dump(output / 'skills-source.lock.json', {'repository': 'fal-ai-community/skills', 'commit': ref,
         'profile': profile, 'registry_sha256': digest,
         'note': 'Generated files: edit canonical repository, then rebuild. No releases are published.'})
    return index


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=['cli', 'claude', 'codex', 'cursor', 'grok'], required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-ref')
    p.add_argument('--codex-app-id', help='Optional connector registration owned by the package maintainer')
    a = p.parse_args(); index = build(a.output, a.profile, a.source_ref, a.codex_app_id)
    print(f'Built {a.profile}: {len(index["skills"])} complete skills at {a.output}')


if __name__ == '__main__': main()
