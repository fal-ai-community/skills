"""Checks the stills that check.mjs prints, so no frame ships with a fallback glyph or an off-centre label.

Glyphs: every character on screen must exist in the face it is set in (Chrome silently falls back to another font when one is
missing; display faces often lack ≈, U+202F, ‒, ± or the thin space).
Chips and tabs: the label's measured baseline must sit where the layout put it (±1.5 px), its caps must be centred on the box
(|dy| ≤ 2 px), and its ink must sit centred left/right (|dx| ≤ 2 px, side bearings included).

  node check.mjs S_map.html:18 S_flux.html:9.3,15.2 | python3 check.py [--css fonts.css] [--faces faces.json]

Faces (family + weight → font file) come from the pages' @font-face rules (--css, default ./fonts.css if it exists; file:// URLs
and paths relative to the css) and/or a JSON map {"Family|500": "/path/font.woff2"} (--faces). A face with no file is a problem.
Exit status 1 when anything is off. Needs fontTools (+ brotli for .woff2): pip install fonttools brotli.
"""
import json
import os
import re
import sys
import urllib.parse
from collections import Counter

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image


def faces_from_css(css):
    """[(family, lo, hi, path)] from @font-face rules; a variable font's weight range (font-weight: 100 900) counts as lo..hi"""
    out = []
    src = open(css, encoding='utf-8').read()
    for block in re.findall(r'@font-face\s*{([^}]*)}', src):
        fam = re.search(r'font-family\s*:\s*["\']?([^;"\']+)["\']?', block)
        url = re.search(r'src\s*:\s*url\(\s*["\']?([^)"\']+)["\']?\s*\)', block)
        wt = re.search(r'font-weight\s*:\s*(\d+|normal|bold)(?:\s+(\d+))?', block)
        if not (fam and url): continue
        u = urllib.parse.unquote(url.group(1))
        path = u[7:] if u.startswith('file://') else (u if os.path.isabs(u) else os.path.join(os.path.dirname(os.path.abspath(css)), u))
        lo = int({'normal': '400', 'bold': '700'}.get(wt.group(1), wt.group(1))) if wt else 400
        hi = int(wt.group(2)) if wt and wt.group(2) else lo
        out.append((fam.group(1).strip(), lo, hi, path))
    return out


def face_file(faces, family, weight):
    w = int(weight)
    hits = [f for f in faces if f[0] == family and f[1] <= w <= f[2]]
    return min(hits, key=lambda f: f[2] - f[1])[3] if hits else None


def parse_font(font):
    """'500 64px "Some Face"' → ('Some Face', '500'); a missing weight is 400"""
    fam = re.search(r'"([^"]+)"|\'([^\']+)\'', font)
    family = (fam.group(1) or fam.group(2)) if fam else font.split()[-1]
    first = font.split()[0]
    weight = {'normal': '400', 'bold': '700'}.get(first, first if first.isdigit() else '400')
    return family, weight


def main(argv):
    opt = {a.split('=')[0]: (a.split('=', 1)[1] if '=' in a else argv[i + 1] if i + 1 < len(argv) else '') for i, a in enumerate(argv) if a.startswith('--')}
    faces = []
    css = opt.get('--css') or ('fonts.css' if os.path.exists('fonts.css') else None)
    if css: faces += faces_from_css(css)
    if opt.get('--faces'):                    # {"Family|500": path} or {"Family|100-900": path}
        for k, v in json.load(open(opt['--faces'])).items():
            fam, w = k.split('|', 1); lo, _, hi = w.partition('-'); faces.append((fam, int(lo), int(hi or lo), v))
    cmaps, reported = {}, set()
    bad = seen = 0
    for ln in sys.stdin:
        if not ln.startswith('{'): continue
        d = json.loads(ln); seen += 1
        if d.get('error'): print(f"{d['page']}: {'PAGE FAILED: ' if 't' not in d else ''}{d['error']}"); bad += 1; continue
        for text, font in {(x['s'], x['font']) for x in d['strings']}:
            key = parse_font(font)
            if key not in cmaps:
                p = face_file(faces, *key)
                try: cmaps[key] = set(TTFont(p).getBestCmap()) if p and os.path.exists(p) else None
                except ImportError as e:                  # WOFF2 needs brotli: pip install fonttools brotli
                    print(f"{d['page']}: cannot read {p}: {e} (pip install brotli)"); bad += 1; cmaps[key] = set(); reported.add(key)
            cm = cmaps[key]
            if cm is None:
                if key not in reported: print(f"{d['page']}: no font file for {key}: pass --css or --faces"); bad += 1; reported.add(key)
                continue
            miss = sorted({c for c in text if ord(c) not in cm})
            if miss: print(f"{d['page']}: MISSING GLYPHS {miss} in {text!r} ({font})"); bad += 1
        im = np.asarray(Image.open(d['png']).convert('L')).astype(float)
        for b in d['boxes']:
            x0, y0, w, h = b['x'], b['y'], b['w'], b['h']
            # 4 px in from the sides (a rounded corner's outside pixels at a fractional position would read as ink), 3 px from top/bottom
            ix0, ix1, iy0, iy1 = int(round(x0 + 4)), int(round(x0 + w - 4)), int(round(y0 + 3)), int(round(y0 + h - 3))
            c = im[iy0:iy1, ix0:ix1]
            if c.size == 0: print(f"{d['page']} t={d['t']} {b['s']!r}: box off screen"); bad += 1; continue
            bg = np.median(c); ink = np.abs(c - bg) > 40
            ys, xs = np.nonzero(ink)
            if len(ys) == 0: print(f"{d['page']} t={d['t']} {b['s']!r}: no ink"); bad += 1; continue
            bottoms = [iy0 + np.nonzero(ink[:, j])[0].max() + 1 for j in range(ink.shape[1]) if ink[:, j].any()]
            base = Counter(bottoms).most_common(1)[0][0]                      # the row most glyphs stand on
            dbase = base - b['base']
            dy = (base - b['cap'] / 2) - (y0 + h / 2)
            l = ix0 + xs.min() - x0; r = x0 + w - (ix0 + xs.max() + 1); dx = (l - r) / 2
            ok = abs(dbase) <= 1.5 and abs(dy) <= 2 and abs(dx) <= 2
            print(f"{d['page']} t={d['t']:.2f} {b['s']!r} ({w:.0f}x{h:.0f}): baseline {dbase:+.1f}  caps dy {dy:+.1f}  dx {dx:+.1f}  {'OK' if ok else 'OFF'}")
            bad += 0 if ok else 1
    if not seen: print('NO STILLS: check.mjs printed nothing (wrong page:time arguments?)'); bad += 1
    print('ALL OK' if bad == 0 else f'{bad} PROBLEMS')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
