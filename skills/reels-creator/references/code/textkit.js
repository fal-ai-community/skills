"use strict";
// textkit: exact text and UI pieces for scene pages that are rendered frame by frame (window.seek(t)). It uses a motion
// core.js that defines the OneShape global when the page loads one, and otherwise its own copy of the six helpers it needs (identical code),
// so it also runs alone. It carries no palette, no fonts, no logo and no style: the page brings its own look.
// The kit only guarantees that what it draws is exact:
//  - text sits on its DOM-measured baseline, and widths leave out tracking's trailing space;
//  - chip and tab labels are centred on the cap height (check.py measures the ink: ±2 px);
//  - counters show one value per 60 fps frame (K.frameTime), so a paused or motion-blurred frame never ghosts two values;
//  - frame sequences decode before a seek resolves, so a render shows the exact frame;
//  - every visible string is registered with its font (window.__strings, for the glyph check), and every chip and tab with its
//    box and baseline (window.__pills, for the centring check).
//
//   const T = TextKit({ W: 1920, H: 1080, stroke: 3, radius: 8, tracking: -0.02 });
//   const F = { head: T.font(500, 64, "Some Display"), chip: T.font(400, 30, "Some Text") };
//   await T.K.assertFonts(Object.values(F));
//   const head = T.rline(L, [{ w: "Two", s: 0.4 }, { w: "words", s: 0.62 }], F.head, "#111", 120, 200);
//   ... await T.ready(); window.seek = (t) => { head(t); }; window.__ready = true;
//
// cfg: W, H (frame), stroke (px, every frame() and stroke bar), radius (px, default corner), tracking (em, default for
// non-mono text), isMono(font) (mono faces default to 0 tracking), curve ([x1, y1, x2, y2] arrival bezier; default the
// measured house curve 0.085, 0.648, 0, 1). All of it is a per-video choice.
// the six core.js helpers textkit uses, copied verbatim, for pages without core.js
function TextKitCore() {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const f2 = (v) => v.toFixed(2);
  const frameTime = (t, fps = 60) => Math.floor(t * fps + 1e-3) / fps;   // 1e-3 frame: times rounded to 5 decimals still land on their frame
  function bezEase(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = (u) => ((ax * u + bx) * u + cx) * u, Y = (u) => ((ay * u + by) * u + cy) * u, dX = (u) => (3 * ax * u + 2 * bx) * u + cx;
    return (p) => {
      p = clamp(p); let u = p;
      for (let i = 0; i < 8; i++) { const e = X(u) - p, d = dX(u); if (Math.abs(e) < 1e-7) return Y(u); if (Math.abs(d) < 1e-6) break; u = clamp(u - e / d); }
      let lo = 0, hi = 1; u = p;
      for (let i = 0; i < 40; i++) { const x = X(u); if (Math.abs(x - p) < 1e-7) break; if (x < p) lo = u; else hi = u; u = (lo + hi) / 2; }
      return Y(u);
    };
  }
  async function assertFonts(specs, sample = "Hamburgefonstiv 0123456789") {
    await Promise.all(specs.map((f) => document.fonts.load(f, sample).catch(() => [])));
    await document.fonts.ready;
    const c = document.createElement("canvas").getContext("2d");
    const wOf = (f) => { c.font = f; return c.measureText(sample).width; };
    const missing = specs.filter((f) => ["monospace", "serif"].every((fb) => Math.abs(wOf(`${f}, ${fb}`) - wOf(f.replace(/(\d+(?:\.\d+)?px)\s.*$/, `$1 ${fb}`))) < 0.01));
    if (missing.length) { window.__fontError = "missing fonts: " + missing.join(" | "); throw new Error(window.__fontError); }
  }
  const mctx = document.createElement("canvas").getContext("2d");
  const measure = (font, s) => { mctx.font = font; return mctx.measureText(s).width; };
  return { clamp, f2, frameTime, bezEase, assertFonts, measure };
}

function TextKit(cfg = {}) {
  const K = typeof OneShape === "function" ? OneShape(1000) : TextKitCore();   // clamp, f2, measure, bezEase, frameTime, assertFonts
  const W = cfg.W ?? 1920, H = cfg.H ?? 1080, SW = cfg.stroke ?? 3, RAD = cfg.radius ?? 8;
  const TRACK = cfg.tracking ?? -0.02, isMono = cfg.isMono ?? ((font) => /mono/i.test(font));
  const house = K.bezEase(...(cfg.curve ?? [0.085, 0.648, 0, 1]));
  const prog = (t, a, b) => K.clamp((t - a) / (b - a));
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html;
    (parent || document.body).appendChild(e); return e;
  };
  const px = (v) => `${K.f2(v)}px`;
  const font = (weight, size, family) => `${weight} ${size}px "${family}"`;

  const REG = (window.__textkit = window.__textkit || { STR: [], PILLS: [], LOADS: [] });   // shared by every kit on the page
  const { STR, PILLS, LOADS } = REG;
  const sizeOf = (f) => parseFloat(f.match(/(\d+(?:\.\d+)?)px/)[1]);
  const widthOf = (f, s, tr = 0) => K.measure(f, s) + tr * sizeOf(f) * Math.max(0, [...s].length - 1);
  const trOf = (f, o) => o.tracking ?? (isMono(f) ? 0 : TRACK);

  // font metrics, measured once per font: line box (1.3 em), the baseline's offset inside it (DOM), cap and x height (canvas)
  const FM = new Map();
  function fm(f) {
    if (FM.has(f)) return FM.get(f);
    const size = sizeOf(f), lh = Math.round(size * 1.3);
    const box = el("div", "", document.body);
    box.style.cssText = `position:absolute;left:-4000px;top:0;font:${f};line-height:${lh}px;white-space:nowrap`;
    box.innerHTML = 'Hxg<span style="display:inline-block;width:1px;height:0;vertical-align:baseline"></span>';
    const base = box.lastChild.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.remove();
    const c = document.createElement("canvas").getContext("2d"); c.font = f;
    const m = { size, lh, base, cap: c.measureText("H").actualBoundingBoxAscent, xh: c.measureText("x").actualBoundingBoxAscent,
                desc: c.measureText("gjpqy").actualBoundingBoxDescent };
    FM.set(f, m);
    return m;
  }

  // a static label whose baseline sits on y; x is its left, centre or right edge (o.align). Returns the element (+ ._w, ._left)
  function text(parent, s, f, color, x, y, o = {}) {
    const m = fm(f), tr = trOf(f, o), w = widthOf(f, s, tr);
    const left = o.align === "right" ? x - w : o.align === "center" ? x - w / 2 : x;
    const e = el("div", "", parent); e.textContent = s;
    e.style.cssText = `position:absolute;left:${px(left)};top:${px(y - m.base)};font:${f};color:${color};letter-spacing:${tr}em;` +
      `white-space:nowrap;line-height:${m.lh}px;${o.css || ""}`;
    e._w = w; e._left = left;
    STR.push({ s, font: f });
    return e;
  }

  // one word or label: opaque from its first frame, o.rise em (0.6) below its slot, landing on the arrival curve in o.dur s
  function word(parent, s, f, color, x, y, t0, o = {}) {
    const e = text(parent, s, f, color, x, y, o), size = sizeOf(f), rise = o.rise ?? 0.6, dur = o.dur ?? 0.7;
    const g = (t, alpha = 1) => {
      if (t < t0 || alpha <= 0.003) { e.style.opacity = "0"; return; }
      e.style.opacity = K.f2(alpha);
      e.style.transform = `translateY(${K.f2(rise * size * (1 - house(prog(t, t0, t0 + dur))))}px)`;
    };
    g.el = e; g.w = e._w; g.left = e._left;
    return g;
  }

  // words on one line, each on its own time: [{w, s, color?}] laid out from x (align left | center | right)
  function line(parent, words, f, color, x, y, o = {}) {
    const tr = trOf(f, o), gap = K.measure(f, " ");
    const ws = words.map((w) => widthOf(f, w.w, tr));
    const total = ws.reduce((a, b) => a + b, 0) + gap * (words.length - 1);
    let cx = o.align === "center" ? x - total / 2 : o.align === "right" ? x - total : x;
    const fs = words.map((w, i) => { const g = word(parent, w.w, f, w.color || color, cx, y, w.s, { ...o, tracking: tr, align: "left" }); cx += ws[i] + gap; return g; });
    const g = (t, alpha = 1) => fs.forEach((h) => h(t, alpha));
    g.w = total; g.fs = fs;
    return g;
  }

  // a whole label rising into place behind a mask on its baseline: every paused frame shows whole glyphs
  function reveal(parent, s, f, color, x, y, t0, o = {}) {
    const m = fm(f), tr = trOf(f, o), w = widthOf(f, s, tr), dur = o.dur ?? 0.75;
    const left = o.align === "right" ? x - w : o.align === "center" ? x - w / 2 : x;
    const top = y - m.base - 4, hgt = m.lh + 8;
    const mask = el("div", "", parent);
    mask.style.cssText = `position:absolute;left:${px(left - 24)};top:${px(top)};width:${px(w + 48)};height:${px(hgt)};overflow:hidden`;
    const e = el("div", "", mask); e.textContent = s;
    e.style.cssText = `position:absolute;left:24px;top:4px;font:${f};color:${color};letter-spacing:${tr}em;white-space:nowrap;line-height:${m.lh}px`;
    STR.push({ s, font: f });
    const g = (t, alpha = 1) => {
      if (t < t0 || alpha <= 0.003) { mask.style.opacity = "0"; return; }
      mask.style.opacity = K.f2(alpha);
      e.style.transform = `translateY(${K.f2(hgt * (1 - house(prog(t, t0, t0 + dur))))}px)`;
    };
    g.w = w; g.left = left; g.el = mask;
    return g;
  }

  // words on one line, each rising whole out of its own mask on its spoken time: [{w, s, color?}] (align left | center | right)
  function rline(parent, words, f, color, x, y, o = {}) {
    const tr = trOf(f, o), gap = K.measure(f, " ");
    const ws = words.map((w) => widthOf(f, w.w, tr));
    const total = ws.reduce((a, b) => a + b, 0) + gap * (words.length - 1);
    let cx = o.align === "center" ? x - total / 2 : o.align === "right" ? x - total : x;
    const fs = words.map((w, i) => { const g = reveal(parent, w.w, f, w.color || color, cx, y, w.s, { ...o, tracking: tr, align: "left", dur: o.dur ?? 0.55 }); cx += ws[i] + gap; return g; });
    const g = (t, alpha = 1) => fs.forEach((h) => h(t, alpha));
    g.w = total; g.fs = fs;
    return g;
  }

  // a chip: the label in a box that hugs it (padX, padY in em), its caps on the box's middle. P.at(t, t0) cuts it on at t0.
  // o: {x, y (top), align: left|center|right of x, bg, fg, padX = 0.26, padY = 0.34, h?, r = radius or [tl, tr, br, bl],
  //     icon: "check" | svg path data (24-unit box), iconColor, tracking}
  function chip(parent, s, f, o) {
    const m = fm(f), size = m.size, tr = trOf(f, { tracking: o.tracking ?? (isMono(f) ? 0 : -0.01) }), tw = widthOf(f, s, tr);
    const padX = Math.round((o.padX ?? 0.26) * size), padY = Math.round((o.padY ?? 0.34) * size);
    const icon = o.icon ? Math.round(m.cap * 1.25) : 0, ig = o.icon ? Math.round(m.cap * 0.5) : 0;
    const h = o.h ?? Math.round(m.cap + 2 * padY), w = Math.round(icon + ig + tw + 2 * padX);
    const left = Math.round(o.align === "right" ? o.x - w : o.align === "center" ? o.x - w / 2 : o.x);
    const r = Array.isArray(o.r) ? o.r : [o.r ?? RAD, o.r ?? RAD, o.r ?? RAD, o.r ?? RAD];
    const box = el("div", "", parent);
    box.style.cssText = `position:absolute;left:${left}px;top:${px(o.y)};width:${w}px;height:${h}px;background:${o.bg};border-radius:${r.map(px).join(" ")}`;
    const baseY = (h + m.cap) / 2;                                   // caps centred: cap top at (h − cap) / 2
    if (o.icon) {
      const sv = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      sv.setAttribute("width", icon); sv.setAttribute("height", icon); sv.setAttribute("viewBox", "0 0 24 24");
      sv.style.cssText = `position:absolute;left:${padX}px;top:${px(h / 2 - icon / 2)}`;
      const d = o.icon === "check" ? "M4 12.6l5 5L20 6.6" : o.icon;
      sv.innerHTML = `<path d="${d}" fill="none" stroke="${o.iconColor || o.fg}" stroke-width="2.6" stroke-linecap="square" stroke-linejoin="miter"/>`;
      box.appendChild(sv);
    }
    const lab = el("div", "", box); lab.textContent = s;
    lab.style.cssText = `position:absolute;left:${padX + icon + ig}px;top:${px(baseY - m.base)};font:${f};color:${o.fg};` +
      `letter-spacing:${tr}em;white-space:nowrap;line-height:${m.lh}px`;
    STR.push({ s, font: f });
    const P = { el: box, w, h, left, top: o.y, baseY, cap: m.cap, inkX: padX + icon + ig, tw, s, font: f };
    PILLS.push(P);
    P.at = (t, t0, alpha = 1) => { box.style.opacity = t < t0 || alpha <= 0.003 ? "0" : K.f2(alpha); };
    return P;
  }

  // an index tab: a square-cornered chip whose bottom edge sits on y (the top edge of the box it labels), left of x (or right
  // with align: "right"). In the same colour as that box's stroke, tab and stroke read as one piece.
  function tab(parent, s, f, o) {
    const m = fm(f), h = o.h ?? Math.round(m.cap * 2.4);
    return chip(parent, s, f, { ...o, y: o.y - h, h, r: o.r ?? 0, padX: o.padX ?? 0.6 });
  }

  // a rounded-rectangle path with per-corner radii [tl, tr, br, bl], starting at the top-left corner, clockwise
  function rr(x, y, w, h, r) {
    const [a, b, c, d] = r;
    return `M${x + a},${y}H${x + w - b}` + (b ? `A${b},${b} 0 0 1 ${x + w},${y + b}` : "") + `V${y + h - c}` +
      (c ? `A${c},${c} 0 0 1 ${x + w - c},${y + h}` : "") + `H${x + d}` + (d ? `A${d},${d} 0 0 1 ${x},${y + h - d}` : "") +
      `V${y + a}` + (a ? `A${a},${a} 0 0 1 ${x + a},${y}` : "") + "Z";
  }

  // a stroke box (cfg.stroke px, outer radius cfg.radius) whose corner is square where its tab sits (o.square: "tl" | "tr"); the
  // stroke draws on from the top-left corner, clockwise: f(p ∈ [0, 1], alpha). o: {x, y, w, h, color, square?, width?}
  function frame(parent, o) {
    const NS = "http://www.w3.org/2000/svg", sv = document.createElementNS(NS, "svg"), sw = o.width ?? SW;
    sv.setAttribute("width", o.w); sv.setAttribute("height", o.h);
    sv.style.cssText = `position:absolute;left:${px(o.x)};top:${px(o.y)};overflow:visible`;
    const ri = Math.max(0, (o.r ?? RAD) - sw / 2), cr = [o.square === "tl" ? 0 : ri, o.square === "tr" ? 0 : ri, ri, ri];
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", rr(sw / 2, sw / 2, o.w - sw, o.h - sw, cr));
    p.setAttribute("fill", "none"); p.setAttribute("stroke", o.color); p.setAttribute("stroke-width", sw);
    sv.appendChild(p); parent.appendChild(sv);
    const L = p.getTotalLength();
    p.setAttribute("stroke-dasharray", `${K.f2(L + 2)} ${K.f2(L + 2)}`);
    const g = (q, alpha = 1) => {
      sv.style.opacity = q <= 0 || alpha <= 0.003 ? "0" : K.f2(alpha);
      p.setAttribute("stroke-dashoffset", K.f2((L + 2) * (1 - K.clamp(q))));
    };
    g.el = sv;
    return g;
  }

  // a picture in a rounded rectangle (o.r: number or [tl, tr, br, bl]); o.pos: object-position. Decoded before ready() resolves.
  function media(parent, src, o) {
    const d = el("div", "", parent), r = Array.isArray(o.r) ? o.r : [o.r ?? RAD, o.r ?? RAD, o.r ?? RAD, o.r ?? RAD];
    d.style.cssText = `position:absolute;left:${px(o.x)};top:${px(o.y)};width:${px(o.w)};height:${px(o.h)};overflow:hidden;` +
      `border-radius:${r.map(px).join(" ")};background:${o.bg || "transparent"}`;
    const img = el("img", "", d); img.src = src;
    img.style.cssText = `position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:${o.pos || "50% 50%"};transform-origin:${o.origin || "50% 50%"}`;
    LOADS.push(img.decode().catch(() => { window.__fontError = "media failed: " + src; }));
    d.img = img;
    return d;
  }

  // a real clip played from its frames (dir/f001.jpg …: n frames at fps; o.name(k) overrides the file name) inside a rounded
  // rectangle. at(t, t0) shows the frame for t − t0 (the first before t0, the last after the clip ends) and resolves once that
  // frame is decoded: make seek async and await it, so the renderer captures the exact frame.
  function seq(parent, dir, n, fps, o) {
    const name = o.name ?? ((k) => `${dir}/f${String(k).padStart(3, "0")}.jpg`);
    const d = media(parent, name(1), o);
    let cur = 1;
    d.at = async (t, t0) => {
      const k = Math.min(n, Math.max(1, Math.floor((t - t0) * fps) + 1));
      if (k === cur) return;
      cur = k; d.img.src = name(k);
      try { await d.img.decode(); } catch (e) { window.__fontError = "frame failed: " + d.img.src; }
    };
    return d;
  }

  // a stopwatch: tabular figures in a DOM box whose right edge stays where the final value ends (x = the final value's left
  // edge, or its right edge with o.align "right"), so digits never shift while it counts. f(t, t0, t1, alpha): linear count,
  // one value per 60 fps frame
  function timer(parent, f, color, x, y, final, fmt, o = {}) {
    const m = fm(f), tr = trOf(f, o);
    const probe = el("span", "", document.body);
    probe.style.cssText = `position:absolute;left:-4000px;top:0;font:${f};letter-spacing:${tr}em;white-space:nowrap;font-variant-numeric:tabular-nums`;
    probe.textContent = fmt(final);
    const w = probe.getBoundingClientRect().width - tr * m.size;       // without the trailing tracking
    probe.remove();
    const right = o.align === "right" ? x : x + w, BOX = 900;
    const e = el("div", "", parent); e.textContent = fmt(final);
    e.style.cssText = `position:absolute;left:${px(right - BOX + tr * m.size)};width:${BOX}px;top:${px(y - m.base)};font:${f};color:${color};` +
      `letter-spacing:${tr}em;white-space:nowrap;line-height:${m.lh}px;font-variant-numeric:tabular-nums;text-align:right`;
    STR.push({ s: fmt(final), font: f }); STR.push({ s: "0123456789", font: f });
    const g = (t, t0, t1, alpha = 1) => {
      const tq = K.frameTime(t);                                       // one value per 60 fps frame: no ghosted digits
      if (tq < t0 || alpha <= 0.003) { e.style.opacity = "0"; return; }
      e.style.opacity = K.f2(alpha);
      e.textContent = fmt(tq >= t1 ? final : final * (tq - t0) / (t1 - t0));
    };
    g.el = e; g.w = w; g.right = right;
    return g;
  }

  // an SVG mark from path data (a logo the brand supplies, an icon): o = {paths: [d, …], viewBox: [w, h], x, y (top-left), h,
  // color, evenodd = true}. Returns {el, w, h}. Never draw a brand mark by hand: use its official paths.
  function mark(parent, o) {
    const NS = "http://www.w3.org/2000/svg", sv = document.createElementNS(NS, "svg");
    const [vw, vh] = o.viewBox, w = o.h * vw / vh;
    sv.setAttribute("viewBox", `0 0 ${vw} ${vh}`); sv.setAttribute("width", K.f2(w)); sv.setAttribute("height", o.h);
    sv.style.cssText = `position:absolute;left:${px(o.x)};top:${px(o.y)};overflow:visible`;
    sv.innerHTML = o.paths.map((d) => `<path ${o.evenodd === false ? "" : 'fill-rule="evenodd" '}d="${d}" fill="${o.color}"/>`).join("");
    parent.appendChild(sv);
    return { el: sv, w, h: o.h };
  }

  // a bar: filled, or a stroke box when o.stroke; corners o.r (default: half the height). f(x, y, w, h, alpha)
  function bar(parent, color, o = {}) {
    const e = el("div", "", parent);
    e.style.cssText = `position:absolute;left:0;top:0;` + (o.stroke ? `box-shadow:inset 0 0 0 ${o.width ?? SW}px ${color}` : `background:${color}`);
    const g = (x, y, w, h, alpha = 1) => {
      Object.assign(e.style, { left: px(x), top: px(y), width: px(Math.max(0, w)), height: px(Math.max(0, h)),
        borderRadius: px(o.r ?? Math.min(w, h) / 2), opacity: K.f2(w < 0.5 || h < 0.5 ? 0 : alpha) });
    };
    g.el = e;
    return g;
  }

  // a plain layer (a div at the origin) for grouping and moving things together, and a solid colour field
  const layer = (parent) => { const g = el("div", "", parent); g.style.cssText = "position:absolute;left:0;top:0;width:0;height:0"; return g; };
  function field(parent, color, o) {
    const e = el("div", "", parent);
    e.style.cssText = `position:absolute;left:${px(o.x)};top:${px(o.y)};width:${px(o.w)};height:${px(o.h)};background:${color}`;
    return e;
  }

  // a circle reveal of a ground from (cx, cy): el.style.clipPath for progress p (0 = closed, 1 = covers the whole frame)
  const circle = (p, cx = W / 2, cy = H / 2) => {
    const R = Math.hypot(Math.max(cx, W - cx), Math.max(cy, H - cy)) + 2;
    return `circle(${K.f2(K.clamp(p) * R)}px at ${K.f2(cx)}px ${K.f2(cy)}px)`;
  };

  const rise = (t, t0, d = 90, dur = 0.8) => d * (1 - house(prog(t, t0, t0 + dur)));
  const ready = async () => { await Promise.all(LOADS); };

  window.__strings = () => STR;
  window.__pills = () => PILLS.filter((P) => P.el.style.opacity !== "0" && getComputedStyle(P.el).visibility !== "hidden").map((P) => {
    const r = P.el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height, base: r.top + P.baseY, cap: P.cap, inkX: r.left + P.inkX, tw: P.tw, s: P.s };
  });
  return { W, H, SW, RAD, K, house, prog, el, px, font, sizeOf, widthOf, fm, text, word, line, reveal, rline, chip, tab, rr, frame,
           media, seq, timer, mark, bar, layer, field, circle, rise, ready };
}
