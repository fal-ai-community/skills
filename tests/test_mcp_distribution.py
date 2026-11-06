"""Validate review-only distribution contracts and complete generated assets."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mcp_distribution', ROOT / 'scripts/build-distribution.py')
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


class MCPDistribution(unittest.TestCase):
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
            lock = distribution.build(first, 'a' * 40)
            self.assertEqual(lock, distribution.build(second, 'a' * 40))
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
                self.assertEqual(skill_lock['commit'], 'a' * 40)
                self.assertEqual(skill_lock['profile'], client)
                self.assertEqual(skill_lock['registry_sha256'],
                                 hashlib.sha256(json.dumps(index, sort_keys=True).encode()).hexdigest())
                self.assertFalse(any(p.is_symlink() for p in (first / client).rglob('*')))

    def test_gemini_uses_remote_http_without_install_hooks_or_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            distribution.build(output, 'a' * 40)
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

    def test_outputs_cannot_overwrite_checkout_or_existing_files(self):
        for output in [ROOT, ROOT / 'skills', ROOT / 'scripts', ROOT.parent]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                distribution.build(output, 'a' * 40)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'existing'; output.mkdir()
            (output / 'keep').write_text('keep')
            with self.assertRaises(ValueError): distribution.build(output, 'a' * 40)
            self.assertEqual((output / 'keep').read_text(), 'keep')
            self.assertEqual(list(output.iterdir()), [output / 'keep'])

    def test_invalid_source_ref_fails_before_output_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'unused'
            with self.assertRaises(ValueError): distribution.build(output, '../../main')
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
