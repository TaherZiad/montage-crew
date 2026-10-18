"""Final master (house rule): STATIC gain to -14 LUFS + 4x-oversampled true-peak limiter (<= -1.5 dBTP), never dynamic
loudnorm (audio.py master falls back to loudnorm's dynamic mode on this mix: +2 dB pushes the voice TP past -1.5 = pumping).
  python master.py <render.mp4|wav> <out.mp4>      video stream copied, AAC 256k 48 kHz; I/TP verified on the ENCODED file
  python master.py --selftest
"""
import pathlib, re, subprocess, sys, tempfile

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG  # noqa: E402


def meas(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def master(src, dst, target=-14.0, tp_max=-1.5):
    i0, _ = meas(src)
    gain, ceil = target - i0, tp_max - 0.1
    for _ in range(4):
        af = (f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={10 ** (ceil / 20):.4f}:attack=3:release=60:level=false:latency=true,"
              f"aresample=48000")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-map", "0:v?", "-map", "0:a:0", "-af", af, "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", dst], check=True)
        i, tp = meas(dst)
        print(f"gain {gain:+.2f} dB, ceiling {ceil:.2f} dBFS@4x -> I {i:.2f} LUFS, TP {tp:.2f} dBTP")
        if abs(i - target) <= 0.2 and tp <= tp_max:
            return i, tp
        gain += target - i
        if tp > tp_max:
            ceil -= tp - tp_max + 0.1
    raise SystemExit("master did not converge: check the render")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        src, out = str(pathlib.Path(d) / "r.mp4"), str(pathlib.Path(d) / "f.mp4")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=320x240:r=30:d=3",
                        "-f", "lavfi", "-i", "aevalsrc=0.4*sin(2*PI*300*t)*(0.5+0.5*sin(2*PI*3*t)):s=48000:d=3",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", src], check=True)
        i, tp = master(src, out)
        assert abs(i + 14) <= 0.2 and tp <= -1.5, (i, tp)
    print("selftest ok")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] == "--selftest":
        selftest()
    else:
        master(sys.argv[1], sys.argv[2])
