#!/usr/bin/env node
import { mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { join, resolve, isAbsolute, dirname } from "node:path";
import { extractBrief } from "../src/brief.mjs";
import { pickDirections, DIRECTIONS } from "../src/directions.mjs";
import { writeMockupPrompt, renderMockup } from "../src/mockup.mjs";
import { implementFromMockup, mockupToDataUri } from "../src/implement.mjs";
import { upgradeSite, iterateSite, describeExisting, implementFromOriginal, generateTiles, screenshotHtml } from "../src/upgrade.mjs";
import { fal } from "@fal-ai/client";
import { buildClip } from "../src/video.mjs";

const HELP = `fal-site — AI-native design pipeline on fal.ai.

Sub-commands:
  upgrade <path|url>        Upgrade a site you (Claude Code / Codex) already coded.
                            Screenshots it → vision LLM writes an edit prompt
                            → gpt-image-2/edit redesigns it → vision LLM emits
                            a Markdown build-spec + JSON design tokens, and
                            crops grid tiles from the mockup. Outputs:
                            after.png + changes.md + tokens.json + tiles/.

  iterate <path|url>        Compare the currently-implemented site to a
                            reference after.png and emit a delta-spec of the
                            residual pixel-level fixes.

  generate "<context>"      Greenfield: brief → mockup prompt → gpt-image-2 mockup
                            → vision LLM implements as single-file HTML.

Usage:
  npx fal-site upgrade ./index.html [options]
  npx fal-site upgrade http://localhost:3000 [options]
  npx fal-site iterate ./index.html --reference .fal-review/after.png
  npx fal-site generate "<context>" [options]

Common options:
  -o, --out <dir>           Output directory
      --context <text>      (upgrade) extra brand context / brief paragraph
      --context-file <p>    (upgrade) read context from file
  -h, --help                Show this help

upgrade options:
  (none beyond common)

generate options:
  -n, --variants <N>        Number of variations (default 4, max ${DIRECTIONS.length})
      --concurrency <N>     Parallel builds (default 2)
      --list-directions     Print design directions and exit
      --mockup-only         Stop after mockup (skip HTML implementation)

Env:
  FAL_KEY                   Required. https://fal.ai/dashboard/keys

Examples:
  # Claude Code has coded ./index.html; ask fal-site to upgrade the design:
  npx fal-site upgrade ./index.html -o .fal-review
  # Feed Claude Code back the change-spec and image:
  cat .fal-review/changes.md && open .fal-review/after.png

  # Or greenfield from scratch:
  npx fal-site generate "Saint-Crampon volunteer bouldering church gym in Lyon" -n 3
`;

async function readStdin() {
  return await new Promise((res) => {
    let buf = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => (buf += c));
    process.stdin.on("end", () => res(buf));
  });
}

function slugify(s) {
  return String(s || "site").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40) || "site";
}

async function runPool(items, concurrency, worker) {
  const results = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.max(1, concurrency) }, async () => {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      try {
        results[i] = { ok: true, value: await worker(items[i], i) };
      } catch (e) {
        results[i] = { ok: false, error: e };
      }
    }
  });
  await Promise.all(workers);
  return results;
}

function parseCommon(argv) {
  // variants defaults to null; each subcommand picks its own default (upgrade=1, generate=4).
  const out = { positional: [], out: null, context: null, contextFile: null, variants: null, concurrency: 2, listDirections: false, mockupOnly: false, reference: null, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") out.help = true;
    else if (a === "-o" || a === "--out") out.out = argv[++i];
    else if (a === "--context") out.context = argv[++i];
    else if (a === "--context-file") out.contextFile = argv[++i];
    else if (a === "--reference") out.reference = argv[++i];
    else if (a === "-n" || a === "--variants") out.variants = parseInt(argv[++i], 10);
    else if (a === "--concurrency") out.concurrency = parseInt(argv[++i], 10);
    else if (a === "--list-directions") out.listDirections = true;
    else if (a === "--mockup-only") out.mockupOnly = true;
    else if (a.startsWith("-")) { console.error(`Unknown flag: ${a}`); process.exit(2); }
    else out.positional.push(a);
  }
  return out;
}

async function cmdImplement(argv) {
  const out = { original: null, after: null, outHtml: null, tilesDir: null, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") out.help = true;
    else if (a === "--original") out.original = argv[++i];
    else if (a === "--after") out.after = argv[++i];
    else if (a === "--out") out.outHtml = argv[++i];
    else if (a === "--tiles-dir") out.tilesDir = argv[++i];
    else { console.error(`implement: unknown flag: ${a}`); process.exit(2); }
  }
  if (out.help) { console.log(HELP); return; }
  if (!out.original || !out.after || !out.outHtml) {
    console.error("implement: --original <html> --after <png> --out <html> are required.");
    process.exit(2);
  }
  const { readFileSync, writeFileSync, mkdirSync } = await import("node:fs");
  fal.config({ credentials: process.env.FAL_KEY });
  const afterBuf = readFileSync(resolve(out.after));
  const { Blob, File } = globalThis;
  const file = new File([new Blob([afterBuf], { type: "image/png" })], "after.png", { type: "image/png" });
  console.error(`[implement] uploading after.png → fal storage`);
  const afterUrl = await fal.storage.upload(file);
  console.error(`[implement] opus-4.7 vision writing new HTML + tile prompts`);
  const { html, tiles } = await implementFromOriginal({ originalHtmlPath: resolve(out.original), afterUrl });
  writeFileSync(resolve(out.outHtml), html);
  console.error(`[implement] ✓ ${out.outHtml}  (${tiles.length} tile(s) to generate)`);

  if (tiles.length) {
    const tilesDir = out.tilesDir ? resolve(out.tilesDir) : resolve(dirname(out.outHtml), "tiles");
    mkdirSync(tilesDir, { recursive: true });
    console.error(`[implement] generating ${tiles.length} tile(s) via flux-2/klein/9b/edit in parallel`);
    const results = await generateTiles({ tiles, mockupUrl: afterUrl, outDir: tilesDir });
    const ok = results.filter((r) => r.ok).length;
    const fail = results.length - ok;
    console.error(`[implement] tiles: ${ok} ok, ${fail} failed → ${tilesDir}`);
    results.forEach((r) => { if (!r.ok) console.error(`   ✗ ${r.file}: ${r.error}`); });
  }
}

async function cmdScreenshot(argv) {
  const out = { target: null, outPath: null, fullPage: false, help: false, width: 1920, height: 1080 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") out.help = true;
    else if (a === "--target") out.target = argv[++i];
    else if (a === "--out") out.outPath = argv[++i];
    else if (a === "--full-page") out.fullPage = true;
    else if (a === "--width") out.width = parseInt(argv[++i], 10);
    else if (a === "--height") out.height = parseInt(argv[++i], 10);
    else { console.error(`screenshot: unknown flag: ${a}`); process.exit(2); }
  }
  if (out.help) { console.log(HELP); return; }
  if (!out.target || !out.outPath) { console.error("screenshot: --target and --out required."); process.exit(2); }
  await screenshotHtml(resolve(out.target), resolve(out.outPath), { viewport: { width: out.width, height: out.height }, fullPage: out.fullPage });
  console.error(`[screenshot] ✓ ${out.outPath}`);
}

async function cmdVideo(argv) {
  const out = { before: null, after: null, mockup: null, title: null, outPath: null, duration: 8, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") out.help = true;
    else if (a === "--before") out.before = argv[++i];
    else if (a === "--after") out.after = argv[++i];
    else if (a === "--mockup") out.mockup = argv[++i];
    else if (a === "--title") out.title = argv[++i];
    else if (a === "--duration") out.duration = parseFloat(argv[++i]);
    else if (a === "--out" || a === "-o") out.outPath = argv[++i];
    else { console.error(`video: unknown flag: ${a}`); process.exit(2); }
  }
  if (out.help) { console.log(HELP); return; }
  if (!out.before || !out.after || !out.title || !out.outPath) {
    console.error("video: --before <png> --after <png> [--mockup <png>] --title <name> --out <mp4> are required.");
    process.exit(2);
  }
  const t0 = Date.now();
  const r = await buildClip({
    beforePath: resolve(out.before),
    afterPath: resolve(out.after),
    mockupPath: out.mockup ? resolve(out.mockup) : null,
    title: out.title,
    outPath: resolve(out.outPath),
    duration: out.duration,
  });
  console.error(`\n✔ video built in ${((Date.now() - t0) / 1000).toFixed(1)}s  (${r.duration}s clip)`);
  console.error(`  mp4: ${r.outPath}`);
}

async function cmdDescribe(argv) {
  const args = parseCommon(argv);
  if (args.help) { console.log(HELP); return; }
  const afterPath = args.positional[0];
  if (!afterPath) {
    console.error("describe: missing path to an existing after.png.\n\n" + HELP);
    process.exit(2);
  }
  if (!existsSync(afterPath)) {
    console.error(`describe: file not found: ${afterPath}`);
    process.exit(2);
  }
  const outDir = args.out
    ? (isAbsolute(args.out) ? args.out : resolve(process.cwd(), args.out))
    : dirname(resolve(afterPath));
  const t0 = Date.now();
  const r = await describeExisting({ afterPath: resolve(afterPath), outDir });
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.error(`\n✔ describe complete in ${elapsed}s`);
  console.error(`  changes: ${r.changesPath}`);
  if (r.tokensPath) console.error(`  tokens:  ${r.tokensPath}`);
  if (r.tilesDir) console.error(`  tiles:   ${r.tilesDir} (${r.tilePaths.length} file(s))`);
  process.stdout.write(`# fal-redesign describe\n\nReference image: ${resolve(afterPath)}\n\n${r.changes}\n`);
}

async function cmdIterate(argv) {
  const args = parseCommon(argv);
  if (args.help) { console.log(HELP); return; }
  const target = args.positional[0];
  if (!target) {
    console.error("iterate: missing target (file path or URL to the implemented site).\n\n" + HELP);
    process.exit(2);
  }
  if (!args.reference) {
    console.error("iterate: --reference <path-to-after.png> is required.");
    process.exit(2);
  }
  if (!existsSync(args.reference)) {
    console.error(`iterate: reference file not found: ${args.reference}`);
    process.exit(2);
  }
  if (!/^https?:/.test(target) && !existsSync(target)) {
    console.error(`iterate: target not found: ${target}`);
    process.exit(2);
  }

  const outDir = args.out
    ? (isAbsolute(args.out) ? args.out : resolve(process.cwd(), args.out))
    : resolve(process.cwd(), ".fal-site-upgrade");

  const t0 = Date.now();
  const r = await iterateSite({ target, referenceAfterPath: resolve(args.reference), outDir });
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.error(`\n✔ iterate complete in ${elapsed}s`);
  console.error(`  current: ${r.currentPath}`);
  console.error(`  delta:   ${r.deltaPath}`);
  process.stdout.write(`# fal-site iterate\n\nCurrent screenshot: ${r.currentPath}\nReference target:  ${resolve(args.reference)}\n\n${r.delta}\n`);
}

async function cmdUpgrade(argv) {
  const args = parseCommon(argv);
  if (args.help) { console.log(HELP); return; }
  const target = args.positional[0];
  if (!target) {
    console.error("upgrade: missing target (file path or URL).\n\n" + HELP);
    process.exit(2);
  }
  if (!/^https?:/.test(target) && !existsSync(target)) {
    console.error(`upgrade: target not found: ${target}`);
    process.exit(2);
  }

  let context = null;
  if (args.contextFile) context = { notes: readFileSync(args.contextFile, "utf8") };
  else if (args.context) context = { notes: args.context };

  const outDir = args.out
    ? (isAbsolute(args.out) ? args.out : resolve(process.cwd(), args.out))
    : resolve(process.cwd(), ".fal-site-upgrade");

  const nVariants = Math.max(1, Math.min(args.variants || 1, 8));
  const t0 = Date.now();
  const r = await upgradeSite({ target, outDir, context, variants: nVariants });
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);

  if (r.mode === "multi") {
    const okCount = r.variants.filter((v) => v.ok).length;
    console.error(`\n✔ upgrade complete in ${elapsed}s — ${okCount}/${r.variants.length} variants`);
    console.error(`  before:  ${r.beforePath}`);
    console.error(`  gallery: ${r.galleryPath}`);
    r.variants.forEach((v) => {
      if (v.ok) console.error(`  - ${v.slug}: ${v.afterPath}`);
      else console.error(`  - ${v.slug}: FAIL ${v.error}`);
    });
    const lines = [`# fal-redesign upgrade — variants`, ``, `Open gallery: ${r.galleryPath}`, ``, `Generated variants:`, ...r.variants.filter((v) => v.ok).map((v) => `- **${v.direction.label}** (${v.direction.slug}) → ${v.afterPath}`), ``, `Next step: pick your favorite, then run`, `\`\`\``, `bash scripts/describe.sh --after <chosen-after-*.png>`, `\`\`\``, `to produce the build-spec for the chosen direction.`];
    process.stdout.write(lines.join("\n") + "\n");
    return;
  }

  // single-variant
  console.error(`\n✔ upgrade complete in ${elapsed}s`);
  console.error(`  before:  ${r.beforePath}`);
  console.error(`  after:   ${r.afterPath}`);
  console.error(`  changes: ${r.changesPath}`);
  if (r.tokensPath) console.error(`  tokens:  ${r.tokensPath}`);
  console.error(`  prompt:  ${r.editPromptPath}`);
  process.stdout.write(`# fal-redesign upgrade\n\nRedesigned reference image: ${r.afterPath}\n\n${r.changes}\n`);
}

async function cmdGenerate(argv) {
  const args = parseCommon(argv);
  if (args.help) { console.log(HELP); return; }

  if (args.listDirections) {
    for (const d of DIRECTIONS) console.log(`${d.slug.padEnd(22)} ${d.label}`);
    return;
  }

  let context = args.positional.join(" ");
  if (args.contextFile) context = readFileSync(args.contextFile, "utf8");
  if (!context.trim() && !process.stdin.isTTY) context = await readStdin();
  if (!context.trim()) {
    console.error("generate: no context provided.\n\n" + HELP);
    process.exit(2);
  }

  if (!process.env.FAL_KEY) {
    console.error("FAL_KEY env var is not set. Get one at https://fal.ai/dashboard/keys");
    process.exit(1);
  }

  const t0 = Date.now();
  console.error(`→ [1/4] extracting brief from context (${context.length} chars)...`);
  const brief = await extractBrief(context);
  console.error(`   brand:   ${brief.brand}`);
  console.error(`   tagline: ${brief.tagline}`);

  const nReq = Math.max(1, Math.min(args.variants || 4, DIRECTIONS.length));
  const directions = pickDirections(nReq);
  console.error(`→ directions (${directions.length}): ${directions.map((d) => d.slug).join(", ")}`);

  const outDir = args.out
    ? (isAbsolute(args.out) ? args.out : resolve(process.cwd(), args.out))
    : resolve(process.cwd(), "fal-site-out");
  const brandSlug = slugify(brief.brand);
  const runDir = join(outDir, `${Date.now()}-${brandSlug}`);
  mkdirSync(runDir, { recursive: true });
  writeFileSync(join(runDir, "brief.json"), JSON.stringify(brief, null, 2));

  const results = await runPool(directions, args.concurrency, async (dir, idx) => {
    const tag = `[${String(idx + 1).padStart(2, "0")}/${directions.length} ${dir.slug}]`;
    const siteDir = join(runDir, `${String(idx + 1).padStart(2, "0")}-${dir.slug}`);
    mkdirSync(siteDir, { recursive: true });

    console.error(`${tag} [2/4] writing mockup prompt...`);
    const mockupPrompt = await writeMockupPrompt({ brief, direction: dir });
    writeFileSync(join(siteDir, "mockup.prompt.txt"), mockupPrompt);

    console.error(`${tag} [3/4] rendering mockup via gpt-image-2...`);
    const mockupUrl = await renderMockup(mockupPrompt);
    const mockupDataUri = await mockupToDataUri(mockupUrl);
    const base64Body = mockupDataUri.split(",", 2)[1];
    writeFileSync(join(siteDir, "mockup.png"), Buffer.from(base64Body, "base64"));

    if (args.mockupOnly) {
      console.error(`${tag} done (mockup only) → ${siteDir}/mockup.png`);
      return { dir: dir.slug, path: join(siteDir, "mockup.png") };
    }

    console.error(`${tag} [4/4] implementing HTML from mockup (vision)...`);
    let html;
    try {
      html = await implementFromMockup({ brief, direction: dir, mockupUrl });
    } catch (e) {
      console.error(`${tag} vision URL failed (${e.message}); retrying with data URI`);
      html = await implementFromMockup({ brief, direction: dir, mockupUrl: mockupDataUri });
    }

    const finalHtml = html.replaceAll("{{HERO_IMAGE}}", mockupDataUri);
    writeFileSync(join(siteDir, "index.html"), finalHtml);
    console.error(`${tag} done → ${siteDir}/index.html`);
    return { dir: dir.slug, path: join(siteDir, "index.html"), mockup: join(siteDir, "mockup.png") };
  });

  const ok = results.filter((r) => r.ok).length;
  const fail = results.length - ok;
  console.error(`\n✔ done in ${((Date.now() - t0) / 1000).toFixed(1)}s  ok=${ok}  fail=${fail}`);
  console.error(`  open: file://${runDir}`);
  results.forEach((r, i) => { if (!r.ok) console.error(`  FAIL [${directions[i].slug}]: ${r.error?.message || r.error}`); });
}

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  if (!cmd || cmd === "-h" || cmd === "--help") { console.log(HELP); return; }
  if (cmd === "upgrade") return cmdUpgrade(argv.slice(1));
  if (cmd === "iterate") return cmdIterate(argv.slice(1));
  if (cmd === "describe") return cmdDescribe(argv.slice(1));
  if (cmd === "implement") return cmdImplement(argv.slice(1));
  if (cmd === "screenshot") return cmdScreenshot(argv.slice(1));
  if (cmd === "video") return cmdVideo(argv.slice(1));
  if (cmd === "generate") return cmdGenerate(argv.slice(1));
  // Back-compat: if first arg is not a subcommand, default to upgrade if it's a file/url, else generate
  if (/^https?:/.test(cmd) || existsSync(cmd)) return cmdUpgrade(argv);
  return cmdGenerate(argv);
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
