"""Host clips with H3 Max Lip Sync: a still of the presenter and the picked take go in, the presenter saying that take comes
out, played 1:1 in the edit (host_reel.py "sync": "clip"; voice-and-host.md §4).

  python3 host_lipsync.py prep <take.mp3> <still.jpg | room_clip.mp4[@seconds]> <out_prefix>
      <out_prefix>_audio.wav  the take's speech (from 0.04 s before its first sound to 0.12 s after its last) placed at
                              0.30 s, then 0.40 s of silence, padded to the model's 5 s minimum; 48 kHz mono, level untouched
      <out_prefix>_frame.jpg  the still, or the clip's frame at the given second (default its first frame)
      prints the audio length and the predicted take_at (where the take's 0 s will sit in the clip)
  python3 host_lipsync.py measure <take.mp3> <lipsync_clip.mp4> [line_id]
      the clip's size, fps and length; take_at measured by cross-correlating the clip's sound with the take (≥ 0.98 expected:
      the model returns the audio resampled to 32 kHz, so the take itself goes into the mix); the edit's host segment

The job: minimax/h3-max/lip-sync/image-to-video with image_url = the frame, audio_url = the wav, resolution "1080P",
enable_transcription true. The output lasts as long as the wav, at 24 fps; about $0.16/s at 1080P (models.md §2).
"""
import json
import subprocess
import sys

import numpy as np

LEAD, TAIL, MIN_LEN, SR = 0.30, 0.40, 5.0, 48000


def pcm(path, sr):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.int16).astype(float) / 32768


def speech_span(a, sr):
    """first and last 10 ms block within 35 dB of the take's loudest block"""
    blk = sr // 100; m = len(a) // blk * blk
    db = 20 * np.log10(np.sqrt(np.mean(a[:m].reshape(-1, blk) ** 2, axis=1)) + 1e-9)
    act = np.where(db > db.max() - 35)[0]
    return act[0] * 0.01, (act[-1] + 1) * 0.01


def prep(take, still, out):
    a = pcm(take, SR); on, off = speech_span(a, SR)
    s0 = max(0.0, on - 0.04); seg = a[int(s0 * SR):int(min(len(a) / SR, off + 0.12) * SR)]
    total = max(MIN_LEN, LEAD + len(seg) / SR + TAIL)
    buf = np.zeros(int(round(total * SR))); i = int(LEAD * SR); buf[i:i + len(seg)] = seg
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le',
                    out + '_audio.wav'], input=(np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)
    src, at = still, '0'
    if '@' in still:
        head, tail = still.rsplit('@', 1)
        try: float(tail); src, at = head, tail
        except ValueError: pass
    seek = ['-ss', at] if src.lower().endswith(('.mp4', '.mov', '.webm', '.mkv')) else []
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *seek, '-i', src, '-frames:v', '1', '-q:v', '2', out + '_frame.jpg'], check=True)
    print(json.dumps({'audio': out + '_audio.wav', 'frame': out + '_frame.jpg', 'audio_len': round(total, 3),
                      'speech_in_take': [round(on, 2), round(off, 2)], 'take_at': round(LEAD - s0, 3)}))


def measure(take, clip, line):
    p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                   'stream=width,height,r_frame_rate:format=duration', '-of', 'json', clip],
                                  capture_output=True, text=True, check=True).stdout)
    st = p['streams'][0]; num, den = st['r_frame_rate'].split('/'); fps = float(num) / float(den or 1)
    sr = 16000; c, t = pcm(clip, sr), pcm(take, sr)
    n = 1 << (len(c) + len(t)).bit_length()
    cc = np.fft.irfft(np.fft.rfft(c, n) * np.conj(np.fft.rfft(t, n)), n)          # cc[k] = sum c[i + k] * t[i]
    k = int(np.argmax(cc)); lag = (k if k < n // 2 else k - n) / sr
    corr = float(cc[k] / np.sqrt(np.sum(c ** 2) * np.sum(t ** 2) + 1e-12))
    ok = corr >= 0.98 and abs(fps - 24) < 0.01
    print(f"{clip}: {st['width']}x{st['height']}, {fps:g} fps, {float(p['format']['duration']):.2f} s; "
          f"take_at {lag:.3f} s, corr {corr:.3f}" + ('' if ok else '  CHECK: not the take, or not 24 fps'))
    print(json.dumps({'kind': 'host', 'line': line, 'clip': clip, 'take_at': round(lag, 2), 'lead': 0.12, 'tail': 0.25}))


if __name__ == '__main__':
    if len(sys.argv) >= 5 and sys.argv[1] == 'prep': prep(*sys.argv[2:5])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'measure': measure(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'H1')
    else: sys.exit(__doc__)
