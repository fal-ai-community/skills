# Installation and validation

These instructions become available from `main` after the PR merges. They do not
publish a release or marketplace listing. During review, clone the PR branch
instead of `main`. Generation is billed to the user's fal account.

## One command: project skills

Requirements: Git with GitHub SSH access and Python 3.10+. Run from the project root.
The installer uses only Python's standard library. It verifies the committed
registry and installs every skill with its references, scripts and assets.
It refuses to overwrite existing skills. Restart the agent after installation.

Codex:

```sh
fal_skills_tmp=$(mktemp -d) && git clone --depth 1 git@github.com:fal-ai-community/skills.git "$fal_skills_tmp" && python3 "$fal_skills_tmp/scripts/install.py" --agent codex
```

Claude Code:

```sh
fal_skills_tmp=$(mktemp -d) && git clone --depth 1 git@github.com:fal-ai-community/skills.git "$fal_skills_tmp" && python3 "$fal_skills_tmp/scripts/install.py" --agent claude
```

Cursor:

```sh
fal_skills_tmp=$(mktemp -d) && git clone --depth 1 git@github.com:fal-ai-community/skills.git "$fal_skills_tmp" && python3 "$fal_skills_tmp/scripts/install.py" --agent cursor
```

Keep the printed temporary clone for inspection, or remove that directory after
installation. The installed files are independent copies. Run `genmedia setup`
after installing the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli)
for terminal model execution. Keep API keys out of skill files and shell history.

For a single skill, add `--skill NAME`. Install its named dependency skills too,
or use the complete bundle. To test without changing agent discovery folders,
add `--destination /an/empty/test/folder`. For upgrades, review and remove or move
only the previously installed fal folders first. The installer never overwrites
an existing skill or edits agent settings.

## Claude Code plugin

The canonical repository also exposes a CLI-based Claude plugin:

```text
/plugin marketplace add git@github.com:fal-ai-community/skills.git
/plugin install fal-ai@fal-community
```

For review without installation: `claude plugin validate /path/to/skills --strict`.
For local loading: `claude --plugin-dir /path/to/skills`. These paths use genmedia;
the MCP profile below is an alternative for hosts with OAuth support.

## MCP plugin bundles

From a reviewed checkout:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/build-packages.py --profile claude --output /tmp/fal-claude-review
.venv/bin/python scripts/build-packages.py --profile codex --output /tmp/fal-codex-review
.venv/bin/python scripts/build-packages.py --profile cursor --output /tmp/fal-cursor-review
.venv/bin/python scripts/build-packages.py --profile grok --output /tmp/fal-grok-review
```

Each output must be empty or absent. Codex, Cursor and Grok default to a hybrid
bundle with six entry points: `fal-media` plus the five outcome workflows. Local
files contain stable production checks. The router fetches current model contracts,
prices and specialist guidance through the connected fal tools only when needed.
It reuses guidance for the current task and preserves its returned version for
reference reads. If guidance is unavailable, local checks remain available; an
unsupported stage is reported instead of replaced with guessed tools or models.

CLI and Claude builds retain the full library by default. To build all 36 skills
for another MCP host, add `--bundle full`. `--bundle hybrid` also works for Claude.
Terminal-only builds require the full library. All 36 source skills, terminal
plans, references and helper code stay in the community repository.

Hybrid bundles include the six `SKILL.md` files, native manifests, a hash registry
and a source lock. They do not install local runtime dependencies. Do not maintain
copies manually. For the existing Codex/Grok repositories, copy only `skills/`
and `skills-source.lock.json` from the matching profile. The lock records the
source commit, bundle type and exact entry points. Preserve their existing
manifests, connector mapping, logos and evals. Their sync scripts enforce this rule.

Claude: validate the generated bundle, then load with
`claude --plugin-dir /tmp/fal-claude-review`. Complete the fal OAuth browser flow
when the MCP connection requests it. No API key belongs in the package.

Cursor: Plugins settings → add a plugin from its GitHub repository URL, using
[fal-grok-plugin](https://github.com/fal-ai-community/fal-grok-plugin) after its
companion PR merges. The `.cursor-plugin` manifest and `mcp.json` configure OAuth.

Grok Bot/Build: use the same Grok package only in a host that accepts its existing
`.grok-plugin` or `.cursor-plugin` format. No universal Grok install URI or CLI was
established from the inspected public documentation. Do not advertise one-click
Grok installation until a host owner validates it. The bundle build and integrity
checks are available now; native install/authentication remains a manual check.

Codex: project skill installation above works without plugin publication.
The Codex build is skills-only by default. It does not embed a connector
registration from the maintainer's account. A distributor with its own registered
connector may pass `--codex-app-id` explicitly. Registration and access remain
separate from public skill installation. Use the public genmedia CLI for terminal
execution, or connect fal through a supported MCP host. See the
[official package guide](https://developers.openai.com/plugins/build/plugins).

## Verification limits

Automated tests use isolated destinations and fake model submissions. Live schema
reads verify candidate contracts without paid generation. Tests do not prove
visual quality, model output fidelity, marketplace acceptance, OAuth in each host,
or a fluent speaker's approval of a localized asset. Those checks need separate
runtime trials; do not label a dry run as a rendered creative result.
