import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";
import { llmVision, gptImage2, downloadAsDataUri } from "./fal.mjs";

const REVIEW_SYSTEM = `You are a brutal but fair design-awards jury member and a senior web designer-engineer.
You are given: a screenshot of a website as it currently renders in a browser, plus the raw HTML file and the brief.

Your job, in one pass:
1. Look at the screenshot and identify the concrete flaws that keep this site from being a design-award winner today — type hierarchy, color harmony, pacing, composition, tension, density, motion, copy craft.
2. Rewrite the complete single-file HTML so that those flaws are fixed and the site visibly levels up — stronger editorial confidence, sharper typography, richer layout, better micro-details, unexpected but tasteful choices.
3. Keep the site self-contained: Tailwind via CDN, Google Fonts link, inline <style>, minimal vanilla JS only if needed. No external assets beyond the hero image.
4. Preserve the hero <img> and write it with src="{{HERO_IMAGE}}" (a new hero will be swapped in after your rewrite).
5. Use only the brand/copy in the brief (tighten or rework phrasing is fine; do not invent facts).
6. End your response with a single JSON block wrapped in ~~~HERO_PROMPT ... ~~~ fences containing ONE field: {"hero_prompt": "<a fresh, rich gpt-image-2 prompt (1-3 sentences) that will produce a better hero image fitting the new design; no text or UI in the image>"}.

Output order (exactly this, nothing else):
<the complete improved <!doctype html> document>
~~~HERO_PROMPT
{"hero_prompt": "..."}
~~~

No preamble, no markdown fences around the HTML, no commentary.`;

export async function screenshotHtml(htmlPath, pngPath) {
  const browser = await puppeteer.launch({ headless: "new" });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle0", timeout: 45_000 });
    // give Tailwind CDN + fonts a moment to settle after networkidle
    await new Promise((r) => setTimeout(r, 800));
    await page.screenshot({ path: pngPath, type: "png", fullPage: false });
  } finally {
    await browser.close();
  }
  return pngPath;
}

function splitReviewOutput(text) {
  const m = text.match(/([\s\S]*?)~~~HERO_PROMPT\s*([\s\S]*?)~~~/);
  if (!m) {
    return { html: cleanupHtml(text), heroPrompt: null };
  }
  const htmlPart = cleanupHtml(m[1]);
  let heroPrompt = null;
  try {
    const json = JSON.parse(m[2].trim());
    heroPrompt = json.hero_prompt || null;
  } catch {}
  return { html: htmlPart, heroPrompt };
}

function cleanupHtml(text) {
  let t = text.trim().replace(/^```(?:html)?\s*/i, "").replace(/```\s*$/, "").trim();
  const i = t.search(/<!doctype html>/i);
  if (i > 0) t = t.slice(i);
  return t;
}

// Encode a local image file as a data: URI (the vision endpoint accepts these).
export function localImageToDataUri(localPath, mime = "image/png") {
  const bytes = readFileSync(localPath);
  return `data:${mime};base64,${Buffer.from(bytes).toString("base64")}`;
}

export async function reviewVariant({ siteDir, brief, direction }) {
  const htmlPath = join(siteDir, "index.html");
  const shotPath = join(siteDir, "_before.png");
  console.log(`   screenshotting ${htmlPath}`);
  await screenshotHtml(htmlPath, shotPath);

  const shotUrl = localImageToDataUri(shotPath, "image/png");

  const html = readFileSync(htmlPath, "utf8");
  const prompt = [
    `BRIEF:`,
    JSON.stringify(brief, null, 2),
    ``,
    `DESIGN DIRECTION: ${direction.label} — ${direction.vibe}`,
    ``,
    `CURRENT HTML (inline, between BEGIN_HTML / END_HTML):`,
    `BEGIN_HTML`,
    html,
    `END_HTML`,
    ``,
    `Use the screenshot to critique and rewrite. Output the rewritten HTML + HERO_PROMPT block now.`,
  ].join("\n");

  console.log(`   vision review → openrouter/router/vision`);
  const raw = await llmVision({
    system_prompt: REVIEW_SYSTEM,
    prompt,
    image_urls: [shotUrl],
    temperature: 0.8,
    max_tokens: 16_000,
    model: "anthropic/claude-sonnet-4.6",
  });

  const { html: improvedHtml, heroPrompt } = splitReviewOutput(raw);
  if (!/<!doctype html>/i.test(improvedHtml)) {
    throw new Error("review did not return a valid <!doctype html> document");
  }

  let heroDataUri = null;
  if (heroPrompt) {
    console.log(`   regenerating hero via gpt-image-2`);
    const url = await gptImage2({ prompt: heroPrompt, image_size: { width: 1536, height: 1024 }, quality: "high" });
    heroDataUri = await downloadAsDataUri(url);
  }

  const finalHtml = heroDataUri
    ? improvedHtml.replaceAll("{{HERO_IMAGE}}", heroDataUri)
    : improvedHtml; // keep old inline hero if no new prompt

  writeFileSync(htmlPath, finalHtml);
  console.log(`   ✓ reviewed site written → ${htmlPath}`);

  // Screenshot the after version too, for side-by-side.
  const afterShot = join(siteDir, "_after.png");
  try {
    await screenshotHtml(htmlPath, afterShot);
    console.log(`   ✓ after-screenshot → ${afterShot}`);
  } catch (e) {
    console.warn(`   after-screenshot failed: ${e.message}`);
  }
  return { heroPrompt, screenshots: { before: shotPath, after: afterShot } };
}
