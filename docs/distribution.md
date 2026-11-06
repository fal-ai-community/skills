# Registry, Gemini CLI and OpenClaw preparation

These adapters prepare review files. The builder does not install clients, change
agent settings, contact a registry or publish anything. CI runs local checks only.
Keep the release steps below pending until the maintainer approves publication.

## Build a review bundle

Use a reviewed checkout and Python 3.10+:

```sh
python3 scripts/build-distribution.py --output /tmp/fal-distribution-review
```

The destination must be absent or empty and outside the checkout. The output
contains Registry metadata, a root-level Gemini extension, and an OpenClaw
configuration example. Each client skill tree contains the complete canonical
library, including references, scripts and assets. The builder reuses the existing
MCP package adapter; it does not maintain another skill library.

`distribution.lock.json` records the full source commit and each file's SHA-256.
Inspect it before installation. Rebuild from a clean reviewed commit for release.
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
openclaw mcp add fal --url https://mcp.fal.ai/mcp-relay --transport streamable-http
openclaw mcp login fal
openclaw mcp doctor fal --probe
```

These commands change the selected OpenClaw profile and start browser OAuth.
Run them only for a requested installation. Do not put tokens in the fragment.
Copy the generated `openclaw/skills/` folders into an empty workspace `skills/`
directory when the complete library is wanted. Review collisions first. Keep
the source lock beside the installed library. See [native MCP setup](https://docs.openclaw.ai/tools/mcp)
and [skill discovery](https://docs.openclaw.ai/tools/skills).

## ClawHub review

The generated OpenClaw skill folders can serve as ClawHub publication inputs.
Preview a selected skill without publication:

```sh
clawhub skill publish /tmp/fal-distribution-review/openclaw/skills/product-ad-campaign --slug fal-product-ad-campaign --name "fal Product Ad Campaign" --changelog "Initial release" --dry-run
```

Use a reviewed, pinned CLI version that supports this documented command. Keep
`--dry-run`. No ClawHub login or publication workflow is included. A maintainer
must confirm the fal publisher identity, slug availability and companion-skill
installation before publication. Individual skills can reference other skills;
install the complete library for dependency coverage during local review.
The MCP connection needs browser OAuth; it requires no environment-variable key.
Terminal fallback paths require their documented local dependencies.
See the [ClawHub quickstart](https://docs.openclaw.ai/clawhub/quickstart).

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
