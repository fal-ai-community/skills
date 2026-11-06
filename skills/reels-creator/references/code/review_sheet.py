"""Review sheet of a finished host_reel.py video: two frames per segment (just after the cut and in the middle), labelled with
their times, plus the loudness summary (integrated LUFS, LRA, true peak). One image shows the whole edit's order and look.

  python3 review_sheet.py <video.mp4> <video_plan.json> <sheet.jpg>

The frame rate and orientation come from the video (9:16: 270x480 tiles, 6 columns; 16:9: 480x270 tiles, 4 columns).
"""
import io
import json
import subprocess
import sys

from PIL import Image, ImageDraw

src, plan, out = sys.argv[1], sys.argv[2], sys.argv[3]
P = json.load(open(plan))
pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'csv=p=0', src],
                    capture_output=True, text=True).stdout.strip().split(',')
W, H = int(pr[0]), int(pr[1]); num, den = pr[2].split('/'); fps = float(num) / float(den or 1)
w, h, cols = (270, 480, 6) if H > W else (480, 270, 4)
ts = []
for s in P['segments']:
    d = s['n'] / fps
    ts += [s['start'] + min(0.3, d / 3), s['start'] + d / 2]
ims = []
for t in ts:
    b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', '-vf', f'scale={w}:{h}', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                       capture_output=True).stdout
    ims.append((t, Image.open(io.BytesIO(b)).convert('RGB')))
rows = -(-len(ims) // cols)
S = Image.new('RGB', (cols * w, rows * (h + 18)), 'white'); d = ImageDraw.Draw(S)
for k, (t, im) in enumerate(ims):
    x = (k % cols) * w; y = (k // cols) * (h + 18); S.paste(im, (x, y + 18)); d.text((x + 4, y + 3), f't={t:.1f}', fill='black')
S.save(out, quality=86)
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = m[m.rfind('Summary:'):]
print(out, '|', ' '.join(l.strip() for l in summ.splitlines() if any(k in l for k in ('I:', 'LRA:', 'Peak:'))))
