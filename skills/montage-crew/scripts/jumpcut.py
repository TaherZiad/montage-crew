"""Remove pauses using word timestamps, render a tight cut and remap word times.

usage: python jumpcut.py <video> <words.json> [--gap 0.3] [--pad 0.08] [--silence auto|-38|0] [--out cut.mp4] [--drop "3.2-4.1,10-12.5"]
                          [--size 1080x1920|1920x1080|9x16|16x9]   (default: the profile's format)
       python jumpcut.py --selftest        (runs scripts/tests/test_jumpcut.py on a synthetic clip)
writes: cut.mp4 (--size, 30fps, h264/aac, bt709), words_cut.json (times in the cut), edl.json (kept source ranges, seconds)
--drop removes extra source ranges (mistakes / retakes) before merging.
--silence also cuts audio silences >= --gap between words: Whisper word gaps alone miss some of them.
  auto (default) = per-file noise floor (10th pct of 20 ms RMS frames) + 8 dB, clamped to [-55, -30] dB. 0 disables.
Safety (AIEV / video-use rules): a silence overlapping a word's core [s+40ms, e-40ms] is vetoed (in Arabic, stops
  and breaths inside words read as silence); every cut is snapped to >= --pad (30-200 ms) from the neighbouring words;
  gaps < 150 ms are never cut; cuts land on frame boundaries (video and audio trimmed on the same frame, so segment
  lengths match and lip-sync can't drift); 30 ms audio fades at every cut edge.
"""
import argparse, json, math, pathlib, subprocess, sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG, FFPROBE, canvas, filter_script_args  # noqa: E402

FPS, GUARD, MIN_GAP, HOP = 30, 0.04, 0.15, 0.02


def keep_ranges(words, gap, pad, drops=(), dur=None):
    ws = [w for w in words if not any(a <= w["s"] < b for a, b in drops)]
    out = []
    for w in ws:
        s, e = max(0.0, w["s"] - pad), w["e"] + pad
        if dur:
            e = min(e, dur)
        if out and s - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    # merge overlaps created by padding
    merged = []
    for r in out:
        if merged and r[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], r[1])
        else:
            merged.append(r)
    return merged


def rms_db(src):
    """20 ms RMS frames of the mono mix, in dBFS."""
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32)
    n = int(16000 * HOP)
    x = x[:len(x) // n * n].reshape(-1, n).astype(np.float64)
    return 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)


def auto_threshold(db):
    floor = float(np.percentile(db, 10))
    return float(np.clip(floor + 8, -55, -30)), floor


def silences(db, thr, min_d):
    edges = np.flatnonzero(np.diff(np.r_[0, (db < thr).astype(int), 0]))
    return [(a * HOP, b * HOP) for a, b in zip(edges[::2], edges[1::2]) if (b - a) * HOP >= min_d]


def subtract(ranges, cuts):
    out = []
    for s, e in ranges:
        cur = s
        for a, b in sorted(cuts):
            if b <= a or b <= cur or a >= e:
                continue
            if a > cur:
                out.append([cur, a])
            cur = max(cur, b)
        if e > cur:
            out.append([cur, e])
    return out


def plan(words, dur, gap=0.3, pad=0.08, drops=(), sil=(), fps=FPS):
    """-> (kept ranges as [start_frame, end_frame], seconds of silence vetoed by the word guard)."""
    gap, pad = max(gap, MIN_GAP), min(max(pad, 0.03), 0.2)
    ws = sorted((w for w in words if not any(a <= w["s"] < b for a, b in drops)), key=lambda w: w["s"])
    cuts, vetoed = [], 0.0
    for a, b in sil:
        if any(a < w["e"] - GUARD and b > w["s"] + GUARD for w in ws):  # silence inside a word = stop/breath, not a pause
            vetoed += b - a
            continue
        prev = max((w["e"] for w in ws if w["e"] - GUARD <= a), default=-1e9)
        nxt = min((w["s"] for w in ws if w["s"] + GUARD >= b), default=1e9)
        if nxt - prev >= MIN_GAP:  # snap to the words: keep >= pad of air on both sides
            cuts.append((max(a, prev + pad), min(b, nxt - pad)))
    ranges = subtract(keep_ranges(ws, gap, pad, dur=dur), cuts)
    # a wordless sliver between two silences (click/breath) would flash as a jump; real speech is never dropped
    ranges = [r for r in ranges if r[1] - r[0] > 0.12 or any(r[0] <= w["s"] < r[1] for w in ws)]
    out, last = [], int(dur * fps + 1e-6)
    for s, e in ranges:  # grow outward to whole frames: never trims speech, video == audio length
        a, b = math.floor(s * fps + 1e-6), min(math.ceil(e * fps - 1e-6), last)
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        elif b > a:
            out.append([a, b])
    return out, vetoed


def remap(t, ranges):
    acc = 0.0
    for s, e in ranges:
        if t < s:
            return acc
        if t <= e:
            return acc + t - s
        acc += e - s
    return acc


def selftest():
    import runpy
    runpy.run_path(str(pathlib.Path(__file__).with_name("tests") / "test_jumpcut.py"), run_name="__main__")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("words", nargs="?")
    ap.add_argument("--gap", type=float, default=0.3)
    ap.add_argument("--pad", type=float, default=0.08)
    ap.add_argument("--drop", default="")
    ap.add_argument("--silence", default="auto", help="auto | dB threshold (e.g. -38) | 0 = off")
    ap.add_argument("--out", default=None)
    ap.add_argument("--size", default=None, help="WxH or 9x16/16x9 (default: profile format)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    src = pathlib.Path(a.video)
    words = json.loads(pathlib.Path(a.words).read_text(encoding="utf-8"))
    dur = float(subprocess.check_output([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)]))
    drops = [tuple(map(float, d.split("-"))) for d in a.drop.split(",") if d]
    sil = []
    if a.silence not in ("0", "0.0", "off"):
        db = rms_db(src)
        if a.silence == "auto":
            thr, floor = auto_threshold(db)
            print(f"silence threshold {thr:.1f} dB (noise floor {floor:.1f} dB = 10th pct of 20 ms RMS, +8 dB, clamp -55..-30)")
        else:
            thr = float(a.silence)
            print(f"silence threshold {thr:.1f} dB (fixed)")
        sil = silences(db, thr, max(a.gap, MIN_GAP))
    frames, vetoed = plan(words, dur, a.gap, a.pad, drops, sil)
    if sil:
        print(f"word guard vetoed {vetoed:.1f}s of {sum(e - s for s, e in sil):.1f}s detected silence (inside words)")
    ranges = [[f0 / FPS, f1 / FPS] for f0, f1 in frames]

    parts, labels = [], []
    for i, (f0, f1) in enumerate(frames):
        d = (f1 - f0) / FPS
        fd = min(0.03, d / 2)  # 30 ms kills the click at the join; clamp so both fades fit a short segment
        parts.append(f"[0:v]fps={FPS}:start_time=0,trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim=start={f0 / FPS:.6f}:end={f1 / FPS:.6f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:st=0:d={fd:.4f},afade=t=out:st={d - fd:.6f}:d={fd:.4f}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    # iPhone HDR (HLG/PQ) converted naively looks washed-out/creamy = reads as an unwanted grade (video-ad-editor v2.9 lesson)
    trc = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                          "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip().strip(",")
    # ponytail: ffmpeg mobius tonemap, close to the phone but not Apple's own converter; use Resolve's HDR->SDR if colours drift
    hdr = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv," \
        if trc in ("arib-std-b67", "smpte2084") else ""
    if hdr:
        print(f"HDR source ({trc}) -> tone-mapped to SDR bt709")
    W, H = canvas(a.size)
    fc = "".join(parts) + "".join(labels) + f"concat=n={len(frames)}:v=1:a=1[vc][ac];" \
         f"[vc]{hdr}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[vo]"
    out = pathlib.Path(a.out) if a.out else src.with_name("cut.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    fcfile = out.with_suffix(".filter.txt")
    fcfile.write_text(fc, encoding="utf-8")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(src), *filter_script_args(fcfile),
                    "-map", "[vo]", "-map", "[ac]", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",  # tagged: Resolve/browsers agree
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)], check=True)

    cut_words = [{**w, "s": round(remap(w["s"], ranges), 3), "e": round(remap(w["e"], ranges), 3)}
                 for w in words if not any(a0 <= w["s"] < b0 for a0, b0 in drops)]
    out.with_name("words_cut.json").write_text(json.dumps(cut_words, ensure_ascii=False, indent=1), encoding="utf-8")
    out.with_name("edl.json").write_text(json.dumps([[round(s, 6), round(e, 6)] for s, e in ranges]), encoding="utf-8")
    kept = sum(e - s for s, e in ranges)
    print(f"{len(ranges)} segments, {dur:.1f}s -> {kept:.1f}s ({out})")


if __name__ == "__main__":
    main()
