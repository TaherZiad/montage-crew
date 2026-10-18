"""Simple painted-wall background lit like the footage (soft light pool, vignette, faint plaster texture).

usage: python wall.py out.png --base "#4a3a48" [--pool 1.35 --cx .42 --cy .36] [--tint "#c05a8a" --tint-side left]
       [--size 1080x1920|1920x1080|9x16|16x9] [--seed 7]
       python wall.py --selftest
Match it to the shot: pool on the side the key light's spill lands (opposite the key), wall luminance
~20–30 % (a wall 1–2 stops under the face), tint = the coloured fill seen on the shadow side of the face.
"""
import argparse, pathlib, sys, tempfile

import cv2
import numpy as np

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import canvas  # noqa: E402



def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--base", default="#4a3a48")
    ap.add_argument("--pool", type=float, default=1.35, help="brightness at the pool centre (x base)")
    ap.add_argument("--cx", type=float, default=0.42); ap.add_argument("--cy", type=float, default=0.36)
    ap.add_argument("--vignette", type=float, default=0.45)
    ap.add_argument("--tint", default=None); ap.add_argument("--tint-side", default="left")
    ap.add_argument("--tint-amt", type=float, default=0.10)
    ap.add_argument("--texture", type=float, default=0.025)
    ap.add_argument("--size", default="1080x1920"); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)

    W, H = canvas(a.size)
    hexrgb = lambda h: np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((x / W - a.cx) / 0.62, (y / H - a.cy) / 0.42)
    light = 1 + (a.pool - 1) * np.exp(-d ** 2 * 1.6)
    light *= 1 - a.vignette * np.clip((np.hypot(x / W - 0.5, (y / H - 0.45) * 1.1) - 0.35) / 0.55, 0, 1) ** 1.5
    img = hexrgb(a.base) * light[..., None]
    if a.tint:
        ramp = (1 - x / W) if a.tint_side == "left" else (x / W)
        img += hexrgb(a.tint) * (a.tint_amt * ramp ** 2 * light)[..., None]
    rng = np.random.default_rng(a.seed)
    tex = sum(cv2.resize(rng.standard_normal((max(2, H // s), max(2, W // s))).astype(np.float32), (W, H),
                         interpolation=cv2.INTER_CUBIC) * amp for s, amp in ((160, 1.0), (40, 0.5), (10, 0.25)))
    img *= (1 + a.texture * tex / 1.2)[..., None]
    img += rng.uniform(-0.5, 0.5, img.shape).astype(np.float32) / 255  # dither: no banding in 8-bit
    cv2.imwrite(a.out, (np.clip(img, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))
    print("wall ->", a.out)


def selftest():
    with tempfile.TemporaryDirectory() as d:
        out = str(pathlib.Path(d) / "w.png")
        main([out, "--base", "#3a4a5a", "--size", "216x384", "--tint", "#c05a8a"])
        im = cv2.imread(out)
        assert im.shape == (384, 216, 3), im.shape
        pool = im[int(384 * .36), int(216 * .42)].mean()
        assert pool > im[5, 5].mean() + 10, (pool, im[5, 5])          # lit pool brighter than the vignetted corner
        main([out, "--size", "16x9"])
        assert cv2.imread(out).shape == (1080, 1920, 3)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        main()
