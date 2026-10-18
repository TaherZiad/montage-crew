"""Safe zone / danger zone map per shot, from the speaker matte + the framing plan.

  python zones.py speaker.mov shots.json out_dir [--presets presets.json] [--fps 4] [--margin 40] [--size WxH|9x16|16x9]
  python zones.py --selftest
Canvas: 9:16 (1080x1920) or 16:9 (1920x1080) — by default the speaker layer's own size.

speaker.mov : RGBA speaker layer (matte.py output) on the SAME timeline as shots.json
shots.json  : [[start_s, end_s, kind], ...]   kind = key of a framing preset
presets     : {"M": {"zoom": 1, "anchor": [540, 960]}, ...}  zoom about the anchor point (the point that stays fixed)
              defaults: M 100 % · C 118 % at the eyes · W 86 % bottom-anchored · P 50 % parked bottom-right (PiP)

DANGER (never put text/graphics here):
  - HEAD: every pixel the head occupies at any moment of the shot, after that shot's framing, + margin
    (the head is the silhouette above the shoulders; the torso is fine to cover - chest band graphics are normal)
  - PLATFORM UI 9:16: top 290 px, bottom 440 px, 120 px both sides, 190 px both sides for y 700-1480 (button column)
    PLATFORM UI 16:9: top 90 px (title bar), bottom 150 px (progress bar + controls), 60 px both sides
  - ZOOM CROP (only for graphics baked INTO the footage layer): outside the region still visible at the
    tightest framing used in the video (overlay tracks above the speaker are not zoomed, so they don't need it)
SAFE: the largest free rectangles in the top band, the chest band and both side gutters.
Writes zones.json + one <shot>_zones.png per shot (red = danger, green = safe) and prints a table.
"""
import argparse, json, pathlib, subprocess, sys

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG, FFPROBE, canvas  # noqa: E402

W, H = 1080, 1920
UI_9X16 = {"top": 290, "bottom": 440, "side": 120, "buttons": 190, "buttons_y": (700, 1480)}  # measured, craft/09 §3
UI_16X9 = {"top": 90, "bottom": 150, "side": 60, "buttons": 0, "buttons_y": (0, 0)}  # title bar, progress bar + controls
UI, DEFAULT_PRESETS = {}, {}


def set_size(w, h):
    """Switch every module-level number (canvas, platform UI, framing presets) to a 9:16 or 16:9 canvas."""
    global W, H
    W, H = int(w), int(h)
    UI.clear()
    UI.update(UI_9X16 if H > W else UI_16X9)
    k = W / 1080 if H > W else 1.0
    DEFAULT_PRESETS.clear()
    DEFAULT_PRESETS.update({
        "M": {"zoom": 1.0, "anchor": [W // 2, H // 2]},
        "C": {"zoom": 1.18, "anchor": [W // 2, round(H * 0.349)]},   # punch-in at the eyes
        "W": {"zoom": 0.86, "anchor": [W // 2, H]},                   # wide, bottom-anchored
        "P": {"zoom": 0.50, "anchor": [W - round(60 * k), H]},        # parked bottom-right (PiP)
    })


set_size(W, H)


def ui_mask(h, w, s):
    """Platform-UI danger mask at analysis scale s (h, w = canvas / s)."""
    ui = np.zeros((h, w), bool)
    ui[: UI["top"] // s] = True; ui[h - UI["bottom"] // s:] = True
    ui[:, : UI["side"] // s] = True; ui[:, w - UI["side"] // s:] = True
    by0, by1 = UI["buttons_y"][0] // s, UI["buttons_y"][1] // s  # like/comment/share column, mirrored on Arabic phones
    if UI["buttons"]:
        ui[by0:by1, : UI["buttons"] // s] = True; ui[by0:by1, w - UI["buttons"] // s:] = True
    return ui


def probe_size(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0:s=x", str(path)], capture_output=True, text=True).stdout.strip()
    return tuple(int(v) for v in out.split("x")[:2]) if "x" in out else (W, H)


def alpha_frames(path, fps, s):
    """Low-res alpha frames (s = downscale factor) with their timestamps."""
    w, h = W // s, H // s
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h},format=yuva444p,extractplanes=a",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    raw = r.stdout
    n = len(raw) // (w * h)
    if not n:
        raise SystemExit(f"no alpha frames from {path}: {r.stderr.decode(errors='replace')[:400]}")
    return np.frombuffer(raw[: n * w * h], np.uint8).reshape(n, h, w), np.arange(n) / fps


def head_mask(a):
    """Head + beard + neck: silhouette rows from the top down to the shoulder line, limited to a central column
    as wide as the head (so shoulder slopes and raised hands beside the face are not counted as head).
    Shoulders/torso are NOT danger - the chest band is the normal place for graphics."""
    m = a > 127
    rows = np.where(m.any(1))[0]
    if not len(rows):
        return np.zeros_like(m)
    y0 = rows[0]
    h = m.shape[0]
    widths = m.sum(1).astype(float)
    b0, b1 = y0 + int(0.03 * h), y0 + int(0.12 * h)  # forehead..cheeks
    band = widths[b0:b1]
    head_w = np.median(band[band > 0]) if (band > 0).any() else widths[rows].max()
    y_sh = next((y for y in range(b1, rows[-1]) if widths[y] > 1.7 * head_w), rows[-1])
    centres = [np.where(m[y])[0].mean() for y in range(b0, b1) if m[y].any()]
    cx = np.median(centres) if centres else m.shape[1] / 2
    x0, x1 = int(max(0, cx - 0.6 * head_w)), int(min(m.shape[1], cx + 0.6 * head_w))
    out = np.zeros_like(m)
    out[y0:y_sh, x0:x1] = m[y0:y_sh, x0:x1]
    return out


def reframe(mask, zoom, anchor, s):
    ax, ay = anchor[0] / s, anchor[1] / s
    M = np.float32([[zoom, 0, ax - ax * zoom], [0, zoom, ay - ay * zoom]])
    return cv2.warpAffine(mask.astype(np.uint8) * 255, M, (mask.shape[1], mask.shape[0]), flags=cv2.INTER_NEAREST) > 0


def largest_rect(free):
    """Largest axis-aligned all-True rectangle (histogram method). Returns x, y, w, h."""
    h, w = free.shape
    heights = np.zeros(w, int)
    best = (0, 0, 0, 0, 0)
    for y in range(h):
        heights = np.where(free[y], heights + 1, 0)
        stack = []
        for x in range(w + 1):
            cur = heights[x] if x < w else 0
            start = x
            while stack and stack[-1][1] >= cur:
                sx, sh = stack.pop()
                area = sh * (x - sx)
                if area > best[0]:
                    best = (area, sx, y - sh + 1, x - sx, sh)
                start = sx
            stack.append((start, cur))
    return best[1:]


def main():
    ap = argparse.ArgumentParser()
    if "--selftest" in sys.argv:
        return selftest()
    ap.add_argument("speaker"); ap.add_argument("shots"); ap.add_argument("out")
    ap.add_argument("--size", help="WxH or 9x16/16x9 (default: the speaker layer's size)")
    ap.add_argument("--presets"); ap.add_argument("--fps", type=float, default=4)
    ap.add_argument("--margin", type=int, default=40, help="px kept clear around the head (full-res)")
    ap.add_argument("--scale", type=int, default=4, help="analysis downscale")
    a = ap.parse_args()
    set_size(*(canvas(a.size) if a.size else probe_size(a.speaker)))
    s = a.scale
    presets = {**DEFAULT_PRESETS, **(json.load(open(a.presets)) if a.presets else {})}
    shots = json.load(open(a.shots))
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    frames, ts = alpha_frames(a.speaker, a.fps, s)
    h, w = H // s, W // s
    ui = ui_mask(h, w, s)
    k = max(1, a.margin // s)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
    result = []
    for i, (t0, t1, kind) in enumerate(shots):
        p = presets[kind]
        idx = [j for j, t in enumerate(ts) if t0 <= t < t1] or [int(np.argmin(np.abs(ts - (t0 + t1) / 2)))]
        head = np.zeros((h, w), bool)
        body = np.zeros((h, w), bool)
        for j in idx:
            head |= reframe(head_mask(frames[j]), p["zoom"], p["anchor"], s)
            body |= reframe(frames[j] > 127, p["zoom"], p["anchor"], s)
        head = cv2.dilate(head.astype(np.uint8), kernel) > 0
        danger = head | ui
        free = ~danger
        ys, xs = np.where(head)
        hb = (int(xs.min()) * s, int(ys.min()) * s, int(xs.max()) * s, int(ys.max()) * s) if len(xs) else None
        bands = {}
        if hb:
            regions = {  # gutters only beside the head (above the neck); chest from the neck down
                "top": (0, 0, w, hb[1] // s),
                "chest": (0, hb[3] // s, w, h),
                "right_gutter": (hb[2] // s, 0, w, hb[3] // s),
                "left_gutter": (0, 0, hb[0] // s, hb[3] // s),
            }
        else:
            regions = {"all": (0, 0, w, h)}
        for name, (x0, y0, x1, y1) in regions.items():
            sub = np.zeros_like(free); sub[y0:y1, x0:x1] = free[y0:y1, x0:x1]
            x, y, rw, rh = largest_rect(sub)
            if rw * rh:
                bands[name] = {"x": int(x) * s, "y": int(y) * s, "w": int(rw) * s, "h": int(rh) * s}
        shot = {"shot": i + 1, "start": t0, "end": t1, "kind": kind, "head_bbox": hb, "safe": bands,
                "body_covers_pct": round(100 * body.mean(), 1)}
        result.append(shot)
        # visual: body silhouette grey, danger red, safe rectangles green
        vis = np.full((h, w, 3), 40, np.uint8)
        vis[body] = (110, 110, 110)
        vis[danger] = (vis[danger] * 0.4 + np.array([0, 0, 200]) * 0.6).astype(np.uint8)
        for name, r in bands.items():
            cv2.rectangle(vis, (r["x"] // s, r["y"] // s), ((r["x"] + r["w"]) // s - 1, (r["y"] + r["h"]) // s - 1), (60, 220, 60), 1)
            cv2.putText(vis, name, (r["x"] // s + 3, r["y"] // s + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (60, 220, 60), 1)
        cv2.putText(vis, f"{i + 1} {kind} {t0:.1f}-{t1:.1f}s", (4, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.imwrite(str(out / f"{i + 1:02d}_{kind}_zones.png"), vis)
    json.dump(result, open(out / "zones.json", "w"), indent=1)
    for r in result:
        best = max(r["safe"].items(), key=lambda kv: kv[1]["w"] * kv[1]["h"]) if r["safe"] else ("-", {})
        print(f"shot {r['shot']:2d} {r['kind']} {r['start']:6.2f}-{r['end']:6.2f}  head {r['head_bbox']}  "
              + "  ".join(f"{n}:{v['w']}x{v['h']}@{v['x']},{v['y']}" for n, v in r["safe"].items()))
    # contact sheet of all shots
    tiles = [cv2.imread(str(p)) for p in sorted(out.glob("*_zones.png"))]
    if tiles:
        cols = 8
        tiles += [np.zeros_like(tiles[0])] * (-len(tiles) % cols)
        cv2.imwrite(str(out / "zones_sheet.png"), np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)]))


def selftest():
    # synthetic speaker: a head (ellipse) on shoulders, alpha only -> the head bbox, UI and safe bands must make sense
    for size in ((1080, 1920), (1920, 1080)):
        set_size(*size)
        s = 4
        h, w = H // s, W // s
        a = np.zeros((h, w), np.uint8)
        cx, top = w // 2, h // 4
        cv2.ellipse(a, (cx, top + h // 12), (w // 14 if H > W else w // 24, h // 12), 0, 0, 360, 255, -1)  # head
        a[top + h // 6:, cx - w // 4: cx + w // 4] = 255                                                    # torso
        hm = head_mask(a)
        ys, xs = np.where(hm)
        assert len(xs) and ys.min() >= top - 2 and ys.max() < top + h // 6 + 4, (size, ys.min(), ys.max())
        ui = ui_mask(h, w, s)
        assert ui[0, w // 2] and ui[h - 1, w // 2] and not ui[h // 2, w // 2]
        assert ui[h // 2, 1] and ui[h // 2, w - 2]
        x, y, rw, rh = largest_rect(~(ui | hm))
        assert rw * rh > 0.15 * w * h, (size, rw, rh)
        z = reframe(hm, DEFAULT_PRESETS["C"]["zoom"], DEFAULT_PRESETS["C"]["anchor"], s)
        assert z.sum() > hm.sum()  # punch-in makes the head bigger
    set_size(1080, 1920)
    print("selftest ok")


if __name__ == "__main__":
    main()
