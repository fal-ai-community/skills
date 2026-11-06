import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml
import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


registry = module('registry', 'scripts/build-skills-index.py')
packages = module('packages', 'scripts/build-packages.py')
installer = module('installer', 'scripts/install.py')
runner = module('runner', 'skills/genmedia/scripts/run_plan.py')
OUTCOMES = ['product-ad-campaign', 'game-asset-production', 'storyboard-to-short-film',
            'ecommerce-product-photography', 'localize-and-repurpose']


class Distribution(unittest.TestCase):
    def test_registry_fresh_and_hashes(self):
        expected = json.loads((ROOT / 'skills/index.json').read_text(encoding='utf-8'))
        self.assertEqual(expected, registry.build_index())
        self.assertGreaterEqual(len(expected['skills']), 36)

    def test_metadata_roundtrip(self):
        for p in (ROOT / 'skills').glob('*/SKILL.md'):
            fm = registry.parse_frontmatter(p.read_text(encoding='utf-8'))
            self.assertEqual(fm['name'], p.parent.name)
            self.assertIsInstance(fm['description'], str)
            self.assertLessEqual(len(fm['description']), 1024)

    def test_all_package_profiles_include_every_asset(self):
        for profile in ['cli', 'claude', 'codex', 'cursor', 'grok']:
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'bundle'
                built = packages.build(out, profile, 'a' * 40)
                for source in (ROOT / 'skills').rglob('*'):
                    if not source.is_file() or any(x in registry.IGNORED for x in source.parts): continue
                    rel = source.relative_to(ROOT)
                    if source.name == 'index.json' or source.name == 'SKILL.md': continue
                    self.assertEqual(source.read_bytes(), (out / rel).read_bytes(), str(rel))
                self.assertEqual(built, registry.build_index(out / 'skills'))
                self.assertFalse(any(p.is_symlink() for p in out.rglob('*')))
                if profile == 'codex':
                    self.assertFalse((out / '.app.json').exists())
                    self.assertNotIn('apps', json.loads((out / '.codex-plugin/plugin.json').read_text(encoding='utf-8')))
                if profile != 'cli':
                    for p in (out / 'skills').glob('*/SKILL.md'):
                        self.assertIn('## Client execution adapter', p.read_text(encoding='utf-8'))

    def test_package_refuses_nonempty_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'keep').write_text('owned', encoding='utf-8', newline='\n')
            with self.assertRaises(ValueError): packages.build(tmp, 'codex')
            self.assertEqual((Path(tmp) / 'keep').read_text(encoding='utf-8'), 'owned')

    def test_install_all_in_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            names = installer.install(tmp)
            self.assertEqual(len(names), len(registry.build_index()['skills']))
            self.assertTrue((Path(tmp) / 'game-asset-production/assets/plan.json').exists())
            self.assertIn('../../fal-workflow/references/recipes.md',
                          (Path(tmp) / 'genmedia-workflow/references/recipes.md').read_text(encoding='utf-8'))
            self.assertTrue((Path(tmp) / 'fal-workflow/references/recipes.md').exists())
            with self.assertRaises(ValueError): installer.install(tmp)

    def test_installer_preserves_unowned_existing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / OUTCOMES[0]; path.mkdir(); (path / 'mine').write_text('keep', encoding='utf-8', newline='\n')
            with self.assertRaises(ValueError): installer.install(tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [path])
            self.assertEqual((path / 'mine').read_text(encoding='utf-8'), 'keep')

    def test_unknown_skill_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): installer.install(Path(tmp) / 'unused', ['unknown'])
            self.assertFalse((Path(tmp) / 'unused').exists())

    def test_outcome_plans_match_read_only_live_contracts(self):
        schemas = json.loads((ROOT / 'tests/fixtures/candidate-schemas.json').read_text(encoding='utf-8'))['models']
        for name in OUTCOMES:
            plan = runner.load_plan(ROOT / 'skills' / name / 'assets/plan.json')
            for stage in plan['stages']:
                schema = schemas[stage['endpoint']]
                values = dict(stage['inputs'])
                # Fill only declared examples; don't invent parameter names.
                for key, value in values.items():
                    prop = schema['properties'][key]
                    if isinstance(value, str) and value.startswith('REPLACE_'):
                        values[key] = prop.get('enum', ['https://example.com/source.png' if 'url' in key else 'test'])[0]
                    elif isinstance(value, list):
                        values[key] = ['https://example.com/source.png']
                jsonschema.validate(values, schema)
                self.assertTrue(set(values).issubset(schema['properties']))

    def test_outcome_entrypoint_assets_exist(self):
        for name in OUTCOMES:
            p = ROOT / 'skills' / name
            self.assertTrue((p / 'assets/plan.json').is_file())
            self.assertIn('assets/plan.json', (p / 'SKILL.md').read_text(encoding='utf-8'))

    def test_original_runtime_files_preserved(self):
        # Compare the baseline of the branch, not a handwritten list of expected text.
        base = json.loads((ROOT / 'docs/source-inventory.json').read_text(encoding='utf-8'))['community_base']
        paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', base,
                                         'skills/fal-redesign'], text=True).splitlines()
        for path in paths:
            original = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{base}:{path}'])
            self.assertEqual((ROOT / path).read_bytes(), original)


class Recovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.plan = self.root / 'plan.json'
        self.plan.write_text(json.dumps({'version': 1, 'stages': [{'id': 'hero',
            'endpoint': 'fal-ai/flux-2/klein/9b', 'inputs': {'prompt': 'A brass kettle'}, 'async': True}]}), encoding='utf-8', newline='\n')
        self.calls = []

    def fake(self, args):
        self.calls.append(args)
        if args[1] == 'run': return {'request_id': 'request-123'}
        if args[1] == 'status': return {'status': 'COMPLETED', 'downloaded_files': [{'path': 'hero.png'}]}
        return {'contract': args[1]}

    def test_dry_run_has_no_side_effects(self):
        result = runner.run(self.plan, 'hero', self.root / 'state', invoke=self.fake)
        self.assertTrue(result['dry_run']); self.assertEqual(self.calls, [])
        self.assertFalse((self.root / 'state').exists())

    def test_submit_then_poll_same_request(self):
        state = self.root / 'state'
        runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        with self.assertRaises(ValueError): runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        result = runner.run(self.plan, 'hero', state, poll=True, invoke=self.fake)
        self.assertEqual(result['phase'], 'complete')
        self.assertEqual([a[1] for a in self.calls].count('run'), 1)
        self.assertEqual(self.calls[-1][3], 'request-123')

    def test_lost_submit_response_is_not_retried(self):
        state = self.root / 'state'
        def uncertain(args):
            if args[1] == 'run': raise OSError('connection lost after server accepted')
            return {}
        with self.assertRaises(OSError): runner.run(self.plan, 'hero', state, execute=True, invoke=uncertain)
        with self.assertRaises(ValueError): runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        with self.assertRaises(ValueError): runner.run(self.plan, 'hero', state, poll=True, invoke=self.fake)
        self.assertEqual(self.calls, [])

    def test_concurrent_stage_lock_prevents_calls(self):
        state = self.root / 'state'; state.mkdir(); (state / 'hero.lock').touch()
        with self.assertRaises(FileExistsError): runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        self.assertEqual(self.calls, [])

    def test_changed_stage_cannot_poll_wrong_request(self):
        state = self.root / 'state'; runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        data = json.loads(self.plan.read_text(encoding='utf-8')); data['stages'][0]['inputs']['prompt'] = 'Changed'
        self.plan.write_text(json.dumps(data), encoding='utf-8', newline='\n')
        with self.assertRaises(ValueError): runner.run(self.plan, 'hero', state, poll=True, invoke=self.fake)

    def test_example_placeholder_cannot_spend(self):
        self.plan.write_text((ROOT / 'skills/product-ad-campaign/assets/plan.json').read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
        with self.assertRaises(ValueError): runner.run(self.plan, 'hero', self.root / 'state', execute=True, invoke=self.fake)
        self.assertEqual(self.calls, [])

    def test_parameter_text_never_runs_in_shell(self):
        data = json.loads(self.plan.read_text(encoding='utf-8')); data['stages'][0]['inputs']['prompt'] = 'literal $(touch /tmp/bad)'
        args = runner.command(data['stages'][0], 'out')
        self.assertIn('literal $(touch /tmp/bad)', args)

    def test_unsafe_stage_path_is_rejected(self):
        data = json.loads(self.plan.read_text(encoding='utf-8')); data['stages'][0]['id'] = '../escape'
        self.plan.write_text(json.dumps(data), encoding='utf-8', newline='\n')
        with self.assertRaises(ValueError): runner.load_plan(self.plan)

    def test_running_status_is_not_reported_complete(self):
        state = self.root / 'state'; runner.run(self.plan, 'hero', state, execute=True, invoke=self.fake)
        result = runner.run(self.plan, 'hero', state, poll=True, invoke=lambda args: {'status': 'IN_PROGRESS'})
        self.assertEqual(result['phase'], 'submitted')


if __name__ == '__main__': unittest.main()

class NativeManifests(unittest.TestCase):
    def test_portable_manifests_against_official_schema(self):
        schema = json.loads((ROOT / 'tests/fixtures/plugin.schema.json').read_text(encoding='utf-8'))
        for profile in ['claude', 'codex', 'cursor', 'grok']:
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'bundle'; packages.build(out, profile)
                jsonschema.validate(json.loads((out / 'plugin.json').read_text(encoding='utf-8')), schema)
                if profile != 'codex':
                    mcp = json.loads((out / 'mcp.json').read_text(encoding='utf-8'))
                    self.assertEqual(mcp['mcpServers']['fal'],
                                     {'type': 'http', 'url': 'https://mcp.fal.ai/mcp-relay'})

    def test_claude_marketplace_source_is_present(self):
        data = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        for entry in data['plugins']:
            plugin_root = ROOT / entry['source']
            manifest = json.loads((plugin_root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
            self.assertEqual(entry['name'], manifest['name'])
            self.assertTrue((plugin_root / manifest['skills']).exists())

class PublicDistribution(unittest.TestCase):
    def test_codex_connector_requires_explicit_distributor_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'bundle'
            packages.build(out, 'codex', codex_app_id='example-distributor-registration')
            mapping = json.loads((out / '.app.json').read_text(encoding='utf-8'))
            self.assertEqual(mapping['apps']['fal-ai']['id'], 'example-distributor-registration')

    def test_candidate_fixtures_contain_no_media_urls_or_source_record_ids(self):
        fixture = (ROOT / 'tests/fixtures/candidate-schemas.json').read_text(encoding='utf-8')
        self.assertNotIn('https://', fixture)
        provenance = json.loads((ROOT / 'docs/source-inventory.json').read_text(encoding='utf-8'))
        for item in provenance['production_skills']:
            self.assertNotIn('id', item)
            self.assertNotIn('version_id', item)

    def test_public_surface_has_no_account_registration_or_private_code_links(self):
        import re
        patterns = [r'asdk_[a-z0-9]{20,}', r'github\.com/fal-ai/',
                    r'api\.fal\.ai/v1/guidance', r'fal\.ai/api/models',
                    r'/Users/[A-Za-z][^\s/]+/', r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                    r'\bgh[pousr]_[A-Za-z0-9]{30,}\b', r'\bd[a-z0-9]{17,23}\b']
        for folder in ['skills', 'docs', 'scripts']:
            for path in (ROOT / folder).rglob('*'):
                if not path.is_file() or '__pycache__' in path.parts: continue
                if path.suffix not in {'.md', '.json', '.py', '.js', '.mjs', '.html'}: continue
                source = path.read_text(encoding='utf-8')
                for pattern in patterns:
                    self.assertIsNone(re.search(pattern, source), f'{path.relative_to(ROOT)}: {pattern}')

    def test_anonymous_access_evidence_has_no_auth_material(self):
        data = json.loads((ROOT / 'docs/public-access-audit.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(data['public_schema_count'], 100)
        self.assertEqual(data['public_schema_count'], len(data['models']))
        for model in data['models']:
            self.assertEqual(model['status'], 200)
            self.assertTrue(model['schema_url'].startswith('https://fal.ai/'))
