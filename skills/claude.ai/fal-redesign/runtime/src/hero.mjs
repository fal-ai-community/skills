import { gptImage2, downloadAsDataUri } from "./fal.mjs";

// Generate a hero image. Returns { url, dataUri }: url is used as vision reference for the LLM,
// dataUri is embedded in the final standalone HTML so the file is truly self-contained.
export async function generateHero({ brief, direction }) {
  const prompt = [
    brief.hero_image_prompt || `Striking editorial hero image for "${brief.brand}": ${brief.one_liner}.`,
    `Art direction: ${direction.vibe}`,
    `Mood & palette: ${brief.palette_hint || "refined, award-winning design"}.`,
    `Composition: wide cinematic hero, strong focal point, intentional negative space on one side for overlay type. NO text, NO logos, NO watermarks, NO UI elements.`,
    `Quality: award-tier, magazine-grade, razor-sharp, never generic stock.`,
  ].join(" ");

  const url = await gptImage2({
    prompt,
    image_size: { width: 1536, height: 1024 },
    quality: "high",
  });
  const dataUri = await downloadAsDataUri(url);
  return { url, dataUri };
}
