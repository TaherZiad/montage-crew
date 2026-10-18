"""Turn a room photo (Pexels/Unsplash, or the user's own) into a 9:16 or 16:9 background plate behind the speaker.

usage: python room.py photo.jpg out.png [--cx .5 --cy .5 --zoom 1] [--flip] [--blur 9] [--exposure .8]
                      [--sat .9] [--warm .05] [--vignette .35] [--size 1080x1920|1920x1080|9x16|16x9]
       python room.py --selftest
--zoom  = crop height / photo height (smaller = closer). Put practicals (lamps) on the key-light side (--flip).
--blur  = lens-blur disc radius in output px (phone at ~2 m: 6–12). Wall should end up 1–2 stops under the face.
"""
import argparse, pathlib, sys, tempfile

import cv2
import numpy as np

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import canvas  # noqa: E402



def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--cx", type=float, default=0.5); ap.add_argument("--cy", type=float, default=0.5)
    ap.add_argument("--zoom", type=float, default=1.0); ap.add_argument("--flip", action="store_true")
    ap.add_argument("--blur", type=int, default=9); ap.add_argument("--exposure", type=float, default=0.8)
    ap.add_argument("--sat", type=float, default=0.9); ap.add_argument("--warm", type=float, default=0.05)
    ap.add_argument("--vignette", type=float, default=0.35); ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args(argv)

    W, H = canvas(a.size)
    img = cv2.imread(a.src)
    if img is None:
        sys.exit(f"cannot read image: {a.src}")
    img = img[..., ::-1]
    if a.flip:
        img = img[:, ::-1]
    ih, iw = img.shape[:2]
    ch = min(ih, int(ih * a.zoom)); cw = int(ch * W / H)
    if cw > iw:
        cw, ch = iw, int(iw * H / W)
    x0 = int(np.clip(a.cx * iw - cw / 2, 0, iw - cw)); y0 = int(np.clip(a.cy * ih - ch / 2, 0, ih - ch))
    f = cv2.resize(img[y0:y0 + ch, x0:x0 + cw], (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    lin = f ** 2.2  # blur + exposure in linear light so lamps bloom like real bokeh
    if a.blur:
        k = np.zeros((2 * a.blur + 1,) * 2, np.float32); cv2.circle(k, (a.blur, a.blur), a.blur, 1, -1)
        lin = cv2.filter2D(lin, -1, k / k.sum())
    lin *= a.exposure * np.array([1 + a.warm, 1, 1 - a.warm], np.float32)
    f = np.clip(lin, 0, 1) ** (1 / 2.2)
    grey = f.mean(axis=2, keepdims=True); f = grey + (f - grey) * a.sat
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    f *= (1 - a.vignette * np.clip(np.hypot(x / W - 0.5, (y / H - 0.45) * 0.9) / 0.7, 0, 1) ** 2)[..., None]
    f += np.random.default_rng(3).uniform(-0.5, 0.5, f.shape).astype(np.float32) / 255
    cv2.imwrite(a.out, (np.clip(f, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))
    print("room ->", a.out, f"crop {cw}x{ch}@{x0},{y0}")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        src, out = str(pathlib.Path(d) / "p.png"), str(pathlib.Path(d) / "r.png")
        y, x = np.mgrid[0:300, 0:400]
        cv2.imwrite(src, np.dstack([x * 255 // 400, y * 255 // 300, np.full_like(x, 90)]).astype(np.uint8))
        main([src, out, "--size", "216x384", "--blur", "3"])
        assert cv2.imread(out).shape == (384, 216, 3)
        main([src, out, "--size", "16x9", "--flip"])
        assert cv2.imread(out).shape == (1080, 1920, 3)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        main()
