"""Voice against bed in a finished host_reel.py mix: RMS while the voice speaks vs in the pauses between voice pieces (music,
clip sound and SFX only), and the loudness targets.

  python3 mix_check.py <video.mp4> <video_plan.json>

Speech windows come from the plan's voice pieces; pauses are the gaps of at least 0.25 s between them (the first and last 0.5 s
left out). Targets: the bed 15–25 dB under the voice, −14 LUFS integrated, true peak ≤ −1 dBFS.
"""
import json
import subprocess
import sys

import numpy as np

src, plan = sys.argv[1], sys.argv[2]
P = json.load(open(plan))
SR = 16000
a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
spans = sorted((v['at'], v['at'] + (v['to'] - v['from']) / v.get('tempo', 1.0)) for v in P['vo'])
db = lambda x: 10 * np.log10(np.mean(x.astype(np.float64) ** 2) + 1e-12)
speech = np.concatenate([a[int(s * SR):int(e * SR)] for s, e in spans])
gaps = [(e, s2) for (_, e), (s2, _) in zip(spans, spans[1:]) if s2 - e >= 0.25]
pause = np.concatenate([a[int((s + 0.05) * SR):int((e - 0.05) * SR)] for s, e in gaps if s > 0.5 and e < P['total'] - 0.5]) if gaps else np.zeros(1)
diff = db(speech) - db(pause)
print(f'speech {db(speech):.1f} dBFS RMS | pauses {db(pause):.1f} dBFS RMS ({len(gaps)} gaps, {len(pause) / SR:.1f} s) | difference {diff:.1f} dB'
      + ('' if 15 <= diff <= 25 else '  ← outside 15–25 dB'))
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = m[m.rfind('Summary:'):]
print(' '.join(l.strip() for l in summ.splitlines() if any(k in l for k in ('I:', 'LRA:', 'Peak:'))))
