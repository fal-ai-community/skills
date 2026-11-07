"""Validate review-only distribution contracts and complete generated assets."""

import hashlib
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import subprocess
from unittest.mock import patch
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mcp_distribution', ROOT / 'scripts/build-distribution.py')
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)
SOURCE_REF = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()


class MCPDistribution(unittest.TestCase):
    def fixture_repo(self, directory):
        """Reuse real commit objects without creating commits or remote clones."""
        fixture = directory / 'source'
        subprocess.run(['git', 'init', '--quiet', '--initial-branch=main', str(fixture)], check=True)
        objects = Path(subprocess.check_output(
            ['git', '-C', str(ROOT), 'rev-parse', '--git-path', 'objects'], text=True).strip())
        if not objects.is_absolute():
            objects = ROOT / objects
        (fixture / '.git/objects/info/alternates').write_text(
            objects.resolve().as_posix() + '\n', encoding='utf-8', newline='\n')
        subprocess.run(['git', '-C', str(fixture), 'update-ref', 'refs/heads/main', SOURCE_REF], check=True)
        return fixture

    def replace_tree_entry(self, fixture, path, mode, object_type, oid):
        def git(*args, data=None):
            return subprocess.check_output(['git', '-C', str(fixture), *args], input=data)

        def replace(tree, parts):
            entries = {}
            for record in filter(None, git('ls-tree', '-z', tree).split(b'\0')):
                metadata, name = record.split(b'\t', 1)
                entries[name.decode()] = metadata
            name = parts[0]
            if len(parts) == 1:
                entries[name] = f'{mode} {object_type} {oid}'.encode()
            else:
                subtree = entries[name].decode().split()[2]
                replacement = replace(subtree, parts[1:])
                entries[name] = f'040000 tree {replacement}'.encode()
            records = [metadata + b'\t' + name.encode() + b'\0'
                       for name, metadata in entries.items()]
            return git('mktree', '-z', data=b''.join(records)).decode().strip()

        return replace(SOURCE_REF, path.split('/'))

    def test_registry_against_official_pinned_schema(self):
        schema = json.loads((ROOT / 'tests/fixtures/mcp-registry-server.schema.json').read_text())
        server = json.loads((ROOT / 'distribution/registry/server.json').read_text())
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(server)
        self.assertEqual(server['$schema'], schema['$id'])
        self.assertEqual(server['remotes'], [
            {'type': 'streamable-http', 'url': 'https://mcp.fal.ai/mcp-relay'}])
        self.assertNotIn('packages', server)
        self.assertNotIn('repository', server)

    def test_complete_exports_are_reproducible_and_hash_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / 'first', Path(tmp) / 'second'
            lock = distribution.build(first, SOURCE_REF, gemini_bundle="full")
            self.assertEqual(lock, distribution.build(second, SOURCE_REF, gemini_bundle="full"))
            for relative, digest in lock['files'].items():
                self.assertEqual(hashlib.sha256((first / relative).read_bytes()).hexdigest(), digest)
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())
            for client in ['gemini', 'openclaw']:
                source_files = [p for p in (ROOT / 'skills').rglob('*') if p.is_file()
                                and not any(x in {'__pycache__', '.DS_Store', 'node_modules'} for x in p.parts)]
                for source in source_files:
                    copied = first / client / source.relative_to(ROOT)
                    self.assertTrue(copied.is_file(), str(copied))
                    if source.name not in {'SKILL.md', 'index.json'}:
                        self.assertEqual(copied.read_bytes(), source.read_bytes())
                index = json.loads((first / client / 'skills/index.json').read_text())
                skill_lock = json.loads((first / client / 'skills-source.lock.json').read_text())
                self.assertEqual(skill_lock['commit'], SOURCE_REF)
                self.assertEqual(skill_lock['profile'], client)
                self.assertEqual(skill_lock['registry_sha256'],
                                 hashlib.sha256(json.dumps(index, sort_keys=True).encode()).hexdigest())
                self.assertFalse(any(p.is_symlink() for p in (first / client).rglob('*')))

    def test_gemini_defaults_to_hybrid_without_optional_runtimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            distribution.build(output, SOURCE_REF)
            gemini = output / 'gemini'
            expected = {'fal-media', 'product-ad-campaign', 'game-asset-production',
                        'storyboard-to-short-film', 'ecommerce-product-photography',
                        'localize-and-repurpose'}
            self.assertEqual({p.parent.name for p in (gemini / 'skills').glob('*/SKILL.md')}, expected)
            self.assertEqual({p.name for p in (gemini / 'skills').rglob('*') if p.is_file()},
                             {'SKILL.md', 'index.json'})
            lock = json.loads((gemini / 'skills-source.lock.json').read_text())
            self.assertEqual(lock['bundle'], 'hybrid')
            self.assertEqual(set(lock['entrypoints']), expected)
            self.assertEqual(lock['profile'], 'gemini')
            # The complete library remains available in the OpenClaw export.
            self.assertTrue((output / 'openclaw/skills/fal-redesign/runtime/package.json').is_file())

    def test_invalid_gemini_bundle_fails_before_output_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'unused'
            with self.assertRaises(ValueError):
                distribution.build(output, SOURCE_REF, gemini_bundle='unknown')
            self.assertFalse(output.exists())

    def test_gemini_uses_remote_http_without_install_hooks_or_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            distribution.build(output, SOURCE_REF)
            manifest = json.loads((output / 'gemini/gemini-extension.json').read_text())
            self.assertEqual(manifest['mcpServers'], {'fal': {'httpUrl': 'https://mcp.fal.ai/mcp-relay'}})
            self.assertTrue((output / 'gemini' / manifest['contextFileName']).is_file())
            self.assertNotIn('settings', manifest)
            self.assertFalse((output / 'gemini/hooks').exists())
            self.assertFalse((output / 'gemini/policies').exists())
            self.assertFalse((ROOT / 'gemini-extension.json').exists())

    def test_openclaw_fragment_has_no_credentials_or_approval_overrides(self):
        config = json.loads((ROOT / 'distribution/openclaw/mcp.config.json').read_text())
        self.assertEqual(config, {'mcp': {'servers': {'fal': {
            'url': 'https://mcp.fal.ai/mcp-relay', 'transport': 'streamable-http',
            'auth': 'oauth', 'enabled': True}}}})

    def test_openclaw_bundle_keeps_companions_and_local_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            distribution.build(output, SOURCE_REF)
            bundle = output / 'openclaw'
            canonical = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
            installed = {p.parent.name for p in (bundle / 'skills').glob('*/SKILL.md')}
            self.assertEqual(installed, canonical)
            outcomes = {'product-ad-campaign', 'game-asset-production',
                        'storyboard-to-short-film', 'ecommerce-product-photography',
                        'localize-and-repurpose'}
            for name in outcomes:
                entry = bundle / 'skills' / name / 'SKILL.md'
                text = entry.read_text()
                companions = set(re.findall(r'`([a-z][a-z0-9-]*)`', text)) & canonical
                self.assertTrue({'fal-media', 'genmedia'} <= companions)
                for companion in companions:
                    self.assertTrue((bundle / 'skills' / companion / 'SKILL.md').is_file())
                for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                    if '://' in target or target.startswith('#'):
                        continue
                    linked = (entry.parent / target.split('#', 1)[0]).resolve()
                    self.assertTrue(linked.is_relative_to(bundle.resolve()))
                    self.assertTrue(linked.exists(), target)

    def test_openclaw_bundle_is_declarative_and_keeps_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            distribution.build(output, SOURCE_REF)
            bundle = output / 'openclaw'
            package = json.loads((bundle / 'package.json').read_text())
            self.assertEqual(package['license'], 'MIT')
            self.assertNotIn('scripts', package)
            self.assertNotIn('dependencies', package)
            self.assertNotIn('openclaw', package)
            self.assertEqual((bundle / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())
            manifest = json.loads((bundle / '.claude-plugin/plugin.json').read_text())
            self.assertTrue((bundle / manifest['skills']).is_dir())
            mcp = json.loads((bundle / manifest['mcpServers']).read_text())
            self.assertEqual(mcp['mcpServers']['fal'], {
                'type': 'http', 'transport': 'streamable-http',
                'url': 'https://mcp.fal.ai/mcp-relay', 'auth': 'oauth'})
            self.assertFalse((bundle / 'hooks').exists())

    def test_outputs_cannot_overwrite_checkout_or_existing_files(self):
        for output in [ROOT, ROOT / 'skills', ROOT / 'scripts', ROOT.parent]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                distribution.build(output, SOURCE_REF)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'existing'; output.mkdir()
            (output / 'keep').write_text('keep')
            with self.assertRaises(ValueError): distribution.build(output, SOURCE_REF)
            self.assertEqual((output / 'keep').read_text(), 'keep')
            self.assertEqual(list(output.iterdir()), [output / 'keep'])

    def test_invalid_source_ref_fails_before_output_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'unused'
            with self.assertRaises(ValueError): distribution.build(output, '../../main')
            self.assertFalse(output.exists())

    def test_local_changes_and_ignored_files_do_not_enter_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fixture = self.fixture_repo(directory)
            manifest = fixture / 'distribution/gemini/gemini-extension.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"name": "LOCAL_CHANGE_NOT_COMMITTED"}')
            (fixture / '.gitignore').write_text('.env\n')
            secret = fixture / 'distribution/.env'
            secret.write_text('REVIEW_CANARY_NOT_A_SECRET')
            subprocess.run(['git', '-C', str(fixture), 'check-ignore', str(secret)], check=True,
                           stdout=subprocess.DEVNULL)
            (fixture / 'distribution/untracked.txt').write_text('LOCAL_UNTRACKED_CANARY')
            # Most tracked inputs are absent locally. The commit remains sufficient.
            with patch.object(distribution, 'ROOT', fixture):
                lock = distribution.build(directory / 'bundle')
            exported = json.loads((directory / 'bundle/gemini/gemini-extension.json').read_text())
            committed = json.loads(subprocess.check_output(
                ['git', '-C', str(ROOT), 'show', f'{SOURCE_REF}:distribution/gemini/gemini-extension.json']))
            self.assertEqual(exported, committed)
            self.assertEqual(lock['commit'], SOURCE_REF)
            self.assertFalse((directory / 'bundle/.env').exists())
            self.assertFalse((directory / 'bundle/untracked.txt').exists())
            for canary in ['LOCAL_CHANGE_NOT_COMMITTED', 'LOCAL_UNTRACKED_CANARY',
                           'REVIEW_CANARY_NOT_A_SECRET']:
                self.assertFalse(any(canary in p.read_text(errors='replace')
                                     for p in (directory / 'bundle').rglob('*') if p.is_file()))

    def test_tracked_symlinks_and_gitlinks_fail_before_snapshot_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fixture = self.fixture_repo(directory)
            blob = subprocess.check_output(
                ['git', '-C', str(fixture), 'hash-object', '-w', '--stdin'],
                input=b'/outside/source/credential').decode().strip()
            for path, mode, kind, oid in [
                ('distribution/gemini/GEMINI.md', '120000', 'blob', blob),
                ('skills/external', '120000', 'blob', blob),
                ('skills/external', '160000', 'commit', SOURCE_REF),
            ]:
                with self.subTest(path=path, mode=mode):
                    tree = self.replace_tree_entry(fixture, path, mode, kind, oid)
                    snapshot = directory / 'snapshot'
                    with patch.object(distribution, 'ROOT', fixture), self.assertRaisesRegex(
                            ValueError, 'regular Git file'):
                        distribution.snapshot_inputs(tree, snapshot)
                    self.assertFalse(snapshot.exists())

    def test_unlisted_tracked_templates_are_not_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fixture = self.fixture_repo(directory)
            blob = subprocess.check_output(
                ['git', '-C', str(fixture), 'hash-object', '-w', '--stdin'],
                input=b'UNLISTED_TRACKED_CANARY').decode().strip()
            tree = self.replace_tree_entry(fixture, 'distribution/extra.txt', '100644', 'blob', blob)
            with patch.object(distribution, 'ROOT', fixture):
                distribution.snapshot_inputs(tree, directory / 'snapshot')
            self.assertFalse((directory / 'snapshot/distribution/extra.txt').exists())

    def test_missing_commits_and_non_commit_objects_are_rejected(self):
        blob = subprocess.check_output(
            ['git', '-C', str(ROOT), 'rev-parse', f'{SOURCE_REF}:LICENSE'], text=True).strip()
        with tempfile.TemporaryDirectory() as tmp:
            for ref in ['0' * 40, blob]:
                with self.subTest(ref=ref), self.assertRaises(ValueError):
                    distribution.build(Path(tmp) / 'unused', ref)
                self.assertFalse((Path(tmp) / 'unused').exists())

    def test_git_replacement_blobs_do_not_change_pinned_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fixture = self.fixture_repo(directory)
            original = subprocess.check_output(
                ['git', '-C', str(fixture), 'rev-parse',
                 f'{SOURCE_REF}:distribution/gemini/gemini-extension.json'], text=True).strip()
            replacement = subprocess.check_output(
                ['git', '-C', str(fixture), 'hash-object', '-w', '--stdin'],
                input=b'{"name":"LOCAL_REPLACEMENT_CANARY"}').decode().strip()
            subprocess.run(['git', '-C', str(fixture), 'replace', original, replacement], check=True)
            with patch.object(distribution, 'ROOT', fixture):
                distribution.build(directory / 'bundle', SOURCE_REF)
            manifest = json.loads((directory / 'bundle/gemini/gemini-extension.json').read_text())
            self.assertEqual(manifest['name'], 'fal-ai')


if __name__ == '__main__':
    unittest.main()
