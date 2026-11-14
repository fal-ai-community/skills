---
name: fan-cam
description: >
  Create personalized live sports broadcast fan-cam videos with genmedia. Use
  this for realistic spectator cutaways, stadium or arena crowd reactions,
  broadcast screenshots, sports TV shots, scoreboard overlays, TV channel bugs,
  and identity-preserving fan reaction videos from a user photo.
---

# Fan cam production with genmedia

Use this skill when the user wants a personalized spectator video that feels
like a real live sports broadcast cutaway. The usual input is one photo of the
person, event details, and a desired reaction or situation.

Runtime is the genmedia CLI. Use the `genmedia` skill for command syntax. Load
`model-routing`, `fal-prompting`, and `genmedia-workflow` when endpoint choice,
model-specific prompt craft, or pipeline execution details matter.

Do not encode private examples, local file paths, user-specific workflow names,
or conversation-specific details into prompts or docs. Keep this skill
generalized.

## References

Load only what is needed:

- `references/prompt-contract.md` for the image prompt and Kling prompt rules.
- `references/genmedia-commands.md` for executable CLI command patterns.
- `references/examples.md` for sport-specific examples.

## Required inputs

Ask only for missing information that changes execution:

- User photo: local path or URL. This is the identity reference.
- Event details: sport, matchup, venue, league, broadcast context, wardrobe,
  scoreboard idea, crowd behavior, and any specific scenario.
- Reaction or situation: excited, happy, laughing, sad, neutral, angry,
  surprised, nervous, focused, eating, distracted, caught on camera, noticing
  the stadium screen, celebrating, disappointed, or another user-specified
  moment.
- Budget or quality preference only when the user explicitly asks for economy,
  preview, or native 4K final output. Otherwise use the standard fan-cam
  defaults: GPT Image 2 edit at `quality=high` with a 3840x2160 frame, then
  Kling v3 Pro.

If the user gives a local image path, upload it once with `genmedia upload` and
reuse the returned URL. If the user gives multiple references, treat the first
person image as the identity source and later images as optional venue,
broadcast, or styling references.

The user photo is an identity reference, not a Kling-ready start frame. Do not
skip GPT Image 2 edit just because the user supplied a person's photo. For a
personalized fan-cam, first use `openai/gpt-image-2/edit` to place the person
inside a realistic 16:9 broadcast scene, then use the approved generated frame
as Kling `start_image_url`.

## Pipeline

Default graph:

```text
photo URL -> prompt planning -> GPT Image 2 edit frame -> optional compression -> Kling v3 image-to-video -> downloaded video manifest
```

The GPT Image 2 edit frame is mandatory when the input is an ordinary person
photo. Only bypass this step if the user explicitly provides an already
approved 16:9 broadcast fan-cam frame and asks to animate that frame.

For high-fidelity personalized broadcast shots, prefer a two-pass frame build:

```text
event brief -> GPT Image 2 broadcast plate -> GPT Image 2 edit with user photo -> quality gate -> Kling v3 Pro
```

Use the plate pass when the scene needs a reliable scoreboard, broadcaster bug,
crowd layout, or central safe-area composition. The plate is a realistic
identity-free sports broadcast frame with an ordinary placeholder spectator.
The second pass uses `openai/gpt-image-2/edit` with `[plate_url, photo_url]` to
adapt that placeholder to the user's appearance. This keeps the user photo from
being treated as the whole composition and reduces edge-cropped or pasted-face
results.

The planning step is performed by the agent using this skill. Do not call a
separate LLM endpoint just to write prompts unless the user explicitly asks for
a hosted planner. Write the image prompt and Kling multi prompts directly.

## Endpoint selection

Always verify endpoints before use:

```bash
genmedia models --endpoint_id openai/gpt-image-2/edit --json
genmedia models --endpoint_id openai/gpt-image-2 --json
genmedia models --endpoint_id fal-ai/kling-video/v3/standard/image-to-video --json
genmedia models --endpoint_id fal-ai/kling-video/v3/pro/image-to-video --json
genmedia models --endpoint_id fal-ai/kling-video/v3/4k/image-to-video --json
```

Inspect schemas before running:

```bash
genmedia schema openai/gpt-image-2/edit --json
genmedia schema openai/gpt-image-2 --json
genmedia schema fal-ai/kling-video/v3/pro/image-to-video --format openapi --json
```

Use `--format openapi` for Kling v3 image-to-video endpoints because compact
schema output may omit top-level fields such as `multi_prompt`,
`start_image_url`, `duration`, `prompt`, `elements`, `shot_type`,
`negative_prompt`, and `cfg_scale`.

Check pricing when cost matters:

```bash
genmedia pricing openai/gpt-image-2/edit --json
genmedia pricing openai/gpt-image-2 --json
genmedia pricing fal-ai/kling-video/v3/standard/image-to-video --json
genmedia pricing fal-ai/kling-video/v3/pro/image-to-video --json
genmedia pricing fal-ai/kling-video/v3/4k/image-to-video --json
```

### GPT Image 2 quality choice

- Use `quality=high` by default for personalized fan-cam frames. GPT Image 2
  price is strongly affected by `low` vs `high`, but fan-cam identity,
  broadcast integration, and readable overlays need the stronger default.
- Use `quality=low` only when the user explicitly requests economy, preview,
  fast iteration, or lower-cost social drafts.
- Use `output_format=jpeg` for the generated broadcast frame unless the user
  needs transparency or lossless output.
- Use 16:9 4K frame size by default:

```json
{"width":3840,"height":2160}
```

### Kling v3 choice

Select the endpoint based on the brief:

- `fal-ai/kling-video/v3/pro/image-to-video`: default fan-cam endpoint. Use it
  for normal personalized sports cutaways, public examples, and any request
  where the user did not explicitly ask for economy.
- `fal-ai/kling-video/v3/standard/image-to-video`: use only when the user
  explicitly asks for economy, preview, fastest iteration, or lower cost.
- `fal-ai/kling-video/v3/4k/image-to-video`: use only for final premium 4K
  delivery or when the user explicitly asks for 4K video. Check pricing first.

Do not choose from memory alone. Verify model status and schema with genmedia in
the current session.

## Shot and duration planning

The agent decides the number and duration of multi prompts.

Hard rules:

- Each multi prompt must be at least 3 seconds.
- Total video duration must be 15 seconds or less.
- Use 2 to 5 multi prompts.
- Set the top-level Kling `duration` equal to the sum of all beat durations.
- If a real user-provided or approved reference is supplied through Kling
  `elements`, every multi prompt must reference `@Element1`. Do not invent
  extra elements just to satisfy a prompt pattern.
- Keep every Kling prompt concise. Aim for 250-430 characters.

Recommended patterns:

- Simple cutaway: 2 beats, 6 seconds total.
- Standard reaction: 3 beats, 9 seconds total.
- Rich fan-cam moment: 4 beats, 12 seconds total.
- Full story beat: 5 beats, 15 seconds total.

Do not always use five beats. Pick the smallest number that expresses the
moment clearly.

## Scene planning

The fan-cam does not need to be only a zoom on the spectator. Design the scene
from the event details:

- A nervous fan watching a decisive point.
- A supporter eating or drinking when the broadcast camera catches them.
- A spectator noticing themselves on the stadium screen.
- A quiet tennis audience reaction during a tiebreak.
- A basketball lower-bowl fan reacting to a buzzer-beater.
- A race grandstand spectator turning toward a pass or crash offscreen.
- A combat sports crowd cutaway during a tense round.
- A watch-party or esports arena reaction if the user specifies it.

Keep the whole video anchored to the generated frame. Use motion, camera
correction, crowd behavior, expression changes, and offscreen event energy to
create the sequence.

## Broadcast logo and overlay

Add a small top-right TV channel bug when it fits the brief. It should feel
sport-specific and broadcast-realistic, but generic unless the user supplies an
exact approved logo or explicitly requests a named network.

Good generic examples:

- `FOOTBALL LIVE`
- `COURT LIVE`
- `BASKET LIVE`
- `RACE LIVE`
- `FIGHT LIVE`
- `MATCH CAM`

Use compact score or timing overlays when the event calls for them. Keep them
small, integrated, and secondary to the spectator. Avoid fake sponsor marks,
large UI graphics, unstable text, and logos that dominate the frame.

## Image prompt requirements

The GPT Image 2 edit prompt must:

- Use the uploaded photo as a visual reference for the featured spectator's
  overall appearance.
- Keep the person consistent through stable visible cues such as age range,
  hairstyle, glasses if present, facial hair if present, clothing color, and
  general face shape. Avoid overloading the prompt with anatomical face terms.
- Create a horizontal 16:9 live TV broadcast screenshot.
- Place the person naturally in the spectator area.
- Make the selected reaction or situation visible but not theatrical.
- Include sport-specific venue, crowd, wardrobe, scoreboard, and broadcast
  language.
- Include realistic TV capture flaws: mild compression noise, subtle motion
  blur, off-center crop, foreground occlusion, focus falloff, imperfect
  background faces, natural venue light, and small exposure inconsistencies.
- Include a small top-right broadcast channel bug when appropriate.

The image prompt must avoid:

- Long negative lists in GPT Image 2 prompts. Keep GPT prompts mostly positive
  and concise; put detailed negatives in the Kling negative prompt instead.
- Beauty retouching, influencer styling, studio portrait, passport photo,
  selfie framing, isolated subject, empty background, oversized graphics, and
  warped scoreboard text.
- Fake sponsor marks, oversized logos, warped scoreboard text, random props
  not requested by the user, CGI crowd, cloned faces, anime, cartoon.

## GPT Image 2 prompt stability

If a direct photo-to-scene edit is rejected or produces a poor composition, do
not solve it by stripping away the broadcast requirements. Switch to the
two-pass plate workflow:

1. Generate a short, positive broadcast plate prompt with `openai/gpt-image-2`.
   Include the sport, venue, safe-area placeholder, compact scoreboard, small
   broadcaster bug, and 4K 16:9 broadcast texture. Avoid identity language and
   long negative lists in this pass.
2. Edit the approved plate with `openai/gpt-image-2/edit` using image URLs in
   this order: `[plate_url, photo_url]`.
3. In the identity edit prompt, lock the scene and ask to adapt only the
   placeholder spectator using the photo as a visual reference. Mention stable
   visible cues, not exhaustive face anatomy.
4. Run a quality gate before Kling. Retry the frame if the person is at an
   image edge, the scoreboard omits teams, text is warped, the face looks
   pasted, the shot feels like a portrait, or large readable apparel/sponsor
   marks dominate the frame.

## Kling prompt requirements

The Kling prompts must:

- Reference `@Element1` in every beat only when the request actually includes a
  real user-provided or approved Kling `elements` entry. Otherwise describe the
  featured spectator from the `start_image_url`; do not invent extra elements.
- Always submit Kling with `generate_audio=true`. Do not use
  `generate_audio=false` in this skill.
- When using `multi_prompt`, do not send `end_image_url`; Kling rejects
  `end_image_url` together with `multi_prompt`.
- Preserve the same person, face, outfit, seat area, crowd, overlay, lighting,
  and channel bug.
- Animate realistic broadcast motion: small head movement, blinking, breath,
  slight hand motion, food/drink gesture if present, nearby fans shifting,
  camera push-in, pan, sidestep, operator correction, or crowd swell.
- Use sport-specific language. Never write generic alternatives like "field or
  court" or "stadium or arena".
- Fit the chosen beat duration.
- If a spoken phrase should be external narration, do not write it as something
  the featured spectator says. Phrase it as an off-screen broadcast commentator,
  arena PA voice, or non-diegetic voiceover, and explicitly state that the
  featured spectator stays silent with no lip sync and no mouth movement
  matching the voice.
- Avoid face morphing, beautification, unstable scoreboard text, unstable logo,
  wrong sport, impossible crowd action, excessive camera movement, and sudden
  scene resets.

## Negative prompt

Use a negative prompt like this and adapt only when needed:

```text
low quality, smeared face, distorted faces, duplicated face, deformed hands, broken fingers, fake sponsor marks, oversized logos, unstable broadcast logo, watermark, text artifacts, unstable broadcast banner, flickering scoreboard, warped scoreboard text, unreadable names, passport photo, studio portrait, glamour portrait, beauty lighting, AI influencer, beautified face, changed face, enlarged eyes, sharpened jawline, pasted face, face cutout, over-smoothed skin, plastic skin, waxy skin, CGI crowd, cloned crowd, anime, cartoon, excessive camera movement, wrong sport, wrong venue
```

## Quality gate

Before returning:

- The selected endpoint and schema were verified with genmedia.
- GPT Image 2 edit used `quality=high` and `image_size={"width":3840,"height":2160}`
  unless the user explicitly requested an economy or preview run.
- If the input was a person photo, a GPT Image 2 edit frame was generated and
  approved before Kling. The raw person photo was not sent directly to Kling as
  the fan-cam start frame.
- Kling used `fal-ai/kling-video/v3/pro/image-to-video` unless the user
  explicitly requested economy/preview or native 4K video.
- Multi prompt durations are each at least 3 seconds.
- Total duration is 15 seconds or less.
- Top-level Kling duration equals the sum of beat durations.
- Every beat references `@Element1` when a real Kling `elements` entry is used.
- No invented extra elements were added.
- Kling request uses `generate_audio=true`.
- Kling request does not combine `multi_prompt` with `end_image_url`.
- Any intended external narration is not lip-synced to the featured spectator;
  verify the mouth does not move like the voice belongs to the person on camera.
- The generated frame is below Kling image limits. If not, compress it.
- The person remains recognizable and not beautified.
- The broadcast bug and scoreboard are small and stable enough.
- Final files were downloaded with `--download`.

Return a compact manifest with endpoint IDs, request IDs, model settings,
prompts used, output URLs, downloaded files, and any visible defects.
