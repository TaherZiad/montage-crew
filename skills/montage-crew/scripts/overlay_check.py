"""Automatic safe-zone QA on the RENDERED overlay layer (HyperFrames .mov ProRes 4444 alpha, or a PNG sequence).
Idea from video-ad-editor 08_safe_check.js: check what was actually drawn, not what was planned.

  python overlay_check.py overlays.mov [--zones out/zones.json] [--fps 5] [--min 300] [--size WxH]
  python overlay_check.py --selftest

Flags TEXT-like overlay pixels — opaque (alpha >= 160) AND bright (luma >= 100): soft glows, dark scrims, glass
panels and the dark split-screen bed all pass — inside:
  - PLATFORM UI (zones.py: 9:16 top 290 · bottom 440 · sides 120 · button column 190 for y 700-1480;
                16:9 top 90 · bottom 150 · sides 60) — the canvas is the overlay's own size
  - HEAD of the speaker for that shot (zones.json head_bbox from zones.py) — skip this for text-BEHIND-speaker layers
Frames where > 50 % of the screen is opaque (flash, wipe, full-frame card) are skipped.
Prints the offending time ranges per zone; exit 3 on any breach (like 08_safe_check), 0 when clean.
"""
import argparse, json, pathlib, subprocess, sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cp1256 console
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import zones  # same measured numbers as the planning step
from mc_profile import FFMPEG, canvas

S = 2  # analysis downscale
W, H = 1080, 1920
w, h = W // S, H // S


def configure(width, height):
    global W, H, w, h
    zones.set_size(width, height)
    W, H, w, h = zones.W, zones.H, zones.W // S, zones.H // S


def ui_mask():
    return zones.ui_mask(h, w, S)


def breaches(alpha, t, ui, shots, min_px, luma=None):
    """[(zone, px)] for one frame (alpha/luma: h×w uint8)."""
    if (alpha >= 160).mean() > 0.5:
        return []
    on = (alpha >= 160) & (luma >= 100 if luma is not None else True)
    if on.mean() > 0.5:
        return []
    out = []
    if (n := int((on & ui).sum()) * S * S) >= min_px:
        out.append(("platform-UI", n))
    for sh in shots:
        if sh["start"] <= t < sh["end"] and sh.get("head_bbox"):
            x0, y0, x1, y1 = (v // S for v in sh["head_bbox"])
            if (n := int(on[y0:y1, x0:x1].sum()) * S * S) >= min_px:
                out.append((f"head(shot {sh['shot']})", n))
    return out


def frames(src, fps):
    cmd = [FFMPEG, "-v", "error", "-i", str(src), "-vf", f"fps={fps},scale={w}:{h},format=yuva444p",
           "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    i = 0
    while buf := p.stdout.read(4 * w * h):  # planes Y U V A
        if len(buf) < 4 * w * h:
            break
        pl = np.frombuffer(buf, np.uint8).reshape(4, h, w)
        yield i / fps, pl[3], pl[0]
        i += 1
    if p.wait():
        sys.exit("❌ ffmpeg could not read an alpha channel — render overlays with alpha (--format mov / png-sequence)")


def selftest():
    configure(1920, 1080)
    ui = ui_mask()
    a = np.zeros((h, w), np.uint8); a[500 // S:560 // S, 600 // S:1300 // S] = 255
    assert breaches(a, 1.0, ui, [], 300) == []
    a[1000 // S:1060 // S, 600 // S:1300 // S] = 255           # over the progress bar
    assert breaches(a, 1.0, ui, [], 300)[0][0] == "platform-UI"
    configure(1080, 1920)
    ui = ui_mask()
    a = np.zeros((h, w), np.uint8)
    a[600 // S:700 // S, 300 // S:700 // S] = 255          # caption-band text: fine
    assert breaches(a, 1.0, ui, [], 300) == []
    a[1700 // S:1760 // S, 300 // S:700 // S] = 255         # under the IG caption/audio bar
    assert breaches(a, 1.0, ui, [], 300)[0][0] == "platform-UI"
    b = np.zeros((h, w), np.uint8); b[400 // S:520 // S, 400 // S:680 // S] = 255
    shots = [{"shot": 1, "start": 0, "end": 2, "head_bbox": [380, 300, 700, 700]}]
    assert breaches(b, 1.0, ui, shots, 300)[0][0] == "head(shot 1)" and breaches(b, 3.0, ui, shots, 300) == []
    assert breaches(np.full((h, w), 255, np.uint8), 1.0, ui, shots, 300) == []  # full-frame flash skipped
    c = np.zeros((h, w), np.uint8); c[1500 // S:, :] = 255                    # dark bed under a split screen
    assert breaches(c, 1.0, ui, [], 300, luma=np.full((h, w), 20, np.uint8)) == []
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("overlay", nargs="?")
    ap.add_argument("--zones")
    ap.add_argument("--fps", type=float, default=5)
    ap.add_argument("--min", type=int, default=300, help="px (full-res) before a zone counts as breached")
    ap.add_argument("--at", type=float, default=0.0, help="timeline start of a trimmed per-beat file (zones use global time)")
    ap.add_argument("--size", help="WxH (default: the overlay's own size)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.overlay:
        return selftest()
    configure(*(canvas(a.size) if a.size else zones.probe_size(a.overlay)))
    shots = json.load(open(a.zones)) if a.zones else []
    ui, hits = ui_mask(), {}
    for t, alpha, luma in frames(a.overlay, a.fps):
        t += a.at
        for zone, n in breaches(alpha, t, ui, shots, a.min, luma):
            hits.setdefault(zone, []).append((t, n))
    if not hits:
        print("✅ overlays clear of platform UI" + (" and the speaker's head" if shots else "")); return
    for zone, ev in hits.items():
        spans, cur = [], [ev[0][0], ev[0][0], ev[0][1]]
        for t, n in ev[1:]:
            if t - cur[1] <= 1.5 / a.fps:
                cur[1], cur[2] = t, max(cur[2], n)
            else:
                spans.append(cur); cur = [t, t, n]
        spans.append(cur)
        print(f"❌ {zone}: " + " · ".join(f"{s:.1f}-{e:.1f}s ({n}px)" for s, e, n in spans))
    sys.exit(3)


if __name__ == "__main__":
    main()
