// Stills and layout data for scene pages (textkit.js). For each page:t1,t2 it seeks, writes <out>/<page>_<t>.png and prints
// one JSON line with the page's strings (for the glyph check) and its visible chips and tabs (for the centring check).
// Pipe it into check.py. Run it in the pages' folder, on the machine that has their fonts:
//   node check.mjs [--w 1920 --h 1080 --out out] [--order] S_map.html:4.2,18.9 S_flux.html:9.3 | python3 check.py --css fonts.css
// --order: each moment is also captured after two other moments (half the scene away, and 0.37 s before); a difference means
// the scene keeps state between seeks, and check.py counts it as a problem.
// playwright (or playwright-core) is resolved from PLAYWRIGHT_FROM (a folder or file that can require it), then the current
// folder. Chrome: CHROME=/path, else the usual macOS / Linux locations, else the Chromium
// Playwright installed (npx playwright install chromium). A page that sets window.W / window.H gets that viewport.
import { createRequire } from "node:module";
import { resolve, basename } from "node:path";
import { mkdirSync, existsSync } from "node:fs";

const argv = process.argv.slice(2), arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const W = +arg("--w", 1920), H = +arg("--h", 1080), OUT = arg("--out", "out"), ORDER = argv.includes("--order");
const specs = argv.filter((a) => !a.startsWith("--") && /\.html?:/.test(a));

function playwright() {
  const from = [process.env.PLAYWRIGHT_FROM, process.cwd()].filter(Boolean);
  for (const f of from) for (const m of ["playwright", "playwright-core"]) {
    const base = /\.(m?js|cjs|json)$/.test(f) ? resolve(f) : resolve(f) + "/";      // createRequire wants a file, or a folder ending in /
    try { return createRequire(base)(m); } catch (e) { /* next */ }
  }
  console.error("playwright not found: npm i playwright here (then npx playwright install chromium), or set PLAYWRIGHT_FROM"); process.exit(2);
}
const { chromium } = playwright();
const CHROME = process.env.CHROME || ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find((p) => existsSync(p));   // none: Playwright's own

const ARGS = ["--force-color-profile=srgb", "--allow-file-access-from-files"].concat(process.platform === "linux" ? ["--no-sandbox"] : []);   // containers and sandboxes
const browser = await chromium.launch({ headless: true, args: ARGS, ...(CHROME ? { executablePath: CHROME } : {}) });
mkdirSync(OUT, { recursive: true });
for (const spec of specs) {
  const k = spec.lastIndexOf(":"), page = spec.slice(0, k), ts = spec.slice(k + 1);
  const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  pg.on("pageerror", (e) => console.error("PAGE ERROR:", page, e.message));
  pg.on("console", (m) => { if (m.type() === "error") console.error("CONSOLE:", page, m.text()); });
  let err = null;
  try {
    await pg.goto("file://" + resolve(page));
    await pg.waitForFunction(() => window.__ready === true || !!window.__fontError, null, { timeout: 60000 });
    err = await pg.evaluate(() => window.__fontError);
  } catch (e) { err = String(e.message || e).split("\n")[0]; }
  if (err) { console.error("ABORT:", page, err); console.log(JSON.stringify({ page, error: err })); await pg.close(); continue; }
  const [pw, ph] = await pg.evaluate(() => [window.W, window.H]);
  if (pw > 0 && ph > 0) await pg.setViewportSize({ width: pw, height: ph });              // the page's own frame size
  const settle = () => pg.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const seekTo = (tt) => pg.evaluate(async (x) => { await window.seek(x); }, tt);          // an async seek (frame sequences) is awaited
  const LOOP = await pg.evaluate(() => window.LOOP || 0);
  for (const t of ts.split(",").map(Number)) {
    if (ORDER) {
      const caps = [];
      for (const p of [LOOP ? (t + LOOP / 2) % LOOP : t + 1, Math.max(0, t - 0.37)]) { await seekTo(p); await seekTo(t); await settle(); caps.push(await pg.screenshot()); }
      if (!caps[0].equals(caps[1])) console.log(JSON.stringify({ page, t, error: `seek order changes pixels at t=${t}` }));
    }
    await seekTo(t);
    await settle();
    const png = `${OUT}/${basename(page).replace(/\.html$/, "")}_${t.toFixed(2)}.png`;
    await pg.screenshot({ path: png });
    const strings = await pg.evaluate(() => (window.__strings ? window.__strings() : []));
    const boxes = await pg.evaluate(() => (window.__pills ? window.__pills() : []));
    console.log(JSON.stringify({ page, t, png, strings, boxes }));
  }
  await pg.close();
}
await browser.close();
