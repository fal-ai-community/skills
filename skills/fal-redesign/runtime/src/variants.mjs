import { llm, llmVision } from "./fal.mjs";

const SYSTEM = `You are an award-winning senior web designer + front-end engineer. Your portfolio consistently earns design-award Site-of-the-Day recognition. You obsess over typography, grid, whitespace, motion, micro-interactions, and copy craft.

Produce ONE complete single-file website (index.html) based on the brief and the given design direction.

Hard requirements:
- Output ONLY the HTML. No markdown fences, no explanations before or after.
- Self-contained single <!DOCTYPE html> document.
- Use Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>
- Extra custom CSS allowed inline in a <style> tag.
- Fonts from Google Fonts <link> tag: pick fonts that match the direction (don't default to Inter).
- Minimal vanilla JS only if truly needed (no libraries beyond Tailwind CDN).
- Use semantic HTML (header, main, section, footer, nav, article).
- Fully responsive, mobile-first, polished at every breakpoint.
- Accessible: color contrast, alt text, aria-labels on interactive elements.
- No lorem ipsum. Use ONLY copy from the brief (you may tighten / restructure it).
- Hero <img> tag must have src="{{HERO_IMAGE}}" (this placeholder will be swapped for a real image data URI afterwards). Give it meaningful alt text and a responsive sizing class.
- Multiple sections (hero + 3-5 content sections + footer), each visually distinct and crafted.
- Ambitious typography: at least one oversized display heading with careful tracking/leading.
- Ambitious layout: break out of the default centered-column cliche.
- Include tasteful motion: CSS transitions on hover/focus, subtle keyframe animations where fitting.
- Do NOT copy any competitor's brand or logo. This is an original site for the brief's brand.

Critical: the output must read as "how did they make this in a browser" level. Think design-award Site-of-the-Day, not a boilerplate landing.`;

export async function generateVariant({ brief, direction, heroImageUrl }) {
  const baseBlocks = [
    `BRIEF:`,
    JSON.stringify(brief, null, 2),
    ``,
    `DESIGN DIRECTION: ${direction.label}`,
    `DIRECTION DETAILS: ${direction.vibe}`,
  ];

  let html;
  if (heroImageUrl) {
    const prompt = [
      ...baseBlocks,
      ``,
      `A hero image has already been generated for this variant (attached). ITS AESTHETIC IS THE LAW FOR THIS SITE:`,
      `- Extract the palette directly from the hero image (2-4 colors) and build the whole page around it (backgrounds, accent, text): they must be visibly coherent.`,
      `- Match the image's mood, rendering style (photo / illustration / 3D / grainy / clean), lighting and level of saturation in the rest of the UI.`,
      `- Choose typography that feels native to the image's era and temperature.`,
      `- Any section, button, divider, gradient and secondary imagery must look like it was cropped from the same visual universe.`,
      ``,
      `Deliver the complete single-file index.html now. The hero <img> must use src="{{HERO_IMAGE}}".`,
    ].join("\n");
    html = await llmVision({
      system_prompt: SYSTEM,
      prompt,
      image_urls: [heroImageUrl],
      temperature: 0.9,
      max_tokens: 16_000,
      model: "anthropic/claude-sonnet-4.6",
    });
  } else {
    const prompt = [
      ...baseBlocks,
      ``,
      `No hero image yet: design with placeholder img src="{{HERO_IMAGE}}". Keep palette and typography tight to the direction.`,
    ].join("\n");
    html = await llm({
      system_prompt: SYSTEM,
      prompt,
      temperature: 1.0,
      max_tokens: 16_000,
      model: "anthropic/claude-sonnet-4.6",
    });
  }

  return cleanupHtml(html);
}

function cleanupHtml(text) {
  let t = text.trim();
  t = t.replace(/^```(?:html)?\s*/i, "").replace(/```\s*$/, "").trim();
  const i = t.search(/<!doctype html>/i);
  if (i > 0) t = t.slice(i);
  if (!/<!doctype html>/i.test(t)) {
    throw new Error(`Variant output is not a valid HTML document: ${t.slice(0, 200)}`);
  }
  return t;
}
