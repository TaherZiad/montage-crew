"""Audio post for Arabic talking-head reels (see references/craft/04-sound-design.md).

  python audio.py voice <in> <out.wav> [--noisy]   # declip + level-match + clean + EQ + de-ess + 2 comps + limiter (48k mono)
  python audio.py master <in> <out>                # two-pass loudnorm -> -14 LUFS, TP -1.5, LRA 7 (copies video if present)
  python audio.py check <file>                     # print integrated loudness / true peak / LRA
  python audio.py --selftest
"""
import json, pathlib, re, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG  # noqa: E402

VOICE = ("aformat=sample_rates=48000:channel_layouts=mono,adeclip,volume={pre}dB,highpass=f=80:poles=2,afftdn=nr={nr}:nf={nf}:tn=1,"
         "agate=threshold=-45dB:range=-10dB:ratio=2:attack=5:release=250,"
         "equalizer=f=120:t=q:w=1:g=1.5,equalizer=f=350:t=q:w=1.4:g=-3,equalizer=f=3200:t=q:w=1.2:g=2.5,"
         "highshelf=f=10000:g=2,deesser=i=0.4:m=0.5:f=0.5,"
         "acompressor=threshold=-21dB:ratio=3:attack=10:release=150:knee=4:makeup=4dB,"
         "acompressor=threshold=-10dB:ratio=6:attack=2:release=60:knee=2,alimiter=limit=-2dB:attack=3:release=60:level=0")
LN = "loudnorm=I=-14:TP=-1.5:LRA=7"


def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def measure(src):
    err = run([FFMPEG, "-hide_banner", "-i", src, "-af", LN + ":print_format=json", "-f", "null", "-"]).stderr
    return json.loads(re.findall(r"\{[^{}]+\}", err)[-1])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] == "--selftest":
        return selftest()
    cmd, src, *rest = argv
    if cmd == "voice":
        noisy = "--noisy" in rest
        # the compressors expect speech around -20 LUFS: level-match first (hot phone/lav recordings clip otherwise)
        pre = max(-12.0, min(12.0, -20 - float(measure(src)["input_i"])))
        chain = VOICE.format(pre=f"{pre:.1f}", nr=18 if noisy else 12, nf=-35 if noisy else -42)
        r = run([FFMPEG, "-y", "-v", "error", "-i", src, "-vn", "-af", chain, "-c:a", "pcm_s16le", rest[0]])
        print(r.stderr or f"voice -> {rest[0]}")
    elif cmd == "master":
        m = measure(src)
        af = (f"alimiter=limit=-1.5dB:level=0,{LN}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
        r = run([FFMPEG, "-y", "-v", "error", "-i", src, "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", rest[0]])
        print(r.stderr or f"master -> {rest[0]}")
    elif cmd == "check":
        m = measure(src)
        print(f"I={m['input_i']} LUFS  TP={m['input_tp']} dBTP  LRA={m['input_lra']}")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        raw, v, m = d / "raw.wav", d / "voice.wav", d / "m.m4a"
        # speech-like: 180 Hz buzz with 4 Hz syllable envelope + room noise, quiet (-30 LUFS-ish)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i",
                        "aevalsrc=0.05*sin(2*PI*180*t)*(0.6+0.4*sin(2*PI*4*t))+0.002*(2*random(0)-1):s=44100:d=4",
                        str(raw)], check=True)
        main(["voice", str(raw), str(v)])
        info = subprocess.run([FFMPEG, "-hide_banner", "-i", str(v)], capture_output=True, text=True).stderr
        assert "48000 Hz, mono" in info, info
        main(["master", str(v), str(m)])
        i = float(measure(str(m))["input_i"])
        assert abs(i + 14) < 1.5, i
    print("selftest ok")


if __name__ == "__main__":
    main()
