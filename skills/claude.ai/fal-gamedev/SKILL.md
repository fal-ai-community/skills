---
name: fal-gamedev
description: >
  Generate 2D pixel art game assets — characters, sprite sheets, background
  removal, and game backgrounds. Trigger for "pixel art character", "sprite
  sheet", "walk cycle", "game sprites", "isometric sprites", "side-scroller
  assets", "RPG character sprites", "idle animation", "attack animation",
  "jump animation", "game background", "parallax background", "isometric map",
  "2D game art", "pixel art animation". Covers character generation
  (nano-banana-pro / gpt-image-2), sprite sheet animation (nano/edit or
  gpt-image-2/edit), background removal (Bria), and background generation
  (parallax layers or isometric map).
metadata:
  author: fal-ai-community
  version: "0.1.0"
---

# 2D Game Assets

> Requires the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli) (run `genmedia init` once).

Full pipeline for 2D pixel art game assets: character → sprite sheets → background removal → game background. Each recipe is independently invokable — run just the part you need.

Always use `--json` so output is machine-readable. Use `--download` to save files locally. Do **not** curl URLs manually — use the `--download` flag.

---

## Execution rules — follow these strictly

1. **Each genmedia command = one Bash tool call** — issue each `genmedia run` and `genmedia status` as its own bare tool call. No variable assignments, no pipes, no shell redirects. This keeps every call matching the `genmedia *` allowlist so it runs without permission prompts.

2. **Parallel jobs → async** — issue each `genmedia run --async` as its own separate Bash tool call (not combined into one shell block). All jobs queue and run in parallel on fal's side; total time ≈ slowest single job. After all are fired, poll each with `genmedia status` sequentially (not in parallel — one failure must not cancel others).
   ```bash
   # Step 1 — fire async (each line = its own Bash tool call, returns request_id immediately)
   genmedia run fal-ai/nano-banana-pro/edit --prompt "$WALK_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
   genmedia run fal-ai/nano-banana-pro/edit --prompt "$IDLE_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json

   # Step 2 — poll sequentially (each line = its own Bash tool call)
   genmedia status fal-ai/nano-banana-pro/edit <walk_request_id> --result --download ./walk.png --json
   genmedia status fal-ai/nano-banana-pro/edit <idle_request_id> --result --download ./idle.png --json
   ```

3. **URL source** — always read `downloaded_files[0].url` from the tool result JSON. This is the correct path for all models (nano, gpt, Bria).

4. **Bria sync** — Bria (`fal-ai/bria/background/remove`) has no queue endpoint and does not support `--async`. Run it sync. It completes in seconds.

5. **Folder structure** — always save into this layout, deriving the character slug from the character description (kebab-case, e.g. `pirate-carrot`):
   ```
   ./game-assets/
     <character-slug>/
       character.png
       sprites/
         walk.png
         idle.png
         attack.png
         jump.png
       backgrounds/
         layer1-sky.png
         layer2-midground.png
         layer3-foreground.png
   ```
   Create the folders before downloading (`mkdir -p`). Use this structure even for partial runs (e.g. just one sprite sheet still goes in `sprites/`).

6. **End summary** — after all downloads complete, print a summary listing every file path and its CDN URL. Format:
   ```
   === Game Assets: pirate-carrot ===
   character        game-assets/pirate-carrot/character.png
                    https://...
   walk             game-assets/pirate-carrot/sprites/walk.png
                    https://...
   ```

7. **400 on status poll** — `genmedia status --result` fetches the result once; it does not poll automatically. A 400 with `"Request is still in progress"` means the job is still running — wait 10 seconds and retry the exact same `genmedia status` call with the same request_id. Do **not** re-fire the original `genmedia run --async` (the job is already running on fal's side). Keep retrying every 10–15 seconds until you get a successful result.

---

## When to use
- Generating a pixel art character from a text description or reference image
- Creating sprite sheet animations (walk, jump, attack, idle) for a side-scroller
- Creating isometric RPG sprite sheets (walk, attack, idle across directions)
- Removing backgrounds from sprite sheets to get transparent PNGs
- Generating parallax backgrounds (3-layer) for side-scrollers
- Generating top-down isometric game maps for RPGs

## Models in the stack
- **Nano Banana Pro** — `fal-ai/nano-banana-pro` — character + background generation; better quality and faster, recommended default
- **Nano Banana Pro Edit** — `fal-ai/nano-banana-pro/edit` — sprite sheet generation from character image
- **GPT-Image-2** — `openai/gpt-image-2` — character + background generation; slower than nano, use when user prefers it or wants cheaper output (`quality=low`)
- **GPT-Image-2 Edit** — `openai/gpt-image-2/edit` — sprite sheet generation; slower than nano, requires model-specific walk prompt; use `quality=low` for cheaper runs
- **Bria RMBG 2.0** — `fal-ai/bria/background/remove` — background removal on all sprite sheets

---

## Recipe 1 — Generate character

Ask the user: character description (text) or an existing image to convert. Ask model preference: `nano` (default, better quality + faster) or `gpt` (slower; use `quality=low` if user wants cheaper output).

```bash
CHARACTER_STYLE_PROMPT="Generate a single character only, centered in the frame on a plain white background. The character should be rendered in detailed 32-bit pixel art style (like PlayStation 1 / SNES era games). Include proper shading, highlights, and anti-aliased edges for a polished look. The character should have well-defined features, expressive details, and rich colors. Show in a front-facing or 3/4 view pose, standing idle, suitable for sprite sheet animation."

IMAGE_TO_PIXEL_PROMPT="Transform this character into detailed 32-bit pixel art style (like PlayStation 1 / SNES era games). IMPORTANT: Must be a FULL BODY shot showing the entire character from head to feet. Keep the character centered in the frame on a plain white background. Include proper shading, highlights, and anti-aliased edges for a polished look. The character should have well-defined features, expressive details, and rich colors. Show in a front-facing or 3/4 view pose, standing idle, suitable for sprite sheet animation. Maintain the character's key features, colors, and identity while converting to pixel art."

# Text → pixel art character (nano)
genmedia run fal-ai/nano-banana-pro \
  --prompt "$CHARACTER_STYLE_PROMPT Character: <character_desc>" \
  --aspect_ratio "1:1" --resolution "1K" \
  --download ./game-assets/<slug>/character.png --json

# Text → pixel art character (gpt)
genmedia run openai/gpt-image-2 \
  --prompt "$CHARACTER_STYLE_PROMPT Character: <character_desc>" \
  --image_size "square_hd" --quality "high" \
  --download ./game-assets/<slug>/character.png --json

# Existing image → pixel art (nano) — upload source image first, then run edit
genmedia upload /path/to/image.png --json
genmedia run fal-ai/nano-banana-pro/edit \
  --prompt "$IMAGE_TO_PIXEL_PROMPT" \
  --image_urls "[\"<uploaded_url_from_above>\"]" \
  --aspect_ratio "1:1" --resolution "1K" \
  --download ./game-assets/<slug>/character.png --json
```

Read `downloaded_files[0].url` from the tool result — this is `CHARACTER_URL`, needed for all sprite sheet recipes.

---

## Recipe 2 — Generate sprite sheets

Pass `CHARACTER_URL` from Recipe 1. Choose `--style side` (side-scroller) or `--style iso` (isometric RPG). Choose model: `nano` or `gpt`.

**Side-scroller sheets** — 4-frame 2×2 grid animations. Covered types: `walk`, `jump`, `attack`, `idle`. Do not generate additional animation types (hurt, death, run, etc.) unless the user explicitly requests them.

Fire all sheets async (each is its own Bash tool call), then poll sequentially:

```bash
WALK_PROMPT="Create a 4-frame pixel art walk cycle sprite sheet of this character. Arrange the 4 frames in a 2x2 grid on white background. The character is walking to the right. Top row (frames 1-2): Frame 1 (top-left): Right leg forward, left leg back - stride position. Frame 2 (top-right): Legs close together, passing/crossing - transition. Bottom row (frames 3-4): Frame 3 (bottom-left): Left leg forward, right leg back - opposite stride. Frame 4 (bottom-right): Legs close together, passing/crossing - transition back. Each frame shows a different phase of the walking motion. This creates a smooth looping walk cycle. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames. Character facing right."

WALK_PROMPT_GPT="Create a 4-frame pixel art walk cycle sprite sheet of this character. Character orientation (critical): The character is shown in SIDE PROFILE, with their face, chest, and front foot pointing toward the RIGHT edge of the image. The character's back is on the LEFT side of the image. This is the same side-profile orientation used in classic 2D platformers like Super Mario Bros or Mega Man moving rightward across the screen. Arrange the 4 frames in a 2x2 grid on white background. Top row (frames 1-2): Frame 1 (top-left): Front leg (right leg) extended forward toward the right edge of the image, back leg extended behind toward the left edge. Frame 2 (top-right): Legs close together, passing pose. Bottom row (frames 3-4): Frame 3 (bottom-left): Opposite stride — back leg (left leg) now forward toward the right edge. Frame 4 (bottom-right): Legs close together, passing pose. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames. All 4 frames must show the character from the SAME side profile angle, facing the RIGHT edge of the image."

JUMP_PROMPT="Create a 4-frame pixel art jump animation sprite sheet of this character. Arrange the 4 frames in a 2x2 grid on white background. The character is jumping. Top row (frames 1-2): Frame 1 (top-left): Crouch/anticipation - character slightly crouched, knees bent, preparing to jump. Frame 2 (top-right): Rising - character in air, legs tucked up, arms up, ascending. Bottom row (frames 3-4): Frame 3 (bottom-left): Apex/peak - character at highest point of jump, body stretched or tucked. Frame 4 (bottom-right): Landing - character landing, slight crouch to absorb impact. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames. Character facing right."

ATTACK_PROMPT="Create a 4-frame pixel art attack animation sprite sheet of this character. Arrange the 4 frames in a 2x2 grid on white background. The character is performing an attack that fits their design - could be a sword slash, magic spell, punch, kick, or energy blast depending on what suits the character best. Top row (frames 1-2): Frame 1 (top-left): Wind-up/anticipation - character preparing to attack, pulling back weapon or gathering energy. Frame 2 (top-right): Attack in motion - the strike or spell being unleashed. Bottom row (frames 3-4): Frame 3 (bottom-left): Impact/peak - maximum extension of attack, weapon fully swung or spell at full power. Frame 4 (bottom-right): Recovery - returning to ready stance. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames. Character facing right. Make the attack visually dynamic and exciting."

IDLE_PROMPT="Create a 4-frame pixel art idle/breathing animation sprite sheet of this character. Arrange the 4 frames in a 2x2 grid on white background. The character is standing still but with subtle idle animation. Top row (frames 1-2): Frame 1 (top-left): Neutral standing pose - relaxed stance. Frame 2 (top-right): Slight inhale - chest/body rises subtly, maybe slight arm movement. Bottom row (frames 3-4): Frame 3 (bottom-left): Full breath - slight upward posture. Frame 4 (bottom-right): Exhale - returning to neutral, slight settle. Keep movements SUBTLE - this is a gentle breathing/idle loop, not dramatic motion. Character should look alive but relaxed. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames. Character facing right."

# Fire all 4 async — each is its own Bash tool call
genmedia run fal-ai/nano-banana-pro/edit --prompt "$WALK_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$JUMP_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$ATTACK_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "21:9" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$IDLE_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json

# Poll each — each is its own Bash tool call, run sequentially
genmedia status fal-ai/nano-banana-pro/edit <walk_request_id> --result --download ./game-assets/<slug>/sprites/walk.png --json
genmedia status fal-ai/nano-banana-pro/edit <jump_request_id> --result --download ./game-assets/<slug>/sprites/jump.png --json
genmedia status fal-ai/nano-banana-pro/edit <attack_request_id> --result --download ./game-assets/<slug>/sprites/attack.png --json
genmedia status fal-ai/nano-banana-pro/edit <idle_request_id> --result --download ./game-assets/<slug>/sprites/idle.png --json

# GPT variants: replace fal-ai/nano-banana-pro/edit with openai/gpt-image-2/edit
# Walk must use WALK_PROMPT_GPT (not WALK_PROMPT)
# Replace --aspect_ratio with explicit --image_size:
#   1:1  → --image_size "square_hd"
#   21:9 → --image_size "{\"width\": 2688, \"height\": 1152}"
```

**Isometric RPG sheets** — 3/4 overhead perspective. Covered types: `walk-down`, `walk-up`, `walk-side`, `attack-down`, `attack-up`, `attack-side`, `idle-iso`. Do not generate additional animation types unless the user explicitly requests them.

> Generate attack-down first — attack-up and attack-side both reference it for style consistency.

```bash
WALK_DOWN_PROMPT="Create a 4-frame pixel art walk cycle sprite sheet of this character walking DOWNWARD (toward the camera) in a top-down isometric RPG perspective (3/4 overhead view, like a classic top-down RPG). Arrange the 4 frames in a 2x2 grid on white background. The character is walking toward the viewer (south/down). Top row: Frame 1 (top-left): Left foot forward stride, arms swinging naturally. Frame 2 (top-right): Feet together, passing/transition pose. Bottom row: Frame 3 (bottom-left): Right foot forward stride, arms swinging naturally. Frame 4 (bottom-right): Feet together, passing/transition back. We see the character's front/face. Top-down 3/4 view - we see the top of their head slightly. Use detailed 32-bit pixel art style with proper shading and highlights. Same character design in all frames."

WALK_UP_PROMPT="Create a 4-frame pixel art walk cycle sprite sheet of this character walking UPWARD (away from the camera) in a top-down isometric RPG perspective (3/4 overhead view, like a classic top-down RPG). Arrange the 4 frames in a 2x2 grid on white background. CRITICAL: ALL 4 frames must show the character from EXACTLY the same angle — their BACK, facing directly away from the camera. Do NOT rotate or twist the character between frames. The ONLY difference between frames should be the leg and arm positions. Top row: Frame 1 (top-left): Left foot forward — BACK VIEW. Frame 2 (top-right): Feet together — BACK VIEW. Bottom row: Frame 3 (bottom-left): Right foot forward — BACK VIEW. Frame 4 (bottom-right): Feet together — BACK VIEW. Use detailed 32-bit pixel art style. Same character design in all frames."

WALK_SIDE_PROMPT="Create a 4-frame pixel art walk cycle sprite sheet of this character WALKING TO THE RIGHT in a top-down isometric RPG perspective (3/4 overhead view, like a classic top-down RPG). Arrange the 4 frames in a 2x2 grid on white background. The character is FACING RIGHT and WALKING RIGHT. Top row: Frame 1 (top-left): Right leg forward, left leg back - stride, arms swinging. Frame 2 (top-right): Legs close together, passing - transition. Bottom row: Frame 3 (bottom-left): Left leg forward, right leg back - opposite stride, arms swinging. Frame 4 (bottom-right): Legs close together, passing - transition back. We see the character's RIGHT-facing side profile from a top-down 3/4 overhead angle. Use detailed 32-bit pixel art style. Same character design in all frames."

ATTACK_DOWN_PROMPT="Create a 4-frame pixel art ATTACK animation sprite sheet of this character attacking DOWNWARD (toward the camera) in a top-down isometric RPG perspective (3/4 overhead view). Arrange the 4 frames in a 2x2 grid on white background. Top row: Frame 1 (top-left): Wind-up/anticipation - preparing to strike. Frame 2 (top-right): Attack in motion - strike unleashed toward camera. Bottom row: Frame 3 (bottom-left): Impact/peak - maximum extension. Frame 4 (bottom-right): Recovery. We see the character's front/face. The attack should fit the character's design. Use detailed 32-bit pixel art style. Make the attack visually dynamic."

ATTACK_UP_PROMPT="Create a 4-frame pixel art ATTACK animation sprite sheet of this character attacking UPWARD (away from the camera) in a top-down isometric RPG perspective. I've also sent you a reference of the same character's front-facing attack. Use the EXACT SAME attack type, weapon, and visual effects - just show it from behind. Arrange the 4 frames in a 2x2 grid on white background. Top row: Frame 1 (top-left): Wind-up from behind. Frame 2 (top-right): Attack unleashed upward/away. Bottom row: Frame 3 (bottom-left): Impact/peak. Frame 4 (bottom-right): Recovery. We see the character's back. MUST use the same attack style as the reference image. Use detailed 32-bit pixel art style."

ATTACK_SIDE_PROMPT="Create a 4-frame pixel art ATTACK animation sprite sheet of this character attacking SIDEWAYS (to the right) in a top-down isometric RPG perspective. I've also sent you a reference of the same character's front-facing attack. Use the EXACT SAME attack type, weapon, and visual effects - just show it from the side profile. Arrange the 4 frames in a 2x2 grid on white background. Character faces RIGHT. Top row: Frame 1 (top-left): Wind-up from side, facing right. Frame 2 (top-right): Strike unleashed to the right. Bottom row: Frame 3 (bottom-left): Impact/peak. Frame 4 (bottom-right): Recovery. IMPORTANT: Show the character's SIDE PROFILE facing RIGHT. MUST use the same attack style as the reference image. Use detailed 32-bit pixel art style."

IDLE_ISO_PROMPT="Create a 4-frame pixel art idle/breathing animation sprite sheet of this character in a top-down isometric RPG perspective (3/4 overhead view). Arrange the 4 frames in a 2x2 grid on white background. Character is FACING TOWARD THE CAMERA (south/down). Top row: Frame 1 (top-left): Neutral standing pose, facing down. Frame 2 (top-right): Slight inhale - body rises subtly. Bottom row: Frame 3 (bottom-left): Full breath - slight upward posture. Frame 4 (bottom-right): Exhale - returning to neutral. Keep movements SUBTLE. Use detailed 32-bit pixel art style. Same character design in all frames."

# Fire walk sheets + idle async — each is its own Bash tool call
genmedia run fal-ai/nano-banana-pro/edit --prompt "$WALK_DOWN_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$WALK_UP_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$WALK_SIDE_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$IDLE_ISO_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "1:1" --resolution "1K" --async --json

# Poll walk results sequentially
genmedia status fal-ai/nano-banana-pro/edit <walk_down_request_id> --result --download ./game-assets/<slug>/sprites/walk-down.png --json
genmedia status fal-ai/nano-banana-pro/edit <walk_up_request_id> --result --download ./game-assets/<slug>/sprites/walk-up.png --json
genmedia status fal-ai/nano-banana-pro/edit <walk_side_request_id> --result --download ./game-assets/<slug>/sprites/walk-side.png --json
genmedia status fal-ai/nano-banana-pro/edit <idle_iso_request_id> --result --download ./game-assets/<slug>/sprites/idle-iso.png --json

# Attack-down sync — needed as reference before firing attack-up and attack-side
genmedia run fal-ai/nano-banana-pro/edit --prompt "$ATTACK_DOWN_PROMPT" --image_urls "[\"$CHARACTER_URL\"]" --aspect_ratio "9:16" --resolution "1K" --download ./game-assets/<slug>/sprites/attack-down.png --json

# Fire attack-up and attack-side async, passing attack-down URL from above result
genmedia run fal-ai/nano-banana-pro/edit --prompt "$ATTACK_UP_PROMPT" --image_urls "[\"$CHARACTER_URL\", \"<attack_down_url>\"]" --aspect_ratio "9:16" --resolution "1K" --async --json
genmedia run fal-ai/nano-banana-pro/edit --prompt "$ATTACK_SIDE_PROMPT" --image_urls "[\"$CHARACTER_URL\", \"<attack_down_url>\"]" --aspect_ratio "16:9" --resolution "1K" --async --json

genmedia status fal-ai/nano-banana-pro/edit <attack_up_request_id> --result --download ./game-assets/<slug>/sprites/attack-up.png --json
genmedia status fal-ai/nano-banana-pro/edit <attack_side_request_id> --result --download ./game-assets/<slug>/sprites/attack-side.png --json

# GPT variants: replace fal-ai/nano-banana-pro/edit with openai/gpt-image-2/edit
# Replace --aspect_ratio with explicit --image_size:
#   1:1  → --image_size "square_hd"
#   9:16 → --image_size "{\"width\": 720, \"height\": 1280}"
#   16:9 → --image_size "{\"width\": 1280, \"height\": 720}"
```

---

## Recipe 3 — Remove backgrounds

Bria has no queue endpoint — run sync (no `--async`). Each is its own Bash tool call:

```bash
genmedia run fal-ai/bria/background/remove --image_url "<walk_url>" --download ./game-assets/<slug>/sprites/walk-transparent.png --json
genmedia run fal-ai/bria/background/remove --image_url "<jump_url>" --download ./game-assets/<slug>/sprites/jump-transparent.png --json
genmedia run fal-ai/bria/background/remove --image_url "<attack_url>" --download ./game-assets/<slug>/sprites/attack-transparent.png --json
genmedia run fal-ai/bria/background/remove --image_url "<idle_url>" --download ./game-assets/<slug>/sprites/idle-transparent.png --json
```

---

## Recipe 4 — Generate backgrounds

**Pipeline note:** Layer 1 (sky) and the isometric map only need `CHARACTER_DESC` — no image reference. Fire Layer 1 async immediately after character generation so it runs in parallel while you generate sprite sheets. Layers 2 and 3 are sequential (each needs the previous layer's URL from the tool result).

**Side-scroller — 3-layer parallax**

```bash
# Layer 1 — sky/backdrop. Fire async (no image dep) so it runs in parallel with sprite generation
genmedia run fal-ai/nano-banana-pro \
  --prompt "Create the SKY/BACKDROP layer for a side-scrolling pixel art game parallax background. This is for a character: <character_desc>. Create an environment that fits this character's world. This is the FURTHEST layer - only sky and very distant elements (distant mountains, clouds, horizon). Style: Pixel art, 32-bit retro game aesthetic. Wide panoramic scene." \
  --aspect_ratio "21:9" --resolution "1K" --async --json

# Poll Layer 1 (after sprite sheets are done), then read its URL from the result
genmedia status fal-ai/nano-banana-pro <layer1_request_id> --result --download ./game-assets/<slug>/backgrounds/layer1-sky.png --json

# Layer 2 — midground (needs CHARACTER_URL + layer1 URL from above result)
genmedia run fal-ai/nano-banana-pro/edit \
  --prompt "Create the MIDDLE layer of a 3-layer parallax background for a side-scrolling pixel art game. I've sent you images of: 1) the character, 2) the sky layer already created. Create the character's ICONIC/CANONICAL location from their story — home village, famous landmarks, signature battlegrounds. Elements should fill the frame from middle down to bottom. Style: Pixel art matching the other images. IMPORTANT: Use a transparent background so this layer can overlay the others." \
  --image_urls "[\"<character_url>\", \"<layer1_url>\"]" \
  --aspect_ratio "21:9" --resolution "1K" --download ./game-assets/<slug>/backgrounds/layer2-midground.png --json

# Bria bg-remove on layer 2 (sync — no queue endpoint)
genmedia run fal-ai/bria/background/remove --image_url "<layer2_url>" --download ./game-assets/<slug>/backgrounds/layer2-transparent.png --json

# Layer 3 — foreground (needs CHARACTER_URL + layer1 URL + layer2-transparent URL from above result)
genmedia run fal-ai/nano-banana-pro/edit \
  --prompt "Create the FOREGROUND layer of a 3-layer parallax background for a side-scrolling pixel art game. I've sent you images of: 1) the character, 2) the sky layer, 3) the middle layer. Create the closest foreground elements (ground, grass, rocks, platforms) that complete the scene. Style: Pixel art matching the other images. IMPORTANT: Use a transparent background so this layer can overlay the others." \
  --image_urls "[\"<character_url>\", \"<layer1_url>\", \"<layer2_transparent_url>\"]" \
  --aspect_ratio "21:9" --resolution "1K" --download ./game-assets/<slug>/backgrounds/layer3-foreground.png --json

# Bria bg-remove on layer 3 (sync — no queue endpoint)
genmedia run fal-ai/bria/background/remove --image_url "<layer3_url>" --download ./game-assets/<slug>/backgrounds/layer3-transparent.png --json

# GPT variant: replace nano endpoints with openai/gpt-image-2 and openai/gpt-image-2/edit
# Use --image_size '{"width": 2688, "height": 1152}' for 21:9 with gpt
```

**Isometric — single top-down map**

```bash
genmedia run fal-ai/nano-banana-pro \
  --prompt "Create a large, detailed top-down isometric pixel art game world map for a character: $CHARACTER_DESC. Do not place the character on the map. Style: Classic RPG top-down map, 3/4 overhead perspective. Include: winding dirt/stone paths connecting areas, a small body of water, a few buildings or structures that fit the character's world, rocky areas or hills, various terrain types. Single large continuous map image (NOT tiled, NOT a tileset). Complete explorable game world viewed from above. Detailed 32-bit pixel art style. Fill the entire image with map content — no empty borders." \
  --aspect_ratio "1:1" --resolution "1K" \
  --download ./game-assets/<slug>/backgrounds/map.png --json
```

---

## Parameters

- **Model** — `nano` is the default: better quality and faster. `gpt` is slower; use it when the user specifically requests it or asks for the cheapest option — in that case set `--quality "low"` to significantly reduce cost
- **Walk + gpt-image-2** — always use `WALK_PROMPT_GPT`, not `WALK_PROMPT`. GPT needs explicit side-profile orientation instructions to get the direction right
- **Attack aspect ratio** — `21:9` (nano) or `2688×1152` (gpt) for side-scroller attacks. Isometric attacks: `9:16` for down/up, `16:9` for side
- **Isometric attack-up and attack-side** — always pass `ATTACK_DOWN_URL` as second reference image to keep attack style consistent across directions
- **Background layers** — generate in order (1 → 2 → 3). Each references previous layers. Layer 1 keeps background; layers 2 and 3 get background-removed
