"""X-PARK: shrink the speaker into a corner with a smoothstep ease (pre-rendered, works with any editor).

usage: python park.py in.mp4 out.mp4 T0 DUR S XT YT [--size 1080x1920|1920x1080|9x16|16x9]
       python park.py --selftest
  T0/DUR = when the move starts and how long it takes (s) · S = final scale (0.34–0.55)
  XT/YT  = final top-left of the parked speaker (px on the canvas)
  9:16 examples: bottom-right 0.55 432 442 · top 0.55 243 110 · corner cam 0.34 650 1000
The background is a blurred, darkened copy of the same frame. With a replaced background, scale the speaker layer
over the plate instead (compose.py "zoom" segments).
"""
import pathlib, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG, FFPROBE, canvas  # noqa: E402


def ease(t0, d):
    x = f"clip((t-{t0})/{d},0,1)"
    return f"({x}^2*(3-2*{x}))"


def park(src, out, t0, dur, s, xt, yt, size=None):
    W, H = canvas(size)
    for v in (t0, dur, s, xt, yt):
        float(v)  # numbers only: they go into an ffmpeg expression
    e = ease(t0, dur)
    fc = (f"[0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},split[a][b];"
          f"[a]gblur=sigma=40,eq=brightness=-0.08:saturation=0.8[bg];"
          f"[b]scale=w='2*trunc({W}*(1-(1-{s})*{e})/2)':h=-2:eval=frame[fg];"
          f"[bg][fg]overlay=x='{xt}*{e}':y='{yt}*{e}':eval=frame,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-c:v", "libx264", "-crf", "16",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", str(out)],
                   check=True)


def selftest():
    import numpy as np
    with tempfile.TemporaryDirectory() as d:
        src, out = pathlib.Path(d) / "s.mp4", pathlib.Path(d) / "p.mp4"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=270x480:r=30:d=2",
                        "-pix_fmt", "yuv420p", str(src)], check=True)
        park(src, out, 0.2, 0.5, 0.5, 120, 220, "270x480")
        wh = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "stream=width,height,nb_frames", "-of", "csv=p=0",
                             str(out)], capture_output=True, text=True).stdout.split(",")
        assert wh[:2] == ["270", "480"] and int(wh[2]) == 60, wh
        last = np.frombuffer(subprocess.run([FFMPEG, "-v", "error", "-sseof", "-0.1", "-i", str(out), "-frames:v", "1",
                                             "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout,
                             np.uint8).reshape(480, 270)
        assert last[:200, :100].std() < last[230:470, 125:265].std()  # blurred background vs sharp parked speaker
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
    else:
        size = a[a.index("--size") + 1] if "--size" in a else None
        park(*a[:7], size=size)
        print("park ->", a[1])
