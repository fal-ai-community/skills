# Source inventory and compatibility

Research date: 2026-11-05 (America/Los_Angeles).

## Canonical source

[fal-ai-community/skills](https://github.com/fal-ai-community/skills) owns the
maintained skill folders and references. `skills/index.json` retains its version-1
schema and lists every distributable file with its byte count and SHA-256 hash.
Existing names remain stable. Identical `genmedia-workflow` references point to
`fal-workflow` through small compatibility documents. Complete installations include
both paths without filesystem symlinks.
Existing runtime assets, including `fal-redesign`, remain intact.

## Inspected distribution packages

| Source | Finding | Action |
| --- | --- | --- |
| [Community skills](https://github.com/fal-ai-community/skills) | Terminal/genmedia execution, 17 existing skills | Canonical source; preserve compatibility names and assets |
| [Grok/Cursor](https://github.com/fal-ai-community/fal-grok-plugin) | Native manifests, OAuth MCP relay, duplicated entry points without references | Preserve manifests, icon, evals and OAuth URL; generate complete MCP bundles |
| [Claude marketplace search result](https://github.com/amlmarketplaces/fal) | Third-party marketplace for an SDK re-export, not fal's production creative skills | Inspect only; do not claim ownership or change it |

No first-party standalone Claude Code package was found in the inspected fal-ai
and fal-ai-community repositories. This change adds a Claude marketplace/manifest
at the canonical repository and a full MCP-capable Claude bundle build profile.

## Published production guidance

The public [discovery registry](https://fal.ai/.well-known/agent-skills/index.json)
returns standalone skills only. It does not enumerate supporting references.
Adapted official guidance is recorded by content checksum in
[source-inventory.json](source-inventory.json). Production database handles and
account-specific identifiers are not included. Public clients use installed skill
files, genmedia discovery, or the public fal MCP connection.

Existing community bodies win on common skill names. Missing reference files are
added. Differing existing reference files remain intact and appear in the source
inventory. New production bodies live once in `references/production-guide.md`;
small entry points describe runtime mapping and limitations. This avoids copying
long production manuals into discovery metadata.

`premiere-actions` and `photoshop-actions` remain in their Adobe host. Importing
panel JSON instructions into coding agents would advertise capabilities they lack.
`video-compositing` and `reels-creator` preserve their production references and
code, but require their documented renderer dependencies. Their entry points
require capability checks and prohibit claims of execution when tools are absent.

This is a reviewed content snapshot, not a live production sync. There is no deployment,
release, publishing workflow, scheduled import or production database update.
Future production changes require a reviewed source refresh.

## Routing and execution

Names preserve installed entry points. Descriptions separate complete outcomes
from individual shots, creative direction, catalog lookup and workflow authoring.
`genmedia-workflow` remains a compatibility entry for `fal-workflow`.

CLI skills use genmedia. MCP bundles use native-tool entry points. Codex, Cursor and Grok ship a hybrid
selection by default: the fal router plus five outcome workflows. The builder
derives their stable production checks from the canonical skill files and omits
optional terminal sections. Model contracts and specialist advice are retrieved
through live tools on demand. This avoids separate workflow authoring in plugin
repositories. The complete library remains available through `--bundle full`.
MCP bundles do not require a CLI to execute model calls. Codex builds contain no connector registration by default. Distributors may
supply their own registration explicitly. OAuth profiles use the public fal relay. Schemas, prices and routing are checked
live; static model defaults are candidates, not current authority.

The shared stage runner has a dry-run default, explicit execution, request logs,
an exclusive stage lock, and no automatic resubmission. A lost submit response
requires reconciliation against account history before any new paid attempt.
A new stage ID represents a new paid attempt, not a way to recover an old one.
