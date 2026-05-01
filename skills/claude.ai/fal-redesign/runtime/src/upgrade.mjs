import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname, resolve, isAbsolute } from "node:path";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";
import sharp from "sharp";
import { fal } from "@fal-ai/client";
import { pickDirections } from "./directions.mjs";

// Model used throughout for VLM#1 + VLM#2, via the OpenRouter router on fal.
// Overridable via env var to quickly swap providers without touching code.
const MODEL = process.env.FAL_SITE_MODEL || "anthropic/claude-opus-4.7";

function ensureKey() {
  if (!process.env.FAL_KEY) {
    throw new Error("FAL_KEY is not set. Get one at https://fal.ai/dashboard/keys and export it.");
  }
  fal.config({ credentials: process.env.FAL_KEY });
}

// Both the screenshot viewport AND the gpt-image-2/edit canvas use 1920x2880 = 5.5M pixels
// (multiples of 16, under the fal-ai/gpt-image-2 input limit of 8.3M pixels, tall desktop aspect).
// A tall canvas captures the scroll story of the page (hero + below-the-fold sections).
// deviceScaleFactor is 1 (native) so the PNG stays under limit.
export async function screenshotHtml(targetPathOrUrl, pngPath, { viewport = { width: 1920, height: 2880 }, fullPage = false, deviceScaleFactor = 1 } = {}) {
  const browser = await puppeteer.launch({ headless: "new" });
  try {
    const page = await browser.newPage();
    await page.setViewport({ ...viewport, deviceScaleFactor });
    const url = /^https?:|^file:/.test(targetPathOrUrl)
      ? targetPathOrUrl
      : pathToFileURL(resolve(targetPathOrUrl)).href;
    await page.goto(url, { waitUntil: "networkidle0", timeout: 60_000 });
    await new Promise((r) => setTimeout(r, 1000)); // Tailwind CDN + fonts settle
    // Screen-format capture: viewport snapshot (what a user sees above the fold),
    // NOT a long full-page scroll: keeps the image legible for the VLM.
    await page.screenshot({ path: pngPath, type: "png", fullPage });
  } finally {
    await browser.close();
  }
  return pngPath;
}

const FAL_MAX_PIXELS = 8_294_400; // fal-ai/gpt-image-2 input limit
const FAL_MAX_EDGE = 3840;

async function uploadLocal(path) {
  let buf = readFileSync(path);
  // Safety: if the PNG is above fal's 8.3M-pixel limit OR > 3840px on an edge, downscale first.
  try {
    const meta = await sharp(buf).metadata();
    const pixels = (meta.width || 0) * (meta.height || 0);
    const maxEdge = Math.max(meta.width || 0, meta.height || 0);
    if (pixels > FAL_MAX_PIXELS || maxEdge > FAL_MAX_EDGE) {
      const scale = Math.min(
        FAL_MAX_EDGE / maxEdge,
        Math.sqrt(FAL_MAX_PIXELS / pixels),
      );
      const w = Math.floor((meta.width * scale) / 16) * 16;
      const h = Math.floor((meta.height * scale) / 16) * 16;
      buf = await sharp(buf).resize(w, h, { fit: "fill" }).png().toBuffer();
    }
  } catch {
    // If sharp can't read it, ship as-is and let fal surface an error.
  }
  const blob = new Blob([buf], { type: "image/png" });
  const file = new File([blob], path.split("/").pop() || "file.png", { type: "image/png" });
  return await fal.storage.upload(file);
}

const EDIT_PROMPT_SYSTEM = `You are a senior web art director. You are writing ONE prompt for the gpt-image-2 image-editing model that will transform the attached screenshot into a production-quality redesign of the same website. The redesign must be better than the original; everything else is open.

Before you write one word of the prompt, do this silent brand analysis. Let the BRAND and its CONTENT decide every visual choice: do not default to any one style (editorial, minimal, brutalist, illustrated, photographic). The goal is the right move for this specific product, not your signature move.

STEP 1: Read the content.
What product is this? Who buys it? What is the emotional register it needs (trust, energy, calm, credibility, wonder, irreverence, warmth, precision, playfulness, craft, hacker, family)? Is the page a utility, a portfolio, a shopfront, a tool, a manifesto, a subscription, a game, a gadget? Write an internal one-sentence brand summary.

STEP 2: Decide the primary visual carrier.
This is the big choice. Pick ONE of the following based on the brand, not on fashion:
  (a) The PRODUCT as a hero image: a large rendered or illustrated object that IS the page's visual focal point (physical goods, instruments, gadgets, wearables, apps-as-objects).
  (b) PHOTOGRAPHY: a single well-framed still or a rhythmic pair, documentary or product-shot or moody, depending on the brand.
  (c) ILLUSTRATION / CHARACTERS / MASCOTS: playful, cel-shaded, retro-game, childlike, hand-drawn, or mascot-led when the brand is playful, collectible, character-driven, consumer-social, or explicitly whimsical.
  (d) TYPOGRAPHY: oversized display type as the visual: only when the brand is text-first (a slow-media product, a manifesto, a newsletter, a literary object, an editorial/serif-leaning product).
  (e) DIAGRAM / INFORMATION GRAPHIC: when the product is technical and the information itself is the story.
  (f) GRAPHIC SYSTEM: flat abstract marks, color blocks, grid tiles: when the brand wants calm, modern, pattern-led.
Name the choice and justify in one sentence. Do NOT default to (d) typography. Do NOT default to (a) product-hero. The brand decides.

STEP 3: Palette.
Pick 3–6 hex values. The palette must fit the brand's register (bright primaries for a playful game, deep ink for a slow-media tool, earthy naturals for a craft product, neon on black for a hacker tool, warm pastels for wellness, etc.). Avoid palettes that ignore the brand (e.g. austere-ink-on-white for a playful children's game is wrong; bright cartoon colors for a premium precision instrument is wrong). No palette is banned, no palette is defaulted.

STEP 4: Typography.
Pick ONE display and ONE body. The pairing must match the brand register: rounded chunky sans for playful, serif with voice for considered/literary, neo-grotesk for precision tools, pixel/mono for retro or technical, hand-lettered for tactile/crafty. Typography in the redesign must be in service of the primary visual carrier chosen in Step 2: if imagery or illustration is carrying the page, keep typography tighter and quieter; if typography is the carrier, make it oversized and confident.

STEP 5: Layout rhythm.
Choose the layout that serves the hero: a full-bleed image page, a tight editorial single-column, an asymmetric magazine spread, a centered-object product page, a gridded catalogue, a comic-strip sequence, a data-dense dashboard, a playful non-grid playground. Pick, do not default.

Only NOW write the single gpt-image-2 edit prompt. It must be a concrete edit-instruction to the image model: not a critique, not generic advice. Every sentence describes a specific, visible change to apply while preserving:
- the brand name and all copy visible in the screenshot (verbatim: do not drop text, do not invent text),
- the information architecture (nav items, section order, CTA semantics).

Specify, in flowing art-director sentences:
1. The primary visual carrier (from Step 2): describe the hero image, illustration, photograph, diagram, or typographic move in concrete visual detail so the image model can render it.
2. The palette: 3–6 hex values and where each is used.
3. The typography: display + body family names, size/case/tracking for the hero.
4. The layout move: how the grid rebalances, how sections are paced, any structural shift.
5. Component detail: buttons, chips, badges, dividers, illustrated accents: how they look in the chosen register.
6. Any supporting imagery or graphical elements beyond the hero (secondary illustrations, textures, diagrammatic icons, pattern tiles).

Output ONLY the prompt text. 350–700 words. No preamble, no markdown, no bullet lists: write it as flowing art-director copy. Open by naming the primary visual carrier choice + the palette hexes + the typography pairing. End with: "Render as a tall desktop web page screenshot, 1920x2880 portrait (showing hero + below-the-fold sections), no browser chrome, no device frame, no watermark, razor-sharp text, no broken glyphs, no duplicated words."`;

export async function writeEditPrompt({ screenshotUrl, context, direction }) {
  const userMsg = [
    context?.brief ? `BRAND CONTEXT (for reference only: do not change the copy):\n${typeof context.brief === "string" ? context.brief : JSON.stringify(context.brief, null, 2)}` : null,
    context?.notes ? `ADDITIONAL NOTES:\n${context.notes}` : null,
    direction ? `DESIGN DIRECTION: ${direction.label}\nDIRECTION DETAILS: ${direction.vibe}\nYour edit prompt must embrace this direction specifically, not a generic improvement. Push every visible decision (palette, typography, grid, motion hints, texture) toward this direction.` : null,
    `Write the gpt-image-2 edit prompt for the attached screenshot now.`,
  ].filter(Boolean).join("\n\n");

  const res = await callVision({
    prompt: userMsg,
    system_prompt: EDIT_PROMPT_SYSTEM,
    image_urls: [screenshotUrl],
    temperature: 0.7,
    max_tokens: 2000,
  });
  return res.trim();
}

async function callVision({ prompt, system_prompt, image_urls, temperature, max_tokens }) {
  try {
    const res = await fal.subscribe("openrouter/router/vision", {
      input: { prompt, system_prompt, image_urls, model: MODEL, temperature, max_tokens },
    });
    const out = res?.data?.output ?? res?.output ?? "";
    if (!out) throw new Error(`empty output: ${JSON.stringify(res).slice(0, 400)}`);
    return out;
  } catch (e) {
    const body = e?.body ? (typeof e.body === "string" ? e.body : JSON.stringify(e.body)) : "";
    const status = e?.status ?? "?";
    throw new Error(`openrouter/router/vision ${status}: ${e.message} ${body.slice(0, 500)}`);
  }
}

export async function editImage({ screenshotUrl, editPrompt }) {
  const res = await fal.subscribe("fal-ai/gpt-image-2/edit", {
    input: {
      prompt: editPrompt,
      image_urls: [screenshotUrl],
      image_size: { width: 1920, height: 2880 },
      quality: "high",
      num_images: 1,
      output_format: "png",
    },
  });
  const url = res?.data?.images?.[0]?.url ?? res?.images?.[0]?.url;
  if (!url) throw new Error(`gpt-image-2/edit returned no image: ${JSON.stringify(res).slice(0, 400)}`);
  return url;
}

const DESCRIBE_SYSTEM = `You are a senior design engineer writing a precise build-spec for another engineer (Claude Code / Codex). You receive ONE image: the newly approved TARGET design that must be implemented exactly.

Describe the TARGET design in enough depth that an engineer can reproduce it in HTML/CSS without seeing it a second time. Never speculate about a "before" or compare versions: just describe what is visible in the TARGET image.

You MUST output TWO things in this order and nothing else:

PART A: a Markdown build-spec using exactly these sections (skip a section only if truly absent):

# Design spec

## Hard constraints (MUST follow literally)
Short bullet list of the non-negotiables the engineer must implement verbatim. Each bullet is a single imperative with a numeric value, for example:
- Headline font-size: \`clamp(72px, 9vw, 128px)\`. Never exceed 128px at any breakpoint.
- Hero max-width: 18ch. Break lines after "image." and after "seconds." and nowhere else.
- Page vertical rhythm: the sections MUST flow in the same order and pacing you see in the TARGET image, with the hero occupying roughly the top third of the page and subsequent sections following below the fold.
- Result grid: exactly 5 columns on desktop, 12px gap, max-width 1600px, each cell aspect 1/1.
- Primary button: linear-gradient(90deg, #XXX → #YYY), radius 10px, height 56px.

Write ONLY constraints that are actually visible in the TARGET. Do not invent values.

## Summary
1-2 sentences on the overall personality of the design.

## Canvas & palette
- Background(s), hex-like notation.
- Primary accent(s).
- Text colors (display, body, muted).

## Typography
- Display family + weight + case + tracking + approximate size.
- Body family + size + leading.
- Any mono / label treatment.

## Layout & sections
Walk top-to-bottom through every visible section in order (nav, hero, each content section, footer). For each section: what it contains, how it is arranged (grid/columns/alignment), exact copy strings you can read, and any visual anchor (wordmark, divider, image, chart).

## Components & micro-details
Buttons (fill, border, radius, label style, icons), tags, chips, badges, dividers, captions, counters, hover-looking states.

## Implementation notes
Concrete Tailwind / CSS / spacing hints (e.g. "hero wordmark clamp(72px, 9vw, 128px), leading 0.95, tracking -0.02em", "section padding 96px top 48px bottom at lg").

Then PART B: a single fenced JSON block titled tokens, matching this schema exactly. Wrap it in \`\`\`json ... \`\`\` fences. Omit fields you genuinely cannot determine; never invent values.

\`\`\`json
{
  "canvas": { "background": "#hex" },
  "colors": {
    "text": "#hex",
    "textMuted": "#hex",
    "accent": "#hex",
    "accentGradient": { "from": "#hex", "to": "#hex", "angleDeg": 90 },
    "line": "#hex"
  },
  "typography": {
    "display": { "family": "Instrument Serif", "weight": 400, "italicAllowed": true, "trackingEm": -0.02, "lineHeight": 0.95, "sizeClamp": "clamp(72px, 9vw, 128px)", "maxPx": 128 },
    "body":    { "family": "Inter", "weight": 400, "sizePx": 15, "lineHeight": 1.55 },
    "mono":    { "family": "JetBrains Mono", "weight": 500, "sizePx": 11, "trackingEm": 0.08, "upperCase": true }
  },
  "hero": {
    "maxWidthCh": 18,
    "lineBreakAfter": ["image.", "seconds."],
    "italicOn": ["Edit it in seconds."]
  },
  "grid": { "cols": 5, "gap": 12, "maxWidth": 1600, "aspect": "1/1" },
  "buttons": {
    "primary":   { "radiusPx": 10, "paddingXpx": 40, "heightPx": 56, "fill": "gradient" },
    "secondary": { "radiusPx": 8, "border": "1px solid #hex" }
  }
}
\`\`\`

Note on imagery: the engineer will be given the full target image (\`after.png\`) as a visual reference. Do NOT output pixel bboxes or image prompts: the engineer reads the image directly to decide which assets to source or placeholder.

Be concise in PART A. Output only PART A followed by PART B. No preamble, no trailing commentary.

Structure (use exactly these sections, skip a section if nothing changed there):

# Change spec

## Summary
1-2 sentences on the overall shift.

## Palette
- Old → New for every color that changed, with hex-like notation.

## Typography
- Heading family, weight, case, tracking. Body family, size, leading.

## Layout & sections
- Per section (hero, nav, sections in order, footer): what to change, what to add, what to remove. Reference exact copy strings where helpful.

## Components & micro-details
- Buttons, tags, dividers, captions, hover states, motion cues.

## Implementation notes
- Any Tailwind or CSS specifics worth knowing (e.g. "use font-serif display at 120px with -0.03em tracking", "two-column asymmetric 7/5 grid at >= lg").

Be concise. No fluff. No "Great news!" preamble. Output Markdown only.`;

const IMPLEMENT_SYSTEM = `You are a staff-level front-end engineer. You are given:
  (A) The ORIGINAL HTML of a website between BEGIN_HTML and END_HTML markers.
  (B) An attached image: the APPROVED REDESIGN (1920×2880).

Your job is twofold.

===== ABSOLUTE LAW =====
THE ATTACHED MOCKUP IMAGE IS THE SPEC. Your output must be a faithful, production-grade reproduction of that mockup in HTML. If a choice you're about to make does NOT match something visible in the mockup, that choice is wrong.

Before writing any HTML, do this silent audit (do not print it):
1. Trace the mockup top-to-bottom. List every section in order: nav, hero, each section, footer.
2. For EACH section: note the grid (cols, gap, container width), the type (display family vs sans body, sizes, weight, case, tracking), the palette (at least 4-6 hex values), the components (buttons, chips, cards, dividers), the imagery and its aspect ratio.
3. Cross-reference against the ORIGINAL HTML to find the copy strings you'll reuse. If the original has more sections than the mockup, keep only those the mockup shows. If the mockup shows something the original lacks (e.g. a new image slot), add it.

===== PART 1: HTML =====
Produce a NEW, complete single-file HTML document that REPRODUCES the mockup:
- PALETTE: use hex values read directly from the mockup. Do not carry over the original site's colors. At minimum identify: background, surface, display text, body text, muted text, primary accent, line/border. Use those in the CSS.
- TYPOGRAPHY: use the exact display family style (e.g. high-contrast serif, didone, grotesk, mono, etc.) you see in the mockup. Pick a Google Font that matches (don't default to Inter unless the mockup shows it). Size, weight, case, tracking must visibly match.
- LAYOUT & GRID: match container width, column count, gaps, vertical rhythm, section padding. If the mockup has an asymmetric grid (e.g. 8/4), use it.
- COMPONENTS: match button shape (pill vs square, gradient vs solid, stroke vs fill), icon style, chip style, card divider style, ribbon tags, counters.
- COPY: preserved verbatim from the ORIGINAL HTML. Keep copy identical, do not invent text. You MAY drop sections the mockup no longer shows.
- IMAGERY: for EVERY photo / illustration / avatar / product shot / background texture visible in the mockup, reference a sequential tile file under \`./tiles/\`, e.g. \`<img src="./tiles/tile-01.jpg" alt="...">\`. Number top-to-bottom, left-to-right, starting at tile-01. Never leave an empty gray box if the mockup shows an image there.
- RESPONSIVE: the desktop view matches the mockup at 1920×1080; mobile/tablet are tasteful reflows.

Hard rules for PART 1:
- Output the complete <!doctype html> document. No markdown fences.
- Tailwind via CDN, Google Fonts via <link>, inline <style> allowed.
- Minimal vanilla JS only if strictly needed.
- Every decision must trace back to something you can point to in the mockup.

PART 2: After the closing </html>, output a single fenced JSON block with the flux prompts for every tile you referenced. Use this exact schema:

\`\`\`tiles
{
  "tiles": [
    { "file": "tile-01.jpg", "width": 1024, "height": 1024, "prompt": "Documentary photograph. Warm natural light. A lone figure walking a dune ridge at golden hour, shallow depth of field. Grainy film, muted palette." },
    { "file": "tile-02.jpg", "width": 1024, "height": 768, "prompt": "..." }
  ]
}
\`\`\`

Rules for PART 2:
- One entry per <img> that references \`./tiles/tile-NN\`. Files must match the paths used in the HTML exactly.
- Each prompt is 1-2 sentences. Describe subject + mood + palette + rendering style (photo/illustration/3D). No text in images.
- Width/height are the intended source dimensions: pick powers-of-16 values between 512 and 1536 matching the aspect ratio the HTML expects (e.g. square → 1024x1024, landscape hero → 1536x1024, portrait → 768x1024).
- If the design has no imagery at all, still output \`"tiles": []\`.

Output ONLY the HTML + the \`\`\`tiles JSON block. No preamble, no fences around the HTML itself.`;

export async function implementFromOriginal({ originalHtmlPath, afterUrl }) {
  const original = readFileSync(originalHtmlPath, "utf8");
  const prompt = [
    `ORIGINAL HTML (preserve copy + information architecture, restyle to match the attached image):`,
    `BEGIN_HTML`,
    original,
    `END_HTML`,
    ``,
    `The attached image is the approved redesign. Produce the full PART 1 (HTML) + PART 2 (\`\`\`tiles JSON block) now.`,
  ].join("\n");
  const raw = await callVision({
    prompt,
    system_prompt: IMPLEMENT_SYSTEM,
    image_urls: [afterUrl],
    temperature: 0.4,
    max_tokens: 16_000,
  });
  return splitImplementedOutput(raw);
}

function splitImplementedOutput(text) {
  // Prefer fenced tiles JSON after </html>.
  const m = text.match(/([\s\S]*?<\/html>)\s*```(?:tiles)?\s*([\s\S]*?)```/);
  if (m) {
    const html = cleanupImplementedHtml(m[1]);
    let tiles = [];
    try {
      const json = JSON.parse(m[2].trim());
      if (Array.isArray(json.tiles)) tiles = json.tiles;
    } catch {}
    return { html, tiles };
  }
  // Fallback: just HTML, no tiles.
  return { html: cleanupImplementedHtml(text), tiles: [] };
}

function cleanupImplementedHtml(text) {
  let t = text.trim().replace(/^```(?:html)?\s*/i, "").replace(/```\s*$/, "").trim();
  const i = t.search(/<!doctype html>/i);
  if (i > 0) t = t.slice(i);
  if (!/<!doctype html>/i.test(t)) throw new Error(`implementer did not return a full HTML document: ${t.slice(0, 200)}`);
  return t;
}

// Generate each referenced tile via fal-ai/flux-2/klein/9b/edit, using the mockup as the style reference.
export async function generateTiles({ tiles, mockupUrl, outDir }) {
  if (!tiles?.length) return [];
  mkdirSync(outDir, { recursive: true });
  const results = await Promise.all(
    tiles.map(async (t, i) => {
      const file = t.file || `tile-${String(i + 1).padStart(2, "0")}.jpg`;
      const w = Number(t.width) || 1024;
      const h = Number(t.height) || 1024;
      const prompt = String(t.prompt || "").trim();
      if (!prompt) return { ok: false, file, error: "empty prompt" };
      try {
        const res = await fal.subscribe("fal-ai/flux-2/klein/9b/edit", {
          input: {
            prompt,
            image_urls: [mockupUrl],
            image_size: { width: w, height: h },
            num_images: 1,
            output_format: "jpeg",
          },
        });
        const url = res?.data?.images?.[0]?.url ?? res?.images?.[0]?.url;
        if (!url) throw new Error("no image returned");
        const r = await fetch(url);
        if (!r.ok) throw new Error(`download failed ${r.status}`);
        const outPath = join(outDir, file);
        writeFileSync(outPath, Buffer.from(await r.arrayBuffer()));
        return { ok: true, file, outPath };
      } catch (e) {
        return { ok: false, file, error: e.message };
      }
    }),
  );
  return results;
}

export async function describeTarget({ afterUrl }) {
  const out = await callVision({
    prompt: `Describe the attached TARGET design image as a build-spec now. Output PART A (Markdown) then PART B (\`\`\`json tokens\`\`\`).`,
    system_prompt: DESCRIBE_SYSTEM,
    image_urls: [afterUrl],
    temperature: 0.3,
    max_tokens: 6000,
  });
  return splitMarkdownAndTokens(out.trim());
}

// Split "<markdown>\n```json\n{...}\n```" into { markdown, tokens }.
function splitMarkdownAndTokens(text) {
  const m = text.match(/([\s\S]*?)```json\s*([\s\S]*?)```\s*$/);
  if (!m) return { markdown: text, tokens: null };
  const markdown = m[1].trim();
  let tokens = null;
  try {
    tokens = JSON.parse(m[2].trim());
  } catch {
    // Attempt to salvage: find the outermost braces.
    const raw = m[2];
    const a = raw.indexOf("{");
    const b = raw.lastIndexOf("}");
    if (a !== -1 && b > a) {
      try { tokens = JSON.parse(raw.slice(a, b + 1)); } catch {}
    }
  }
  return { markdown, tokens };
}

export async function upgradeSite({ target, outDir, context, variants = 1 }) {
  ensureKey();
  if (!outDir) outDir = join(process.cwd(), ".fal-site-upgrade");
  mkdirSync(outDir, { recursive: true });

  const beforePath = join(outDir, "before.png");
  console.error(`[fal-design upgrade] 1/${variants > 1 ? "3" : "4"} screenshotting ${target} → ${beforePath}`);
  await screenshotHtml(target, beforePath);

  console.error(`[fal-design upgrade] 2/${variants > 1 ? "3" : "4"} uploading screenshot`);
  const beforeUrl = await uploadLocal(beforePath);

  if (variants > 1) {
    return await runMultiVariant({ outDir, beforePath, beforeUrl, context, variants });
  }

  // Single-variant path (default).
  const afterPath = join(outDir, "after.png");
  const editPromptPath = join(outDir, "edit-prompt.txt");
  const changesPath = join(outDir, "changes.md");
  const tokensPath = join(outDir, "tokens.json");

  // If FAL_SITE_DIRECTION is set, pickDirections returns [match]; otherwise we leave
  // direction undefined so the prompt defaults to freeform brand-analysis.
  const forced = process.env.FAL_SITE_DIRECTION ? pickDirections(1)[0] : undefined;
  console.error(`[fal-design upgrade] 3/4 VLM#1 (opus-4.7) → edit prompt${forced ? ` (direction: ${forced.slug})` : ""}`);
  const editPrompt = await writeEditPrompt({ screenshotUrl: beforeUrl, context, direction: forced });
  writeFileSync(editPromptPath, editPrompt);

  console.error(`[fal-design upgrade] 4/4 gpt-image-2/edit → redesigned image`);
  const afterUrl = await editImage({ screenshotUrl: beforeUrl, editPrompt });
  const afterRes = await fetch(afterUrl);
  if (!afterRes.ok) throw new Error(`failed to download redesigned image: ${afterRes.status}`);
  writeFileSync(afterPath, Buffer.from(await afterRes.arrayBuffer()));

  console.error(`[fal-design upgrade] describing target (opus-4.7 vision) + tokens`);
  const { markdown, tokens } = await describeTarget({ afterUrl });
  writeFileSync(changesPath, markdown);
  if (tokens) writeFileSync(tokensPath, JSON.stringify(tokens, null, 2));

  return { mode: "single", beforePath, afterPath, editPromptPath, changesPath, changes: markdown, tokens, tokensPath: tokens ? tokensPath : null };
}

async function runMultiVariant({ outDir, beforePath, beforeUrl, context, variants }) {
  const dirs = pickDirections(variants);
  console.error(`[fal-design upgrade] 3/3 fanning out ${dirs.length} direction(s) in parallel: ${dirs.map((d) => d.slug).join(", ")}`);

  const results = await Promise.all(
    dirs.map(async (direction, i) => {
      const idx = String(i + 1).padStart(2, "0");
      const slug = `${idx}-${direction.slug}`;
      const afterPath = join(outDir, `after-${slug}.png`);
      const editPromptPath = join(outDir, `edit-prompt-${slug}.txt`);
      try {
        const editPrompt = await writeEditPrompt({ screenshotUrl: beforeUrl, context, direction });
        writeFileSync(editPromptPath, editPrompt);
        const afterUrl = await editImage({ screenshotUrl: beforeUrl, editPrompt });
        const r = await fetch(afterUrl);
        if (!r.ok) throw new Error(`download failed ${r.status}`);
        writeFileSync(afterPath, Buffer.from(await r.arrayBuffer()));
        console.error(`   ✓ ${slug}`);
        return { ok: true, slug, direction, afterPath, editPromptPath };
      } catch (e) {
        console.error(`   ✗ ${slug}: ${e.message}`);
        return { ok: false, slug, direction, error: e.message };
      }
    }),
  );

  const galleryPath = join(outDir, "gallery.html");
  writeFileSync(galleryPath, buildGalleryHtml(results, beforePath));

  return { mode: "multi", beforePath, galleryPath, variants: results };
}

function buildGalleryHtml(results, beforePath) {
  const cards = results.map((r) => {
    if (!r.ok) {
      return `<a class="card fail"><span class="num">${r.slug}</span><span class="label">${r.direction.label}</span><span class="slug">${r.direction.slug}</span><span class="err">${r.error}</span></a>`;
    }
    const rel = r.afterPath.split("/").pop();
    return `<a class="card" href="./${rel}" target="_blank" rel="noopener"><img loading="lazy" src="./${rel}" alt="" /><span class="num">${r.slug}</span><span class="label">${r.direction.label}</span><span class="slug">${r.direction.slug}</span></a>`;
  }).join("\n");
  const beforeRel = beforePath.split("/").pop();
  return `<!doctype html><meta charset="utf-8"><title>fal-design: variants</title>
<style>
:root{color-scheme:dark;--bg:#0a0a0b;--fg:#f2f0ea;--mut:#8a8781;--acc:#ff5c2b}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
header{padding:40px 32px 16px;border-bottom:1px solid #1a1a1a}
h1{margin:0;font-size:clamp(28px,4vw,56px);letter-spacing:-0.02em;font-weight:700}
p.sub{margin:6px 0 0;color:var(--mut);max-width:70ch;font-size:14px}
.before{display:flex;gap:16px;padding:24px 32px;border-bottom:1px solid #1a1a1a;align-items:center}
.before img{max-height:140px;border:1px solid #222;border-radius:8px}
.before .cap{color:var(--mut);font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-family:ui-monospace,monospace}
main{padding:24px 32px 64px;display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px}
.card{position:relative;display:flex;flex-direction:column;background:#111;border:1px solid #222;border-radius:16px;color:var(--fg);text-decoration:none;overflow:hidden;transition:transform .25s, border-color .25s}
.card img{width:100%;height:auto;display:block;aspect-ratio:16/10;object-fit:cover;background:#222}
.card:hover{border-color:var(--acc);transform:translateY(-2px)}
.card .num,.card .label,.card .slug,.card .err{padding:4px 14px}
.card .num{color:var(--mut);font-size:11px;font-family:ui-monospace,monospace;padding-top:12px}
.card .label{font-size:18px;font-weight:600;letter-spacing:-0.01em;padding-top:2px}
.card .slug{color:var(--mut);font-size:12px;font-family:ui-monospace,monospace;padding-bottom:14px}
.card.fail .err{color:#f66;font-size:12px;padding-bottom:14px}
.card.fail{opacity:.55}
</style>
<header>
  <h1>fal-design: variants</h1>
  <p class="sub">${results.filter((r) => r.ok).length} of ${results.length} redesigns rendered. Pick your favorite, then run <code>describe.sh --after &lt;file&gt;</code> to produce the build-spec for it.</p>
</header>
<section class="before"><img src="./${beforeRel}" alt="before"><span class="cap">Before: current site</span></section>
<main>${cards}</main>`;
}

const DELTA_SYSTEM = `You are a senior design QA engineer. You receive two attached images:

  IMAGE 1 = CURRENT IMPLEMENTATION: a screenshot of the live site the engineer has shipped.
  IMAGE 2 = REFERENCE TARGET: the approved design to match.

The engineer has already done one implementation pass. Your job is a surgical delta-spec: only the pixel-level residual fixes needed to make CURRENT match TARGET.

Rules:
- Do NOT re-describe the whole design. Skip anything that already matches.
- Prioritize: (1) type scale + line breaks, (2) section density / max-widths, (3) exact colors, (4) component details (buttons, chips, borders), (5) casing / capitalization.
- Be quantitative: "headline max-width 18ch instead of full width", "clamp hero to 128px", "add gradient #4B3BFF → #8B5BFF on Search button", "break headline after 'image.' only".
- Output Markdown, 10-30 bullets under a single "# Delta spec" heading.
- No compliments, no summary, no trailing notes.`;

export async function deltaSpec({ currentUrl, targetUrl }) {
  const out = await callVision({
    prompt: `IMAGE 1 is CURRENT (live site). IMAGE 2 is TARGET (reference). Write the delta-spec now.`,
    system_prompt: DELTA_SYSTEM,
    image_urls: [currentUrl, targetUrl],
    temperature: 0.3,
    max_tokens: 3000,
  });
  return out.trim();
}

export async function describeExisting({ afterPath, outDir }) {
  ensureKey();
  if (!outDir) outDir = dirname(afterPath);
  mkdirSync(outDir, { recursive: true });

  const changesPath = join(outDir, "changes.md");
  const tokensPath = join(outDir, "tokens.json");

  console.error(`[fal-design describe] 1/3 uploading ${afterPath}`);
  const afterUrl = await uploadLocal(afterPath);

  console.error(`[fal-design describe] 2/3 opus-4.7 vision → build-spec + tokens`);
  const { markdown, tokens } = await describeTarget({ afterUrl });
  writeFileSync(changesPath, markdown);
  if (tokens) writeFileSync(tokensPath, JSON.stringify(tokens, null, 2));

  return { changesPath, tokensPath: tokens ? tokensPath : null, changes: markdown, tokens };
}

export async function iterateSite({ target, referenceAfterPath, outDir }) {
  ensureKey();
  if (!outDir) outDir = join(process.cwd(), ".fal-site-upgrade");
  mkdirSync(outDir, { recursive: true });

  const currentPath = join(outDir, "current.png");
  const deltaPath = join(outDir, "delta.md");

  console.error(`[fal-site iterate] 1/3 screenshotting implemented site → ${currentPath}`);
  await screenshotHtml(target, currentPath);

  console.error(`[fal-site iterate] 2/3 uploading current + reference to fal storage`);
  const currentUrl = await uploadLocal(currentPath);
  const targetUrl = await uploadLocal(referenceAfterPath);

  console.error(`[fal-site iterate] 3/3 vision delta-spec (opus-4.7)`);
  const delta = await deltaSpec({ currentUrl, targetUrl });
  writeFileSync(deltaPath, delta);

  return { currentPath, deltaPath, delta };
}

