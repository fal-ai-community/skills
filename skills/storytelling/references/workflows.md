# Storytelling workflows

## Native multi-prompt sequence

Use only when schema supports multiple prompts, shot arrays, scenes, timeline,
or keyframe-like fields.

1. Inspect schema and identify the exact multi-shot fields.
2. Convert the story into concise shot prompts.
3. Keep one continuity anchor outside the repeated shot details if schema
   supports a global prompt.
4. Run async and download the completed result.
5. Check whether the model returned one video or per-shot files.

## Manual per-shot video

Use when the model supports only one shot at a time.

1. Create a shot table.
2. Generate or upload a reference frame for each shot.
3. Run each shot with unique download templates.
4. Record endpoint, request id, prompt, local output path, and defects.
5. Return clips in timeline order. Do not claim they are stitched unless they
   are actually stitched by the model or another tool.

## First-frame to last-frame

1. Generate or choose the opening frame.
2. Generate or choose the target final frame.
3. Upload both frames if local.
4. Inspect schema for accepted first/last frame fields.
5. Prompt the transition as one physical motion or transformation.
6. Run async and download.

## Character narrative

1. Use `character-design` to create or confirm the anchor.
2. Build shot variables around action, expression, and location.
3. Use image-to-video from approved stills when identity drift matters.
4. Compare each result to the anchor before advancing to the next shot.

## Product narrative

1. Use `commercial` to define product invariants.
2. Plan the sequence around hook, feature, context, proof, final frame.
3. Use the same product reference for every shot if schema allows it.
4. Keep motion modest when packaging fidelity matters.

## Audio narrative

1. Search for narration, music, or sound generation models with `genmedia
   models`.
2. Inspect schema and run audio jobs with `--download`.
3. Use transcript or beat timing to set shot durations.
4. Return audio path and visual clip paths separately unless a model produces
   combined audio-video output.
