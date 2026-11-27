"""Background swap at 4K: out = orig + k * (newbg - oldplate), where k = opacity*fade*(1-alpha).
Renders one segment [start_frame, end_frame) to a video-only file."""
import subprocess, sys, numpy as np, cv2
src, bg, plate_path, out, s0, s1, opacity = sys.argv[1:8]
s0, s1, opacity = int(s0), int(s1), float(opacity)
W, H, w, h = 3840, 2160, 1920, 1080
FS, fs = W * H * 3, w * h * 3
plate = np.load(plate_path).astype(np.float32)          # 1080p
pc = plate[:80, :80].mean()
plate4k = cv2.resize(plate, (W, H), interpolation=cv2.INTER_CUBIC)
t0 = s0 / 30.0
n_frames = s1 - s0
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.6f}', '-i', src, '-frames:v', str(n_frames),
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=fs * 2)
up = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.6f}', '-i', src, '-frames:v', str(n_frames),
                       '-vf', 'scale=3840:2160:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                      stdout=subprocess.PIPE, bufsize=FS * 2)
bgd = subprocess.Popen(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-i', bg,
                        '-vf', f'fps=30,trim=start_frame={s0 % 900}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE, bufsize=FS * 2)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', '-threads', '4', out], stdin=subprocess.PIPE)
n = 0
while n < n_frames:
    a = dec.stdout.read(fs); A = up.stdout.read(FS); b = bgd.stdout.read(FS)
    if len(a) < fs or len(A) < FS or len(b) < FS:
        break
    o = np.frombuffer(a, np.uint8).reshape(h, w, 3).astype(np.float32)
    f = float(np.clip(o[:80, :80].mean() / pc, 0, 1))
    if f > 0.9:
        f = 1.0
    m = np.abs(o - plate * f).max(-1)
    alpha = np.clip((m - 12) / 40, 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    k = cv2.resize((opacity * f) * (1 - alpha), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    O = np.frombuffer(A, np.uint8).reshape(H, W, 3).astype(np.float32)
    G = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    res = O + k * (G - plate4k)
    enc.stdin.write(np.clip(res + 0.5, 0, 255).astype(np.uint8).tobytes())
    n += 1
enc.stdin.close(); enc.wait()
for p in (dec, up, bgd):
    p.kill()
print(out, 'frames', n, 'expected', n_frames)
