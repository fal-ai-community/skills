"""Checks the host segments of a finished host_reel.py video for two faults: frames repeated or skipped, and a voice off the lips.
- Picture: the segment's frame-to-frame changes against the clip's own over the same span. A clip played 1:1 moves exactly as
  its source (r ≈ 0.99, no frame off); a repeated frame (a 30 fps cut of 24 fps clips repeats every 5th one) or a skipped one
  (a retimed face) shows as a frame whose change differs from the clip's. Only the part above the captions is compared: a
  caption's word highlight changes on every word.
- Voice: the final mix over the segment against the clip's own sound over the same span. An H3 Max Lip Sync clip carries the
  take its lips were made from, so the lag is how far the voice sits from the lips: within ±20 ms it matches.

  python3 host_check.py <video.mp4> <video_plan.json>        (run where host_reel.py ran: the plan's clip paths are relative)
"""
import json
import subprocess
import sys

import numpy as np

SR, TW = 16000, 180


def probe(path):
    st = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                                    '-of', 'json', path], capture_output=True, text=True, check=True).stdout)['streams'][0]
    num, den = st['r_frame_rate'].split('/')
    return st['width'], st['height'], float(num) / float(den or 1)


def changes(path, t0, n, w, h, top, fps):
    """mean change from each frame to the next, at the master's rate, in the part above the captions only (the top 55 % of a
    9:16 frame, 75 % of a 16:9 one)"""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0.0, t0):.4f}', '-i', path, '-frames:v', str(n), '-vf',
                          f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w)[:, :int(h * top)].astype(float)
    return np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))


def sound(path, t0, d):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.4f}', '-t', f'{d:.4f}', '-i', path, '-vn', '-ac', '1', '-ar', str(SR),
                          '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(float) / 32768


def lag(a, b, most=0.3):
    """seconds b must move to line up with a, searched within ±most s, and the normalised correlation there"""
    m = min(len(a), len(b)); a, b = a[:m], b[:m]
    n = 1 << (2 * m).bit_length()
    cc = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    k = int(most * SR); cand = np.r_[cc[:k + 1], cc[-k:]]; lags = np.r_[np.arange(k + 1), np.arange(-k, 0)]
    i = int(np.argmax(cand))
    return lags[i] / SR, float(cand[i] / np.sqrt(np.sum(a ** 2) * np.sum(b ** 2) + 1e-12))


src, plan = sys.argv[1], sys.argv[2]
W, H, fps = probe(src); th = int(round(H * TW / W / 2)) * 2
print(f'{src}: {W}x{H}, {fps:g} fps' + ('' if abs(fps - 24) < 0.01 else '  (the master should be 24 fps)'))
for s in json.load(open(plan))['segments']:
    if s['kind'] != 'host': continue
    t0, n, d, top = s['start'], s['n'], s['n'] / fps, (0.55 if H > W else 0.75)
    da = changes(src, t0, n, TW, th, top, fps)
    at = lambda idx: [round(float(t0 + (i + 1) / fps), 2) for i in idx]
    dup = at(np.where(da < max(0.05, 0.1 * float(np.median(da))))[0])          # a frame equal to the one before
    pre = min(2, int(s['in'] * fps))                       # the clip from 2 frames early: find the frame it lines up on
    db = changes(s['clip'], s['in'] - pre / fps, n + pre + 2, TW, th, top, fps)
    fit = [(float(np.corrcoef(da, db[k:k + len(da)])[0, 1]), k - pre, db[k:k + len(da)])
           for k in range(min(len(db) - len(da), pre + 2) + 1)] if len(db) >= len(da) > 2 else []
    r, off, b = max(fit, key=lambda x: x[0]) if fit else (0.0, 0, None)
    bad = at(np.where(np.abs(da - b) > np.maximum(0.3, 0.5 * b))[0]) if b is not None else ['the clip is shorter than the segment']
    line = (f"{t0:7.2f}  host {s.get('line', '')}: {len(da) + 1} frames, {len(dup)} repeated{' ' + str(dup[:8]) if dup else ''}, "
            f"picture against the clip r {r:.3f}{f' ({off:+d} frame(s) from its in point)' if off else ''}, "
            f"{len(bad)} frame(s) off{' ' + str(bad[:8]) if bad else ''}")
    ok = r >= 0.95 and len(bad) <= max(1, len(da) // 50) and len(dup) <= 1
    if 'warp' in s: print(line + '; retimed ("sync": "video"), voice not checked  CHECK'); continue
    lg, c = lag(sound(src, t0, d), sound(s['clip'], s['in'], d))
    ok = ok and abs(lg) <= 0.02
    print(line + f"; voice {lg * 1000:+.0f} ms against the clip's own sound (corr {c:.2f})" + ('' if ok else '  CHECK'))
