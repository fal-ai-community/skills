# Fan cam prompt contract

Use this reference to write the generated frame prompt and Kling multi prompts.

## Planning contract

Inputs:

- User photo URL or uploaded URL.
- Event details.
- Reaction or situation.
- Budget or quality target, only when the user explicitly gives one.

The user photo is the identity reference. It is not a finished fan-cam frame.
When the input is an ordinary person photo, the image-generation step must use
`openai/gpt-image-2/edit` to create the broadcast scene before any Kling run.

Outputs to produce before running models:

```json
{
  "plate_prompt": "...",
  "image_prompt": "...",
  "image_quality": "high",
  "image_size": { "width": 3840, "height": 2160 },
  "kling_endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
  "beats": [
    { "duration": "3", "prompt": "..." }
  ],
  "total_duration": "..."
}
```

Rules:

- `beats.length` must be 2 to 5.
- Every beat duration must be at least 3 seconds.
- Total duration must be 15 seconds or less.
- Default GPT Image 2 edit quality is `high` with a 3840x2160 16:9 frame.
  Use `low` only for explicitly requested economy or preview runs.
- Default Kling endpoint is `fal-ai/kling-video/v3/pro/image-to-video`. Use
  Standard only for explicitly requested economy or preview runs. Use native
  4K only when explicitly requested for final video delivery.
- If using a real user-provided or approved Kling `elements` entry, every beat
  prompt must reference `@Element1`. Do not invent extra elements just to
  satisfy this pattern.
- Do not expose internal planning text to the user unless they ask for prompts.

## Image prompt build order

1. Identity reference.
2. Event context.
3. Spectator situation or reaction.
4. Broadcast composition.
5. Sport-specific overlay.
6. Channel bug.
7. Realism texture.
8. Negative constraints.

Do not treat the identity photo as a `start_image_url` for Kling. The image
prompt must turn that photo into a realistic 16:9 spectator broadcast frame.
The approved generated frame becomes the Kling `start_image_url`.

For difficult or high-fidelity shots, use a plate prompt first:

```text
Create a horizontal 16:9 4K realistic live [sport] broadcast crowd cutaway.
[Venue and crowd context]. Put one ordinary [gender-neutral/adult] spectator
placeholder in the [center/center-left/center-right] safe area, full head and
upper torso visible, same scale and softness as nearby fans, watching the
[court/pitch/track/ring] rather than posing. Add compact lower-corner
scoreboard text: [EXACT SCORE]. Add a small top-right [BROADCASTER] bug. Use
long-lens TV compression, foreground occlusion, natural venue lighting, and
imperfect background faces. No portrait framing, no oversized graphic, no
warped scoreboard text, no large readable apparel or sponsor marks.
```

Then use an identity edit prompt:

```text
Use the first image as the locked broadcast scene. Use the second uploaded
image as reference for the [position/wardrobe] spectator only. Adapt that
seated spectator to match the reference through overall appearance, age range,
hairstyle, glasses if present, facial hair if present, and clothing color. Keep
the same seat position, body scale, long-lens softness, venue lighting, crowd
layout, foreground occlusion, broadcaster bug, and exact scoreboard. Output one
horizontal 16:9 4K realistic live TV crowd screenshot. Avoid portrait framing,
edge crop, pasted cutout look, glamour retouching, oversized graphics, and
warped scoreboard text.
```

## Reaction mapping

Use the selected reaction as visible physical direction:

- Excited: alert eyes, lifted cheeks, energized shoulders, forward lean.
- Happy: natural smile, relaxed face, warm eyes, open posture.
- Laughing: candid mid-laugh, cheeks raised, mouth naturally open, body tilted
  toward friends or the event.
- Sad: downcast eyes, deflated shoulders, closed mouth, disappointed stillness.
- Neutral: calm face, minimal expression, steady gaze.
- Angry: narrowed eyes, tense jaw, restrained complaint, no aggression.
- Surprised: raised brows, wider eyes, slight head turn, caught off guard.
- Nervous: stiff shoulders, tight mouth, fixed stare, small hand tension.
- Focused: locked eyes, minimal mouth movement, concentrated posture.
- Eating or drinking: preserve candid broadcast realism. Keep food or drink
  ordinary and sport-venue plausible, not a comedy prop unless requested.

Blend reaction with event logic. A tennis spectator may be restrained; a
basketball or football fan may be more animated; a combat sports crowd may be
tense; a racing grandstand may track fast offscreen motion.

## Scene archetypes

Pick the archetype that best matches user details:

### Classic spectator cutaway

The person watches the event naturally, unaware or barely aware of the camera.
Use 2 or 3 beats.

### Caught-on-camera moment

The person is eating, drinking, talking to a friend, holding a scarf, checking
the big screen, or reacting at the exact wrong or funny moment. Keep it candid,
not slapstick. Use 3 or 4 beats.

### Stadium screen or broadcast feature

The person notices the stadium screen or broadcast camera. Use subtle
recognition, not a staged pose. Use 4 or 5 beats.

### Tense match moment

The offscreen event intensifies. Crowd motion rises around the person while
the person stays nervous, focused, surprised, or disappointed. Use 3 to 5 beats.

### Celebration or disappointment

The surrounding crowd erupts or deflates. The person reacts in a natural way
that matches the chosen reaction and the sport. Use 3 or 4 beats.

## Beat patterns

Choose the smallest useful pattern.

### 6 seconds, 2 beats

1. Establish the broadcast cutaway.
2. Subtle reaction and crowd rise.

### 9 seconds, 3 beats

1. Establish the exact cutaway.
2. Reaction-specific motion.
3. Camera correction or crowd rise.

### 12 seconds, 4 beats

1. Establish the cutaway.
2. Person reaction or situation detail.
3. Broadcast camera push, pan, or sidestep.
4. Event-specific crowd response.

### 15 seconds, 5 beats

1. Establish the cutaway.
2. Person micro-motion and nearby crowd.
3. Broadcast reframing or tighter angle.
4. Offscreen event tension or reveal.
5. Crowd reaction peak or held final moment.

## Kling beat prompt template

```text
Use @Element1 as the exact [sport] live broadcast cutaway. Preserve [person,
wardrobe, crowd, seat layout, overlay, top-right channel bug, lighting]. Animate
[beat-specific movement]. Keep [reaction] natural and candid. No face morphing,
no beautification, no unstable text, no wrong sport.
```

Use `@Element1` only when a real approved `elements` entry is in the payload.
Otherwise say "the featured spectator in the start image" or equivalent. Keep
prompts concise. Do not list every constraint in every beat. Put the highest-
risk continuity constraints in each beat: identity, overlay, channel bug,
crowd layout, and reaction.

## Audio and voiceover contract

- Kling requests in this skill must use `generate_audio=true`.
- Do not combine `multi_prompt` with `end_image_url`.
- Do not invent extra Kling elements. Use `elements` only for real
  user-provided or approved references.
- Do not write external narration as dialogue from the featured spectator.
- If using Kling native audio for a line, phrase it as an off-screen broadcast
  commentator, arena PA voice, or non-diegetic voiceover and add: the featured
  spectator stays silent, lips do not move, no lip sync.

Good native-audio pattern:

```json
{
  "duration": "6",
  "generate_audio": true,
  "shot_type": "customize",
  "cfg_scale": 0.32,
  "start_image_url": "<approved 16:9 spectator frame>",
  "multi_prompt": [
    {
      "duration": "3",
      "prompt": "Use the start image as the same live NBA timeout crowd shot. The featured spectator is silent and watches the missed t-shirt cannon moment with a small amused reaction. No visible person speaks."
    },
    {
      "duration": "3",
      "prompt": "Keep the camera on the same spectator and crowd. An off-camera arena PA or crowd-mic voice from the venue says, \"that was close!\" It is not the spectator speaking; no lip sync, no mouth movement matching the words."
    }
  ],
  "negative_prompt": "featured spectator speaking, lip sync, lips moving to narration, mouth forming words, on-camera subject says the line, dialogue from visible fan, visible fan voice, face morphing, unstable scoreboard, wrong sport, camera leaving crowd, end image url"
}
```

## Overlay guidance

Use overlays only when they improve realism:

- Football: score, clock, half or match time.
- Basketball: team abbreviations, score, quarter, game clock.
- Tennis: player names, sets, games, point score.
- Racing: timing tower or position strip.
- Combat sports: round and clock.
- Esports: match HUD or lower-third style, not overloaded UI.

Use a small top-right broadcast bug:

- Generic, sport-specific, and short.
- Prefer 1 to 2 words plus LIVE when useful.
- Keep it secondary to the spectator.
- If the user supplies an exact approved network logo or asks for a named
  network, preserve it as a small broadcast bug. Otherwise use a generic bug.

## Realism checklist

The frame should have:

- Professional TV lens, not phone selfie.
- Slightly compressed broadcast feed texture.
- Natural venue light, not glamor lighting.
- Foreground occlusion from heads, shoulders, railings, cups, or scarves.
- Imperfect but believable background faces.
- Ordinary posture.
- Sport-specific crowd behavior.
- Scoreboard and channel bug small enough to feel like TV, not a poster.
- Person fully inside the frame, not at an edge.
- Scoreboard includes actual teams or names from the brief.
- No large readable apparel or sponsor marks dominating the shot unless the
  user explicitly supplied or requested them.
