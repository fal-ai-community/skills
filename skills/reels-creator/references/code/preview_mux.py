"""Rendered scenes joined with their voice takes for a quick review clip (a motion test, a scene check), before the full edit.
Each take starts so its first word lands --lead seconds into its scene (0.16, as host_reel.py places it), padded or cut to the
scene's length.

  python3 preview_mux.py out/test.mp4 out/S_map.mp4:vo/V1_s404 out/S_flux.mp4:vo/V5_s404 [--lead=0.16]

Each take needs its Scribe file next to it (vo/V1_s404.scribe.json, the saved Scribe v2 result).
"""
import json
import os
import subprocess
import sys

args = [a for a in sys.argv[1:] if not a.startswith('--')]
LEAD = float(next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--lead=')), 0.16))
out, specs = args[0], args[1:]
ins, fc, vs = [], [], []
for k, sp in enumerate(specs):
    clip, take = sp.rsplit(':', 1)
    if os.path.splitext(take)[1].lower() in ('.mp3', '.wav'): take = os.path.splitext(take)[0]
    ws = [w for w in json.load(open(take + '.scribe.json'))['words'] if w.get('type', 'word') == 'word']
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', clip]).decode())
    st = ws[0]['start'] - LEAD
    ins += ['-i', clip, '-i', take + '.mp3']
    pre = f'adelay={int(round(-st * 1000))}:all=1,' if st < 0 else f'atrim=start={st:.3f},'
    fc.append(f'[{2 * k + 1}:a]{pre}asetpts=PTS-STARTPTS,apad,atrim=0:{dur:.3f},aresample=48000[a{k}]')
    fc.append(f'[{2 * k}:v]setpts=PTS-STARTPTS[v{k}]')
    vs.append(f'[v{k}][a{k}]')
fc.append(''.join(vs) + f'concat=n={len(specs)}:v=1:a=1[v][a]')
cmd = ['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print(out)
