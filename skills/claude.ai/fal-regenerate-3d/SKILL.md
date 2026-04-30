---
name: fal-regenerate-3d
description: Build a fully-interactive 3D character-selector experience powered entirely by fal.ai. Generates stylized characters (FLUX.2 / GPT-Image-2), rigged animated GLBs (Meshy v6), themed companion creatures, per-character PATINA floor textures, looped Seedance video backgrounds, and a Three.js scene with palette swaps, breathing reflections, transition effects and a CREATE-YOUR-OWN flow.
---

# fal-regenerate-3d Skill

End-to-end recipe to ship a polished, multi-character 3D web experience using fal.ai models.
This is the recipe that powers **[fal-roster.vercel.app](https://fal-roster.vercel.app)** — a cyberpunk character selector with 10 unique operatives, each with a matching companion creature, environment-themed floor texture, animated background and color palette.

## What it builds

For each character you get:

- A **stylized 3D character GLB** (rigged + animated, baked into the file)
- A **companion creature GLB** (small static, themed to match the character)
- A **per-character PBR floor** (basecolor / normal / roughness / metalness, all generated)
- A **looped video background** keyed to the biome
- A **3-color palette** that drives the whole UI (CSS custom properties)
- A **portrait crop** for the roster card

All packaged into a single static HTML page with a Three.js scene. ~25–35 MB of GLBs total after compression.

## Pipeline

```
1. GPT-Image-2          → 1024x1536 character full-body T-pose (per character)
2. Meshy v6             → image-to-3d, enable_rigging=true, animation_action_id={chosen}
                          → animated GLB (idle, dance, alert, etc.)
3. GPT-Image-2/edit     → companion creature image, color-locked to character palette
4. Meshy v6             → image-to-3d, enable_rigging=false → static creature GLB
5. PATINA               → fal-ai/patina/material/extract on the character image,
                          returns basecolor + normal + roughness + metalness for the floor
6. Seedance 2.0         → fal-ai/bytedance/seedance-2.0/fast/image-to-video, 8s loop
7. gltf-transform CLI   → resize 1024 → webp q80 → draco
                          (typically 95–96% size reduction, ~400–800 KB final)
8. Three.js scene       → MeshStandardMaterial floor with alphaMap circular cutout,
                          mirrored reflection (refl.y = root.y, scale.y = -1),
                          breathing animation on companions,
                          per-character palette via CSS custom properties (--c1/--c2/--c3),
                          per-character floor texture swap on character click,
                          transition lines + radial flash on swap
```

## CREATE-YOUR-OWN flow

Visitors with a FAL key can generate their own character + companion live, in-browser:

```
flux-2 klein 9b (text-to-image)
  └─ character full-body image
       ├─ Meshy v6 (rigged + animated) → character GLB
       └─ flux-2 klein 9b/edit         → companion image
                                          └─ Meshy v6 (no rig) → companion GLB
```

Cost: ~$2–3 per generation (4 fal calls). Runs in background — modal closes on Generate so the user can keep using the experience while the gen runs. The `CREATE YOUR OWN` tile transforms into a loading state, then becomes the new character card with a `↻ re-create` button.

## Key fal endpoints used

| Step | Endpoint |
|------|----------|
| Character image (curated) | `openai/gpt-image-2` |
| Character image (live) | `fal-ai/flux-2/klein/9b` |
| Companion image | `fal-ai/gpt-image-2/edit` or `fal-ai/flux-2/klein/9b/edit` |
| 3D character/companion | `fal-ai/meshy/v6/image-to-3d` |
| Per-character floor PBR | `fal-ai/patina/material/extract` |
| Background video | `fal-ai/bytedance/seedance-2.0/fast/image-to-video` |
| Logo / icon cleanup | `fal-ai/bria/background/remove` |

## Meshy animation IDs

Curated dance / idle action IDs (full list at https://docs.meshy.ai/en/api/animation-library):

| ID | Animation |
|----|-----------|
| 0 | Idle (default) |
| 2 | Alert |
| 36 | Confused (scratch) |
| 48 | Mirror viewing |
| 64 | All_Night_Dance |
| 405 | Joyful_Dance_with_Hand_Sway |
| 591 | Hip_Hop_Dance |
| 64–83 | Various Pop_Dance variants |

## Three.js scene notes

- **Floor**: `PlaneGeometry(7, 7, 220, 220)` cut into a disc via radial-gradient `alphaMap`. High tessellation enables real `displacementMap` (uses basecolor as height).
- **Reflection**: clone of the root with `scale.y = -1`, `BackSide`, `depthWrite = false`, `renderOrder = -1`. For characters whose origin is at the feet, `refl.position.y = root.position.y` produces a visible mirror; the floor's `transparent = true; opacity ≈ 0.5` lets it bleed through.
- **Breathing**: per-frame `scale.setScalar(base * (1 + sin(t*1.3)*0.025))` + a small Y bob on companions. The reflection mirrors the bob so the mirror stays consistent.
- **Palette swap**: `:root.style.setProperty('--c1', hex)` etc. Every UI element (sparklines, pulses, bars, model pills, edge map dots) derives its color from `var(--c1)` / `var(--c2)`.
- **Floor swap**: `texLoader.load()` 4 PBR maps from `assets/floor/{charId}/`, dispose old textures, set `floorMat.color` back to white (since the basecolor is already char-themed).
- **Transition**: 9 diagonal lines sweep across the viewport (`@keyframes tfx-sweep`) on character click + a radial flash; bg video crossfades between two `<video>` elements; character GLB slides out and the new one slides in.

## Reference implementation

- **Live**: https://fal-roster.vercel.app
- **Source**: https://github.com/lovisdotio/fal-roster
- **Skill repo**: https://github.com/lovisdotio/skills-fal-ai

## Cost reference (curated build)

For one full character:

| Step | Approx. cost |
|------|-------------:|
| 1 GPT-Image-2 (character) | $0.04 |
| 1 Meshy v6 rigged + animated | $0.80 |
| 1 GPT-Image-2/edit (companion) | $0.04 |
| 1 Meshy v6 static (companion) | $0.20 |
| 1 PATINA floor (4 maps) | $0.04 |
| 1 Seedance fast (bg video) | $0.08 |
| **Total per character** | **~$1.20** |
| **10 characters** | **~$12** |

Runtime parallelizes well — the original 10-character set was generated in ~10 minutes wall-clock with 9 concurrent jobs per stage.
