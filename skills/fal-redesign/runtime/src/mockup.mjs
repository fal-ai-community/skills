import { llm, gptImage2 } from "./fal.mjs";

// Step A: ask the text router to write a very rich gpt-image-2 prompt describing the ENTIRE website
//         as a pixel-perfect desktop mockup (Dribbble-style), including every visible piece of copy,
//         nav, CTAs and sections.
// Step B: feed that prompt to gpt-image-2 and return the generated mockup URL.

const PROMPTWRITER_SYSTEM = `You are a senior art director + prompt engineer. You write detailed prompts for the OpenAI gpt-image-2 model (which renders sharp in-image text very well).

Given a brand BRIEF and a DESIGN DIRECTION, produce ONE prompt that will generate a pixel-perfect, full-desktop website mockup: as if it were a single long screenshot from a top design-award Site-of-the-Day.

Your prompt MUST describe, concretely and in order from top to bottom:
- Overall canvas: tall desktop web page screenshot, flat front-on view, no hand/mockup frame, no browser chrome, the page content fills the whole image edge-to-edge.
- The exact typography (serif vs sans, weight, tracking), palette (hex-ish words), spacing, grid.
- A navigation bar with the brand wordmark and 3-5 named links (derive from the brief).
- A hero section with the exact tagline, one supporting line of body copy, a primary CTA label and a secondary CTA label: quote them verbatim from the brief.
- 3 to 5 body sections: each with its heading, short body copy, and any labels, tags, stats or captions. All text must be READABLE in the final image.
- A footer with the brand, a short line, and 3-4 footer links.
- The visual mood: imagery style, photo vs illustration, texture, grain, lighting.
- A single hero image or artwork described concretely (subject, framing, palette).
- Explicit quality directives: "razor-sharp text rendering", "no lorem ipsum", "no broken glyphs", "no duplicated words".

The result is ONE PROMPT STRING: 400 to 900 words: ready to paste into gpt-image-2. No JSON, no markdown, no bullet lists, no preamble. Write it as flowing but very specific art-director copy. End with: "Render as a single tall desktop web page screenshot, 1440x2880, no mockup frame, no device, no watermark."`;

export async function writeMockupPrompt({ brief, direction }) {
  const text = await llm({
    system_prompt: PROMPTWRITER_SYSTEM,
    prompt: [
      `BRIEF:`,
      JSON.stringify(brief, null, 2),
      ``,
      `DESIGN DIRECTION: ${direction.label}: ${direction.vibe}`,
      ``,
      `Write the single gpt-image-2 prompt now.`,
    ].join("\n"),
    temperature: 0.8,
    max_tokens: 3000,
  });
  return text.trim();
}

export async function renderMockup(mockupPrompt) {
  // 1440x2880 = 4.15MP, 2:4 = 1:2 ratio, well within gpt-image-2 limits and shaped like a real long desktop page.
  const url = await gptImage2({
    prompt: mockupPrompt,
    image_size: { width: 1440, height: 2880 },
    quality: "high",
  });
  return url;
}
