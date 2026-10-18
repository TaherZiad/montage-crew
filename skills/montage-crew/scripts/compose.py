"""Final render WITHOUT any editor: layers -> one MP4 (ffmpeg, bt709 in and out), plus an FCP7 XML timeline of the
same layers that DaVinci Resolve and Premiere Pro both import.

  python compose.py <work> --format 9x16|16x9 --out <output_dir>/<name> [--xml] [--ae] [--layers-out]
                    [--layers FILE] [--sfx FILE] [--dur S] [--fps 30] [--no-master]
  python compose.py --selftest            renders a 3 s demo from synthetic inputs and checks picture, sound and XML

Inputs
  <work>/_team/layers.json (or --layers): [{"layer": "plate|behind|aroll|speaker|split|captions|motion|voice|music|<extra>",
      "file": "<work-relative or absolute>", "at": s, "in": s (opt), "dur": s (opt), ...options}]
    track order (bottom -> top): plate, behind, aroll/speaker, split, captions, motion, then any other name (extra tracks,
    in list order). Audio: voice (if none, the aroll's own sound is the voice), music.
    options per item: "fit": "cover" (default) | "contain";
                      "zoom": {"segments": [...]} or a work-relative framing.json — hold {"s","e","z"[,"tx","ty"]} or
                              eased move {"s","e","z0","z1"[,"tx0","tx1","ty0","ty1"]}, s/e in TIMELINE seconds,
                              ty + = image up; "anchor": [x, y] = the canvas point that stays fixed (default centre);
                      "fade_in" / "fade_out": s (alpha fades);
                      audio: "gain_db" (voice 0, music -18), "duck": true (music dips under the voice, default on)
  <work>/audio/sfx_cues.json (or --sfx): [{"file", "start", "gain_db"}]   file = absolute, work- or skill-relative
Outputs
  <out>.mp4  1080x1920 or 1920x1080, H.264 yuv420p bt709 (tagged), AAC 48 kHz, mastered to -14 LUFS / <= -1.5 dBTP
             (master.py; --no-master keeps the raw mix)
  --xml: <out>/project/timeline.xml (xmeml v4) + <out>/project/media/ (copies of every file it uses)
         Resolve: File > Import > Timeline · Premiere: File > Import. Eased zooms become linear keyframes there.
  --ae:  <out>/project/ae_import.jsx + <out>/project/media/ — After Effects: File > Scripts > Run Script File. One comp at
         the format/fps, every layer and sound placed at its start/duration, zooms as linear scale/position keys.
         The script only imports and builds (no file writing, no network; no AE preference needs changing).
  --layers-out: <out>/project/layers/NN_<layer>_<name>.<ext> numbered bottom -> top (video, then audio) + order.txt
         (file, start s, end s, track) + layers.csv — for CapCut / Final Cut: put each file at its start on its own track.
  All exports use the same track layout (overlapping items of one layer go to extra tracks).
"""
import argparse, json, math, os, pathlib, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from urllib.parse import quote

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mc_profile  # noqa: E402
from mc_profile import FFMPEG, FFPROBE, canvas, filter_script_args  # noqa: E402

URL_PREFIX = "file:" + "//localhost/"  # split on purpose (privacy-grep false positive)
ORDER = {"plate": 1, "behind": 2, "aroll": 3, "speaker": 3, "split": 4, "captions": 5, "motion": 6}
AUDIO = ("voice", "music")
STILL = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
MATRIX = {"bt709": "bt709", "smpte170m": "bt601", "bt470bg": "bt601", "bt2020nc": "bt2020", "bt2020c": "bt2020",
          "smpte240m": "smpte240m", "fcc": "fcc"}


# ── probing ────────────────────────────────────────────────────────────────
def probe(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,width,height,color_space,color_range,color_transfer,nb_frames",
                        "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"❌ cannot read {path}: {r.stderr.strip()[:200]}")
    js = json.loads(r.stdout or "{}")
    v = next((s for s in js.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"dur": float(js.get("format", {}).get("duration") or 0), "w": v.get("width"), "h": v.get("height"),
            "audio": any(s.get("codec_type") == "audio" for s in js.get("streams", [])),
            "video": bool(v), "space": v.get("color_space"), "range": v.get("color_range"), "trc": v.get("color_transfer")}


def still(path):
    return pathlib.Path(path).suffix.lower() in STILL


# ── spec ───────────────────────────────────────────────────────────────────
def resolve_file(f, work):
    p = pathlib.Path(f).expanduser()
    for cand in ([p] if p.is_absolute() else [pathlib.Path(work) / p, mc_profile.SKILL_DIR / p]):
        if cand.is_file():
            return cand.resolve()
    raise SystemExit(f"❌ missing file: {f}")


def load_items(work, layers_file, sfx_file):
    work = pathlib.Path(work)
    lf = pathlib.Path(layers_file) if layers_file else work / "_team" / "layers.json"
    items = json.loads(lf.read_text(encoding="utf-8-sig"))
    if not isinstance(items, list):
        raise SystemExit("❌ layers.json must be a list of {layer, file, at, ...}")
    out = []
    for n, it in enumerate(items):
        if not isinstance(it, dict) or "layer" not in it or "file" not in it:
            raise SystemExit(f"❌ layers.json item {n}: needs layer + file")
        it = {"at": 0.0, "in": 0.0, **it}
        it["path"] = resolve_file(it["file"], work)
        it["info"] = probe(it["path"])
        z = it.get("zoom")
        if isinstance(z, str):
            it["zoom"] = json.loads(resolve_file(z, work).read_text(encoding="utf-8-sig"))
        if isinstance(it.get("zoom"), list):
            it["zoom"] = {"segments": it["zoom"]}
        it["seq"] = n
        out.append(it)
    sf = pathlib.Path(sfx_file) if sfx_file else work / "audio" / "sfx_cues.json"
    sfx = []
    if sf.is_file():
        for c in json.loads(sf.read_text(encoding="utf-8-sig")):
            sfx.append({**c, "path": resolve_file(c["file"], work), "start": float(c["start"])})
    return out, sfx


def item_len(it, total=None):
    """seconds the item occupies on the timeline."""
    if it.get("dur"):
        return float(it["dur"])
    if still(it["path"]):
        return max(0.0, (total or 0) - float(it["at"]))
    return max(0.0, it["info"]["dur"] - float(it["in"]))


def timeline_len(items, sfx):
    ends = [float(i["at"]) + item_len(i) for i in items if not still(i["path"]) or i.get("dur")]
    ends += [c["start"] + probe(c["path"])["dur"] for c in sfx]
    return max(ends or [0.0])


# ── zoom expressions ───────────────────────────────────────────────────────
def _ease(x):
    return f"if(lt({x},0.5),4*pow({x},3),1-pow(-2*{x}+2,3)/2)"


def curve(segs, key, default):
    """ffmpeg expression in t (timeline seconds) for z / tx / ty from hold+move segments."""
    def ends(sg):
        if key in sg:
            return float(sg[key]), float(sg[key])
        a = float(sg.get(key + "0", sg.get(key, default)))
        return a, float(sg.get(key + "1", a))
    if not segs:
        return f"{default}"
    segs = sorted(segs, key=lambda s: float(s["s"]))
    expr = f"{ends(segs[-1])[1]}"
    for sg in reversed(segs):
        s, e = float(sg["s"]), float(sg["e"])
        a, b = ends(sg)
        x = f"clip((t-{s})/{max(e - s, 1e-3)},0,1)"
        seg = f"{a}" if a == b else f"({a}+({b}-({a}))*{_ease(x)})"
        expr = f"if(lt(t,{e}),{seg},{expr})"
    return f"if(lt(t,{float(segs[0]['s'])}),{ends(segs[0])[0]},{expr})"


def value_at(segs, key, default, t):
    """the same curve in Python (XML keyframes + tests)."""
    def ends(sg):
        if key in sg:
            return float(sg[key]), float(sg[key])
        a = float(sg.get(key + "0", sg.get(key, default)))
        return a, float(sg.get(key + "1", a))
    if not segs:
        return default
    segs = sorted(segs, key=lambda s: float(s["s"]))
    if t < float(segs[0]["s"]):
        return ends(segs[0])[0]
    for sg in segs:
        if t < float(sg["e"]):
            a, b = ends(sg)
            x = min(max((t - float(sg["s"])) / max(float(sg["e"]) - float(sg["s"]), 1e-3), 0), 1)
            return a + (b - a) * (4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2)
    return ends(segs[-1])[1]


# ── render ─────────────────────────────────────────────────────────────────
def matrix_for(info):
    m = MATRIX.get(info.get("space") or "")
    if not m:  # untagged: HD and up is bt709 in practice (phones, HyperFrames, screen recorders)
        m = "bt709" if (info.get("h") or 0) >= 720 or (info.get("w") or 0) >= 1280 else "bt601"
    rng = "full" if info.get("range") == "pc" else "tv"
    return m, rng


def build(items, sfx, W, H, fps, D):
    """-> (input args, filter graph text, video label, audio label)."""
    args, fc, k = [], [], 0
    vis = sorted([i for i in items if i["layer"] not in AUDIO and i["info"]["video"]],
                 key=lambda i: (ORDER.get(i["layer"], 7), i["seq"] if i["layer"] in ORDER else 0, i["seq"]))
    fc.append(f"color=c=black:s={W}x{H}:r={fps}:d={D:.3f},format=rgba[base0]")
    cur = "base0"
    voice_from_aroll = not any(i["layer"] == "voice" for i in items)
    abus = []  # (label, kind)
    for it in vis:
        ln = item_len(it, D)
        if ln <= 0:
            continue
        p = str(it["path"])
        if still(p):
            args += ["-loop", "1", "-framerate", str(fps), "-t", f"{ln:.3f}", "-i", p]
        else:
            args += (["-ss", f"{float(it['in']):.3f}"] if float(it["in"]) else []) + ["-t", f"{ln:.3f}", "-i", p]
        m, rng = matrix_for(it["info"])
        if it["info"].get("trc") in ("smpte2084", "arib-std-b67"):
            print(f"⚠️ {pathlib.Path(p).name} is HDR: run it through jumpcut.py first (tone-maps to SDR bt709)")
        at = float(it["at"])
        fit = "decrease" if it.get("fit") == "contain" else "increase"
        crop = f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black@0" if fit == "decrease" else f"crop={W}:{H}"
        chain = [f"fps={fps}"] if not still(p) else []
        chain += [f"scale={W}:{H}:force_original_aspect_ratio={fit}:flags=lanczos:in_color_matrix={m}:in_range={rng}",
                  "format=rgba", crop, f"setpts=PTS-STARTPTS+{at:.6f}/TB"]
        if it.get("fade_in"):
            chain.append(f"fade=t=in:st={at:.3f}:d={float(it['fade_in']):.3f}:alpha=1")
        if it.get("fade_out"):
            chain.append(f"fade=t=out:st={at + ln - float(it['fade_out']):.3f}:d={float(it['fade_out']):.3f}:alpha=1")
        segs = (it.get("zoom") or {}).get("segments") or []
        ax, ay = it.get("anchor") or [W / 2, H / 2]
        if segs:
            z, tx, ty = curve(segs, "z", 1.0), curve(segs, "tx", 0.0), curve(segs, "ty", 0.0)
            chain.append(f"scale=w='max(2,2*trunc({W}*({z})/2))':h='max(2,2*trunc({H}*({z})/2))':eval=frame:flags=bicubic")
            x, y = f"{ax}-{ax}*({z})+({tx})", f"{ay}-{ay}*({z})-({ty})"
        else:
            x, y = "0", "0"
        fc.append(f"[{k}:v]" + ",".join(chain) + f"[v{k}]")
        fc.append(f"[{cur}][v{k}]overlay=x='{x}':y='{y}':eval=frame:eof_action=pass:format=rgb[base{k + 1}]")
        cur = f"base{k + 1}"
        if it["layer"] == "aroll" and voice_from_aroll and it["info"]["audio"]:
            fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                      f"adelay={int(round(at * 1000))}:all=1,volume={float(it.get('gain_db', 0))}dB[a{k}]")
            abus.append((f"a{k}", "voice"))
        k += 1
    fc.append(f"[{cur}]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv,trim=duration={D:.3f}[vout]")

    for it in [i for i in items if i["layer"] in AUDIO]:
        if not it["info"]["audio"]:
            continue
        ln = item_len(it, D)
        args += (["-ss", f"{float(it['in']):.3f}"] if float(it["in"]) else []) + ["-t", f"{ln:.3f}", "-vn", "-i", str(it["path"])]
        g = float(it.get("gain_db", 0 if it["layer"] == "voice" else -18))
        fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                  f"adelay={int(round(float(it['at']) * 1000))}:all=1,volume={g}dB[a{k}]")
        abus.append((f"a{k}", it["layer"] + ("" if it.get("duck", True) else "_noduck")))
        k += 1
    for c in sfx:
        args += ["-i", str(c["path"])]
        fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={float(c.get('gain_db', 0))}dB,"
                  f"adelay={int(round(c['start'] * 1000))}:all=1[a{k}]")
        abus.append((f"a{k}", "sfx"))
        k += 1

    voices = [l for l, kd in abus if kd == "voice"]
    music = [l for l, kd in abus if kd == "music"]
    rest = [l for l, kd in abus if kd not in ("voice", "music")]
    mix = []
    if voices:
        fc.append("".join(f"[{l}]" for l in voices) + f"amix=inputs={len(voices)}:normalize=0:duration=longest,"
                  f"asplit=2[vox][vsc]" if len(voices) > 1 else f"[{voices[0]}]asplit=2[vox][vsc]")
        mix.append("vox")
    if music:
        fc.append("".join(f"[{l}]" for l in music) + (f"amix=inputs={len(music)}:normalize=0:duration=longest[mus]"
                                                      if len(music) > 1 else "anull[mus]"))
        if voices:  # duck the bed under the voice
            fc.append("[mus][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[musd]")
            mix.append("musd")
        else:
            mix.append("mus")
    elif voices:
        fc.append("[vsc]anullsink")
    mix += rest
    if mix:
        fc.append("".join(f"[{l}]" for l in mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,"
                  f"apad=whole_dur={D:.3f},atrim=duration={D:.3f}[aout]")
    else:
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={D:.3f}[aout]")
    return args, ";\n".join(fc), bool(mix)


def render(work, fmt, out, layers_file=None, sfx_file=None, dur=None, fps=30, do_master=True):
    W, H = canvas(fmt)
    items, sfx = load_items(work, layers_file, sfx_file)
    D = float(dur) if dur else timeline_len(items, sfx)
    if D <= 0:
        raise SystemExit("❌ nothing to render: no timed layer (give --dur for stills only)")
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    args, graph, has_audio = build(items, sfx, W, H, fps, D)
    final = out.with_suffix(".mp4") if out.suffix != ".mp4" else out
    raw = final.with_name(final.stem + ".premaster.mp4") if do_master and has_audio else final
    with tempfile.TemporaryDirectory() as td:
        gf = pathlib.Path(td) / "graph.txt"
        gf.write_text(graph, encoding="utf-8")
        cmd = [FFMPEG, "-v", "error", "-y", *args, *filter_script_args(gf), "-map", "[vout]", "-map", "[aout]",
               "-r", str(fps), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
               "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{D:.3f}", "-movflags", "+faststart", str(raw)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            (out.parent / (final.stem + ".graph.txt")).write_text(graph, encoding="utf-8")
            raise SystemExit(f"❌ ffmpeg failed (graph saved next to the output):\n{r.stderr[-1500:]}")
    if raw != final:
        import master
        master.master(str(raw), str(final))
        raw.unlink()
    print(f"✅ {final}  {W}x{H} {D:.2f}s ({len(items)} layers, {len(sfx)} sfx)")
    return final, items, sfx, D, (W, H)


# ── FCP7 XML (xmeml v4) ────────────────────────────────────────────────────
def _url(p):
    p = pathlib.Path(p).resolve().as_posix()
    return URL_PREFIX + quote(p.lstrip("/"), safe="/:")


def _sub(parent, tag, text=None, **attr):
    e = ET.SubElement(parent, tag, {k: str(v) for k, v in attr.items()})
    if text is not None:
        e.text = str(text)
    return e


def _rate(parent, fps):
    r = _sub(parent, "rate")
    _sub(r, "timebase", fps); _sub(r, "ntsc", "FALSE")


def copy_media(paths, media_dir):
    """copies (hard links when possible) into media_dir; returns {source: copy}."""
    media_dir.mkdir(parents=True, exist_ok=True)
    out, used = {}, set()
    for src in paths:
        if src in out:
            continue
        name, n = src.name, 1
        while name.lower() in used:
            name = f"{src.stem}_{n}{src.suffix}"; n += 1
        used.add(name.lower())
        dst = media_dir / name
        if dst.exists():
            dst.unlink()
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        out[src] = dst
    return out


def plan(items, sfx, D, fps):
    """The NLE track layout shared by every export: (video lanes bottom->top, audio lanes), each lane a list of
    {item, path, info, layer, rec_in, rec_out, n, src_in, db} in frames. Items of one layer group that overlap in
    time go to extra lanes (an NLE track can't stack)."""
    N = int(round(D * fps))
    entry = lambda it, path, info, layer, a, n, src_in, db=0.0: {"item": it, "path": path, "info": info, "layer": layer,
                                                                 "rec_in": a, "rec_out": min(a + n, N), "n": n,
                                                                 "src_in": src_in, "db": db}

    def pack(seq):
        lanes = []
        for e in seq:
            lane = next((l for l in lanes if l[0] <= e["rec_in"]), None)
            if lane is None:
                lane = [0, []]; lanes.append(lane)
            lane[0] = e["rec_in"] + e["n"]
            lane[1].append(e)
        return [l[1] for l in lanes]

    vis = sorted([i for i in items if i["layer"] not in AUDIO and i["info"]["video"]],
                 key=lambda i: (ORDER.get(i["layer"], 7), i["seq"] if i["layer"] in ORDER else 0, i["seq"]))
    groups = {}
    for it in vis:
        groups.setdefault(ORDER.get(it["layer"], 7 + it["seq"]), []).append(it)
    vtracks = []
    for key in sorted(groups):
        seq = []
        for it in sorted(groups[key], key=lambda i: (float(i["at"]), i["seq"])):
            n = int(round(item_len(it, D) * fps))
            if n > 0:
                seq.append(entry(it, it["path"], it["info"], it["layer"], int(round(float(it["at"]) * fps)), n,
                                 int(round(float(it["in"]) * fps))))
        vtracks += pack(seq)
    atracks = []
    voice = [i for i in items if i["layer"] == "voice"] or [i for i in items if i["layer"] == "aroll" and i["info"]["audio"]]
    for group, default_db in ((voice, 0.0), ([i for i in items if i["layer"] == "music"], -18.0)):
        lane = [entry(it, it["path"], it["info"], it["layer"], int(round(float(it["at"]) * fps)),
                      int(round(item_len(it, D) * fps)), int(round(float(it["in"]) * fps)),
                      float(it.get("gain_db", default_db if it["layer"] != "aroll" else 0)))
                for it in group if it["info"]["audio"]]
        if group:
            atracks.append(lane)
    seq = []
    for c in sorted(sfx, key=lambda c: c["start"]):
        info = probe(c["path"])
        seq.append(entry(c, c["path"], info, "sfx", int(round(c["start"] * fps)), max(1, int(math.ceil(info["dur"] * fps))),
                         0, float(c.get("gain_db", 0))))
    return vtracks, atracks + pack(seq)


def export_xml(items, sfx, D, W, H, fps, xml_path, name="montage-crew"):
    xml_path = pathlib.Path(xml_path)
    media = copy_media([i["path"] for i in items] + [c["path"] for c in sfx], xml_path.parent / "media")
    N = int(round(D * fps))
    root = ET.Element("xmeml", version="4")
    seq = _sub(root, "sequence", id="sequence-1")
    _sub(seq, "name", name); _sub(seq, "duration", N); _rate(seq, fps)
    tc = _sub(seq, "timecode"); _rate(tc, fps); _sub(tc, "string", "00:00:00:00"); _sub(tc, "frame", 0)
    _sub(tc, "displayformat", "NDF")
    med = _sub(seq, "media")
    vid = _sub(med, "video")
    sc = _sub(_sub(vid, "format"), "samplecharacteristics")
    _rate(sc, fps); _sub(sc, "width", W); _sub(sc, "height", H); _sub(sc, "anamorphic", "FALSE")
    _sub(sc, "pixelaspectratio", "square"); _sub(sc, "fielddominance", "none")
    aud = _sub(med, "audio")
    _sub(aud, "numOutputChannels", 2)
    asc = _sub(_sub(aud, "format"), "samplecharacteristics"); _sub(asc, "depth", 16); _sub(asc, "samplerate", 48000)

    files, ids = {}, {"clip": 0}

    def file_el(parent, it_path, info, length_frames):
        if it_path in files:
            return _sub(parent, "file", id=files[it_path])
        fid = files[it_path] = f"file-{len(files) + 1}"
        f = _sub(parent, "file", id=fid)
        copy = media[it_path]
        _sub(f, "name", copy.name); _sub(f, "pathurl", _url(copy)); _rate(f, fps); _sub(f, "duration", length_frames)
        m = _sub(f, "media")
        if info.get("video"):
            vsc = _sub(_sub(m, "video"), "samplecharacteristics")
            _rate(vsc, fps); _sub(vsc, "width", info.get("w") or W); _sub(vsc, "height", info.get("h") or H)
        if info.get("audio"):
            a = _sub(m, "audio")
            s2 = _sub(a, "samplecharacteristics"); _sub(s2, "depth", 16); _sub(s2, "samplerate", 48000)
            _sub(a, "channelcount", 2)
        return f

    def clip(track, it_path, info, rec_in, rec_out, src_in, kind, filters=None):
        ids["clip"] += 1
        c = _sub(track, "clipitem", id=f"clipitem-{ids['clip']}")
        flen = max(int(round(info["dur"] * fps)), src_in + rec_out - rec_in) if info["dur"] else src_in + rec_out - rec_in
        _sub(c, "name", media[it_path].name); _sub(c, "enabled", "TRUE"); _sub(c, "duration", flen); _rate(c, fps)
        _sub(c, "start", rec_in); _sub(c, "end", rec_out); _sub(c, "in", src_in); _sub(c, "out", src_in + rec_out - rec_in)
        if still(it_path):
            _sub(c, "stillframe", "TRUE")
        file_el(c, it_path, info, flen)
        for f in filters or []:
            c.append(f)
        st = _sub(c, "sourcetrack"); _sub(st, "mediatype", kind); _sub(st, "trackindex", 1)
        return c

    def motion(it, rec_in, src_in, n):
        """Basic Motion: scale (% of source) + centre offset, keyframed at segment edges (linear between)."""
        info = it["info"]
        sw, sh = info.get("w") or W, info.get("h") or H
        fitk = (min if it.get("fit") == "contain" else max)(W / sw, H / sh)
        segs = (it.get("zoom") or {}).get("segments") or []
        ax, ay = it.get("anchor") or [W / 2, H / 2]
        times = sorted({rec_in, rec_in + n - 1} | {int(round(float(s[k]) * fps)) for s in segs for k in ("s", "e")
                                                     if rec_in <= round(float(s[k]) * fps) < rec_in + n})
        eff = ET.Element("filter")
        e = _sub(eff, "effect")
        _sub(e, "name", "Basic Motion"); _sub(e, "effectid", "basic"); _sub(e, "effectcategory", "motion")
        _sub(e, "effecttype", "motion"); _sub(e, "mediatype", "video")
        ps = _sub(e, "parameter"); _sub(ps, "parameterid", "scale"); _sub(ps, "name", "Scale")
        _sub(ps, "valuemin", 0); _sub(ps, "valuemax", 1000)
        pc = _sub(e, "parameter"); _sub(pc, "parameterid", "center"); _sub(pc, "name", "Center")
        for fr in times:
            t = fr / fps
            z = value_at(segs, "z", 1.0, t)
            dx = (ax - W / 2) * (1 - z) + value_at(segs, "tx", 0.0, t)
            dy = (ay - H / 2) * (1 - z) - value_at(segs, "ty", 0.0, t)
            when = fr - rec_in + src_in
            k1 = _sub(ps, "keyframe"); _sub(k1, "when", when); _sub(k1, "value", round(100 * fitk * z, 3))
            k2 = _sub(pc, "keyframe"); _sub(k2, "when", when)
            v = _sub(k2, "value"); _sub(v, "horiz", round(dx / W, 5)); _sub(v, "vert", round(dy / H, 5))
        _sub(ps, "value", round(100 * fitk * value_at(segs, "z", 1.0, rec_in / fps), 3))
        return eff

    def level(db):
        eff = ET.Element("filter")
        e = _sub(eff, "effect")
        _sub(e, "name", "Audio Levels"); _sub(e, "effectid", "audiolevels"); _sub(e, "effectcategory", "audiolevels")
        _sub(e, "effecttype", "audiolevels"); _sub(e, "mediatype", "audio")
        p = _sub(e, "parameter"); _sub(p, "parameterid", "level"); _sub(p, "name", "Level")
        _sub(p, "valuemin", 0); _sub(p, "valuemax", 3.98109); _sub(p, "value", round(10 ** (db / 20), 5))
        return eff

    vtracks, atracks = plan(items, sfx, D, fps)
    for lane in vtracks:
        tr = _sub(vid, "track")
        for e in lane:
            clip(tr, e["path"], e["info"], e["rec_in"], e["rec_out"], e["src_in"], "video",
                 [motion(e["item"], e["rec_in"], e["src_in"], e["n"])])
        _sub(tr, "enabled", "TRUE"); _sub(tr, "locked", "FALSE")
    for lane in atracks:
        tr = _sub(aud, "track")
        for e in lane:
            clip(tr, e["path"], e["info"], e["rec_in"], e["rec_out"], e["src_in"], "audio", [level(e["db"])])
        _sub(tr, "enabled", "TRUE"); _sub(tr, "locked", "FALSE")

    ET.indent(root)
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(xml_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n')
        f.write(ET.tostring(root, encoding="utf-8"))
    print(f"✅ {xml_path} ({ids['clip']} clips, media in {xml_path.parent / 'media'})")
    return xml_path


def check_xml(xml_path):
    """structural check: [] when fine, else problems."""
    errs = []
    root = ET.parse(xml_path).getroot()
    if root.tag != "xmeml":
        return ["root is not xmeml"]
    seq = root.find("sequence")
    N = int(seq.findtext("duration"))
    defined = {f.get("id"): f for f in root.iter("file") if f.find("pathurl") is not None}
    for c in root.iter("clipitem"):
        s, e, i, o = (int(c.findtext(k)) for k in ("start", "end", "in", "out"))
        if not (0 <= s < e <= N) or o - i != e - s:
            errs.append(f"{c.get('id')}: bad times start {s} end {e} in {i} out {o}")
        f = c.find("file")
        if f is None or f.get("id") not in defined:
            errs.append(f"{c.get('id')}: file reference missing")
    for tr in root.iter("track"):
        spans = sorted((int(c.findtext("start")), int(c.findtext("end"))) for c in tr.findall("clipitem"))
        if any(b[0] < a[1] for a, b in zip(spans, spans[1:])):
            errs.append("two clips overlap on one track")
    for fid, f in defined.items():
        url = f.findtext("pathurl")
        from urllib.parse import unquote
        p = unquote(url[len(URL_PREFIX):]) if url.startswith(URL_PREFIX) else None
        if os.name != "nt" and p:
            p = "/" + p
        if not p or not os.path.isfile(p):
            errs.append(f"{fid}: media not found at {url}")
    if seq.find("media/video/track") is None:
        errs.append("no video track")
    return errs


# ── After Effects (ExtendScript) + plain layer export (CapCut / Final Cut) ──
AE_JSX = r'''// montage-crew -> After Effects: File > Scripts > Run Script File..., pick this file.
// It imports the files in media/ next to it and builds one comp. It never writes files or uses the network.
(function () {
    var NAME = @@NAME@@, W = @@W@@, H = @@H@@, FPS = @@FPS@@, DUR = @@DUR@@;
    // bottom -> top: [file, layer, start s, source in s, duration s, still, gain dB or null, [[t, scale %, x, y]] or null]
    var L = [
@@ROWS@@
    ];
    var here = new File($.fileName).parent;
    app.beginUndoGroup("montage-crew import");
    var folder = app.project.items.addFolder(NAME);
    var comp = app.project.items.addComp(NAME, W, H, 1, DUR, FPS);
    comp.parentFolder = folder;
    var cache = {}, missing = [];
    for (var i = 0; i < L.length; i++) {
        var r = L[i], src = cache[r[0]];
        if (!src) {
            var f = new File(here.fsName + "/" + r[0]);
            if (!f.exists) { missing.push(r[0]); continue; }
            src = cache[r[0]] = app.project.importFile(new ImportOptions(f));
            src.parentFolder = folder;
        }
        var lay = comp.layers.add(src);
        lay.name = r[1];
        lay.startTime = r[5] ? r[2] : r[2] - r[3];
        lay.inPoint = r[2];
        lay.outPoint = r[2] + r[4];
        if (lay.hasAudio) {
            if (r[6] === null) { lay.audioEnabled = false; }
            else { lay.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([r[6], r[6]]); }
        }
        if (r[7]) {
            var tg = lay.property("ADBE Transform Group"), sc = tg.property("ADBE Scale"), po = tg.property("ADBE Position");
            for (var k = 0; k < r[7].length; k++) {
                var q = r[7][k];
                if (r[7].length == 1) { sc.setValue([q[1], q[1]]); po.setValue([q[2], q[3]]); }
                else { sc.setValueAtTime(q[0], [q[1], q[1]]); po.setValueAtTime(q[0], [q[2], q[3]]); }
            }
        }
    }
    app.endUndoGroup();
    comp.openInViewer();
    if (missing.length) { alert("montage-crew: missing next to this script:\n" + missing.join("\n")); }
})();
'''
JSX_FORBIDDEN = ("system.callSystem", "File.execute", ".execute(", "$.evalFile", "eval(", "app.scheduleTask", "Socket",
                 "app.executeCommand", "#include", ".open(")


def jsx_str(s):
    """The ONLY way a value enters the jsx: a JSON string literal, ASCII-only (\\uXXXX), safe in ES3."""
    return json.dumps(str(s), ensure_ascii=True)


def jsx_forbidden(js):
    """forbidden calls in the CODE (string literals blanked first: a layer named "system.callSystem" is only data)."""
    code = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', js)
    return [w for w in JSX_FORBIDDEN if w in code]


def jsx_num(x):
    x = float(x)
    return repr(round(x, 4)) if math.isfinite(x) else "0"


def ae_keys(e, W, H, fps):
    """[(t, scale %, x, y)] at the same times the XML keys use (segment edges); one entry = a static transform."""
    it, info = e["item"], e["info"]
    sw, sh = info.get("w") or W, info.get("h") or H
    fitk = (min if it.get("fit") == "contain" else max)(W / sw, H / sh)
    segs = (it.get("zoom") or {}).get("segments") or []
    ax, ay = it.get("anchor") or [W / 2, H / 2]
    a, n = e["rec_in"], e["n"]
    frames = sorted({a} | ({a + n - 1} if segs else set()) |
                    {int(round(float(s[k]) * fps)) for s in segs for k in ("s", "e") if a <= round(float(s[k]) * fps) < a + n})
    out = []
    for fr in frames:
        t = fr / fps
        z = value_at(segs, "z", 1.0, t)
        dx = (ax - W / 2) * (1 - z) + value_at(segs, "tx", 0.0, t)
        dy = (ay - H / 2) * (1 - z) - value_at(segs, "ty", 0.0, t)
        out.append((t, 100 * fitk * z, W / 2 + dx, H / 2 + dy))
    return out


def export_ae(items, sfx, D, W, H, fps, jsx_path, name="montage-crew"):
    jsx_path = pathlib.Path(jsx_path)
    mdir = jsx_path.parent / "media"
    media = copy_media([i["path"] for i in items] + [c["path"] for c in sfx], mdir)
    vtracks, atracks = plan(items, sfx, D, fps)
    # a video layer whose sound is also on an audio lane (the a-roll as voice) keeps its sound in AE; others are muted
    heard = {(id(e["item"])): e["db"] for lane in atracks for e in lane}
    rows = []
    for lane, is_video in [(l, True) for l in vtracks] + [(l, False) for l in atracks]:
        for e in lane:
            if not is_video and any(x["item"] is e["item"] for l in vtracks for x in l):
                continue
            copy = media[e["path"]]
            if copy.parent.resolve() != mdir.resolve() or not copy.is_file():
                raise SystemExit(f"❌ AE export: {copy} is not in {mdir}")
            keys = "[" + ", ".join("[" + ", ".join(jsx_num(v) for v in k) + "]" for k in ae_keys(e, W, H, fps)) + "]" \
                if is_video else "null"
            db = jsx_num(heard[id(e["item"])]) if id(e["item"]) in heard else ("null" if is_video else jsx_num(e["db"]))
            rows.append("        [" + ", ".join([jsx_str("media/" + copy.name), jsx_str(e["layer"]), jsx_num(e["rec_in"] / fps),
                                                 jsx_num(e["src_in"] / fps), jsx_num((e["rec_out"] - e["rec_in"]) / fps),
                                                 "true" if still(e["path"]) else "false", db, keys]) + "]")
    js = AE_JSX
    for k, v in (("@@NAME@@", jsx_str(name)), ("@@W@@", str(int(W))), ("@@H@@", str(int(H))), ("@@FPS@@", jsx_num(fps)),
                 ("@@DUR@@", jsx_num(D)), ("@@ROWS@@", ",\n".join(rows))):
        js = js.replace(k, v)
    bad = jsx_forbidden(js)
    if bad:
        raise SystemExit(f"❌ AE export: forbidden call in the jsx: {bad}")
    jsx_path.parent.mkdir(parents=True, exist_ok=True)
    jsx_path.write_bytes(js.encode("ascii"))
    print(f"✅ {jsx_path} ({len(rows)} layers, media in {mdir})")
    return jsx_path


def export_layers(items, sfx, D, fps, out_dir):
    """<out_dir>/NN_<layer>_<name>.<ext> numbered bottom -> top (video, then audio) + order.txt + layers.csv."""
    import csv, re
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vtracks, atracks = plan(items, sfx, D, fps)
    rows, n = [], 0
    for kind, lanes in (("video", vtracks), ("audio", atracks)):
        for ti, lane in enumerate(lanes, 1):
            for e in lane:
                n += 1
                safe = lambda s: re.sub(r"[^\w.-]+", "_", str(s)).strip("._")[:40] or "x"
                dst = out_dir / f"{n:02d}_{safe(e['layer'])}_{safe(pathlib.Path(e['path']).stem)}{pathlib.Path(e['path']).suffix.lower()}"
                if dst.exists():
                    dst.unlink()
                try:
                    os.link(e["path"], dst)
                except OSError:
                    shutil.copy2(e["path"], dst)
                rows.append({"file": dst.name, "kind": kind, "track": f"{kind[0].upper()}{ti}",
                             "start_s": round(e["rec_in"] / fps, 3), "end_s": round(e["rec_out"] / fps, 3),
                             "source_in_s": round(e["src_in"] / fps, 3), "gain_db": e["db"] if kind == "audio" else ""})
    (out_dir / "order.txt").write_text(
        "# bottom -> top. file<TAB>start s<TAB>end s<TAB>track. Place each file at its start on its own track.\n" +
        "".join(f"{r['file']}\t{r['start_s']:.3f}\t{r['end_s']:.3f}\t{r['track']}\n" for r in rows), encoding="utf-8")
    with open(out_dir / "layers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["file"])
        w.writeheader(); w.writerows(rows)
    print(f"✅ {out_dir} ({len(rows)} files + order.txt + layers.csv)")
    return out_dir


# ── selftest ───────────────────────────────────────────────────────────────
def _frame(path, t, W, H):
    import numpy as np
    raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t}", "-i", str(path), "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(int)


def selftest():
    import numpy as np
    with tempfile.TemporaryDirectory() as d:
        work = pathlib.Path(d) / "work"
        (work / "_team").mkdir(parents=True); (work / "audio").mkdir()
        run = lambda *a, **k: subprocess.run([FFMPEG, "-v", "error", "-y", *a], check=True, **k)
        clay, sky = (0xD9, 0x77, 0x57), (0x33, 0x66, 0x99)
        import cv2
        cv2.imwrite(str(work / "plate.png"), np.full((1920, 1080, 3), clay[::-1], np.uint8))
        run("-f", "lavfi", "-i", "color=c=0x336699:s=540x960:r=30:d=3.5", "-f", "lavfi",
            "-i", "aevalsrc='0.3*sin(2*PI*440*t)*(0.6+0.4*sin(2*PI*3*t))':s=48000:d=3.5",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-c:a", "aac", "-shortest", str(work / "aroll.mp4"))
        spk = np.zeros((960, 540, 4), np.uint8); spk[300:700, 170:370] = (0xE0, 0xC0, 0xA0, 255)  # opaque box = "speaker"
        cap = np.zeros((960, 540, 4), np.uint8); cap[100:160, 120:420] = (255, 255, 255, 255)        # caption bar
        for name, fr, secs in (("speaker.mov", spk, 3), ("captions.mov", cap, 1)):
            run("-f", "rawvideo", "-pix_fmt", "rgba", "-s", "540x960", "-r", "30", "-i", "-", "-c:v", "prores_ks",
                "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(work / name), input=fr.tobytes() * (30 * secs))
        run("-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*1500*t)*exp(-40*t)':s=48000:d=0.25", str(work / "audio" / "click.wav"))
        run("-f", "lavfi", "-i", "aevalsrc='0.2*sin(2*PI*220*t)':s=44100:d=3", str(work / "audio" / "music.wav"))
        layers = [
            {"layer": "plate", "file": "plate.png", "at": 0},
            {"layer": "aroll", "file": "aroll.mp4", "at": 0, "anchor": [1020, 1860],          # PiP that grows
             "zoom": {"segments": [{"s": 0, "e": 1.0, "z": 0.3}, {"s": 1.0, "e": 1.6, "z0": 0.3, "z1": 0.45},
                                   {"s": 1.6, "e": 3, "z": 0.45}]}},
            {"layer": "speaker", "file": "speaker.mov", "at": 0},
            {"layer": "captions", "file": "captions.mov", "at": 1.0, "fade_in": 0.1},
            {"layer": "music", "file": "audio/music.wav", "at": 0, "gain_db": -20},
        ]
        (work / "_team" / "layers.json").write_text(json.dumps(layers), encoding="utf-8")
        (work / "audio" / "sfx_cues.json").write_text(json.dumps([{"file": "audio/click.wav", "start": 1.0, "gain_db": -6}]),
                                                      encoding="utf-8")
        out = pathlib.Path(d) / "out" / "demo"
        final, items, sfx, D, (W, H) = render(work, "9x16", out, dur=3.0)
        info = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                               "stream=codec_name,width,height,pix_fmt,color_space,color_primaries,color_transfer,sample_rate:"
                               "format=duration", "-of", "json", str(final)], capture_output=True, text=True).stdout
        js = json.loads(info)
        v = next(s for s in js["streams"] if s["codec_name"] == "h264")
        a = next(s for s in js["streams"] if s["codec_name"] == "aac")
        assert (v["width"], v["height"], v["pix_fmt"]) == (1080, 1920, "yuv420p"), v
        assert v.get("color_space") == "bt709" and v.get("color_primaries") == "bt709" and v.get("color_transfer") == "bt709", v
        assert a["sample_rate"] == "48000" and abs(float(js["format"]["duration"]) - 3.0) < 0.1, js
        f0, f2 = _frame(final, 0.5, W, H), _frame(final, 2.5, W, H)
        near = lambda px, rgb, tol=6: all(abs(int(c) - x) <= tol for c, x in zip(px, rgb))
        assert near(f0[300, 100], clay), f0[300, 100]                      # plate: bt709 in/out keeps the colour
        assert near(f0[1100, 540], (0xE0, 0xC0, 0xA0)), f0[1100, 540]       # speaker alpha layer
        assert near(f0[480, 540], clay), f0[480, 540]                       # outside the speaker = plate (alpha works)
        assert near(f0[1850, 1000], sky), f0[1850, 1000]                    # the PiP a-roll in its corner
        f15 = _frame(final, 1.5, W, H)
        assert not near(f0[260, 540], (255, 255, 255), 30) and near(f15[260, 540], (255, 255, 255), 8)  # caption 1.0-2.0 s
        assert not near(f2[260, 540], (255, 255, 255), 30)
        pip = lambda f: int((np.abs(f - np.array(sky)) < 12).all(axis=2).sum(axis=1).max())
        assert 1.35 < pip(f2) / pip(f0) < 1.65, (pip(f0), pip(f2))         # zoom 0.30 -> 0.45
        import master
        i, tp = master.meas(str(final))
        assert abs(i + 14) <= 0.3 and tp <= -1.4, (i, tp)
        x = export_xml(items, sfx, D, W, H, 30, out / "project" / "timeline.xml")
        errs = check_xml(x)
        assert not errs, errs
        root = ET.parse(x).getroot()
        assert len(root.findall("sequence/media/video/track")) == 4 and len(root.findall("sequence/media/audio/track")) == 3
        assert int(root.findtext("sequence/duration")) == 90
        # After Effects jsx: hostile names stay inert string data, forbidden calls absent, valid JS (node --check)
        hostile = ['");system.callSystem("calc");//', chr(92), "a" + chr(10) + "b", "*/", "x" + chr(0x2028) + "y",
                   "<script>alert(1)</script>", "Taher عربي mixed", "'; app.quit(); '"]
        items2 = items + [dict(items[3], layer=h, seq=100 + k) for k, h in enumerate(hostile)]
        jsx = export_ae(items2, sfx, D, W, H, 30, out / "project" / "ae_import.jsx", hostile[0])
        js = jsx.read_text(encoding="ascii")
        assert not jsx_forbidden(js) and jsx_forbidden('x;' + 'system.callSystem("calc")')
        assert jsx_forbidden(js.replace("app.endUndoGroup();", "File.execute();")), "the guard sees code"
        assert all(jsx_str(h) in js for h in hostile) and "media/aroll.mp4" in js and "media/music.wav" in js
        assert js.count("media/aroll.mp4") == 1, "a-roll imported once (its sound rides on the video layer)"
        assert len(re.findall(r"^\s+\[\"media/", js, re.M)) == 4 + len(hostile) + 2, js  # 4 video + hostile + music + click
        node = mc_profile.tool("node")
        if os.path.isfile(node):
            chk = pathlib.Path(d) / "ae_check.js"   # node --check refuses the .jsx extension
            shutil.copyfile(jsx, chk)
            r = subprocess.run([node, "--check", str(chk)], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            rt = pathlib.Path(d) / "rt.js"
            rt.write_text("var a = [" + ", ".join(jsx_str(h) for h in hostile) + "]; process.stdout.write(JSON.stringify(a));",
                          encoding="ascii")
            got = subprocess.run([node, str(rt)], capture_output=True, text=True, encoding="utf-8").stdout
            assert json.loads(got) == hostile, got
        # CapCut / Final Cut: numbered layer files + order.txt + layers.csv
        lay = export_layers(items, sfx, D, 30, out / "project" / "layers")
        order = [l.split("\t") for l in (lay / "order.txt").read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
        assert [o[0] for o in order][:4] == ["01_plate_plate.png", "02_aroll_aroll.mp4", "03_speaker_speaker.mov",
                                            "04_captions_captions.mov"], order
        assert len(order) == 7 and order[3][1] == "1.000" and all((lay / o[0]).is_file() for o in order), order
        assert (lay / "layers.csv").read_text(encoding="utf-8").startswith("file,kind,track,start_s")
        # 16:9 from the same layers (contain-fit plate is fine; just size + duration)
        final16, *_ = render(work, "16x9", pathlib.Path(d) / "out" / "demo16", dur=1.0, do_master=False)
        p16 = probe(final16)
        assert (p16["w"], p16["h"]) == (1920, 1080) and abs(p16["dur"] - 1.0) < 0.1, p16
        # unit checks
        segs = [{"s": 1, "e": 2, "z0": 1, "z1": 2}]
        assert value_at(segs, "z", 1, 0.5) == 1 and value_at(segs, "z", 1, 1.5) == 1.5 and value_at(segs, "z", 1, 3) == 2
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work", nargs="?")
    ap.add_argument("--format", default=None, help="9x16 | 16x9 (default: the profile's; 'both' -> call twice)")
    ap.add_argument("--out", help="<output_dir>/<name> (writes <name>.mp4)")
    ap.add_argument("--xml", action="store_true", help="also write <out>/project/timeline.xml + media/")
    ap.add_argument("--ae", action="store_true", help="also write <out>/project/ae_import.jsx + media/ (After Effects)")
    ap.add_argument("--layers-out", action="store_true",
                    help="also write <out>/project/layers/ numbered files + order.txt + layers.csv (CapCut, Final Cut)")
    ap.add_argument("--layers"); ap.add_argument("--sfx")
    ap.add_argument("--dur", type=float); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--no-master", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.work:
        return selftest()
    fmt = a.format or mc_profile.load_profile()["format"]
    if fmt == "both":
        raise SystemExit("❌ --format both: run compose twice (9x16 and 16x9) with each aspect's own layers file")
    if not a.out:
        raise SystemExit("❌ --out <output_dir>/<name> is required")
    final, items, sfx, D, (W, H) = render(a.work, fmt, a.out, a.layers, a.sfx, a.dur, a.fps, not a.no_master)
    base = pathlib.Path(a.out)
    base = base.with_suffix("") if base.suffix == ".mp4" else base
    if a.xml:
        x = export_xml(items, sfx, D, W, H, a.fps, base / "project" / "timeline.xml", base.name)
        errs = check_xml(x)
        if errs:
            raise SystemExit("❌ XML check:\n" + "\n".join(errs))
    if a.ae:
        export_ae(items, sfx, D, W, H, a.fps, base / "project" / "ae_import.jsx", base.name)
    if a.layers_out:
        export_layers(items, sfx, D, a.fps, base / "project" / "layers")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
