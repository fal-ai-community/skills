// Renders a seek(t) scene page to MP4: Playwright opens the page, waits for window.__ready, seeks every frame and pipes the
// screenshots into ffmpeg (H.264, yuv420p, BT.709 tags). Only the MP4 is written.
//   node render.mjs index.html out.mp4 [--fps 24] [--dur 7.4] [--w 1080 --h 1920] [--crf 16] [--png]
// Size: the page's window.W / window.H, else --w / --h (default 1920x1080). Length: --dur, else window.LOOP.
// playwright (or playwright-core) is resolved from PLAYWRIGHT_FROM, then the current folder. Browser: CHROME=/path, else the
// Chromium Playwright installed (npx playwright install chromium). --png: lossless frames (slower than the default JPEG q95).
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { resolve } from "node:path";
import { existsSync } from "node:fs";

const argv = process.argv.slice(2), arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const [page, out] = argv.filter((a, i) => !a.startsWith("--") && !(i > 0 && argv[i - 1].startsWith("--") && argv[i - 1] !== "--png"));
if (!page || !out) { console.error("usage: node render.mjs page.html out.mp4 [--fps 24] [--dur s] [--w 1920 --h 1080] [--crf 16] [--png]"); process.exit(2); }
const FPS = +arg("--fps", 24), CRF = String(arg("--crf", 16)), PNG = argv.includes("--png");

function playwright() {
  for (const f of [process.env.PLAYWRIGHT_FROM, process.cwd()].filter(Boolean)) {
    for (const m of ["playwright", "playwright-core"]) {
      try { return createRequire(resolve(f) + "/")(m); } catch (e) { /* next */ }
    }
  }
  console.error("playwright not found: npm i playwright here, then npx playwright install chromium"); process.exit(2);
}
const { chromium } = playwright();
const CHROME = process.env.CHROME && existsSync(process.env.CHROME) ? process.env.CHROME : undefined;
const ARGS = ["--force-color-profile=srgb", "--allow-file-access-from-files", "--autoplay-policy=no-user-gesture-required"]
  .concat(process.platform === "linux" ? ["--no-sandbox"] : []);
const browser = await chromium.launch({ headless: true, args: ARGS, ...(CHROME ? { executablePath: CHROME } : {}) });
const pg = await browser.newPage({ viewport: { width: +arg("--w", 1920), height: +arg("--h", 1080) }, deviceScaleFactor: 1 });
pg.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
pg.on("console", (m) => { if (m.type() === "error") console.error("CONSOLE:", m.text()); });

await pg.goto("file://" + resolve(page));
await pg.waitForFunction(() => window.__ready === true || !!window.__fontError, null, { timeout: 120000 });
const err = await pg.evaluate(() => window.__fontError);
if (err) { console.error("ABORT:", err); await browser.close(); process.exit(1); }
const [pw, ph] = await pg.evaluate(() => [window.W, window.H]);
if (pw > 0 && ph > 0) await pg.setViewportSize({ width: pw, height: ph });
const DUR = +arg("--dur", 0) || (await pg.evaluate(() => window.LOOP || 0));
if (!DUR) { console.error("no length: set window.LOOP in the page or pass --dur"); await browser.close(); process.exit(2); }
const N = Math.round(DUR * FPS);

const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-c:v", PNG ? "png" : "mjpeg", "-framerate", String(FPS), "-i", "-",
  "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF, "-pix_fmt", "yuv420p",
  "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", resolve(out)],
  { stdio: ["pipe", "inherit", "inherit"] });
const done = new Promise((r) => ff.on("close", r));
const t0 = Date.now();
for (let i = 0; i < N; i++) {
  await pg.evaluate(async (t) => { await window.seek(t); }, i / FPS);                 // an async seek (frame sequences) is awaited
  await pg.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const buf = await pg.screenshot(PNG ? { type: "png" } : { type: "jpeg", quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
}
ff.stdin.end();
const code = await done;
await browser.close();
if (code !== 0) { console.error("ffmpeg failed with code", code); process.exit(1); }
console.log(`${out}  ${N} frames, ${DUR.toFixed(2)} s at ${FPS} fps, rendered in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
