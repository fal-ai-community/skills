# Video Generation

A routing skill, not a pipeline. Nine intents, each with a primary endpoint and
a named fallback: identify the intent, settle the settings that drive cost,
submit, poll, hand back the file. Anything needing a bespoke multi-stage
workflow belongs to a sibling skill.

## Hand off instead of routing here

- **A new camera angle on an existing shot** — same subject, same moment, new
  viewpoint: re-angle a frame of the shot as **character-sheet** does for angle
  variants (`fal-ai/qwen-image-edit-2511-multiple-angles`), or with the
  image-edit pick from `recommend_model`; check it, then animate it on the
  image-to-video row below.
- **Two or more characters staged across several clips** — who stands where and
  faces which way, held across shots that never see each other: write each
  character's screen side, facing and eyeline into every shot's row and keep
  them identical across cuts (see **fal-shot-craft**, continuity anchors). To
  continue from a previous clip, extract its last frame and pass it as
  the route's start-frame field on the image-to-video row (`image_url` on H3,
  Seedance and Veo; `start_image_url` on Wan and Kling v3 pro; Flux 3 also needs an end frame).
- **Captions burned onto a finished cut**: word timings from scribe-v2 as
  described in **fal-audio-generation** (transcribing the cut's demuxed audio,
  so a transcript is never a prerequisite), grouped per the "Caption cues" rule
  in **fal-motion-graphics**, burned in the sandbox per **video-compositing**.
  Captions and any other on-screen text owed on the same file burn in one pass,
  in one skill. Never invent caption copy for a commercial asset.
- **Resizing a finished still creative to platform specs**:
  `prepare_media_transform` only upscales, cuts out or downscales a still — it
  does not change its aspect ratio. Recompose it with an image edit that sets
  `aspect_ratio` (`recommend_model` with the image attached), say it was
  regenerated, and check copy and logo against the source. Reframing a *video*
  stays here.

Route here whenever none of those claims the request.

**What handing off means, mechanically.** Find the sibling with
`search_guidance` and load it with `read_guidance` (`kind: "skill"`, plus the
`id` and `version_id` that search returns; the skill name alone does not load
it), then
follow that document for the item it owns, and
tell the user in one line which item went to which skill. If the sibling is not
installed or will not load, do not quietly build the thing yourself: name the
skill the job needs, and offer a substitute only if you label it explicitly as
not the specialist output.

**A request can split.** One message can hold items this skill owns and items a
sibling owns — that is the normal case, not an edge. Do the owned items in
full, hand the rest off, and close out by naming the file being passed onward
and anything the sibling still needs.
If every item hands off, stop there — the submit and delivery steps below are
n/a, and forcing an output into existence to satisfy them is the bug.

**A delegated step still imposes an order.** Extend, reframe, restyle and
upscale re-render every pixel, so anything burned into the frame — captions,
timestamps, watermarks, lower-thirds — does not survive passing through them.
On-screen text is burned **last**, after every re-rendering step, whatever order
the user listed the asks in. If the user wants captions first and a reframe
second, reorder the plan and say so in one line; following the stated order
silently ruins the text and neither skill will own the failure.

**This paragraph was already here when a production run dropped its on-screen
text entirely** — the script specified lower-thirds, every clip rendered, and the
words never appeared, because "burn last" told nobody to burn *at all*. An
ordering rule is not an owner. So the obligation is now explicit and it is
yours: when a request carries on-screen text and you are handing the burn-in to a
sibling, **your closing line must name the text still owed, and the file it is
owed on**, in the same sentence that names the file you are passing over. "Handing
`cut-final.mp4` to video-compositing; owed in that one burn: voiceover captions and lower-thirds NINE FATHOMS,
FREE SHIPPING, ninefathoms.co.uk, burned after this reframe, not before." A
hand-off that names the file but not the debt is how the debt disappears — and
if no sibling is available to burn it, the text is an undelivered part of the
request and you say so, rather than delivering silent footage as complete.

## Cost comes first

Video bills **per second of generated output**, not per call. One
default-length clip costs more than a whole image pack, and the same prompt at
8s/audio-on can cost several times what it costs at 4s/audio-off.
**Four** multipliers run at once here. **Duration** is linear — 8s is exactly
twice 4s, and every generation primary stops at 15s, so a careless `duration` is
a nearly 4× overspend. **Resolution** is roughly linear and then a cliff: the H3
Max primaries serve `480P`/`768P` (fal's routing), and an exact 2K/4K take
leaves Max for base `minimax/h3/*`; Veo 3.1 Fast's 4k rate is
$0.30/s silent and $0.35/s with audio. **Audio** costs more only on Veo (about half again on Veo 3.1 Fast at
720p/1080p, double on full Veo 3.1) and Kling (+50–75%), and it is
**on by default on every Seedance and Veo route, both LTX 2.5 routes, both Kling v3 pro routes,
Flux 3 first-last-frame and the Wan 3.0 Prime routes (there the field is
`audio`)**, so it is the multiplier most likely to be paid by accident. H3 routes have no audio switch.
**Route** is the fourth and the one under your control before a single frame
renders: on H3 Max, reference-to-video can bill differently from text or image,
so price the route you will actually send.

**Price the tier you send.** `get_pricing` returns one unit price per endpoint
for the account you are working in, which is a single tier (on H3 Max, the
480P rate; on Veo, the with-audio rate), not a split by resolution or audio.
Call it to confirm the account's rate, and quote the tier you will actually
send from the published per-tier rates below, saying which tier the quote
assumes. Where the table below has the route, quote its tier and use
`get_pricing` only as a check: a unit price that matches no tier (or is 0) is
noted as "`get_pricing` returns a different unit price", not quoted. For a
route not in the table, quote the per-tier rate in that route's own block where
one is given, else `get_pricing`'s rate. When neither gives a price for a route, say the cost is unknown and
show the confirmation card. A missing price never changes the route choice.

Published per-tier rates, from the fal model pages on 2026-10-28 (they change):

| Route | Per second of output |
|---|---|
| H3 Max text, image | $0.0325 at 480P, $0.052 at 768P, $0.104 at 1080P (promotional until Oct 31, then $0.05 / $0.08 / $0.16) |
| H3 Max reference | $0.05 at 480P, $0.08 at 768P, $0.16 at 1080P, plus reference tokens past 4,096 at $0.02 per 1,000 |
| Seedance 2.5 (`/us`) | about $0.2205 at 480p, $0.473 at 720p, $1.164 at 1080p ($0.0214 per 1,000 tokens at 480p/720p, $0.0234 at 1080p; tokens ≈ height × width × seconds × 24 ÷ 1024, and video references add their input seconds, with the whole price then ×0.6, about $0.2838/s at 720p); same with or without audio |
| Wan 3.0 Prime | $0.068 at 480p, $0.14 at 720p, $0.28 at 1080p |
| LTX 2.5 pro | $0.12 at 720p, $0.17 at 1080p |
| Kling v3 pro | $0.112 silent, $0.168 with audio, $0.196 with voice control |
| Flux 3 first-last-frame | $0.17 at 720p, $0.29 at 1080p |
| Ray v3.2 reframe | $0.06 at 540p, $0.12 at 720p, $0.36 at 1080p, per started source second |
Never inherit a number from the route a pick replaced. A quote carrying a stale
rate is worse than no quote: it reads as verified.

Two routes bill on something other than output seconds. **Reframe bills the
input** — `fal-ai/ltx-2.3/reframe` charges on the source's duration, so a 30s
clip is a 30s bill however trivial the reframe. **SeedVR bills megapixels** —
$0.001 per `width × height × frames`, so length and frame rate multiply.

**Quote before you spend.** Compute `rate × seconds` for the chosen route and
put the figure in the intake card. Ask before submitting whenever the estimate
clears roughly $1, the user named no duration, or the request is exploratory.
For a re-run of an approved shape — same route, same length, new prompt — skip
the card and go.

**A chained job is quoted per step, and ordered by what each step bills on.**
Chained video work is the normal case, not the exception. Quote one line per
paid route plus a running total, and gate the card on the total, not on any
single line — two sub-$1 steps that sum past $1 still get the card. When a
later step's bill depends on an earlier step's *output* (reframe bills its
input's duration, so reframing an extended clip costs more than reframing the
original), compute it from the planned output length and mark it an estimate.
Then sequence for cost: extend pays only for new seconds while reframe pays for
the whole source, so reframe-then-extend is cheaper than extend-then-reframe —
unless the un-reframed extended cut is itself a deliverable, in which case the
user's order stands. Say which order you chose and why in the quote.

**Draft when the concept is unproven.** `fal-ai/veo3.1/lite` (720p) is the
low-cost Veo route for a short test before you commit to a long finish; price it
with `get_pricing`. Two
caveats now that the primaries are H3 Max. It is **Veo's** prompt grammar, so a
draft that works there is evidence about the shot, not about the wording you will
send to H3 Max. And the primary has its own draft lane: H3 Max at `480P` keeps the
final route's grammar, so prefer it unless Veo lite is clearly cheaper for the
length. Compare H3 Max's unit rate with Veo lite's `get_pricing`
rate, which is its with-audio rate; send `generate_audio: false` and say the
silent rate is lower.

## Step 0 — One intake card

Call `ask_user_questions` **once** (if your host has no question tool, ask the same questions in one plain message and wait for the
reply before spending; that reply counts as the card), carrying only the questions still
unanswered. Every field has a default; if the request already answers one, drop
that question rather than asking it back.

   These are the **user-facing** options. Every one of them is spelled differently
   per route, so read the route's block before building the payload: what the card
   offers and what the endpoint accepts are two different vocabularies, and the
   card must never offer a value the chosen route cannot take.

1. **Duration** (header `Length`) — default **4s**, deliberately short. Offer
   `4s`, `6s`, `8s`, plus free text where the route takes arbitrary integers,
   and put each option's dollar cost in its option text. **On the wire the
   spelling differs**: H3 Max wants a number of seconds (`4`, decimals allowed,
   0.92–15), base MiniMax H3 an integer 5–15, Seedance a bare string `"4"`, Veo
   `"4s"`. The card's `4s` is a label, not a payload value. Every generation
   primary stops at 15s; a longer ask is a routing change, not a bigger number:
   up to 30s goes to `bytedance/seedance-2.5/us/*`; with both end frames,
   16–20s goes to Flux 3 first-last-frame and 21–30s to
   `bytedance/seedance-2.5/us/image-to-video` with `end_image_url`.
2. **Resolution** (header `Resolution`) — default **768P** on the H3 Max
   primaries (`480P` for drafts; fal's routing serves Max at these two), and
   exact `2K`/`4K` only as a move to base `minimax/h3/*`. A `1080p` ask goes to
   H3 Max `1080P`, which refines a native 768P render; say so, and say that the
   routing does not cover it. Decide resolution before you decide the fallback,
   not after.
3. **Aspect** (header `Shape`) — default **16:9**, with `9:16` for vertical and
   `1:1` only where supported. H3 Max text-to-video takes `21:9`, `16:9`, `4:3`,
   `1:1`, `3:4`, `9:16`; reference-to-video adds `adaptive` (its default); the
   image route has no aspect field and follows the supplied frame, so on H3 Max
   image-to-video drop this question unless the user asked for a shape; if the
   asked shape differs from the still, recompose the still first with an image
   edit that sets `aspect_ratio` (as the still-resize hand-off does), say so,
   then animate. On other
   image routes, `auto` inherits the source frame; naming an aspect that differs
   from the source re-composes rather than reframes, so if the user wants the
   *same* footage in a new shape that is a reframe job (see the guardrail).
4. **Audio** (header `Sound`) — default **off**. On means a native soundtrack
   generated with the video; Veo and Kling charge more for it, while Seedance,
   LTX 2.5, Flux 3 and Wan bill the same either way. H3 routes have no
   audio flag, so this card applies only when the pick is a Seedance, Veo, LTX 2.5, Kling,
   Flux 3 or Wan route. On H3 there is no switch; skip the card and say that
   any soundtrack the route returns is discarded unless the user wants it.
5. **Motion brief** (header `What happens`) — free text; default is to derive it
   from the supplied image or the user's sentence and echo that derived brief
   back inside this same card for confirmation.
6. **Framing** (header `Framing`, conditional) — only when the request could
   mean either a generative reframe or a free crop (see the guardrail): offer
   both with the dollar figure on the paid one. The guardrail's default applies
   if this goes unanswered; it never blocks on the answer.

The five standing headers fit a single-route job. A real request can raise
questions none of them ask — reframe-versus-crop, what to do about an item that
hands off to a sibling — and those go on the **same single card** under their
own headers. Adding a needed header is correct; spending a second card is not.

If the brief answers everything and the estimate is under $1, make **zero**
`ask_user_questions` calls and submit. If it answers everything but the estimate
clears $1, still show a single one-question confirmation card carrying the
figure. Never treat a spend as confirmed without a reply: use the card (on a host with no question tool, one plain message, then wait for the reply).

When the answer to a priced question is a preference rather than one of the
offered options ("keep it roughly as it is, no upscaling"), map it to the
nearest option that honours the preference, state the mapping and its price in
the delivery note, and proceed — do not spend a second card re-asking.

## Routing table

Every row was checked against a live schema. Fallbacks are named, not implied.
A pure restyle stays on the Restyle row even when `recommend_model` returns H3
Max reference. The H3 Max primaries follow fal's published routing (`recommend_model` returns
these picks, plus others such as LTX 2.5 for fast subject motion, with an
input contract). Use `recommend_model`'s pick when it differs from the row's
primary only because of a capability it names (for example LTX 2.5 for fast
subject motion: `fps: 50`, 720p or 1080p, `duration` `6`, `8` or `10` sent
explicitly since it defaults to `auto`, `resolution: "720p"` for a `480P` or
`768P` shot since it defaults to `1080p`, `generate_audio` sent explicitly;
only when the shot is 10s or less and `16:9` or `9:16`, rounding the duration
up to 6, 8 or 10 and re-quoting, otherwise keep the row's primary); the Restyle, Extend,
Upscale and Reframe rows and the moderation rule always win.

| Intent | Primary | Fallback | Why the primary wins |
|---|---|---|---|
| Text to video | `minimax/h3-max/text-to-video` | `minimax/h3/text-to-video` | fal's published default for every unnamed video request up to 15s; base H3 is the exact 2K/4K route and the fallback when Max can't serve |
| Image to video | `minimax/h3-max/image-to-video` | `minimax/h3/image-to-video` | Published default for one starting still; the canvas follows the supplied frame |
| First and last frame | `minimax/h3-max/image-to-video` | `blackforestlabs/flux-3/first-last-frame-to-video` | Same endpoint as image-to-video — add the optional `end_image_url`; Flux 3 when both ends must be *required*, or 16–20s (21–30s → `bytedance/seedance-2.5/us/image-to-video` with `end_image_url`) |
| Reference to video | `minimax/h3-max/reference-to-video` | `minimax/h3/reference-to-video` | Published default for image/video/audio references and footage edits other than a pure restyle: `reference_image_urls` (max 9), `reference_video_urls` and `reference_audio_urls` (max 3 each), 12 files total; audio can't be the only reference |
| Restyle footage | `decart/lucy-edit/pro` | `fal-ai/luma-dream-machine/ray-2/modify` | Purpose-built video edit; Ray adds adherence control |
| Extend a clip | `fal-ai/ltx-2.3/extend-video` | `fal-ai/veo3.1/fast/extend-video` | Only route that honours an arbitrary length (2–20s, either end); Veo extend is locked to exactly +7s at 720p |
| Upscale | `fal-ai/topaz/upscale/video` | `fal-ai/seedvr/upscale/video` | Per-second billing is predictable; 19 restoration models |
| Reframe to new aspect | `fal-ai/ltx-2.3/reframe` | `luma/agent/ray/v3.2/reframe` | Needs no prompt; Ray adds `3:4`, `4:3` and `21:9` and takes a prompt, but drops LTX's `4:5`/`5:4` — the enums overlap, neither contains the other |
| Add sound to a clip | `sonilo/v1.1/video-to-video-sound-effects` | `fal-ai/kling-video/video-to-audio` | Returns a muxed video at $0.009/s; Kling is flat $0.035 |

**Route on content as well as on intent, and do it on the first attempt.** The
table above picks a route by *what kind of job* it is. One thing overrides it:
**moderation exposure.** A frame carrying a photorealistic human likeness — a
supplied face, a realistic person as the subject — or heavy gore-adjacent imagery
can be refused, and the families differ in what you can do about it. Veo 3.1
exposes **`safety_tolerance`**, a string `"1"`–`"6"`, so a refusal there has a lever.
**No Seedance route exposes any moderation field at all**: its filtering is
server-side and undocumented, so a refusal has no remedy except changing route.
The H3 Max primaries expose only `enable_safety_checker` (default `true`); how
they treat photoreal faces is not mapped here, so record a refusal you hit
rather than assuming either way.

**Veo fit test:** a shot fits Veo 3.1 Fast when it is 8s or less, `16:9` or
`9:16`, with image references only (`image_urls`), no `target_audio_url`, no
middle or exact first/last frame on a reference row, and both frames present
for a first-last shot (an image-route shot fits when its still is `16:9` or
`9:16`). Round the duration up to `4s`, `6s` or `8s`
(reference-to-video is always `8s`); send `720p` for a 480P/480p/720p/768P shot,
`1080p` for 1080P/1080p, and `4k` for 2K/4K (re-quote); send `generate_audio` per the Sound or Clip audio
answer (no answer → `false`); send `safety_tolerance` at its default `"4"` and
never raise it to get past a refusal. When the pick is a **Seedance** route, a
moderation-sensitive shot that fits goes to Veo 3.1 Fast from the start; one
that does not fit is tried once on Seedance. Any other pick (H3 Max, base H3,
Wan, Kling, Flux 3, LTX) is tried once: a refusal moves a fitting shot to Veo
3.1 Fast and counts toward the retry ceiling; a refusal on Veo, whether the shot went
there first or was moved there, ends the shot, and a refused shot is never retried with `enable_safety_checker:
false`. A moderation refusal is not a
"Max can't serve" case: it never goes to base H3 or the cross-family escapes,
and a refused shot that does not fit Veo stops; offer the user a re-cut that
fits Veo, a rewritten shot, or dropping it. One run spent **three
separate rounds of 422s** discovering this by collision — refused on a photoreal
human reference, re-prompted, refused again on a skull-heavy frame — because
route-by-content was treated as a repair rather than a first-pass decision. A 422 on
a route with no tolerance control is not a transient failure to retry; it is the
wrong route, and the retry ceiling below applies to it.

*Observed on the Seedance 2.5 family. The 2.0 routes have the same absent
field, so the same reasoning holds, but the specific refusals were measured on 2.5
— treat the boundary as unmapped rather than known, and record what you hit.*

**Three of the four generation fallbacks are same-family on purpose — and that
is a known limit, not an oversight.** Base H3 is the right fallback for an exact
2K/4K ask or a request Max can't serve, and it needs little prompt rewriting
because the grammar is shared. Its payload is not shared: base H3 takes
`duration` as an integer from 5 to 15 and defaults `resolution` to `2K`, so
round the duration up to a whole number of at least 5 (a 4s or 4.5s card value
becomes `5`) and send `resolution` explicitly. It is the *wrong* fallback for a family-wide
outage or a capability the family lacks. When MiniMax as a whole is unavailable
or cannot do the job, the cross-family escapes are
`bytedance/seedance-2.5/us/text-to-video` (fal's published Seedance pick) and
its `/image-to-video` and `/reference-to-video` siblings (see the Seedance 2.5
block below),
`alibaba/wan-3.0-prime/text-to-video`, `/image-to-video` or
`/reference-to-video` when a request's inputs fit nothing else (and always
`/reference-to-video` with `file_url` or `web_url` plus `enable_thinking: true`
for document or webpage conditioning), and
`blackforestlabs/flux-3/first-last-frame-to-video` for 16–20s with both end
frames. Say which you took
and why. Never retry the same family a third time — see the retry ceiling below.

**Lipsync is deliberately absent.** A talking head driven by supplied speech is
a different job — search the registry for `lipsync` and read the schema first,
because those endpoints bill on *input* seconds.

## Per-endpoint parameters

These endpoints disagree constantly. Read the block for the route you take.

**Negative prompts do not travel.** This census is exhaustive for the table
above, so a route in neither list is a route this table does not carry.
Accepts `negative_prompt`: Veo 3.1's text, image, first-last, **extend** and
**lite** routes, and both Kling v3 pro routes. Does not: **every Seedance 2.5
route**, every Seedance 2.0 route, every Wan 3.0 Prime route, both LTX 2.5 routes, Flux 3
first-last-frame, both Veo reference routes, every MiniMax H3 route, and all
the restyle, reframe, upscale and sound routes.
Where the field is absent, carry the avoidance as a positive clause in the
prompt itself — "empty concrete floor" rather than "no furniture" — and tell the
user the exclusion is unenforced on that route. Never append a negative list to
a positive prompt; that asks for exactly what you were avoiding.

**`minimax/h3-max/text-to-video` · `/image-to-video` · `/reference-to-video`** —
the primaries. `prompt` and `prompt_expansion_mode` are required:
`disabled`, `balanced` (default, about a second) or `quality` (up to ~30s);
send it explicitly, and use `disabled` when the prompt was already written to a
validated format such as **h3-cinematic-prompter**. `duration` is a **number**
from 0.92 to 15, default `5`; the output can run about 0.7s longer than asked.
`resolution`: fal's routing serves Max at `480P` or `768P` (default); the
schema also lists `1080P`, a refinement of a native 768P source, which the
routing does not cover. Text-to-video takes `aspect_ratio` (`21:9`, `16:9`, `4:3`, `1:1`,
`3:4`, `9:16`; default `16:9`). The image route takes optional `image_url` and
`end_image_url` and **no aspect field** — the canvas follows the first frame,
or the last when only that is given. Reference adds `aspect_ratio` with
`adaptive` (default), `image_url` as an exact first frame, `end_image_url`, and
`middle_image_url` with `middle_frame_time` (needs `image_url` and
`end_image_url`, and 480P or 768P); refer to references in the prompt
as Image 1, Video 1, Audio 1. `reference_conditions` is an ordered alternative
to the `reference_*_urls` arrays; never combine the two. `target_audio_url`
(text and image routes) pins a supplied clip of at least 2s as the soundtrack.
**No `negative_prompt` and no audio switch.** `enable_safety_checker` defaults
`true`.

**`bytedance/seedance-2.5/us/text-to-video` · `/image-to-video` ·
`/reference-to-video`** — the cross-family fallback. fal's routing picks it
for text-to-video; the image and reference siblings are this skill's choice.
`prompt` is required on text-to-video; the image route requires `image_url`
(prompt optional) and takes an optional `end_image_url`; reference carries
`image_urls`, `video_urls` and `audio_urls` arrays and a `task` enum
(`reference` default, `editing`, `extension`, `auto`). **`duration` is a string
enum** — `"auto"` (default) and `"4"` through `"30"`. `resolution` is `480p`,
`720p` (default) or `1080p`; there is no 4k. `aspect_ratio` defaults to `auto`
(and is fixed to `auto` on image-to-video).
`generate_audio` **defaults `true`**, and there is no `negative_prompt`. Billing
is per 1,000 tokens, so read the rate with `get_pricing` and price the exact
length and resolution before sending.

**`bytedance/seedance-2.0/text-to-video` · `/image-to-video` ·
`/reference-to-video`**, and their `/fast/` and `/mini/` siblings — an
alternative to 2.5 that fal's routing no longer picks; use it only when it is
named or 2.5 cannot serve the request. Only the base tier reaches `4k`. `prompt` required on
all of them; `image_url` also required on the image routes. **`duration` is a string enum of bare integers** —
`"auto"` (default) and `"4"` through `"15"`, one per second. Note the shape: it is
`"4"`, **not** `"4s"`. Veo's `"4s"` spelling 422s here, and a pre-flight that
checks the field *name* will not catch it (rule 20). Past 15s leaves this family
entirely. `aspect_ratio` is the widest enum in the table and is identical on all
three routes: `auto`, which is the default, plus `21:9`, `16:9`, `4:3`, `1:1`,
`3:4` and `9:16`. On an image route the default inherits the source frame's own
ratio rather than imposing one. `generate_audio` **defaults
`true`** on every tier. **No `negative_prompt` field exists** on any of them.
First-and-last-frame is this same image-to-video endpoint with the optional
`end_image_url` added — unlike Flux 3, where both ends are required.
Reference-to-video carries `image_urls`, `video_urls` and `audio_urls` as separate
arrays.

**The tiers differ in exactly two ways, and one of them is a routing decision.**
`resolution` on the **base** routes is `480p`, `720p`, `1080p` or `4k`, default
`720p` — the only Seedance routes that reach 4k. On both `/fast/` and
`/mini/` it is `480p` or `720p` only, so *a request above 720p cannot be served by
the fallback column* — it stays on base or leaves the family. `bitrate_mode`
(`standard` default, or `high`) exists on base and `/fast/` but **not on
`/mini/`**; it raises quality at the same resolution, and therefore the bill.
Everything else — duration enum, aspect enum, audio default, required fields — is
identical across all three, which is why `/fast/` needs no prompt rewriting.

**`alibaba/wan-3.0-prime/text-to-video` · `/image-to-video` ·
`/reference-to-video`** — text requires `prompt`; image requires
`start_image_url` (not `image_url`); reference takes `reference_image_urls`
(up to 10), `reference_video_urls` and `reference_audio_urls` (up to 5 each,
15 s total each), and `file_url` or `web_url` with `enable_thinking: true` for
document or webpage conditioning. `duration` is an integer from 2 to 30,
default `5` (null lets the model choose; never send `null`, and round a decimal
card value up). `resolution` is `480p`, `720p` or `1080p` and **defaults to `1080p`**, so
send it explicitly. `aspect_ratio` defaults to `adaptive` (no `21:9`).
`audio` (not `generate_audio`) **defaults `true`**; `enable_prompt_expansion`
defaults `true`. See the per-tier rates above;
the `1080p` default is the most expensive tier.

**Rates are not in the OpenAPI schema for any Seedance tier.** Quote the Seedance 2.5 row above; for 2.0 tiers quote `get_pricing`'s token
rate with the same token formula, and never carry a figure over from a route this one
replaced. A quote with a stale rate is worse than no quote: it reads as verified.

**`fal-ai/veo3.1/fast` · `/image-to-video` · `/first-last-frame-to-video`** —
no longer primary for any row (it takes shots refused on H3 Max and
moderation-sensitive shots that would otherwise go to Seedance); kept because it is the only 1080p/4k route here
with `negative_prompt` support, and the extend fallback's source.
`prompt` required. `duration` is a **string enum**: `"4s"`, `"6s"`, `"8s"`,
default `"8s"`. `resolution`: `720p`, `1080p` or `4k`, default `720p`. Aspect
on text-to-video is `16:9` or `9:16`; the image routes add `auto` and default
to it. `negative_prompt` accepted. `safety_tolerance` is a **string** `"1"`–`"6"`
(default `"4"`). `generate_audio` **defaults `true`**. `auto_fix` defaults
`true` on text-to-video, `false` on the image routes. Image routes need
`image_url`; first-last needs `first_frame_url` and `last_frame_url`.
**$0.10/s silent, $0.15/s with audio at 720p or 1080p; $0.30/$0.35 at 4k.**

**`fal-ai/veo3.1/fast/reference-to-video`** — `image_urls` (array) and `prompt`
required, `duration` a **`const` of `"8s"`** — this route makes 8-second clips
and nothing else, so any other length belongs elsewhere — aspect `16:9` or
`9:16` with no `auto`, and **no `negative_prompt` at all**. `generate_audio`
**defaults `true`**. Same rates as above. The non-fast
`fal-ai/veo3.1/reference-to-video` is the identical shape at **$0.20/$0.40 per
second** — an 8s 1080p clip with sound is **$3.20**. Use it only on request.

**`fal-ai/veo3.1/fast/extend-video`** — the fallback, and a narrow one.
`video_url` and `prompt` required. `duration` and `resolution` are both OpenAPI
**`const`** values — `"7s"` and `"720p"` — so this route adds exactly seven
seconds at 720p and can do nothing else. Any extend for a different length, or
above 720p, goes straight to `fal-ai/ltx-2.3/extend-video`; reach for this one
only when the source is Veo's own output and +7s at 720p is acceptable, where
it continues natively. **Note what that precondition now means:** the generation
primaries are H3 Max, so a clip this skill produced itself is *not* Veo output
and this fallback does not apply to it. It is for a Veo clip the user brings in,
or one made deliberately via the Veo row. For everything else the extend fallback
is effectively `fal-ai/ltx-2.3/extend-video` alone — if that route is down, say so
rather than sending an H3 clip here. `aspect_ratio` is `auto`, `16:9` or `9:16` (default
`auto`) — never use it to get a vertical "for free": that re-renders the whole
source through the model, and the aspect change belongs to reframe. Extend
re-encodes the entire file either way — a source that is not exactly 16:9 comes
back rescaled (a 2544x1456 input returns 1920x1080), so even the untouched
seconds are not bit-identical. `negative_prompt` accepted. `generate_audio`
**defaults `true`**. You pay for the new seconds only: **$0.10/s silent,
$0.15/s with audio.**
**`fal-ai/veo3.1/lite`** is the Veo draft lane (see Draft above for when H3 Max
`480P` is preferred): same `"4s"`/`"6s"`/`"8s"` duration
enum as fast, `resolution` only `720p` or `1080p` (**no 4k**),
`negative_prompt` accepted, `generate_audio` again **`true`**, at **$0.03/s
silent and $0.05/s with audio at 720p**.

**`fal-ai/kling-video/v3/pro/text-to-video` · `/image-to-video`** — `duration`
is a **string enum of every integer from `"3"` to `"15"`**, default `"5"`: the
route for anything past 8 seconds. Text aspect is `16:9`, `9:16` or square
`1:1`; the image route has **no aspect field at all** and derives shape from
`start_image_url` (plus optional `end_image_url`, and an `elements` array whose
objects carry `reference_image_urls`, `frontal_image_url`, `video_url` and
`voice_id` — those four are element members, not top-level fields).
`negative_prompt` **ships with a non-empty default** —
`blur, distort, and low quality` — so replace it rather than appending.
`cfg_scale` 0.5; `shot_type` `customize` or `intelligent`; **no `resolution`
field**. `generate_audio` **defaults `true`**, and audio or voice control
raises the rate (see the per-tier rates above).

**`minimax/h3/image-to-video` · `/text-to-video` · `/reference-to-video`** —
`duration` is a plain **integer, bounded 5–15**, default `5` — a 4s ask is a
422, not a short clip. `resolution` is
`480P`, `768P`, `2K` or `4K` and **defaults to `2K`** — more than the `768P`
rate you likely budgeted, so send `768P` explicitly unless 2K was asked for.
`prompt_expansion_mode` defaults to `balanced` and rewrites your prompt;
`enable_safety_checker` also defaults `true`. The image route takes `image_url`
plus optional `end_image_url` and has **no aspect field**; text and reference
routes do, reference defaulting to `adaptive`. Reference takes three arrays —
`reference_image_urls` (max 9), `reference_video_urls` and
`reference_audio_urls` (max 3 each). **No
audio flag exists on any H3 route.** Read the rate per route with
`get_pricing`: it returns one unit price, not one per resolution, and may
return none for a route. Never auto-select base H3: fal's routing reserves
it for exact 2K/4K takes, a named request, or a request Max can't serve.

**`blackforestlabs/flux-3/first-last-frame-to-video`** — `start_image_url` and
`end_image_url` both required. `duration` is an **integer enum from 5 to 20**,
default `5`; `resolution` is `720p` (default), `1080p`, `1440p` or `2160p`
(above 720p is finished by an upsampler); the aspect enum is the widest
here, covering `auto`, ultrawide, wide, square and both verticals.
`safety_tolerance` is an **integer** (default `2`), unlike Veo's string.
`generate_audio` **defaults `true`** (same price either way). See the per-tier
rates above.

**`decart/lucy-edit/pro`** — `video_url` and `prompt` required. The `resolution`
enum holds **only `720p`**, so the cheaper 480p tier in the price list is not
reachable here. `enhance_prompt` **defaults `true`** and rewrites a restyle
instruction that was probably already exact — send `false` when it is precise.
`sync_mode` **defaults `true`**, blocking rather than queuing; send `false` for
anything beyond a few seconds. Read the rate with `get_pricing`.

**`fal-ai/luma-dream-machine/ray-2/modify`** — `video_url` required, `prompt`
and an `image_url` style reference optional. The lever is `mode`, a nine-value
enum: `adhere_1`–`adhere_3` stay close to the source, `flex_1`–`flex_3` (default
`flex_1`) allow moderate change, `reimagine_1`–`reimagine_3` change the most. No
duration or resolution field — it follows the source. Read the rate with
`get_pricing`.

**`fal-ai/ltx-2.3/extend-video`** — the general-purpose extend and the primary.
`video_url` required, `prompt` optional. `duration` is a plain **number,
bounded 2–20**, default `5` — the only extend route that honours an arbitrary
length. `mode` is `start` or `end` (default `end`) — also the only route here
that can prepend footage *before* a clip. `context` (1–20) sets how many source
seconds condition the continuation, and it is the only adherence lever this
route has — there is no cfg or mode-style control. Two consequences. Set
`context` so it covers only the final shot: if the source has an internal cut,
a window spanning the cut feeds the model a montage and invites it to cut
again. And when an extension wanders — an uninvited camera move, the subject
drifting out of frame, a fresh cut — the retry is `context` lowered (2 is a
working floor) plus a prompt that pins the camera explicitly ("locked, no
pull-back, no zoom, no reveal"), not the same payload resubmitted.
**$0.10/s of new video.**

**`fal-ai/topaz/upscale/video`** — `video_url` required, `upscale_factor` number
default `2`. `model` is a 19-value enum, default `Proteus`; the `Starlight`
family is the detail-synthesis tier and `Gaia 2` bills at half price. Optional
`target_fps` (16–60) — pushing past 30 doubles the bill. **$0.01/s for output to
720p, $0.02/s to 1080p, $0.08/s above 1080p; doubled at 60fps.**

**`fal-ai/seedvr/upscale/video`** — `video_url` required. `upscale_mode` is
`factor` (default, reads `upscale_factor`) or `target` (reads
`target_resolution`: `720p`, `1080p`, `1440p` or `2160p`, default `1080p`).
**$0.001 per megapixel of `width × height × frames`** — check the frame count
before submitting, not the running time.

**`fal-ai/ltx-2.3/reframe`** — `video_url` required. Aspect options are square,
`4:5`, `5:4`, and both `9:16` / `16:9`, defaulting to widescreen; `resolution`
is `720p` or `1080p` and **defaults to `1080p`, double the price**. There is
**no prompt field here** — a user instruction about what should fill the new
edges cannot be carried on this route, so either accept the model's own
extension or switch to the Ray fallback, which does take one. **$0.10/s at
720p, $0.20/s at 1080p, billed on the input's duration.**

**`luma/agent/ray/v3.2/reframe`** — `video_url`, `prompt` **and** the aspect
field are all **required**; the prompt is not optional here. Its aspect enum
adds portrait `3:4`, landscape `4:3` and `21:9` over LTX's, but **drops `4:5`
and `5:4`** — a 4:5 job cannot fall back here. `resolution` is
`540p`, `720p` or `1080p`, default `540p`; optional `source_position` places the
original inside the new frame. Billed per started second of source; see the
per-tier rates above and say which resolution the quote assumes.

**`sonilo/v1.1/video-to-video-sound-effects`** — `video_url` required, `prompt`
optional (describe the sound, not the picture), `segments` to time individual
effects, `audio_format` default `aac`. **$0.009/s of output per sample.**

**`fal-ai/kling-video/video-to-audio`** — `video_url` required, and **both
prompt fields ship with content-bearing defaults**: `background_music_prompt` is
`intense car race`, `sound_effect_prompt` is `Car tires screech as they
accelerate in a drag race`. Send both explicitly every time — omitting them does
not mean silence, it means a car chase. `asmr_mode` defaults `false`. **$0.035
flat per video.**

## Default-on flags to pin explicitly

Set each of these on the payload even when you want the default value, so the
intent is visible in the request.

- **`generate_audio: true`** on **every Seedance route, 2.0 and 2.5, at all three
  tiers**, on every Veo 3.1 route (fast, lite, image, first-last, reference,
  extend), on both Kling v3 pro routes and on Flux 3 first-last-frame, and
  `generate_audio: true` on both LTX 2.5 routes, `audio: true` on the Wan 3.0 Prime routes — that is every route here that can
  make sound (H3 has no audio switch).
  Veo and Kling charge 50–100% more for audio; Seedance, LTX 2.5, Flux 3 and
  Wan bill the same either way, so there `false` only drops an unwanted track. Step 0 defaults `Sound` to **off**, so on
  the default path you are always sending `false` explicitly, never by omission.
- **Prompt rewriters:** `prompt_expansion_mode: "balanced"` on every MiniMax H3
  and H3 Max route, `enhance_prompt: true` on `decart/lucy-edit/pro`.
- **Expensive resolution defaults:** `2K` on MiniMax H3 (billed above `768P`;
  read the rate with `get_pricing`) and `1080p` on `fal-ai/ltx-2.3/reframe`
  (double price).
- **`sync_mode: true`** on `decart/lucy-edit/pro` — blocks instead of queuing.
- **Non-empty text defaults:** `negative_prompt` on Kling v3 pro, and both
  prompt fields on `fal-ai/kling-video/video-to-audio`.
- **`duration: "auto"`** on every Seedance route. The 2.0 enum runs to `"15"`
  and the 2.5 enum to `"30"`. Never send `auto`: you are letting the model
  choose the bill, and on 2.5 the ceiling is more than 7× the 4s default.
  Always send an explicit value, and price it first.

## Model IDs drift — query, never remember

The table above is a snapshot. Endpoints get renamed, versioned and retired —
and fields get pinned. **Before the first submit of a session, print the
route's fields with their constraints, not just its name:**

```
curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<slug>" \
  | python3 -c "
import json,sys
doc=json.load(sys.stdin)
sch=(doc or {}).get('components',{}).get('schemas',{})
if not sch: print('UNRESOLVED'); sys.exit(1)
for n,s in sch.items():
    if n.endswith('Input'):
        print(n,'required:',s.get('required',[]))
        for f,p in s.get('properties',{}).items():
            print(' ',f,{k:p[k] for k in ('type','const','enum','default') if k in p})
"
```

`UNRESOLVED` means the slug is gone. Then **check every value the payload will
carry against the printed `const` or `enum`** — a check that only confirms a
field's name exists will pass a route that rejects your value. A `const` is not
a default you can override: `duration` on `fal-ai/veo3.1/fast/extend-video` is
a `const` `"7s"`, so a `"4s"` payload is a guaranteed 422 that field-name
pre-flight pronounces healthy. If a `const` or `enum` excludes the value the
job needs, the route cannot serve the request — move to the row that can before
building a payload. **If the slug fails, or the intent matches no row above,
search the registry rather than guessing a name:**

```sh
genmedia models "<intent words>" --json
genmedia pricing <verified-endpoint-id> --json
```

In a connected MCP host, use its model discovery/recommendation and pricing tools.
Check the caller's actual access before choosing a route. Then
read the new endpoint's schema for its real field names before building a
payload. Never assemble one from a sibling endpoint's parameters.

## Submit, poll, deliver

1. Fetch the schema for the settled route and build the payload from that
   schema's field names and enums only.
2. Submit one run. Do not fan out into variants unless the user asked for them
   and approved the multiplied cost — two 8s clips is two full bills.
3. Poll to completion. Video jobs run minutes, not seconds, and 1080p or 4k can
   take several — do not resubmit on slowness.
4. On a 4xx, read the error before retrying. A rejected enum or unknown field is
   a payload bug, not a transient failure — resubmitting unchanged fails again,
   while a queued-then-failed render may already have been billed.
5. **Check the clip moved, before you deliver it.** A generation route can return
   a technically valid video in which nothing happens — a frozen macro shot, a
   still in a video container — and every other check in this skill passes it,
   because they all ask whether the *source* survived. Liveness fails in the
   opposite direction from preservation and neither implies the other.
6. Deliver the URL, and state the route, final duration, resolution, whether
   audio was generated, the measured motion figure from step 5, and the actual
   cost.

### The motion check, and why the obvious version does not work

Decode every frame. Take the mean absolute luminance difference of each adjacent
pair, at the delivered resolution, and **sum** those within each one-second window
at the delivered fps. Judge the **minimum** window, never the average — a clip
that freezes only in its middle seconds must fail here, and averaging hides
exactly that.

**Do not ship a fixed floor.** A hard-coded threshold is how this check fails
while looking like it works: the same measure reads ~0.25 on a single adjacent
pair of a visibly alive texture and ~8 as a summed one-second window, so a
threshold without its window and its resolution attached is meaningless. Worse, a
floor set below the route's own re-render noise passes anything: a sibling skill's
liveness floor sat at 6 while its route's noise floor was ~70, and a confirmation
run measured 69.64 and passed on a clip that had not changed at all.

So calibrate, per route, before trusting the number:

1. **Known-bad control.** Build a deliberately frozen clip — one frame repeated
   for the full duration, encoded through the same settings — and measure it. That
   is your zero. If it does not read near zero, the measurement is broken, not the
   clip.
2. **Known-good control.** Measure a clip you can see is moving. That is your
   ceiling.
3. **Set the floor between them, nearer the bad end**, and record all three
   numbers alongside the verdict. A verdict without its controls is an opinion.

Report the figure, not a pass/fail: "min 1-second window 7.9, frozen control
0.001, floor 2.0" is auditable. "Motion check: PASS" is not, and is what let a
frozen shot reach a human reviewer.

## Guardrails

- **One retry, then change route — and the retry changes a named lever.**
  Resubmitting the same payload pays twice for the same failure. Move the lever
  in the direction of the fault (a wandering LTX extension: `context` down and
  the camera pinned in the prompt; a frozen or too-timid result wants the
  opposite correction); if the second attempt fails the same way, move to the
  named fallback rather than paying a third time.
  **This ceiling is per shot, and it is the one that gets broken.** A real
  production run took three attempts on a single shot, because on a multi-shot
  job the count lives in your head instead of on the page. So keep it on the
  page: track attempts per shot, and on the second failure stop retrying that
  shot and either change route or take it to the review pause with the failure
  named. Two attempts on eight shots is sixteen renders — the ceiling exists
  because that is a bill, not a nuisance.
- **A shot prompt carries exactly one physical action.** The same run lost three
  renders to a shot brief that asked for two things at once — tie the bag *and*
  set it by the window. Models do not refuse the second action, they blend it,
  and the result reads as a mistake rather than a miss. One clear beat per clip;
  if the idea needs two, that is two clips, which by the rule above is also the
  cheaper way to get it.
- **Never raise duration to fit more of the idea in.** Two 4s clips cost what
  one 8s clip costs and give two attempts. Length is the user's creative
  decision, not a quality lever.
- **A generative route redraws every frame — and that includes extend and
  reframe, not just animating a still.** If a logo, product, face or specific
  room must survive *as itself*, nothing that passes through a generative model
  preserves it. Extend can walk the subject out of frame: a product ad whose
  hero drifts off-screen in the added seconds is a failed deliverable, so check
  the extension holds the subject before delivering. Reframe fills the new
  regions with invented picture — around people that means faces, torsos and
  limbs that were never shot, a rights and approvals problem on advertising
  footage, not a cosmetic one — and it re-renders the pixels that were already
  correct, so logos and any burned-in text degrade. Keep motion small, keep
  duration short, and check every generative output against the source before
  delivering.
- **Reframe invents, crop discards — and the agent decides which by looking at
  the frame, not by asking.** A "vertical cut" can mean either. A crop is a
  free ffmpeg operation that loses the edges; reframe is a paid render that
  fabricates them. When the frame contains people, faces, logos or a product
  that must survive as shot, default to the free crop whenever the subject fits
  the target frame; reach for reframe when the scene must genuinely extend and
  the frame tolerates invention. This is read off the footage itself — a user's
  intake answer is evidence, not the verdict. State the choice, the rejected
  alternative and both prices in the delivery note; the conditional `Framing`
  header (Step 0) is the optional escalation and never blocks the run. And
  upscaling does not restore missing content: from a 480p source, 4k output is
  a clean 4k render of 480p detail.
- **Probe the source before spending, and not only for limits.** `ffprobe` the
  dimensions, duration, fps and audio track — several routes constrain input
  video (Kling's element inputs cap at 200MB, 3–10s, 24–60fps), and an
  out-of-bounds source fails after the upload, not before. Then check whether
  the clip is a single take: an extend route continues only the **last shot**,
  so on a multi-shot montage "extend this clip" silently means "extend the
  final shot". Proceed on that reading, say which shot is being continued in
  the delivery note, and size LTX's `context` to that shot alone.
- **Never substitute a route silently.** Name the fallback and its different
  rate in the reply.
