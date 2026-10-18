"""Self-check for jumpcut.py on a synthetic clip: tone = speech, low noise = pause, white frame = tone on.

run: python scripts/tests/test_jumpcut.py   (or python scripts/jumpcut.py --selftest)
Proves: no cut inside a word (a 0.4 s silent dip INSIDE a word is vetoed), gaps < 150 ms kept, silence pass still
trims a real pause the word pass keeps, cuts frame-aligned, audio/video lengths equal and in sync frame by frame.
"""
import json, pathlib, subprocess, sys, tempfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import jumpcut as jc
from mc_profile import FFMPEG

FPS = 30
# words in frames @30 fps; w2 has a silent dip 63-75 (a stop/breath inside a word)
WORDS = [(30, 48), (51, 90), (135, 150), (163, 181)]
TONE = [(30, 48), (51, 63), (75, 90), (135, 150), (163, 181)]
DUR = 210


def on(t_expr, spans):
    return "+".join(f"gte({t_expr},{a / FPS:.6f})*lt({t_expr},{b / FPS:.6f})" for a, b in spans)


def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, check=True, **kw).stdout


def main():
    words = [{"w": f"w{i}", "s": a / FPS, "e": b / FPS} for i, (a, b) in enumerate(WORDS)]

    # 1. pure logic: < 150 ms gap is never cut, even with the tightest pad and a gap flag below the floor
    frames, _ = jc.plan(words, DUR / FPS, gap=0.05, pad=0.03, sil=[(1.6, 1.7)])
    assert any(a <= 48 and b >= 51 for a, b in frames), frames

    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        src, wj = d / "src.mov", d / "words.json"
        run(FFMPEG, "-v", "error", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s=320x240:r={FPS}:d={DUR / FPS},"
                                 f"drawbox=x=0:y=0:w=iw:h=ih:c=white:t=fill:enable='{on('t+0.0167', TONE)}'",
            "-f", "lavfi", "-i", f"aevalsrc='0.3*sin(2*PI*440*t)*({on('t', TONE)})+0.003*(2*random(0)-1)':s=48000:d={DUR / FPS}",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(src))
        wj.write_text(json.dumps(words))
        log = run(sys.executable, str(pathlib.Path(jc.__file__)), str(src), str(wj), "--size", "1080x1920", text=True)
        print(log.strip())
        cut = d / "cut.mp4"
        edl = json.loads((d / "edl.json").read_text())
        fr = [[round(s * FPS), round(e * FPS)] for s, e in edl]

        # 2. frame-aligned EDL
        assert all(abs(s * FPS - a) < 1e-4 and abs(e * FPS - b) < 1e-4 for (s, e), (a, b) in zip(edl, fr)), edl
        # 3. no cut inside any word (the in-word dip 63-75 included) and the 0.1 s gap 48-51 kept
        for a, b in WORDS + [(48, 51)]:
            assert any(s <= a and b <= e for s, e in fr), (a, b, fr)
        # 4. silence pass still works: the 0.43 s pause 150-163 (kept by the word pass) is trimmed but not to 0
        assert not any(s <= 150 and 163 <= e for s, e in fr), fr
        # 5. rendered lengths: video frames == EDL frames, audio within one AAC frame of video
        n = sum(b - a for a, b in fr)
        vid = np.frombuffer(run(FFMPEG, "-v", "error", "-i", str(cut), "-vf", "scale=8:8,format=gray", "-f", "rawvideo", "-"),
                            np.uint8).reshape(-1, 64).mean(1) > 128
        aud = np.frombuffer(run(FFMPEG, "-v", "error", "-i", str(cut), "-ac", "1", "-ar", "48000", "-f", "f32le", "-"), np.float32)
        assert len(vid) == n, (len(vid), n)
        assert abs(len(aud) / 48000 - n / FPS) < 1024 / 48000, (len(aud) / 48000, n / FPS)
        # 6. lip-sync: tone on <=> white frame, for every frame of the cut (a 1-frame lag fails every onset)
        ch = aud[:n * 1600].reshape(-1, 1600).astype(np.float64)
        loud = 20 * np.log10(np.sqrt((ch ** 2).mean(1)) + 1e-9) > -30
        bad = np.flatnonzero(loud != vid[:len(loud)])
        assert len(bad) == 0, f"av mismatch at cut frames {bad.tolist()}"
        print(f"test_jumpcut ok: {len(fr)} segments {fr}, {n} frames, audio {len(aud) / 48000:.3f}s vs video {n / FPS:.3f}s, "
              f"{int(loud.sum())} tone frames all in sync")


if __name__ == "__main__":
    main()
