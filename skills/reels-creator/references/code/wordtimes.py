"""Scene-relative word times for an animation scene built on one voice take (a host_reel.py b-roll segment whose clip is the
rendered scene): the first word lands 0.16 s after the cut, and the scene lasts last-word-end − first-word-start + 0.44 s.
Put these times in the scene's seek(t) so every label appears on its spoken word.

  python3 wordtimes.py vo/V3_s101[.mp3] [first_word_index] [end_word_index_exclusive]

Needs vo/V3_s101.scribe.json (the saved Scribe v2 result). The segment in the edit is {"kind": "broll", "clip": <scene.mp4>, "in": 0,
"line": <line id>, "words": [first, end], "captions": false}.
"""
import json
import os
import sys

tk = sys.argv[1]
tk = tk[:-len(os.path.splitext(tk)[1])] if os.path.splitext(tk)[1].lower() in ('.mp3', '.wav', '.json') else tk
if tk.endswith('.scribe'): tk = tk[:-7]
a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
d = json.load(open(tk + '.scribe.json'))
ws = [w for w in d['words'] if w.get('type', 'word') == 'word']
b = int(sys.argv[3]) if len(sys.argv) > 3 else len(ws)
ws = ws[a:b]; t0 = ws[0]['start']
print(f"{tk}  words [{a},{b})  scene length {ws[-1]['end'] - t0 + 0.44:.2f} s")
print('  '.join(f"{i + a}:{w['text']}@{0.16 + w['start'] - t0:.2f}" for i, w in enumerate(ws)))
