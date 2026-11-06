"""Review sheet for a clip: frames at a fixed rate in a labelled grid, so a whole take can be judged in one image.

  python3 sheet.py <clip.mp4> <out.jpg> [--fps=4] [--cols=4] [--w=600]
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw


def main(src, dst, fps=4.0, cols=4, w=600):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'fps={fps},scale={w}:-2', '-q:v', '3', f'{td}/%03d.jpg'], check=True)
        fs = sorted(os.listdir(td))
        ims = [Image.open(f'{td}/{f}').convert('RGB') for f in fs]
    if not ims: sys.exit(f'{src}: no frames')
    iw, ih = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * iw, rows * (ih + 20)), 'white')
    d = ImageDraw.Draw(S)
    for i, im in enumerate(ims):
        x, y = (i % cols) * iw, (i // cols) * (ih + 20)
        S.paste(im, (x, y + 20)); d.text((x + 4, y + 4), f'{os.path.basename(src)}  t={i / fps:.2f}', fill='black')
    S.save(dst, quality=88)
    print(dst, len(ims), 'frames')


if __name__ == '__main__':
    opt = {a.split('=')[0][2:]: a.split('=')[1] for a in sys.argv[3:] if a.startswith('--')}
    main(sys.argv[1], sys.argv[2], float(opt.get('fps', 4)), int(opt.get('cols', 4)), int(opt.get('w', 600)))
