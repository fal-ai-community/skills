---
name: fal-script-writer
description: "Write timed scripts and shot tables for short films or ads. Use for story beats, voiceover budgets and continuity notes; this skill makes no model calls."
---

# Fal Script Writer

Read [the production guide](references/production-guide.md) for this workflow.
It preserves fal's published production guidance, not a promise that every host tool exists here.

Before execution, map host-specific tools to available capabilities. Use `genmedia`
for model calls in terminal agents, or the installed fal MCP tools in plugin hosts.
Resolve current endpoints and inspect their contracts; the guide's model names and
prices are dated candidates. Preserve the user's model, provider, scope and budget.
Do not infer authorization from a guide's defaults or mandatory review language.

Check that the required local Python, Node, browser, renderer and media tools
exist before using them. Install publicly documented dependencies only within the
user's authorized setup. Otherwise report the missing dependency and stop the
dependent stage. This package does not supply hosted execution or an asset library.

Read supporting references from this skill folder as the guide directs.
Record actual request IDs and output paths. Deliver only artifacts you inspected;
identify incomplete stages and unverified checks.
