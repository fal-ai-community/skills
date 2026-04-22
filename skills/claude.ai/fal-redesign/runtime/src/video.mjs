import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { spawn } from "node:child_process";
import puppeteer from "puppeteer";
import sharp from "sharp";

// ---- Small HTML → PNG helper for label pills ----

async function renderHtmlToPng({ html, width, height, outPath, omitBackground = true }) {
  const browser = await puppeteer.launch({ headless: "new" });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: 1 });
    await page.setContent(html, { waitUntil: "networkidle0" });
    await new Promise((r) => setTimeout(r, 400));
    await page.screenshot({ path: outPath, type: "png", omitBackground });
  } finally {
    await browser.close();
  }
  return outPath;
}

function labelPillHtml({ eyebrow, main }) {
  const esc = (s) => String(s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  // Right-aligned inside its canvas so the pill's visible RIGHT edge aligns with the PNG's right edge.
  return `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600&family=Inter:wght@600&display=swap" rel="stylesheet">
<style>
  html,body{margin:0;padding:0;background:transparent;font-family:'Inter',system-ui,sans-serif}
  body{display:flex;justify-content:flex-end;align-items:center;height:100vh;width:100vw}
  .pill{display:inline-flex;align-items:center;gap:16px;padding:18px 26px;background:rgba(255,255,255,0.88);border-radius:999px;color:#0A0A0B;box-shadow:0 8px 32px rgba(0,0,0,0.20),0 2px 8px rgba(0,0,0,0.08);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
  .eyebrow{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#6A6560}
  .sep{width:1px;height:22px;background:#D7D1C2}
  .main{font-family:'Inter';font-size:20px;font-weight:600;letter-spacing:-0.01em;color:#0A0A0B}
</style>
<div class="pill">
  <span class="eyebrow">${esc(eyebrow)}</span>
  <span class="sep"></span>
  <span class="main">${esc(main)}</span>
</div>`;
}

function centerBadgeHtml({ label }) {
  const esc = (s) => String(s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  return `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  html,body{margin:0;padding:0;background:transparent;font-family:'JetBrains Mono',monospace}
  .badge{display:inline-flex;align-items:center;gap:10px;padding:10px 16px;background:rgba(10,10,11,0.55);border:1px solid rgba(242,240,234,0.12);border-radius:999px;color:rgba(242,240,234,0.92);font-size:11px;font-weight:500;letter-spacing:0.24em;text-transform:uppercase;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
  .dot{width:7px;height:7px;border-radius:999px;background:rgba(242,240,234,0.9)}
</style>
<div class="badge"><span class="dot"></span>${esc(label)}</div>`;
}

// ---- ffmpeg wrapper ----

function runFfmpeg(args, { cwd, timeoutMs = 240_000 } = {}) {
  return new Promise((res, rej) => {
    const p = spawn("ffmpeg", args, { cwd, stdio: ["ignore", "ignore", "pipe"] });
    let stderr = "";
    let killed = false;
    const to = setTimeout(() => {
      killed = true;
      try { p.kill("SIGKILL"); } catch {}
      rej(new Error(`ffmpeg timed out after ${timeoutMs}ms`));
    }, timeoutMs);
    p.stderr.on("data", (c) => { stderr += c.toString(); });
    p.on("close", (code) => {
      clearTimeout(to);
      if (killed) return;
      if (code === 0) res();
      else rej(new Error(`ffmpeg exited ${code}\n${stderr.slice(-1800)}`));
    });
    p.on("error", (e) => { clearTimeout(to); rej(e); });
  });
}

// Hold at top for HOLD_START, ease-in-out-scroll for the middle, hold at bottom for HOLD_END.
// p = clip((t - HOLD_START) / TEASE, 0, 1); y = rng * (3*p^2 - 2*p^3).
function easeYExpr(T, rng, { holdStart = 1.2, holdEnd = 0.5 } = {}) {
  const tease = Math.max(0.1, T - holdStart - holdEnd);
  const p = `clip((t-${holdStart})/${tease.toFixed(2)}\\,0\\,1)`;
  return `(${rng.toFixed(1)})*(3*pow(${p}\\,2)-2*pow(${p}\\,3))`;
}

// ---- Public API: split-screen BEFORE / AFTER scrolling clip with middle badge ----

export async function buildClip({ beforePath, afterPath, mockupPath = null, title = "", outPath, workDir, duration = 8.0 }) {
  if (!existsSync(beforePath)) throw new Error(`before image not found: ${beforePath}`);
  if (!existsSync(afterPath)) throw new Error(`after image not found: ${afterPath}`);
  if (mockupPath && !existsSync(mockupPath)) throw new Error(`mockup image not found: ${mockupPath}`);
  if (!workDir) workDir = resolve(dirname(outPath), ".video-work");
  mkdirSync(workDir, { recursive: true });

  // Render label pills (white bg, dark text, big) + center badge (dark chip).
  const leftLabel = join(workDir, "label-left.png");
  const rightLabel = join(workDir, "label-right.png");
  const centerBadge = join(workDir, "badge-center.png");
  await renderHtmlToPng({ html: labelPillHtml({ eyebrow: "Original", main: "Claude Code" }), width: 720, height: 120, outPath: leftLabel });
  await renderHtmlToPng({ html: labelPillHtml({ eyebrow: "fal redesign", main: "Redesigned" }), width: 720, height: 120, outPath: rightLabel });
  await renderHtmlToPng({ html: centerBadgeHtml({ label: "gpt-image-2 reference" }), width: 360, height: 52, outPath: centerBadge });

  // Optional mockup thumbnail anchored to the seam, bottom-right panel. Track its final size
  // so we can position it + its label precisely in the filter graph.
  let mockupThumb = null;
  let thumbW = 0;
  let thumbH = 0;
  if (mockupPath) {
    mockupThumb = join(workDir, "mockup-thumb.png");
    const m = await sharp(mockupPath).metadata();
    const innerW = 220;
    const innerH = Math.min(320, Math.round((m.height / m.width) * innerW / 2) * 2);
    await sharp(mockupPath)
      .resize({ width: innerW, height: innerH, fit: "cover", position: "top" })
      .extend({ top: 6, bottom: 6, left: 6, right: 6, background: { r: 255, g: 255, b: 255, alpha: 1 } })
      .png()
      .toFile(mockupThumb);
    thumbW = innerW + 12;
    thumbH = innerH + 12;
  }

  // Prepare scaled half-canvas versions so both panels fit 960×1080 and can pan.
  //   - Each panel target is 960 wide.
  //   - We scale each source to width 960 and let the height follow its aspect.
  //   - The pan range is scaledHeight - 1080.
  const beforeScaledPath = join(workDir, "left-scaled.png");
  const afterScaledPath = join(workDir, "right-scaled.png");
  const [beforeH, afterH] = await Promise.all([
    scaleToWidth(beforePath, beforeScaledPath, 960),
    scaleToWidth(afterPath, afterScaledPath, 960),
  ]);
  const leftPan = Math.max(0, beforeH - 1080);
  const rightPan = Math.max(0, afterH - 1080);

  // ffmpeg: 5 inputs. 0=left-scaled, 1=right-scaled, 2=left-label, 3=right-label, 4=center-badge.
  //   - Crop each side to 960×1080, panning y from 0 → panRange over `duration` with ease-in-out.
  //   - hstack into one 1920×1080 frame.
  //   - Overlay left label top-left, right label top-right, center badge at bottom-center under the seam.
  const T = duration;
  const leftYExpr = easeYExpr(T, leftPan);
  const rightYExpr = easeYExpr(T, rightPan);

  // Inputs: 0=left-scaled, 1=right-scaled, 2=left-label, 3=right-label, 4=center-badge, 5=mockup-thumb (optional).
  const inputs = [
    "-loop", "1", "-t", String(T), "-i", beforeScaledPath,
    "-loop", "1", "-t", String(T), "-i", afterScaledPath,
    "-loop", "1", "-t", String(T), "-i", leftLabel,
    "-loop", "1", "-t", String(T), "-i", rightLabel,
    "-loop", "1", "-t", String(T), "-i", centerBadge,
  ];
  if (mockupThumb) {
    inputs.push("-loop", "1", "-t", String(T), "-i", mockupThumb);
  }

  const filter = [
    `[0:v]crop=960:1080:0:${leftYExpr}:exact=1,format=yuv420p,setsar=1[left]`,
    `[1:v]crop=960:1080:0:${rightYExpr}:exact=1,format=yuv420p,setsar=1[right]`,
    // A 2-px hairline between the panels.
    `[left][right]hstack=inputs=2,drawbox=x=959:y=0:w=2:h=1080:color=0xF2F0EA@0.12:t=fill[canvas]`,
    // Labels: both anchored at bottom-right of their respective panel.
    // Left panel spans x=0..960, so label sits at x = 960 - w - 48.
    `[canvas][2:v]overlay=x=960-w-48:y=H-h-48[withL]`,
    // Right panel spans x=960..1920, label sits at x = 1920 - w - 48 = W - w - 48.
    `[withL][3:v]overlay=x=W-w-48:y=H-h-48[withR]`,
  ];
  if (mockupThumb) {
    // Thumb anchored to the bottom, its LEFT edge sitting ~16px off the seam (x=960).
    const thumbX = 960 + 16;
    const thumbY = 1080 - thumbH - 24;
    const badgeY = thumbY - 52 - 8; // 52 = badge height, 8 = gap above the thumb
    filter.push(`[withR][5:v]overlay=x=${thumbX}:y=${thumbY}[withThumb]`);
    filter.push(`[withThumb][4:v]overlay=x=${thumbX}:y=${badgeY}[out]`);
  } else {
    filter.push(`[withR][4:v]overlay=x=(W-w)/2:y=H-h-40[out]`);
  }

  const args = [
    "-y",
    ...inputs,
    "-filter_complex", filter.join(";"),
    "-map", "[out]",
    "-r", "30",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",
    "-crf", "20",
    "-movflags", "+faststart",
    outPath,
  ];

  await runFfmpeg(args);
  return { outPath, duration: T };
}

// Scale to width, then extend with a white band on top so the site's header sits lower in frame
// and the first seconds of the clip show a clear "edge of the page" feel.
async function scaleToWidth(inPath, outPath, targetWidth, { topPad = 80 } = {}) {
  const m = await sharp(inPath).metadata();
  const scale = targetWidth / m.width;
  const inner = Math.round(m.height * scale / 2) * 2;
  const h = inner + topPad;
  await sharp(inPath)
    .resize({ width: targetWidth, height: inner, fit: "fill" })
    .extend({ top: topPad, bottom: 0, left: 0, right: 0, background: { r: 255, g: 255, b: 255, alpha: 1 } })
    .png()
    .toFile(outPath);
  return h;
}

// Convenience wrapper for run-all.sh / CLI usage.
export async function buildClipsFromDirs({ dirs, outDir, titleMap }) {
  mkdirSync(outDir, { recursive: true });
  const results = [];
  for (const d of dirs) {
    const before = join(d, "before.png");
    const after = join(d, "after.png");
    const title = (titleMap && titleMap[d]) || d.split("/").pop();
    const outPath = join(outDir, `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.mp4`);
    console.error(`[fal-redesign video] building ${title} → ${outPath}`);
    try {
      await buildClip({ beforePath: before, afterPath: after, title, outPath });
      results.push({ ok: true, title, outPath });
    } catch (e) {
      console.error(`   ✗ ${title}: ${e.message}`);
      results.push({ ok: false, title, error: e.message });
    }
  }
  return results;
}
