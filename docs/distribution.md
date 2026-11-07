# Registry, Gemini CLI and OpenClaw preparation

These adapters prepare review files. The builder does not install clients, change
agent settings, contact a registry or publish anything. CI runs local checks only.
Keep the release steps below pending until the maintainer approves publication.

## Build a review bundle

Use Python 3.10+ and a checkout with a reviewed commit:

```sh
python3 scripts/build-distribution.py --output /tmp/fal-distribution-review
```

The builder defaults to `HEAD`. To select another local commit, pass its full
SHA with `--source-ref`. Uncommitted edits, ignored files and untracked files
never enter the export. Commit intended changes before rebuilding.

The builder reads Git blobs from that commit. It includes only the explicitly allowlisted
client/Registry templates, the canonical tracked `skills/` tree, the license,
and the two package/index helpers. It rejects symlinks and submodules in these
inputs before materialization. Other tracked files in `distribution/` are not
automatically exported; update the template allowlist for an intended addition.

The destination must be absent or empty and outside the checkout. The output
contains Registry metadata, a root-level Gemini extension, and an OpenClaw
configuration example. Each client skill tree contains the complete canonical
library, including references, scripts and assets. The builder reuses the existing
MCP package adapter; it does not maintain another skill library.

`distribution.lock.json` records the full source commit and each file's SHA-256.
Inspect it before installation. Rebuild from the reviewed commit for release.
Generation uses the connected fal account's credits. Local composition still
requires the tools specified by each skill.

## Official MCP Registry

The proposed identity is `ai.fal/mcp`. The maintainer must prove control of
`fal.ai` before publication. The public remote endpoint uses Streamable HTTP and
browser OAuth. This entry requests no API key or static authorization header.

`distribution/registry/server.json` follows the official `2025-12-11` schema.
The complete schema fixture in `tests/fixtures/mcp-registry-server.schema.json`
comes from the [official schema URL](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).
Tests validate the file offline. No server source repository is declared because
this repository contains skills and adapters, rather than the hosted server.

After approval, use the current publisher's domain verification process and
publish the reviewed metadata. See the [remote-only quickstart](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx)
and [authentication guide](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/authentication.mdx).
Confirm that the namespace is available before the first publication. Namespace
availability and ownership are not proved by JSON Schema validation.

Do not add a publisher workflow, credentials or a DNS challenge to this PR.
Publishing to the upstream Registry does not guarantee a curated client listing.

## Gemini CLI

The generated `gemini/` folder is a complete extension. Its manifest uses
`httpUrl` for Streamable HTTP. Gemini discovers its `skills/` folders on demand.
It requests no installation scripts, hooks or automatic tool approvals.

For a local review installation, use an isolated Gemini profile:

```sh
fal_gemini_review_profile=$(mktemp -d)
GEMINI_CLI_HOME="$fal_gemini_review_profile" gemini extensions install /tmp/fal-distribution-review/gemini
GEMINI_CLI_HOME="$fal_gemini_review_profile" gemini extensions list
GEMINI_CLI_HOME="$fal_gemini_review_profile" gemini
```

Restart Gemini, then use `/mcp auth fal` when the client requests sign-in. Confirm
that fal tools load before a generation task. Preserve any existing `fal` server
configuration: Gemini's user settings can override the extension's MCP entry.
The installer above changes only the temporary profile. It is not part of the
builder. Keep the profile path if a later review session must reuse it.

The repository root deliberately has no Gemini manifest. Therefore this checkout
is not directly installable through `gemini extensions install <repo-url>`.
Build the local folder first. After approval, place the generated extension at the
root of its public adapter repository. Add the `gemini-cli-extension` GitHub topic
only when gallery indexing is approved. No topic or release is added by this PR.
See [extension installation](https://geminicli.com/docs/extensions/reference/)
and [gallery indexing](https://geminicli.com/docs/extensions/releasing/).

## OpenClaw

`openclaw/mcp.config.json` is a configuration fragment, not a replacement for a
user's settings. Merge only the `mcp.servers.fal` entry into the chosen profile.
Alternatively, use the current native CLI:

```sh
openclaw mcp add fal --url https://mcp.fal.ai/mcp-relay --transport streamable-http --auth oauth
```

This command changes the selected OpenClaw profile. The explicit `auth: "oauth"`
field enables native OAuth; the URL alone does not enable it. For a running
Gateway, use **Settings → MCP → Sign in** to authorize the shared connection.

For CLI authorization, first stop the Gateway for the selected installation.
The CLI login command runs offline and refuses a server without `auth: "oauth"`.
Complete sign-in, then restart the Gateway if it was running:

```sh
openclaw mcp login fal
openclaw mcp doctor fal --probe
```

Run these steps only for a requested installation. Do not put tokens in the
fragment. See [OAuth transport requirements](https://docs.openclaw.ai/cli/mcp/transports)
for the current CLI workflow.
Copy the generated `openclaw/skills/` folders into an empty workspace `skills/`
directory when the complete library is wanted. Review collisions first. Keep
the source lock beside the installed library. See [native MCP setup](https://docs.openclaw.ai/tools/mcp)
and [skill discovery](https://docs.openclaw.ai/tools/skills).

## ClawHub bundle

Publish the generated `openclaw/` folder as one `bundle-plugin`. It uses the
supported Claude bundle format and contains all canonical skills and companions.
The included MIT license remains with the package. Do not publish the five
outcome folders alone: they reference companion skills and shared helpers.

Preview the complete artifact with a pinned CLI before publication:

```sh
npx --yes clawhub@0.25.1 package publish /tmp/fal-distribution-review/openclaw --family bundle-plugin --bundle-format claude --name @fal-ai-community/creative-suite --owner fal-ai-community --version 0.1.0 --source-repo fal-ai-community/skills --source-commit REVIEWED_FULL_COMMIT_SHA --source-path distribution/openclaw --changelog "Initial complete creative workflow bundle" --dry-run
```

Replace `REVIEWED_FULL_COMMIT_SHA` with the commit recorded in the generated
source lock. The source repository and exporter are canonical; publication uploads
the reviewed generated bundle, including the complete `skills/` tree. The source
path names the adapter templates, not a separately maintained skill library.

Confirm the authenticated publisher can manage `@fal-ai-community` before
removing `--dry-run`. Do not publish under an unrelated personal owner or claim a
third-party listing. After approval and successful publication checks, users can
install the complete package:

```sh
openclaw plugins install clawhub:@fal-ai-community/creative-suite
```

Then authorize the fal MCP connection using the OpenClaw setup above. Installation
does not grant automatic approval for paid generations. No publisher workflow or
credential is added to this repository.

See [bundle mapping](https://docs.openclaw.ai/plugins/bundles) and
[ClawHub publishing](https://docs.openclaw.ai/clawhub/publishing).

## Required runtime checks before publication

Record the client and CLI versions. Test browser sign-in, tool discovery, schema
and price reads, refresh, reconnect and result delivery. Use an approved budget
for a real generation task. Verify long jobs without duplicate submissions.
The local tests prove bundle integrity and manifest contracts. They do not prove
OAuth interoperability, generation quality or marketplace acceptance.

## Goose

The current Goose contributor instructions retire new third-party directory
entries. Use the official Registry route instead of a directory PR. For a
requested local installation, open `goose configure`, choose Add Extension, then
Remote Extension (Streamable HTTP). Enter `https://mcp.fal.ai/mcp-relay` and complete
the browser OAuth flow when requested. The current client handles discovery and
client registration. Do not supply a client identifier from another installation.

For a session-only connection:

```sh
goose session --with-streamable-http-extension "https://mcp.fal.ai/mcp-relay"
```

See the [current extension guide](https://github.com/aaif-goose/goose/blob/main/documentation/docs/getting-started/using-extensions.md)
and [directory retirement discussion](https://github.com/aaif-goose/goose/discussions/10830).
No Goose catalog submission or authenticated runtime check is performed here.
