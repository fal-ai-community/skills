// Thin fal.ai HTTP client (no external deps).
// Uses the sync endpoint https://fal.run/<model> with FAL_KEY in header.

const FAL_BASE = "https://fal.run";

function getKey() {
  const k = process.env.FAL_KEY;
  if (!k) {
    throw new Error(
      "FAL_KEY is not set. Get one at https://fal.ai/dashboard/keys and export it: export FAL_KEY=..."
    );
  }
  return k;
}

export async function falRun(model, payload, { timeoutMs = 240_000 } = {}) {
  const key = getKey();
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${FAL_BASE}/${model}`, {
      method: "POST",
      headers: {
        "Authorization": `Key ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`fal ${model} failed: ${res.status} ${res.statusText} ${body.slice(0, 400)}`);
    }
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

// Text-only LLM through fal -> OpenRouter unified router.
// Docs: https://fal.ai/models/openrouter/router
export async function llm({
  prompt,
  system_prompt,
  model = "anthropic/claude-sonnet-4.6",
  temperature = 0.9,
  max_tokens = 12_000,
  reasoning = false,
} = {}) {
  const out = await falRun("openrouter/router", {
    prompt,
    system_prompt,
    model,
    temperature,
    max_tokens,
    reasoning,
  });
  if (out.error) throw new Error(`openrouter/router error: ${out.error}`);
  return out.output ?? "";
}

// Vision LLM: same router, with images attached.
// Docs: https://fal.ai/models/openrouter/router/vision
export async function llmVision({
  prompt,
  image_urls,
  system_prompt,
  model = "anthropic/claude-sonnet-4.6",
  temperature = 0.6,
  max_tokens = 4_000,
} = {}) {
  if (!Array.isArray(image_urls) || !image_urls.length) {
    throw new Error("llmVision requires image_urls: string[]");
  }
  const out = await falRun("openrouter/router/vision", {
    prompt,
    image_urls,
    system_prompt,
    model,
    temperature,
    max_tokens,
  });
  if (out.error) throw new Error(`openrouter/router/vision error: ${out.error}`);
  return out.output ?? "";
}

export async function gptImage2({ prompt, image_size = { width: 1536, height: 1024 }, quality = "high" }) {
  const out = await falRun("fal-ai/gpt-image-2", {
    prompt,
    image_size,
    quality,
    num_images: 1,
    output_format: "png",
  });
  const url = out?.images?.[0]?.url;
  if (!url) throw new Error(`gpt-image-2 returned no image: ${JSON.stringify(out).slice(0, 300)}`);
  return url;
}

export async function downloadAsDataUri(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download ${url} failed: ${res.status}`);
  const mime = res.headers.get("content-type") || "image/png";
  const buf = Buffer.from(await res.arrayBuffer());
  return `data:${mime};base64,${buf.toString("base64")}`;
}
