"""X-PUSH: eased push-in anchored on the eyes (pre-rendered, works with any editor).

usage: python push.py in.mp4 out.mp4 T0 DUR AMOUNT [--size 1080x1920|1920x1080|9x16|16x9] [--eyes 0.33]
       python push.py --selftest
  AMOUNT 0.12–0.28 over DUR 0.47–0.6 s (14–18 frames). Upscales ×2 first so the move has no 2-px stepping jitter.
  --eyes = the eye line as a fraction of the crop's free height (0.33 for a normal talking head).
"""
import pathlib, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG, FFPROBE, canvas  # noqa: E402


def push(src, out, t0, dur, amount, size=None, eyes=0.33):
    W, H = canvas(size)
    for v in (t0, dur, amount, eyes):
        float(v)  # numbers only: they go into an ffmpeg expression
    x = f"clip((t-{t0})/{dur},0,1)"
    e = f"({x}^2*(3-2*{x}))"
    W2, H2 = 2 * W, 2 * H
    vf = (f"scale={W2}:{H2}:force_original_aspect_ratio=increase:flags=lanczos,crop={W2}:{H2},"
          f"scale=w='2*trunc({W2}*(1+{amount}*{e})/2)':h=-2:eval=frame,"
          # offsets from the same eased curve: crop's iw/ih stay at the first frame's size when scale changes per frame
          f"crop={W2}:{H2}:x='{W2}*{amount}*{e}/2':y='{H2}*{amount}*{e}*{eyes}',scale={W}:{H}:flags=lanczos,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-crf", "16",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", str(out)],
                   check=True)


def selftest():
    import numpy as np
    with tempfile.TemporaryDirectory() as d:
        src, out = pathlib.Path(d) / "s.mp4", pathlib.Path(d) / "p.mp4"
        # a white square in the middle: after a 0.25 push it must be ~25 % wider
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=270x480:r=30:d=1.5",
                        "-vf", "drawbox=x=105:y=210:w=60:h=60:c=white:t=fill", "-pix_fmt", "yuv420p", str(src)], check=True)
        push(src, out, 0.2, 0.5, 0.25, "270x480", 0.5)

        def width(at):
            f = np.frombuffer(subprocess.run([FFMPEG, "-v", "error", "-ss", str(at), "-i", str(out), "-frames:v", "1",
                                              "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout,
                              np.uint8).reshape(480, 270)
            xs = np.where(f[240] > 128)[0]
            return len(xs), (xs.min() + xs.max()) / 2
        (w0, c0), (w1, c1) = width(0.0), width(1.3)
        assert 1.18 < w1 / w0 < 1.32 and abs(c1 - c0) <= 2, (w0, c0, w1, c1)  # bigger, still centred
        n = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "stream=nb_frames", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True).stdout.strip()
        assert n == "45", n
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
    else:
        size = a[a.index("--size") + 1] if "--size" in a else None
        eyes = float(a[a.index("--eyes") + 1]) if "--eyes" in a else 0.33
        push(*a[:5], size=size, eyes=eyes)
        print("push ->", a[1])
