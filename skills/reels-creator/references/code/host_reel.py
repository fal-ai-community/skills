"""Host-led video, 16:9 or 9:16: the host's on-camera lines (talking clips rendered from the line's own voice take: H3 Max Lip
Sync, image + take) between b-roll clips and rendered animation scenes, ending on a silent end card; the presenter's voice
throughout, word-by-word captions, the clips' own sound ducked under the voice, an optional music bed and one-shot SFX,
−14 LUFS. H.264/AAC, BT.709, 24 fps (the native rate of H3 Max, Seedance and FLUX clips: a 30 fps cut repeats every 5th frame).

  python3 host_reel.py <edit.json> <out_basename> [--plan]   → <out>.mp4, <out>_plan.json (--plan: the plan only, no render)
  python3 host_reel.py --join <out_basename> <part_basename> …   → <out>.mp4 from parts rendered separately (below)

A host segment's picture is never retimed: "sync": "clip" (the default) plays the clip 1:1 from its own frames
and puts the take back on at "take_at", the second inside the clip where the take's 0 s sits (H3 Max Lip Sync was given the
take padded with silence, so its lips already follow the take). A face sped up or slowed down to fit a voice reads as broken
video. The older modes stay for clips that re-voice the line in their own tempo (Seedance, Kling): "video" retimes the picture
onto the take, and "audio" slides take pieces onto the clip's word times, which can split connected speech. Every voice
cut, b-roll ones too, is set from the take's sound, in its silence: Scribe marks word starts 0.01–0.11 s after the sound begins,
so cuts made from its times would clip first consonants. The plan ends with a cut check that lists any cut inside a word or inside
connected speech.

edit.json:
  {"fps": 24, "w": 1080, "h": 1920, "font": "…/SomeFace.ttf",
   "lines": {"A1": {"take": "vo/A1_s303.mp3", "scribe": "vo/A1_s303.scribe.json", "text": "…"}, …},
   "segments": [
     {"kind": "host", "line": "A1", "clip": "out/HOST_A1.mp4", "take_at": 0.21, "lead": 0.12, "tail": 0.25, "push": 0.03},
     {"kind": "broll", "clip": "out/B_cat.mp4", "in": 1.2, "min": 2.6, "line": "V1", "words": [0, 4]},
     {"kind": "broll", "clip": "out/S_map.mp4", "in": 0, "line": "V2", "words": [0, 50], "captions": false}, …,
     {"kind": "card", "clip": "out/S_end.mp4", "dur": 3.5, "music_db": -14}],
   "ambience_db": -12, "duck_db": -22,
   "music": {"file": "audio/bed.mp3", "from": 0, "db": -20, "duck_db": -25, "fade_in": 0.4, "fade_out": 1.0},
   "sfx": [{"file": "sfx/tick.wav", "seg": 3, "at": 1.25, "db": -16, "duck": false}, …]}
  A host segment ("sync": "clip", the default): the clip plays 1:1 from "lead" s before the take's first sound to "tail" s after its
  last, "take_at" being where the take's 0 s sits in the clip (host_lipsync.py measure: the clip's audio against the take), "push"
  a slow zoom-in (0.03 = 3 %). The clip's own audio is never mixed (it is the take again, resampled). "sync": "video" (warp the
  picture onto the take, never slower than 0.8×; "squeeze" q cuts q × the extra pause the clip adds at the take's own pauses of
  ≥ 0.25 s) and "sync": "audio" (take pieces slid onto the clip's word times) need "clip_scribe" and are only for clips that
  re-voiced the line; both change the host's timing, so never use them without asking the user.
  A b-roll segment speaks words [a, b) of its line, its first word 0.16 s after its cut; it lasts span + 0.44 s, or at least
  "min" seconds. An animation scene is a b-roll segment whose clip is the rendered scene, timed by wordtimes.py to the same
  rule, with "captions": false (the scene carries its own words, and no caption tail spills onto it).
  A card segment has no line: it plays its clip from "in" (default 0) for "dur" seconds with no voice, no captions and none of
  the clip's own sound, while the music carries on; "music_db" lifts the bed to that level over the card's first 0.5 s. The end
  card after the last line is one, so a video never ends on its last word.
  Caption keys (defaults follow the frame: 9:16 → y 1320, size 92, 3 words / 16 chars a phrase; 16:9 → y 0.875 h, size 0.05 h,
  5 / 30): "caption_y", "caption_size", "caption_weight" (a named instance of a variable font, "ExtraBold"), "caption_pill" and
  "caption_active_text" (RGB of the spoken word's pill and its letters), "caption_words" / "caption_chars".
  "x264_preset": the encoder preset (default "slow"; "veryfast" renders several times faster, e.g. in a sandbox with a
  per-command time limit, at a slightly larger file).
  Parts: a long video renders as parts, its edit split at segment boundaries, each part planned and rendered on its own, then
  joined by --join: the pictures are copied, and the sound is each part's raw mix (<part>_mix_raw.wav) joined sample-exact,
  normalised once and encoded once. The parts' AAC tracks joined directly put the voice 21–50 ms late after a few joins (each
  part's encoder priming adds up). The music's "fade_out" goes on the last part only and "fade_in" on the first only (the plan
  warns otherwise: either one dips the bed at a join).
  Every "in" snaps to the frame grid: an in-point between two frames made the segment start on a repeated frame.
  "caption_func_words": words a caption phrase should not end on (default: English "of", "the", "and"…); a video in another
  language passes that language's own function words.
  "sfx": one-shot sounds at "at" seconds on the output timeline, or "at" seconds after segment "seg" starts (index in segments);
  "from"/"dur" trim the file, "db" its level (−18), "duck": true lowers it under the voice like the clips' own sound.
"""
import difflib
import functools
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SR = 48000
PRE, POST = 0.04, 0.06            # audio kept before a chunk's first word and after its last
QUIET = -40.0                     # dB under a take's speech level: a real pause. Sentence and comma pauses measured −41…−69,
                                  # the dips inside connected speech −5…−39


def jl(p): return json.load(open(p))


def words_of(scribe):
    return [(w['text'], float(w['start']), float(w['end'])) for w in jl(scribe)['words'] if w.get('type') == 'word']


def load_audio(p, t0=None, dur=None, ch=1, tempo=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', p]
    if tempo:                                                 # cut first (sample-accurate atrim), then change speed, keep pitch
        cmd += ['-af', f'atrim=start={max(0.0, t0 or 0):.4f}' + (f':duration={dur:.4f}' if dur is not None else '') + f',asetpts=PTS-STARTPTS,atempo={tempo:.4f}']
    else:                                                     # output-side seek: sample-accurate on short files
        if t0 is not None: cmd += ['-ss', f'{max(0.0, t0):.4f}']
        if dur is not None: cmd += ['-t', f'{dur:.4f}']
    cmd += ['-vn', '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
    return a.reshape(-1, ch) if ch > 1 else a


def fade(a, ms=8):
    n = min(len(a) // 2, int(SR * ms / 1000))
    if n > 0:
        r = np.linspace(0, 1, n, dtype=np.float32)
        a[:n] *= r; a[-n:] *= r[::-1]
    return a


def movavg(x, k):
    c = np.cumsum(np.concatenate([[0.0], x.astype(np.float64)]))
    h = k // 2
    i0 = np.clip(np.arange(len(x)) - h, 0, len(x)); i1 = np.clip(np.arange(len(x)) + h + 1, 0, len(x))
    return ((c[i1] - c[i0]) / np.maximum(1, i1 - i0)).astype(np.float32)


def chunks_by_gap(ws, gap=0.12):
    out, cur = [], [0]
    for i in range(1, len(ws)):
        if ws[i][1] - ws[i - 1][2] > gap: out.append(cur); cur = [i]
        else: cur.append(i)
    out.append(cur)
    return out


@functools.lru_cache(None)
def envelope(path):
    """a take's 10 ms frames in dB under its speech level (95th percentile)"""
    a, k = load_audio(path), int(0.01 * SR)
    fr = 20 * np.log10(np.sqrt(np.mean(a[:len(a) // k * k].reshape(-1, k) ** 2, axis=1)) + 1e-9)
    return fr - np.percentile(fr, 95)


def gap_cut(env, end, start):
    """the quietest 10 ms point between a word that ends at `end` and the next one, which starts at `start`: (time, dB).
    Scribe puts word starts 0.01–0.11 s after the sound begins (median 0.05 s), so the search stops 0.06 s short
    of `start`, before the next word's onset and its stop closures ("a|bout")."""
    i0, i1 = max(0, int((end - 0.03) / 0.01)), min(len(env), int((start - 0.06) / 0.01) + 1)
    if i1 <= i0: return (end + start) / 2, 0.0
    j = i0 + int(np.argmin(env[i0:i1]))
    return (j + 0.5) * 0.01, float(env[j])


def edge_cut(env, t, side, lim):
    """where a piece starts before a word that begins at t (side -1) or ends after one that ends at t (side +1), never past lim
    (the neighbouring word or the take's edge): at the edge of the silence next to the word (≥ 0.12 s before it, ≥ 0.08 s
    after), so a stop closure inside a word is never taken for it. With no silence there, the quietest point."""
    q = env <= QUIET
    if side < 0:
        i0, i1 = max(0, int(max(lim, t - 0.3) / 0.01)), min(len(env), int(t / 0.01) + 1)
        f = i1 - 1
        while f >= i0:
            if not q[f]: f -= 1; continue
            g = f
            while g > i0 and q[g - 1] and f - g < 11: g -= 1
            if f - g >= 11 or g == i0: return (f + 0.2) * 0.01
            f = g - 1
    else:
        i0, i1 = max(0, int((t - 0.03) / 0.01)), min(len(env), int(min(lim, t + 0.4) / 0.01) + 1)
        f = i0
        while f < i1:
            if not q[f]: f += 1; continue
            g = f
            while g + 1 < i1 and q[g + 1] and g - f < 7: g += 1
            if g - f >= 7 or g + 1 == i1: return (f + 0.8) * 0.01
            f = g + 1
    if i1 <= i0: return t
    j = i0 + int(np.argmin(env[i0:i1]))
    return (j + 0.5) * 0.01


def chunks_by_pause(tw, env):
    """the take's phrases, split only where the take really pauses (≤ QUIET between two words), with the cut times. A gap in
    Scribe's times is not a pause: "guy | never" had 0.16 s between the words and no silence at all."""
    out, cur, cuts = [], [0], []
    for i in range(1, len(tw)):
        c, db = gap_cut(env, tw[i - 1][2], tw[i][1])
        if db <= QUIET: out.append(cur); cur = [i]; cuts.append(c)
        else: cur.append(i)
    out.append(cur)
    return out, cuts


def pairs(tts, clip):
    """take word index → clip word index, for the words both transcripts share (in order)"""
    norm = lambda w: w.lower().replace('\u2019', "'").strip('.,;:?!"')
    pair = {}
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(w[0]) for w in tts], [norm(w[0]) for w in clip], autojunk=False).get_opcodes():
        if op == 'equal': pair.update({i1 + k: j1 + k for k in range(i2 - i1)})
    return pair


def tidy(kn, rmin=0.8):
    """drop inner knots until the clip never plays slower than rmin × real time and both times only go forward"""
    kn = sorted(kn)
    while len(kn) > 2:
        r = [(kn[i + 1][0] - kn[i][0]) / max(1e-6, kn[i + 1][1] - kn[i][1]) if kn[i + 1][1] > kn[i][1] else -1 for i in range(len(kn) - 1)]
        bad = [i for i, x in enumerate(r) if x < rmin]
        if not bad: break
        i = min(bad, key=lambda i: r[i])
        kn.pop(i + 1 if i + 1 < len(kn) - 1 else i)
    return kn


def video_sync(tw, cw, lead, tail, q, env):
    """the take plays whole, cut only where it really pauses (chunks_by_pause), and the clip is retimed onto it: each shared
    word's start and end in the clip are knots (clip time, output time), so a word plays near 1:1 and a pause the model added
    inside a phrase is skipped like a jump cut. Where the take pauses ≥ 0.25 s the silence follows the clip's pause less q × what
    the clip adds, never shorter than the take's own; at any shorter pause the take runs on seamlessly across the cut.
    Returns (chunks, output start of every take word, chunk end times, knots, cut times in the take)."""
    pair = pairs(tw, cw)
    if len(pair) < 0.8 * len(tw):
        raise SystemExit(f"words don't match: take {len(tw)}, clip {len(cw)}, shared {len(pair)}")
    (chs, cuts), o, ends = chunks_by_pause(tw, env), {}, []
    for k, ch in enumerate(chs):
        cur = lead
        if k:
            a, b = chs[k - 1][-1], ch[0]
            tg = tw[b][1] - tw[a][2]
            g = tg
            if a in pair and b in pair and tg >= 0.25:     # only a clear pause of the take's own grows toward the clip's; at a
                cg = cw[pair[b]][1] - cw[pair[a]][2]       # shorter one the pieces abut, so a doubtful split stays seamless
                g = max(tg, cg - q * max(0.0, cg - tg))
            cur = ends[-1] + g
        s0 = tw[ch[0]][1]
        for i in ch: o[i] = cur + tw[i][1] - s0
        ends.append(cur + tw[ch[-1]][2] - s0)
    i0, iL = min(pair), max(pair)
    c_in = max(0.0, cw[pair[i0]][1] - o[i0])
    kn = [(cw[pair[i]][1], o[i]) for i in sorted(pair)] + [(cw[pair[i]][2], o[i] + tw[i][2] - tw[i][1]) for i in sorted(pair)]
    last_end = cw[pair[iL]][2] + (ends[-1] - (o[iL] + tw[iL][2] - tw[iL][1]))
    kn = tidy([(c_in, 0.0)] + [x for x in kn if x[0] > c_in] + [(last_end + tail, ends[-1] + tail)])
    return chs, o, ends, kn, cuts


def align(tts, clip, max_err=0.08, max_stretch=0.15):
    """split the take into pause-separated chunks and map each onto the clip: a plain shift (median of clip word start − take
    word start) when that fits, else a shift plus a small speed change (least squares, ≤ max_stretch); split again if neither
    fits. Only words both transcripts share count (Scribe may write "2019" in one and "twenty nineteen" in the other).
    Returns (chunk, off, err, scale): clip time = s0 + off + scale·(take time − s0), with s0 the chunk's first take word."""
    norm = lambda w: w.lower().replace('\u2019', "'").strip('.,;:?!"')
    pair = {}
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(w[0]) for w in tts], [norm(w[0]) for w in clip], autojunk=False).get_opcodes():
        if op == 'equal': pair.update({i1 + k: j1 + k for k in range(i2 - i1)})
    if len(pair) < 0.8 * len(tts):
        raise SystemExit(f"words don't match: take {len(tts)}, clip {len(clip)}, shared {len(pair)}")
    todo, done = chunks_by_gap(tts), []
    while todo:
        ch = todo.pop(0)
        s0 = tts[ch[0]][1]
        x = np.array([tts[i][1] - s0 for i in ch if i in pair]); y = np.array([clip[pair[i]][1] - s0 for i in ch if i in pair])
        if not len(x): done.append((ch, None, 0.0, 1.0)); continue
        off = float(np.median(y - x)); sc = 1.0; err = float(np.max(np.abs(y - x - off)))
        if err > max_err and len(x) > 2 and x.max() - x.min() >= 0.4:
            k, c = np.polyfit(x, y, 1)
            if abs(k - 1) <= max_stretch:
                e2 = float(np.max(np.abs(y - (c + k * x))))
                if e2 < err: off, sc, err = float(c), float(k), e2
        cuts = [j for j in range(1, len(ch)) if any(i in pair for i in ch[:j]) and any(i in pair for i in ch[j:])]
        if err > max_err and cuts:                 # split where the clip adds (or drops) the most time between two words, and try again
            def jump(j):
                l = max(i for i in ch[:j] if i in pair); r = min(i for i in ch[j:] if i in pair)
                return abs((clip[pair[r]][1] - clip[pair[l]][1]) - (tts[r][1] - tts[l][1])), tts[ch[j]][1] - tts[ch[j - 1]][2]
            j = max(cuts, key=jump)
            todo[:0] = [ch[:j], ch[j:]]
            continue
        done.append((ch, off, err, sc))
    done.sort(key=lambda c: c[0][0])
    for n, (ch, off, err, sc) in enumerate(done):  # a chunk with no shared word takes the nearest chunk's mapping
        if off is None:
            near = min((d for d in done if d[1] is not None), key=lambda d: abs(tts[d[0][0]][1] - tts[ch[0]][1]))
            ns0 = tts[near[0][0]][1]; s0 = tts[ch[0]][1]
            done[n] = (ch, near[1] + (near[3] - 1) * (s0 - ns0), err, near[3])
    return done


def display_words(text, tw):
    """the script's own words (so "2019" and "84%" on screen even when the voice and Scribe spell them out), with a clause-end flag;
    a script word spoken as several words sits on the first of them and the rest get '' (merged into it at the end of plan)"""
    ws = text.split()
    if len(ws) == len(tw): return [(w.strip('.,;:'), w[-1] in '.,;:?!') for w in ws]
    norm = lambda w: w.lower().replace('\u2019', "'").strip('.,;:?!"')
    out, lead = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(w) for w in ws], [norm(w[0]) for w in tw], autojunk=False).get_opcodes():
        src = ws[i1:i2]
        if j1 == j2:                       # script words nobody heard: glue them onto the last shown word
            k = max((k for k, d in enumerate(out) if d[0]), default=None)
            if k is None: lead += src
            else: out[k] = ((out[k][0] + ' ' + ' '.join(src)).strip('.,;:'), src[-1][-1] in '.,;:?!')
        elif op == 'equal':
            shown = [(w.strip('.,;:'), w[-1] in '.,;:?!') for w in src]
            if lead: shown[0] = (' '.join(lead + src[:1]).strip('.,;:'), src[0][-1] in '.,;:?!'); lead = []
            out += shown
        else:                              # replace / insert: the script's words on the first heard word, '' on the rest
            sh = lead + src; lead = []
            out.append((' '.join(sh).strip('.,;:'), sh[-1][-1] in '.,;:?!') if sh else ('', False))
            out += [('', False)] * (j2 - j1 - 1)
    return out


def plan(E):
    fps = E.get('fps', 24)
    grid = lambda x: round(x * fps) / fps   # in-points on the frame grid: one between two frames repeats the segment's first frame
    t, segs, vo, caps = 0.0, [], [], []
    for s in E['segments']:
        n0 = len(caps)
        if s['kind'] == 'card':            # no line: the clip plays for "dur" s under the music alone, never captioned
            n = round(s['dur'] * fps)
            segs.append({'kind': 'card', 'clip': s['clip'], 'in': grid(s.get('in', 0.0)), 'n': n, 'start': t, 'captions': False,
                         **({'music_db': s['music_db']} if 'music_db' in s else {})})
            t += n / fps
            continue
        L = E['lines'][s['line']]
        tw = words_of(L['scribe'])
        disp = display_words(L['text'], tw)
        sync = s.get('sync', 'clip') if s['kind'] == 'host' else None
        if sync == 'clip':                 # rendered from this take: 1:1 picture, the take back on at "take_at", nothing retimed
            if 'take_at' not in s:
                raise SystemExit(f"host {s['line']}: no \"take_at\" (host_lipsync.py measure <take> <clip>). A clip that re-voiced "
                                 "the line (Seedance, Kling) is not lip-synced to the take: make an H3 Max Lip Sync clip instead")
            ta, lead, tail = s['take_at'], s.get('lead', 0.12), s.get('tail', 0.25)
            env = envelope(L['take'])
            f0 = edge_cut(env, tw[0][1], -1, 0.0)
            f1 = edge_cut(env, tw[-1][2], 1, len(env) * 0.01)
            c_in = grid(max(0.0, ta + f0 - lead))        # H3 clips are 24 fps like the master: c_in lands on a frame of the clip
            n = round((ta + f1 + tail - c_in) * fps); dur = n / fps
            vo.append({'file': L['take'], 'from': round(f0, 3), 'to': round(f1, 3), 'at': round(t + ta + f0 - c_in, 4), 'err': 0.0})
            for i in range(len(tw)):
                caps.append((disp[i][0], t + ta + tw[i][1] - c_in, t + ta + tw[i][2] - c_in, disp[i][1] or i == len(tw) - 1))
            segs.append({'kind': 'host', 'clip': s['clip'], 'in': round(c_in, 4), 'n': n, 'start': t, 'push': s.get('push', 0.0), 'line': s['line']})
        elif sync == 'video':
            cw = words_of(s['clip_scribe'])
            lead, tail = s.get('lead', 0.12), s.get('tail', 0.25)
            env = envelope(L['take'])
            chs, o, ends, kn, cuts = video_sync(tw, cw, lead, tail, s.get('squeeze', 0.5), env)
            for k, ch in enumerate(chs):                   # one piece per phrase; neighbours share their cut, in the take's silence
                a0 = cuts[k - 1] if k else edge_cut(env, tw[ch[0]][1], -1, 0.0)
                a1 = cuts[k] if k + 1 < len(chs) else edge_cut(env, tw[ch[-1]][2], 1, len(env) * 0.01)
                at = t + o[ch[0]] - (tw[ch[0]][1] - a0)
                if at < 0: a0, at = a0 - at, 0.0
                vo.append({'file': L['take'], 'from': round(a0, 3), 'to': round(a1, 3), 'at': round(at, 4), 'err': 0.0})
                for i in ch:
                    caps.append((disp[i][0], t + o[i], t + o[i] + tw[i][2] - tw[i][1], disp[i][1] or i == len(tw) - 1))
            n = round((ends[-1] + tail) * fps); dur = n / fps
            sp = [(b[0] - a[0]) / (b[1] - a[1]) for a, b in zip(kn, kn[1:])]
            segs.append({'kind': 'host', 'clip': s['clip'], 'in': kn[0][0], 'n': n, 'start': t, 'push': s.get('push', 0.0), 'line': s['line'],
                         'warp': [[round(a, 4), round(b, 4)] for a, b in kn], 'speed': [round(min(sp), 2), round(max(sp), 2)]})
        elif sync == 'audio':
            cw = words_of(s['clip_scribe'])
            c_in = max(0.0, cw[0][1] - s.get('lead', 0.12))
            c_out = cw[-1][2] + s.get('tail', 0.25)
            pieces = []
            for ch, off, err, sc in align(tw, cw):
                s0 = tw[ch[0]][1]
                m = lambda x, s0=s0, off=off, sc=sc: s0 + off + sc * (x - s0)      # take time → clip time
                a0 = tw[ch[0]][1] - PRE
                nxt = tw[ch[-1] + 1][1] if ch[-1] + 1 < len(tw) else None
                a1 = min(tw[ch[-1]][2] + POST, nxt - 0.03) if nxt else tw[ch[-1]][2] + POST
                pieces.append((ch, m, a0, a1, err, sc))
            # "squeeze" q: Seedance often leaves longer pauses between phrases than the take (it fills a generous clip length);
            # the extra pause (clip gap − take gap) between two pieces is cut by the fraction q in the output, the clip playing
            # faster through that pause only. Speech plays 1:1, so lips stay on the voice. knots: (clip time, output time).
            q, knots, cut = s.get('squeeze', 0.0), [(c_in, 0.0)], 0.0
            for (_, m0, _, e0, _, _), (_, m1, b1, _, _, _) in zip(pieces, pieces[1:]):
                ce, cs = m0(e0), m1(b1)                    # previous piece's end, next piece's start (clip time)
                extra = (cs - ce) - max(0.0, b1 - e0)      # pause the clip adds beyond the take's own
                if q > 0 and extra > 0.04:
                    knots += [(ce, ce - c_in - cut), (cs, cs - c_in - cut - q * extra)]
                    cut += q * extra
            knots.append((c_out, c_out - c_in - cut))
            ck, ok = [k[0] for k in knots], [k[1] for k in knots]
            w = lambda c: float(np.interp(c, ck, ok))     # clip time → output time (segment-relative)
            n = round((c_out - c_in - cut) * fps); dur = n / fps
            for ch, m, a0, a1, err, sc in pieces:
                vo.append({'file': L['take'], 'from': a0, 'to': a1, 'at': t + w(m(a0)), 'err': round(err, 3), **({'tempo': round(1 / sc, 4)} if sc != 1 else {})})
                for i in ch:
                    caps.append((disp[i][0], t + w(m(tw[i][1])), t + w(m(tw[i][2])), disp[i][1] or i == len(tw) - 1))
            segs.append({'kind': 'host', 'clip': s['clip'], 'in': c_in, 'n': n, 'start': t, 'push': s.get('push', 0.0), 'line': s['line'],
                         **({'warp': [[round(a, 4), round(b, 4)] for a, b in knots]} if cut > 0 else {})})
        else:
            a, b = s['words']
            a0 = tw[a][1] - PRE
            a1 = min(tw[b - 1][2] + POST, tw[b][1] - 0.03) if b < len(tw) else tw[b - 1][2] + POST
            dly = s.get('delay', 0.12)
            n = round(max(s.get('min', 0), dly + (a1 - a0) + 0.22) * fps); dur = n / fps
            env = envelope(L['take'])                      # the audio itself is cut in the take's silence, the first word lands as before
            f0 = edge_cut(env, tw[a][1], -1, tw[a - 1][2] if a else 0.0)
            f1 = edge_cut(env, tw[b - 1][2], 1, tw[b][1] if b < len(tw) else len(env) * 0.01)
            at = t + dly - (a0 - f0)
            if at < 0: f0, at = f0 - at, 0.0
            vo.append({'file': L['take'], 'from': round(f0, 3), 'to': round(f1, 3), 'at': round(at, 4), 'err': 0})
            for i in range(a, b) if s.get('captions', True) else ():    # "captions": false when the clip carries the words itself
                caps.append((disp[i][0], t + dly + tw[i][1] - a0, t + dly + tw[i][2] - a0, disp[i][1] or i == b - 1))
            segs.append({'kind': 'broll', 'clip': s['clip'], 'in': grid(s['in']), 'n': n, 'start': t, 'line': s['line'], 'words': [a, b],
                         **({'captions': False} if not s.get('captions', True) else {})})
        seg_caps, caps[n0:] = caps[n0:], []
        for c in seg_caps:                 # a '' word belongs to the shown word before it in this segment ("twenty nineteen" → one "2019")
            if c[0]: caps.append(c)
            elif len(caps) > n0: p = caps[-1]; caps[-1] = (p[0], p[1], c[2], p[3] or c[3])
        t += dur
    return segs, vo, caps, t


def cut_check(E, vo, loud=-30.0, slack=0.06):
    """every voice cut must fall where its take is quiet. Flags a piece that starts or ends while the take still sounds (louder
    than `loud` dB under its speech level), and a split between two words with no real pause between them that the video opens
    or closes by more than `slack` s: such a split clips the first sound of the next word and sounds like a stutter."""
    scribe, by, out = {L['take']: L['scribe'] for L in E['lines'].values()}, {}, []
    for v in vo: by.setdefault(v['file'], []).append(v)
    for f, ps in by.items():
        env, tw, ps = envelope(f), words_of(scribe[f]), sorted(ps, key=lambda v: v['from'])
        for v in ps:
            for t, side in ((v['from'], 'starts'), (v['to'], 'ends')):
                db = env[min(len(env) - 1, max(0, int(t / 0.01)))]
                if db > loud:
                    w = min(tw, key=lambda w: abs((w[1] + w[2]) / 2 - t))
                    out.append(f"{f} {side} at {t:.2f} s while the take still sounds ({db:.0f} dB), near '{w[0]}'")
        for p, q in zip(ps, ps[1:]):
            ia = max((i for i, w in enumerate(tw) if w[1] < p['to']), default=None)      # last word begun in p
            ib = min((i for i, w in enumerate(tw) if w[2] > q['from']), default=None)    # first word still sounding in q
            if ia is None or ib is None or ib > ia + 1: continue
            if ib <= ia:
                out.append(f"{f} cuts inside '{tw[ib][0]}' at {q['from']:.2f} s")
                continue
            tg = tw[ib][1] - tw[ia][2]
            og = q['at'] + (tw[ib][1] - q['from']) / q.get('tempo', 1) - p['at'] - (tw[ia][2] - p['from']) / p.get('tempo', 1)
            if gap_cut(env, tw[ia][2], tw[ib][1])[1] > QUIET and abs(og - tg) > slack:
                out.append(f"{f} split inside connected speech: '{tw[ia][0]} | {tw[ib][0]}', {tg:.2f} s apart in the take, {og:.2f} s in the video")
    return out

FUNC = {'of', 'a', 'an', 'the', 'to', 'as', 'and', 'or', 'in', 'on', 'at', 'for', 'with', 'is', 'be', 'so'}


def phrases(caps, max_words=3, max_chars=16, gap=0.3, func=FUNC):
    """clauses (script punctuation, or a pause that doesn't follow "and", "the"…), each cut into groups of ≤ max_words words
    (one more if the group stays ≤ max_chars) and ≤ max_chars + 2 characters. Among the valid cuts, the lowest score wins:
    uneven lengths, a group ending on "the", "and"… (+10), each group (+2), and a lone short word that would only flash (+4)."""
    clauses, cur = [], []
    for w in caps:
        if cur and w[1] - cur[-1][2] > gap and cur[-1][0].lower() not in func: clauses.append(cur); cur = []
        cur.append(w)
        if w[3]: clauses.append(cur); cur = []
    if cur: clauses.append(cur)
    out = []
    for cl in clauses:
        n = len(cl); chars = len(' '.join(w[0] for w in cl))
        def splits(i, parts):               # every way to cut words i… into `parts` contiguous groups
            if parts == 1: yield [cl[i:]]; return
            for j in range(i + 1, n - parts + 2):
                for rest in splits(j, parts - 1): yield [cl[i:j]] + rest
        def best_at(k):
            best = None
            for sp in splits(0, k):
                lens = [len(' '.join(w[0] for w in g)) for g in sp]
                if any(len(g) > max_words + (1 if L <= max_chars else 0) or L > max_chars + 2 for g, L in zip(sp, lens)): continue
                score = (max(lens) - min(lens) + 10 * sum(g[-1][0].lower() in func for g in sp[:-1]) + 2 * k
                         + 4 * sum(len(g) == 1 and L < 7 for g, L in zip(sp, lens)) * (n > 1))
                if best is None or score < best[0]: best = (score, sp)
            return best
        k_hi = max(-(-n // max_words), -(-chars // max_chars), 1) + 1
        cands = [b for b in (best_at(k) for k in range(max(1, -(-n // (max_words + 1))), min(n, k_hi) + 1)) if b]
        k = min(n, k_hi) + 1
        while not cands and k <= n: cands = [b for b in [best_at(k)] if b]; k += 1
        out += min(cands, key=lambda b: b[0])[1] if cands else [[w] for w in cl]
    return out


class Captioner:
    """one phrase at a time, the spoken word in a roomy amber pill, the rest white with a soft per-letter halo (no band, no box)"""
    def __init__(self, font_path, W, H, y=1320, size=86, weight='ExtraBold', pill=(242, 162, 58), active_text=(20, 22, 25)):
        self.W, self.H, self.y = W, H, y
        self.font = ImageFont.truetype(font_path, size)
        try: self.font.set_variation_by_name(weight)
        except Exception: pass
        self.pill, self.active_text = tuple(pill) + (255,), tuple(active_text) + (255,)
        self.cache = {}

    def layer(self, words, active):
        key = (tuple(words), active)
        if key in self.cache: return self.cache[key]
        f = self.font
        padx, pady = 26, 16
        space = f.getlength(' ') * 0.9 + padx  # the pill's padding never touches the next word
        widths = [f.getlength(w) for w in words]
        total = sum(widths) + space * (len(words) - 1)
        W, H = self.W, 260
        x0 = (W - total) / 2
        asc, desc = f.getmetrics()
        base_y = H / 2 - (asc + desc) / 2
        halo = Image.new('L', (W, H), 0); dh = ImageDraw.Draw(halo)
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); di = ImageDraw.Draw(img)
        x = x0
        boxes = []
        for i, w in enumerate(words):
            boxes.append((x, widths[i]))
            dh.text((x, base_y), w, font=f, fill=255)
            x += widths[i] + space
        halo = halo.filter(ImageFilter.GaussianBlur(9))
        sh = Image.new('RGBA', (W, H), (8, 8, 10, 0)); sh.putalpha(halo.point(lambda v: int(v * 0.62)))
        img = Image.alpha_composite(img, sh); di = ImageDraw.Draw(img)
        if active is not None:
            bx, bw = boxes[active]
            top = base_y + asc * 0.18 - pady; bot = base_y + asc + desc * 0.35 + pady
            di.rounded_rectangle((bx - padx, top, bx + bw + padx, bot), radius=26, fill=self.pill)
        for i, w in enumerate(words):
            di.text((boxes[i][0], base_y), w, font=f, fill=self.active_text if i == active else (255, 255, 255, 255))
        arr = np.asarray(img).astype(np.float32) / 255.0
        self.cache[key] = arr
        return arr

    def draw(self, frame, phrase, t):
        if phrase is None: return frame
        words = [w[0] for w in phrase]
        active = None
        for i, w in enumerate(phrase):
            nxt = phrase[i + 1][1] if i + 1 < len(phrase) else w[2] + 0.35
            if w[1] - 0.03 <= t < max(nxt, w[2]): active = i
        lay = self.layer(words, active)
        h = lay.shape[0]; y0 = int(self.y - h / 2)
        y0c, y1c = max(0, y0), min(frame.shape[0], y0 + h)      # a layer reaching past the frame edge is clipped
        lay = lay[y0c - y0:y1c - y0]
        reg = frame[y0c:y1c].astype(np.float32) / 255.0
        a = lay[..., 3:4]
        frame[y0c:y1c] = ((reg * (1 - a) + lay[..., :3] * a) * 255).astype(np.uint8)
        return frame


def phrase_at(ph, t, cuts=()):
    for k, p in enumerate(ph):
        end = min(ph[k + 1][0][1] - 0.02, p[-1][2] + 0.45) if k + 1 < len(ph) else p[-1][2] + 0.6
        end = min([end] + [c - 1e-6 for c in cuts if c > p[0][1]])   # a phrase ends at the next cut, never over the next shot
        if p[0][1] - 0.06 <= t < end: return p
    return None


def normalise(mix, out):
    """the raw stereo mix → <out>_mix_raw.wav, and two-pass loudnorm (−14 LUFS, true peak −1.5) → <out>_mix.wav"""
    raw, wav = out + '_mix_raw.wav', out + '_mix.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', raw], input=mix.astype('<f4').tobytes(), check=True)
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(m[m.rfind('{'):m.rfind('}') + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
          f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', ln, '-ar', str(SR), wav], check=True)
    return wav


def join(out, parts):
    """parts of one edit, each rendered by main() → <out>.mp4: the pictures copied, the raw mixes joined sample-exact (each part
    trimmed or padded to its plan's length), normalised once and encoded once"""
    lst = out + '_parts.txt'
    with open(lst, 'w') as f:
        f.writelines(f"file '{os.path.abspath(p + '.mp4')}'\n" for p in parts)
    pic = out + '_picture.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-map', '0:v', '-c', 'copy', pic], check=True)
    mixes = []
    for p in parts:
        a, k = load_audio(p + '_mix_raw.wav', ch=2), round(jl(p + '_plan.json')['total'] * SR)
        mixes.append(np.pad(a[:k], ((0, max(0, k - len(a))), (0, 0))))
    wav = normalise(np.concatenate(mixes), out)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', out + '.mp4'], check=True)
    os.remove(pic); os.remove(lst)
    print(out + '.mp4', f'{sum(len(m) for m in mixes) / SR:.2f} s from {len(parts)} parts', flush=True)


def main(edit_path, out, plan_only=False):
    E = jl(edit_path)
    fps, W, H = E.get('fps', 24), E.get('w', 1080), E.get('h', 1920)
    tall = H > W                                           # 9:16 keeps the vertical reels' caption defaults; 16:9 scales to the frame
    segs, vo, caps, total = plan(E)
    ph = phrases(caps, E.get('caption_words', 3 if tall else 5), E.get('caption_chars', 16 if tall else 30),
                 func=set(E['caption_func_words']) if 'caption_func_words' in E else FUNC)
    cuts = cut_check(E, vo)
    json.dump({'segments': segs, 'vo': vo, 'captions': caps, 'total': total, 'cut_check': cuts}, open(out + '_plan.json', 'w'), indent=1, ensure_ascii=False)
    for s in segs: print(f"{s['start']:6.2f}  {s['n'] / fps:5.2f} s  {s['kind']:5s}  {s['clip']}  in {s['in']:.2f}" +
                         (f"  speed {s['speed'][0]}–{s['speed'][1]}×" if 'speed' in s else ''))
    for v in vo: print(f"   vo {v['file']} {v['from']:.2f}-{v['to']:.2f} → {v['at']:.2f}  (err {v['err']}" + (f", tempo {v['tempo']}" if 'tempo' in v else '') + ')')
    for c in cuts: print('   CUT', c)
    M = E.get('music')
    if M and segs and segs[-1]['kind'] != 'card' and M.get('fade_out', 2.0) > 0:
        print(f"   MUSIC fade_out {M.get('fade_out', 2.0)} s and no end card at the end: on a part before the last, set \"fade_out\": 0")
    if M and M.get('from', 0) > 0 and M.get('fade_in', 0.3) > 0:
        print(f"   MUSIC fade_in {M.get('fade_in', 0.3)} s with \"from\" {M['from']}: on a part after the first, set \"fade_in\": 0")
    print('cut check: ' + (f'{len(cuts)} cut(s) to fix (above)' if cuts else 'every voice cut falls in a pause of its take'))
    if plan_only: print(f'total {total:.2f} s (plan only)'); return

    # ---- sound: the voice takes, the b-roll's own sound ducked under the voice, then -14 LUFS
    N = int(total * SR) + SR
    voice = np.zeros(N, np.float32)
    for v in vo:
        a = fade(load_audio(v['file'], v['from'], v['to'] - v['from'], tempo=v.get('tempo')))
        i0 = int(v['at'] * SR); voice[i0:i0 + len(a)] += a[:max(0, N - i0)]
    amb = np.zeros((N, 2), np.float32)
    for s in segs:
        if s['kind'] != 'broll': continue
        a = load_audio(s['clip'], s['in'], s['n'] / fps, ch=2)
        if len(a) == 0: continue
        a = np.stack([fade(a[:, 0].copy(), 30), fade(a[:, 1].copy(), 30)], 1)
        i0 = int(s['start'] * SR); amb[i0:i0 + len(a)] += a[:max(0, N - i0)]
    env = movavg(np.abs(voice), int(0.12 * SR))
    duck = movavg((env > 0.01).astype(np.float32), int(0.25 * SR))
    g_hi, g_lo = 10 ** (E.get('ambience_db', -12) / 20), 10 ** (E.get('duck_db', -22) / 20)
    gain = g_hi + (g_lo - g_hi) * np.clip(duck * 1.5, 0, 1)
    mix = amb * gain[:, None] + voice[:, None]
    M = E.get('music')
    if M:                                                  # optional music bed: {file, from, db, duck_db, fade_in, fade_out}, ducked like the ambience
        a = load_audio(M['file'], M.get('from', 0), total, ch=2)[:N]
        a = np.pad(a, ((0, max(0, N - len(a))), (0, 0)))
        ti, fo, fi = int(total * SR), int(M.get('fade_out', 2.0) * SR), int(M.get('fade_in', 0.3) * SR)
        env_m = np.ones(N, np.float32); env_m[max(0, ti - fo):ti] = np.linspace(1, 0, min(fo, ti)); env_m[ti:] = 0
        env_m[:fi] *= np.linspace(0, 1, fi)
        m_hi, m_lo = 10 ** (M.get('db', -18) / 20), 10 ** (M.get('duck_db', -26) / 20)
        g_m = (m_hi + (m_lo - m_hi) * np.clip(duck * 1.5, 0, 1)) * env_m
        for s in segs:                                     # a card's "music_db" lifts the bed for the ending, ramped in over 0.5 s
            if s['kind'] == 'card' and 'music_db' in s:
                i0 = int(s['start'] * SR); i1 = min(N, i0 + int(s['n'] / fps * SR))
                up = 10 ** ((s['music_db'] - M.get('db', -18)) / 20)
                r = np.full(i1 - i0, up, np.float32); k = min(len(r), int(0.5 * SR)); r[:k] = np.linspace(1, up, k)
                g_m[i0:i1] *= r
        mix = mix + a * g_m[:, None]
    for x in E.get('sfx', []):                             # optional one-shot sounds: {file, at, seg?, from?, dur?, db, duck?}
        a = load_audio(x['file'], x.get('from'), x.get('dur'), ch=2)
        if len(a) == 0: continue
        a = np.stack([fade(a[:, 0].copy(), 4), fade(a[:, 1].copy(), 4)], 1) * 10 ** (x.get('db', -18) / 20)
        i0 = int(((segs[x['seg']]['start'] if 'seg' in x else 0.0) + x['at']) * SR)
        if i0 < 0: a, i0 = a[-i0:], 0
        a = a[:max(0, N - i0)]
        if x.get('duck'): a = a * (gain[i0:i0 + len(a)] / g_hi)[:, None]
        mix[i0:i0 + len(a)] += a
    mix = mix[:int(total * SR)]
    wav = normalise(mix, out)

    # ---- picture: every segment cover-cropped to W x H at fps, a gentle push-in on the host, captions on top
    cap = Captioner(E['font'], W, H, E.get('caption_y', 1320 if tall else round(0.875 * H)), E.get('caption_size', 92 if tall else round(0.05 * H)),
                    E.get('caption_weight', 'ExtraBold'), E.get('caption_pill', (242, 162, 58)), E.get('caption_active_text', (20, 22, 25)))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                            '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', E.get('x264_preset', 'slow'), '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k',
                            '-shortest', '-movflags', '+faststart', out + '.mp4'], stdin=subprocess.PIPE)
    fi, cut_ts = 0, [s['start'] for s in segs[1:]]
    for s in segs:
        warp = s.get('warp')
        vf = ('' if warp else f'fps={fps},') + f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}'
        ss = s['in'] if warp else max(0.0, s['in'] - 0.25 / fps)   # a quarter frame early: the frame at "in" comes first
        dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f"{ss:.4f}", '-i', s['clip']] + ([] if warp else ['-frames:v', str(s['n'])]) +
                               ['-vf', vf, '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
        if warp:                                           # a squeezed host clip: native frames, picked at the warped clip time
            num, den = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0',
                                       s['clip']], capture_output=True, text=True).stdout.strip().split('/')
            src_fps = float(num) / float(den or 1)
            ck, ok = [k[0] for k in warp], [k[1] for k in warp]
        last, got = None, -1
        for j in range(s['n']):
            want = j if not warp else int(round((float(np.interp(j / fps, ok, ck)) - s['in']) * src_fps))
            while got < want:
                buf = dec.stdout.read(W * H * 3)
                if len(buf) < W * H * 3: break
                last = np.frombuffer(buf, np.uint8).reshape(H, W, 3); got += 1
            fr = last.copy()
            if s.get('push'):                  # a sub-pixel crop box: whole-pixel steps made the picture jump every ~8 frames
                z = 1 + s['push'] * j / max(1, s['n'] - 1); cw, ch = W / z, H / z; x0, y0 = (W - cw) / 2, (H - ch) / 2
                fr = np.asarray(Image.fromarray(fr).resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))).copy()
            t = fi / fps
            if s.get('captions', True):                # a phrase's tail never spills onto a segment without captions (a UI scene)
                fr = cap.draw(fr, phrase_at(ph, t, cut_ts), t)
            enc.stdin.write(fr.tobytes()); fi += 1
        dec.stdout.close(); dec.kill(); dec.wait()
    enc.stdin.close(); enc.wait()
    print(out + '.mp4', f'{fi / fps:.2f} s', flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--join': join(sys.argv[2], sys.argv[3:])
    else: main(sys.argv[1], sys.argv[2], '--plan' in sys.argv[3:])
