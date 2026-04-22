import { llm } from "./fal.mjs";

const BRIEF_SYSTEM = `You are a senior brand strategist + creative director. Given raw context about a product, person, event or idea, return a compact JSON brief used to design a website. Be inventive when context is sparse, but never fabricate numbers, dates, quotes or testimonials. Write copy that sounds human, confident, specific.

Output STRICT JSON. No markdown fences, no prose before or after. Schema:

{
  "brand": string,                 // short brand / site name
  "tagline": string,               // max 10 words, punchy
  "one_liner": string,             // one sentence, 15-25 words, concrete value
  "about_paragraph": string,       // 2-3 sentences
  "audience": string,              // who is this for, 1 sentence
  "tone": string,                  // e.g. "editorial / confident / dry wit"
  "palette_hint": string,          // e.g. "bone white, ink black, single hot-red accent"
  "sections": [                    // 3 to 5 sections, each with a short heading + 1-2 sentence body
    {"heading": string, "body": string}
  ],
  "features": [string],            // 3-5 one-line feature bullets
  "cta_primary": string,           // short CTA label (2-4 words)
  "cta_secondary": string,         // optional short CTA label
  "hero_image_prompt": string      // rich prompt for gpt-image-2 to generate a striking hero image fitting the brand. 1-3 sentences, visually concrete, no text in image.
}`;

export async function extractBrief(context) {
  const raw = await llm({
    system_prompt: BRIEF_SYSTEM,
    prompt: `Raw context:\n\n${context}\n\nReturn the JSON brief now.`,
    temperature: 0.7,
    max_tokens: 2000,
  });
  return parseJsonLoose(raw);
}

function parseJsonLoose(text) {
  const trimmed = text.trim();
  // Strip accidental markdown fences
  const cleaned = trimmed
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/```\s*$/, "")
    .trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    // Fall back: find first { ... last }
    const a = cleaned.indexOf("{");
    const b = cleaned.lastIndexOf("}");
    if (a !== -1 && b !== -1 && b > a) {
      return JSON.parse(cleaned.slice(a, b + 1));
    }
    throw new Error(`Could not parse brief JSON. Raw: ${cleaned.slice(0, 400)}`);
  }
}
