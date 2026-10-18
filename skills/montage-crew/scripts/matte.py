"""Speaker matte with RobustVideoMatting (ONNX): temporally stable, hair-level edges (u2net flickers on video).
Optional background replacement in the same pass: contact shadow on the new wall, light wrap, matched grain.

usage: python matte.py <in.mp4> <out.mov> [--bg wall.png --comp comp.mp4] [--skin 0.7] [--start S] [--dur D]
       python matte.py speaker.mov out2.mov --rgba-in --bg other.png [--comp comp2.mp4] [--speed 1.1]
             (no AI pass: bake light wrap for a new background into the RGBA layer, optional retime)
                       [--shadow "-45,25,28,0.28"] [--wrap 0.35] [--grain 1.1] [--ratio 0.25] [--size 1080x1920|16x9]
                       [--cpu | --gpu]
       python matte.py --selftest
writes: out.mov  ProRes 4444, straight alpha (speaker only, retouched; edge colours from RVM's foreground estimate,
                 no old-wall halo; no light wrap, so it can go over any background)
        comp.mp4 speaker over --bg with light wrap (H.264 CRF 13) — the A-roll for the edit
skin   = retouch strength 0–1: skin mask by YCrCb, edge-preserving smoothing, pores added back.
         Excludes hair/beard/eyes/shirt; check the mask on each new shoot.
shadow = dx,dy,blur,opacity in px: push it AWAY from the key light (key frame-right → dx negative).
         Plain wall right behind the speaker only; a room plate (wall metres away) gets "0,0,1,0".
device = CUDA when onnxruntime-gpu sees an NVIDIA card (install with --gpu), else CPU (≈2–6 fps at 1080p; slow but fine).
model  = rvm_mobilenetv3_fp32.onnx (RobustVideoMatting, GPL-3.0, 15 MB), downloaded + SHA-256 checked on first use.
Screen recordings never need this (no speaker to cut out).
"""
import argparse, os, pathlib, queue, subprocess, sys, tempfile, threading, time

import cv2
import numpy as np

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG, canvas  # noqa: E402

A = None  # parsed args
W = H = 0


def session(model, cpu):
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count(); so.log_severity_level = 3
    providers = ["CPUExecutionProvider"]
    if not cpu and "CUDAExecutionProvider" in ort.get_available_providers():
        if os.name == "nt":  # a torch CUDA wheel in the same venv carries cuBLAS/cuDNN
            try:
                import torch
                os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
            except Exception:
                pass
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    return ort.InferenceSession(str(model), so, providers=providers)


def run(sess, img, rec, ratio):
    src = img.transpose(2, 0, 1)[None].astype(np.float32) / 255
    fgr, pha, *rec = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                                     "downsample_ratio": ratio})
    return fgr[0].transpose(1, 2, 0), pha[0, 0], rec


def retouch(img, f):
    m = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb), (76, 136, 88), (245, 184, 130)).astype(np.float32) / 255
    m = cv2.GaussianBlur(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), (0, 0), 5)
    base = cv2.bilateralFilter(cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA), 11, 28, 8)
    base = cv2.resize(base, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    smooth = base + (f - cv2.GaussianBlur(f, (0, 0), 1.0)) * 0.55  # keep pores
    return f + (smooth - f) * (m * A.skin)[..., None]


def composite(fg, alpha, i, bgset):
    BG, BG_SOFT, SHIFT, sb, so_ = bgset
    a3 = alpha[..., None]
    shadow = cv2.GaussianBlur(cv2.warpAffine(alpha, SHIFT, (W, H)), (0, 0), sb) * so_
    bg = BG * (1 - shadow[..., None])
    bg += np.random.default_rng(i).normal(0, A.grain / 255, (H, W, 1)).astype(np.float32)
    wrap = (1 - cv2.GaussianBlur(alpha, (0, 0), 12))[..., None] * A.wrap
    fg = fg + (BG_SOFT - fg) * wrap
    return fg, fg * a3 + bg * (1 - a3)


def writer(p, pack):
    """Pack + write in a background thread: blocking pipe writes on Windows serialised the loop (2.3 -> ~6 fps)."""
    q = queue.Queue(maxsize=6)

    def loop():
        while (item := q.get()) is not None:
            p.stdin.write(pack(*item))
    th = threading.Thread(target=loop, daemon=True); th.start()
    return q, th


def pack_rgba(fg, al):
    return np.dstack([(np.clip(fg, 0, 1) * 255 + 0.5).astype(np.uint8), (al * 255 + 0.5).astype(np.uint8)]).tobytes()


def pack_rgb(c):
    return (np.clip(c, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()


def main(argv=None):
    global A, W, H
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out", nargs="?")
    ap.add_argument("--rgba-in", action="store_true", help="src is a speaker .mov from an earlier run")
    ap.add_argument("--bg"); ap.add_argument("--comp")
    ap.add_argument("--shadow", default="-45,25,28,0.28"); ap.add_argument("--wrap", type=float, default=0.35)
    ap.add_argument("--skin", type=float, default=0)
    ap.add_argument("--grain", type=float, default=1.1, help="bg grain std in 8-bit levels (match the footage's flat-wall noise)")
    ap.add_argument("--ratio", type=float, default=0.25, help="0.25 for HD/1080p, 0.4 for 720p")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=0)
    ap.add_argument("--size", default=None, help="WxH or 9x16/16x9 (default: the profile's format)")
    ap.add_argument("--fps", default="30")
    ap.add_argument("--speed", type=float, default=1.0, help="retime (frames dropped/duplicated to --fps)")
    ap.add_argument("--cpu", action="store_true", help="force CPU")
    ap.add_argument("--gpu", action="store_true", help="prefer CUDA (the default already uses it when available)")
    ap.add_argument("--model", default=None, help=argparse.SUPPRESS)
    A = a = ap.parse_args(argv)
    W, H = canvas(a.size)
    sess = None
    if not a.rgba_in:
        model = a.model
        if not model:
            import fetch_assets
            model = fetch_assets.ensure_rvm()
        sess = session(model, a.cpu)
        print("matte on", sess.get_providers()[0])
    C = 4 if a.rgba_in else 3
    ratio = np.array([a.ratio], np.float32)

    vf = (f"setpts=PTS/{a.speed},fps={a.fps}," if a.speed != 1 else "") + \
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    dec = ([FFMPEG, "-v", "error"] + (["-ss", str(a.start)] if a.start else []) + ["-i", a.src]
           + (["-t", str(a.dur)] if a.dur else [])
           + ["-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgba" if a.rgba_in else "rgb24", "-"])
    raw_in = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-s", f"{W}x{H}", "-r", a.fps]
    p_in = subprocess.Popen(dec, stdout=subprocess.PIPE)
    p_out = a.out and subprocess.Popen(raw_in + ["-pix_fmt", "rgba", "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444",
                                       "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuva444p10le,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0",
                                       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", a.out],
                                       stdin=subprocess.PIPE)
    p_comp = a.comp and subprocess.Popen(raw_in + ["-pix_fmt", "rgb24", "-i", "-", "-c:v", "libx264", "-crf", "13",
                                                   "-preset", "medium", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                                                   "-color_trc", "bt709", "-colorspace", "bt709", a.comp], stdin=subprocess.PIPE)
    bgset = None
    if a.bg:
        bgimg = cv2.imread(a.bg)
        if bgimg is None:
            sys.exit(f"cannot read background: {a.bg}")
        BG = cv2.resize(bgimg[..., ::-1], (W, H)).astype(np.float32) / 255
        sx, sy, sb, so_ = map(float, a.shadow.split(","))
        bgset = (BG, cv2.GaussianBlur(BG, (0, 0), 25), np.float32([[1, 0, sx], [0, 1, sy]]), sb, so_)

    def frames():
        n = W * H * C
        while len(buf := p_in.stdout.read(n)) == n:
            yield np.frombuffer(buf, np.uint8).reshape(H, W, C)

    q_out = p_out and writer(p_out, pack_rgba)
    q_comp = p_comp and writer(p_comp, pack_rgb)
    it = frames()
    head = [] if a.rgba_in else [f for _, f in zip(range(15), it)]
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    for f in head:  # warm the recurrent state so frame 0 is as clean as frame 15
        rec = run(sess, f, rec, ratio)[2]

    t0, count = time.time(), 0
    for img in [*head, *it]:
        if a.rgba_in:
            fg, alpha = img[..., :3].astype(np.float32) / 255, img[..., 3].astype(np.float32) / 255
        else:
            fgr, alpha, rec = run(sess, img, rec, ratio)
            edge = ((alpha > 0.02) & (alpha < 0.98))[..., None]
            fg = img.astype(np.float32) / 255
            if a.skin:
                fg = retouch(img, fg)
            fg = np.where(edge, fgr, fg)
        if bgset:
            fgw, comp = composite(fg, alpha, count, bgset)
            if a.rgba_in:
                fg = fgw  # re-composite mode: the RGBA layer carries the wrap for this background
            if q_comp:
                q_comp[0].put((comp,))
        if q_out:
            q_out[0].put((fg, alpha))
        count += 1
        if count % 300 == 0:
            print(f"{count} frames, {count / (time.time() - t0):.1f} fps", flush=True)
    for p, q in ((p_out, q_out), (p_comp, q_comp)):
        if p:
            q[0].put(None); q[1].join(); p.stdin.close(); p.wait()
    p_in.wait()
    print(f"{count} frames -> {a.out or ''}{' + ' + a.comp if a.comp else ''} ({count / max(time.time() - t0, 1e-6):.1f} fps)")
    return count


def selftest():
    """Offline. Re-composite path always (no model needed); the AI pass too when the model is already on disk."""
    import fetch_assets
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        src, rgba, bg = d / "src.mp4", d / "spk.mov", d / "bg.png"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x406080:s=216x384:r=30:d=1",
                        "-vf", "drawbox=x=70:y=80:w=76:h=300:c=0xd0a080:t=fill", "-pix_fmt", "yuv420p", str(src)], check=True)
        cv2.imwrite(str(bg), np.full((384, 216, 3), (40, 60, 90), np.uint8))
        # a hand-made RGBA speaker (box = person) -> re-composite over a new background, with retime
        fr = np.zeros((384, 216, 4), np.uint8); fr[80:380, 70:146] = (0xd0, 0xa0, 0x80, 255)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "216x384", "-r", "30", "-i", "-",
                        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(rgba)],
                       input=fr.tobytes() * 30, check=True)
        n = main([str(rgba), str(d / "o.mov"), "--rgba-in", "--bg", str(bg), "--comp", str(d / "c.mp4"), "--size", "216x384",
                  "--speed", "1.25"])
        assert 22 <= n <= 26, n
        ok, fr = cv2.VideoCapture(str(d / "c.mp4")).read()
        assert ok and abs(int(fr[200, 108, 2]) - 0xd0) < 25 and abs(int(fr[200, 10, 0]) - 40) < 15, (fr[200, 108], fr[200, 10])
        model = fetch_assets.PINS["rvm"]["name"]
        have = [p for p in (fetch_assets.models_dir() / "rvm" / model, pathlib.Path.home() / ".cache" / "rvm" / model)
                if p.is_file() and fetch_assets.is_verified(p, fetch_assets.PINS["rvm"]["sha256"])]
        if have:
            main([str(src), str(d / "m.mov"), "--size", "216x384", "--cpu", "--ratio", "0.4", "--model", str(have[0])])
            info = subprocess.run([FFMPEG, "-hide_banner", "-i", str(d / "m.mov")], capture_output=True, text=True).stderr
            assert "yuva444p" in info, info
        else:
            print("(RVM model not downloaded yet: AI pass skipped)")
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        main()
