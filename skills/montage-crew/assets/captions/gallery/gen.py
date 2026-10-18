"""Build the caption-style gallery (a HyperFrames composition that also plays in a browser) + optional render helpers.
  python gen.py              -> index.html (uses ../../fonts, ../../gsap.min.js [CDN fallback], ../../rtl-kit.js, ../caption-styles.js)
  open index.html?play       -> plays every style in a loop in any browser (open the file locally)
  npx hyperframes@0.8.151 render  (in this folder) -> full.mp4; then optional:
  python gen.py sheet        -> gallery.jpg contact sheet from snapshots/ (+ schemes.jpg swatches; needs opencv)
  python gen.py cut full.mp4 -> previews/CAP-xx.mp4 (3.2 s loop per style)
One segment of SEG s per style, a dialect-neutral sample phrase on a neutral placeholder frame (placeholder-speaker.svg, no real person)."""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).parent
CAP = HERE.parent
SEG = 3.2
WORDS = "في دقيقة واحدة تتعلم بناء موقع".split()
KEY = 5
SNAP = 2.25  # seconds into each segment (all words out, key word active)


def styles():
    js = (CAP / "caption-styles.js").read_text(encoding="utf-8")
    sty = re.findall(r'S\("(CAP-\d+)", "([^"]+)",.*?schemes: \["(SC-\d+)"', js)
    sch = dict(re.findall(r'"(SC-\d+)": \{ name: "([^"]+)"', js))
    return sty, sch


def build():
    sty, sch = styles()
    css = (CAP / "caption-styles.css").read_text(encoding="utf-8").replace('url("fonts/', 'url("../../fonts/')
    segs, words, caps = [], [], []
    for n, (sid, name, scid) in enumerate(sty):
        S = n * SEG
        segs.append(f'''  <section id="s{n}" class="seg">
    <div class="lbl"><b>{sid}</b><span>{name}</span><em>{scid} · {sch[scid]}</em></div>
    <div id="cap{n}" class="capbox"></div>
  </section>''')
        words.append([{"w": w, "s": round(S + 0.25 + j * 0.3, 3), "e": round(S + 0.5 + j * 0.3, 3)} for j, w in enumerate(WORDS)])
        caps.append({"sid": sid, "scheme": scid, "S": S})
    dur = round(len(sty) * SEG, 2)
    html = f'''<!doctype html>
<html lang="ar">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>Caption styles gallery</title>
<script src="../../gsap.min.js"></script>
<script>window.gsap || document.write('<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js" integrity="sha256-wXS/zlOnKUGNV6ithiXnJHx5OiL++OKFHjz6PenNgoA=" crossorigin="anonymous"><' + '/script>');</script>
<script src="../../rtl-kit.js"></script>
<script src="../caption-styles.js"></script>
<style>
{css}
  html, body {{ margin: 0; background: #000; }}
  #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
  #bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; }}
  .seg {{ position: absolute; inset: 0; opacity: 0; }}
  .capbox {{ position: absolute; inset: 0; }}
  .lbl {{ position: absolute; left: 0; right: 0; top: 70px; text-align: center; color: #fff; font-family: "Montserrat", sans-serif;
    text-shadow: 0 2px 14px rgba(0,0,0,.7); }}
  .lbl b {{ display: block; font-weight: 900; font-size: 92px; letter-spacing: .02em; }}
  .lbl span {{ display: block; font-weight: 700; font-size: 50px; }}
  .lbl em {{ display: block; font-style: normal; font-weight: 500; font-size: 34px; opacity: .75; margin-top: 6px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{dur}">
  <img id="bg" src="placeholder-speaker.svg" alt="" />
{chr(10).join(segs)}
</div>
<script>
  gsap.defaults({{ lazy: false }});
  const tl = gsap.timeline({{ paused: true }});
  const SEG = {SEG}, CAPS = {json.dumps(caps)}, WORDS = {json.dumps(words, ensure_ascii=False)};
  CAPS.forEach((c, n) => {{
    tl.set("#s" + n, {{ opacity: 1 }}, c.S);
    tl.set("#s" + n, {{ opacity: 0 }}, c.S + SEG - 0.001);
    const cap = {{ i: [0, 1, 2, 3, 4, 5], key: {KEY}, t1: c.S + SEG - 0.2 }};
    CS.apply(tl, [cap], WORDS[n], c.sid, c.scheme, {{ root: "#cap" + n }});
  }});
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
  // Browser preview (open index.html?play): fit to the window and loop. Renders ignore this.
  if (location.search.indexOf("play") >= 0) {{
    document.body.style.zoom = Math.min(innerWidth / 1080, innerHeight / 1920);
    tl.eventCallback("onComplete", function () {{ tl.restart(); }});
    tl.play(0);
  }}
</script>
</body>
</html>
'''
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print("index.html", len(sty), "styles,", dur, "s; snapshot times:")
    print(",".join(str(round(n * SEG + SNAP, 3)) for n in range(len(sty))))


def sheet():
    import cv2, numpy as np
    sty, sch = styles()
    snaps = sorted((HERE / "snapshots").glob("*.png"))
    snaps = [p for p in snaps if "end" not in p.name][: len(sty)]
    cols, tw, th = 7, 360, 640
    rows = -(-len(snaps) // cols)
    out = np.full((rows * (th + 10) + 10, cols * (tw + 10) + 10, 3), 18, np.uint8)
    for k, p in enumerate(snaps):
        im = cv2.resize(cv2.imread(str(p)), (tw, th), interpolation=cv2.INTER_AREA)
        lab = f"{k + 1:02d}"
        cv2.rectangle(im, (0, 0), (92, 56), (0, 0, 0), -1)
        cv2.putText(im, lab, (10, 44), cv2.FONT_HERSHEY_DUPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
        r, c = divmod(k, cols)
        out[10 + r * (th + 10):10 + r * (th + 10) + th, 10 + c * (tw + 10):10 + c * (tw + 10) + tw] = im
    cv2.imwrite(str(HERE / "gallery.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    # colour-scheme swatches
    js = (CAP / "caption-styles.js").read_text(encoding="utf-8")
    rows_ = re.findall(r'"(SC-\d+)": \{ name: "([^"]+)", ink: "(#\w+)", acc: "(#\w+)", acc2: "(#\w+)", stk: "(#\w+)"', js)
    sw = np.full((len(rows_) * 90 + 20, 1000, 3), 24, np.uint8)
    hx = lambda h: tuple(int(h[i:i + 2], 16) for i in (5, 3, 1))
    for k, (sid, nm, ink, acc, acc2, stk) in enumerate(rows_):
        y = 10 + k * 90
        cv2.putText(sw, f"{sid} {nm}", (14, y + 52), cv2.FONT_HERSHEY_DUPLEX, 1.0, (235, 235, 235), 1, cv2.LINE_AA)
        for j, (lab, h) in enumerate([("ink", ink), ("acc", acc), ("acc2", acc2), ("stk", stk)]):
            x = 440 + j * 140
            cv2.rectangle(sw, (x, y + 6), (x + 128, y + 80), hx(h), -1)
            cv2.rectangle(sw, (x, y + 6), (x + 128, y + 80), (90, 90, 90), 1)
            cv2.putText(sw, h, (x + 8, y + 72), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0) if sum(hx(h)) > 380 else (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(str(HERE / "schemes.jpg"), sw, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("gallery.jpg", out.shape, "schemes.jpg")


def cut(full):
    sty, _ = styles()
    (HERE / "previews").mkdir(exist_ok=True)
    for n, (sid, *_r) in enumerate(sty):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(n * SEG), "-t", str(SEG), "-i", full, "-c:v", "libx264", "-crf", "22",
                        "-pix_fmt", "yuv420p", "-vf", "scale=540:960", "-an", str(HERE / "previews" / f"{sid}.mp4")], check=True)
    print("previews:", len(sty))


if __name__ == "__main__":
    a = sys.argv[1:] or ["build"]
    {"build": build, "sheet": sheet}.get(a[0], lambda: cut(a[1]))()
