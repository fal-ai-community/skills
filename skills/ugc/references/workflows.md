# UGC workflows

## Portrait plus script

Use when the user supplies or approves a face image and script.

1. Keep script short and conversational.
2. Upload the portrait.
3. If using generated audio, create or upload the voice first.
4. Run `veed/fabric-1.0` or `veed/fabric-1.0/text` after schema inspection.
5. Download the result from `genmedia status`.
6. Reject outputs with mouth drift, frozen expression, or identity drift.

## Existing footage plus new audio

Use when the user has a real creator clip and wants new speech.

1. Upload the source video and clean audio.
2. Inspect `fal-ai/sync-lipsync/v2`.
3. Run async with `video_url` and `audio_url` or matching schema fields.
4. Compare the result to the source video. The body, background, and timing
   should stay stable.

## Product b-roll plus voiceover

Use when no face is needed.

1. Generate or upload a product still.
2. Create 2-5 b-roll clips: problem, product action, proof, lifestyle, close.
3. Use Seedance image-to-video for final clips.
4. Return the clips in edit order with voiceover notes.
5. Do not claim the clips are stitched unless a model or editor has stitched
   them.

## Hook variant set

Use for paid social testing.

1. Keep the product and proof constant.
2. Produce 3-5 hooks that vary by angle only: pain, curiosity, demo, result,
   objection.
3. Reuse the same speaker, crop, and product references for fair comparison.
4. Return a manifest with hook, endpoint, request id, output path, and defects.

## UGC to polished ad

Use when the user wants native creator footage but a cleaner final.

1. Generate the creator or demo clip first.
2. Generate product hero stills with `commercial` or `marketing`.
3. Add a clean final frame with safe space for external copy.
4. Keep platform-native pacing; do not over-style the creator shot.
