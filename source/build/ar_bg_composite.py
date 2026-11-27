import subprocess, sys, numpy as np
src, bg, plate_path, out, = sys.argv[1:5]
limit = int(sys.argv[5]) if len(sys.argv) > 5 else 0
W, H = 1920, 1080
FS = W * H * 3
plate = np.load(plate_path).astype(np.float32)
pc = plate[:80, :80].mean()

dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE, bufsize=FS * 2)
bgd = subprocess.Popen(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-i', bg,
                        '-vf', 'fps=30,scale=1920:1080:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE, bufsize=FS * 2)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', '30', '-i', '-', '-i', src, '-map', '0:v', '-map', '1:a', '-c:a', 'copy',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart', '-shortest', out], stdin=subprocess.PIPE)
n = 0
while True:
    a = dec.stdout.read(FS)
    if len(a) < FS:
        break
    b = bgd.stdout.read(FS)
    o = np.frombuffer(a, np.uint8).reshape(H, W, 3).astype(np.float32)
    g = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    # global fade level (fade from/to black) from the empty top-left corner
    f = float(np.clip(o[:80, :80].mean() / pc, 0, 1))
    if f > 0.9:
        f = 1.0
    d = o - plate * f
    m = np.abs(d).max(-1, keepdims=True)
    alpha = np.clip((m - 12) / 40, 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    res = alpha * o + (1 - alpha) * (g * f + d)
    enc.stdin.write(np.clip(res + 0.5, 0, 255).astype(np.uint8).tobytes())
    n += 1
    if limit and n >= limit:
        break
    if n % 300 == 0:
        print(n, flush=True)
enc.stdin.close(); enc.wait(); dec.kill(); bgd.kill()
print('frames', n)
