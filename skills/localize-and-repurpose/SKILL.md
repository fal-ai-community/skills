---
name: localize-and-repurpose
description: "Localize and repurpose existing creative content with fal. Deliver translated speech, accurate subtitles and channel cuts while preserving meaning, brand assets and source provenance."
---

# Localize and repurpose content

Turn an existing approved asset into verified locale and channel variants.

## Source and language contract

Collect the source media, transcript if available, target locales, glossary,
protected names, exact claims, voice permissions, target channels and budget.
Read `fal-audio-generation` for dubbing and timed transcription; read
`branded-graphics` for exact brand assets. Keep the original master unchanged.

1. Inspect source streams and duration. Extract an audio container before a speech
   endpoint that requires `audio_url`; a video path is not an audio URL.
2. Transcribe with a current timed endpoint such as
   `fal-ai/elevenlabs/speech-to-text/scribe-v2`. Check its language-code convention.
   Filter timing tokens by their actual type before building captions.
3. Translate the verified transcript for meaning, register, units and the supplied
   glossary. Preserve claims and proper nouns; do not invent stronger promises.
   Mark uncertain translations for a fluent reviewer before calling them approved.
4. For a dub, inspect `fal-ai/elevenlabs/dubbing`: `target_lang` plus the proper
   source URL. Compare voices, speaker identity and meaning against the source.
   Do not add lip sync unless requested and supported by the chosen contract.
5. Re-transcribe the localized output for actual word timings. Build SRT/VTT from
   those timings, not proportional estimates from the original captions.
6. Make requested platform cuts from meaningful sentence/scene boundaries. Reframe
   around the subject; do not stretch footage. Recompose exact text/logo assets for
   each aspect ratio. Preserve RTL layout and glyph coverage where applicable.
7. Assemble with an available verified renderer. Check that dubbing did not remove
   requested music/effects. Keep localized voice, music and picture stems separate.

## Acceptance and delivery

Deliver folders by locale and channel, localized video/audio, SRT/VTT, translated
copy, glossary decisions and manifest. Verify no missing lines, caption order,
nonnegative timestamps, caption ends within runtime, text coverage and source/target
meaning. Listen to names and numbers. State when native-language review remains
outstanding. Do not publish or distribute variants without a separate instruction.

## Execute and recover

Read the `genmedia` skill for terminal execution, or `fal-media` for connected MCP
execution. Read only the named production references needed by this brief.
Use current published routing or discover a candidate. Verify exact endpoints,
input schemas, output shape and price units before constructing inputs. Preserve
an explicitly named model. Candidate IDs below were schema-checked on 2026-11-05;
availability and price can change.

For terminal agents, copy [the example plan](assets/plan.json) into the project.
Replace every `REPLACE_` value with the actual prompt, URL or locale. Inspect each
stage's live schema and price, then run the shared helper from the installed
`genmedia` skill (locate its installation path; do not assume the current directory):

```sh
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero --execute --state ./production-state
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero --poll --state ./production-state
```

The first command prints a dry run. Use the actual stage ID from the plan.
`--execute` spends on that stage only. The helper records schema, pricing and the
submission response. It refuses a second submission for the same stage. `--poll`
checks the saved request and downloads its output. A failed or uncertain submit
needs manual reconciliation, not a blind retry. Copy verified output URLs into
later stage inputs after visual review. Never use a local path where a URL is required.

For MCP hosts, perform the same stages with current tool contracts: use
`recommend_model` unless the user names an endpoint; use its returned input contract
and `next_call` when provided. Otherwise inspect the schema. Use `run_model` for
bounded operations, or `submit_job`, `check_job` and `get_job_result` for queued work.
Record the request ID immediately. Do not install genmedia merely to follow a CLI example.

Keep a project manifest with source assets, endpoint, inputs, request ID, output URL,
local file, dimensions/duration, cost estimate, and QA findings for every stage.
Produce only the requested variants within the existing budget. Return observed
failures and missing capabilities; do not substitute a plan for a requested artifact.
