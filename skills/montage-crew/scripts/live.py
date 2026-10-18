"""OPTIONAL LIVE timeline in DaVinci Resolve: every layer the team finishes goes into Resolve at once, so the user
watches (and edits) the video as it grows. Not needed for anything else: compose.py renders the final without Resolve.
Setup (once): scripts/LIVE_RESOLVE.md. Needs a Resolve MCP/bridge install + profile.json "resolve_live":
{"enabled": true, "python": "<that install's venv python>", "mcp_dir": "<that install's folder>"}
(or env MC_RESOLVE_PYTHON / MC_RESOLVE_MCP_DIR). Run these with THAT python:

  $PYR live.py ping                                    is the bridge up? prints product/project/timeline (exit 1 if not)
  $PY live.py setup <work> <timeline>                 open (or create once) the reel timeline: 1080x1920@30, named tracks
  $PY live.py put   <work> <layer> <file> [--at S] [--in S] [--dur S]   place/replace one layer (versioned file names!)
  $PY live.py sfx   <work> audio/sfx_cues.json        place/replace all SFX cues on A3-A6
  $PY live.py camera <work> <layer> <file> <framing.json> [--parallax 0.4] [--tilt-parallax 0] [--grade bg_setup.json] [--in S]   smooth zoom/rise moves (1 clip/frame)
  $PY live.py state <work>                            what did the USER change since our last placement? (exit 2 = changes)
  python live.py --selftest

Layers -> tracks:  V1 plate · V2 behind · V3 aroll/speaker · V4 split · V5 captions · V6 motion · A1 voice · A2 music · A3-A6 sfx
Rules baked in:
- Never recreates or deletes a timeline, never touches items we didn't place (the user's own clips stay).
- Replacing a layer deletes only OUR previous items that the user left untouched; if they moved/trimmed/deleted one, it is
  kept and reported — the user's edit wins, the leader adapts (and tells the owning agent).
- Re-rendered layers must get a NEW file name (captions_v2.mov): Resolve caches media by path.
- Manifest of what we placed: <work>/resolve/live.json.
"""
import json, pathlib, sys

FPS = 30
LAYERS = {"plate": ("video", 1), "behind": ("video", 2), "aroll": ("video", 3), "speaker": ("video", 3), "split": ("video", 4),
          "captions": ("video", 5), "motion": ("video", 6), "extra": ("video", 7), "voice": ("audio", 1), "music": ("audio", 2)}
SFX_TRACKS = [3, 4, 5, 6]
V_NAMES = ["Plate", "Behind", "Speaker", "Split", "Captions", "Motion", "Extra"]
A_NAMES = ["Voice", "Music", "SFX 1", "SFX 2", "SFX 3", "SFX 4"]


def diff(ours, live):
    """ours: manifest items; live: {uid: (start, end)} now on the timeline -> (deleted, changed, untouched uids)."""
    deleted, changed, same = [], [], []
    for it in ours:
        now = live.get(it["uid"])
        if now is None:
            deleted.append(it)
        elif tuple(now) != (it["start"], it["end"]):
            changed.append({**it, "now": list(now)})
        else:
            same.append(it["uid"])
    return deleted, changed, same


def selftest():
    import os, tempfile
    with tempfile.TemporaryDirectory() as d:  # not set up -> a clear message, never a crash or a GUI
        keep = {k: os.environ.pop(k, None) for k in ("MONTAGE_CREW_HOME", "MC_RESOLVE_MCP_DIR", "MC_RESOLVE_PYTHON")}
        os.environ["MONTAGE_CREW_HOME"] = d
        try:
            connect_resolve()
            raise AssertionError("connect without setup")
        except SystemExit as e:
            assert "LIVE_RESOLVE.md" in str(e), e
        os.environ["MC_RESOLVE_MCP_DIR"] = d
        try:
            connect_resolve()
            raise AssertionError("connect to a non-install")
        except SystemExit as e:
            assert "not a Resolve MCP install" in str(e), e
        os.environ["MC_RESOLVE_PYTHON"] = "python"  # bare name: refused (would search the cwd on Windows)
        try:
            resolve_cfg()
            raise AssertionError("relative python accepted")
        except SystemExit as e:
            assert "absolute path" in str(e), e
        for k, v in keep.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    ours =[{"uid": "a", "layer": "captions", "start": 0, "end": 90}, {"uid": "b", "layer": "motion", "start": 30, "end": 60},
            {"uid": "c", "layer": "sfx", "start": 45, "end": 50}]
    d, c, s = diff(ours, {"a": (0, 90), "b": (36, 60)})
    assert [x["uid"] for x in d] == ["c"] and c[0]["now"] == [36, 60] and s == ["a"]
    sp = zoom_spans({"segments": [{"s": 0, "e": 1, "z": 1.0}, {"s": 1, "e": 1.3, "z0": 1.0, "z1": 1.2}, {"s": 1.3, "e": 2, "z": 1.2}]})
    assert sp[0] == (0, 30, 1.0, 0.0, 0.0) and len(sp) == 11 and sp[-1] == (39, 60, 1.2, 0.0, 0.0) and 1.0 < sp[5][2] < 1.2
    sp2 = zoom_spans({"segments": [{"s": 0, "e": 0.3, "z0": 1.0, "z1": 1.0, "ty0": 0, "ty1": 325}, {"s": 0.3, "e": 1, "z": 1, "ty": 325}]})
    assert len(sp2) == 10 and 0 < sp2[4][3] < 325 and sp2[-1] == (9, 30, 1.0, 325.0, 0.0)
    assert all(sp[i][1] == sp[i + 1][0] for i in range(len(sp) - 1))  # gapless
    sp3 = zoom_spans({"segments": [{"s": 0, "e": 0.3, "z0": 1.0, "z1": 1.0, "tx0": 0, "tx1": 10}, {"s": 0.3, "e": 1, "z": 1, "tx": 10}]})
    assert 0 < sp3[4][4] < 10 and sp3[-1] == (8, 30, 1.0, 0.0, 10.0)  # tx = horizontal offset (Pan); last move frame merges
    print("selftest ok")


# ── Resolve side ───────────────────────────────────────────────────────────
def _tool(name):
    """absolute ffmpeg/ffprobe from PATH only (never the cwd) — same lookup as every other script."""
    sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import mc_profile
    return mc_profile.tool(name)


SETUP = "LIVE Resolve is optional and not set up. See scripts/LIVE_RESOLVE.md (or use compose.py: no Resolve needed)."


def resolve_cfg():
    """{"enabled", "python", "mcp_dir"} from env, else the profile's resolve_live."""
    import os
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import mc_profile
    cfg = dict(mc_profile.load_profile().get("resolve_live") or {})
    if os.environ.get("MC_RESOLVE_MCP_DIR"):
        cfg.update(enabled=True, mcp_dir=os.environ["MC_RESOLVE_MCP_DIR"])
    if os.environ.get("MC_RESOLVE_PYTHON"):
        cfg["python"] = os.environ["MC_RESOLVE_PYTHON"]
    py = cfg.get("python")
    if py and not (os.path.isabs(os.path.expanduser(py)) and os.path.isfile(os.path.expanduser(py))):
        sys.exit(f"❌ resolve_live.python must be the absolute path of an existing python file, got {py!r}. " + SETUP)
    return cfg


def connect_resolve():
    """the Resolve object through the user's own Resolve MCP install (its console bridge works on the free edition)."""
    cfg = resolve_cfg()
    d = pathlib.Path(cfg.get("mcp_dir") or "").expanduser()
    if not cfg.get("enabled") or not cfg.get("mcp_dir"):
        sys.exit("❌ " + SETUP)
    if not (d / "src" / "utils" / "resolve_bridge_client.py").is_file():
        sys.exit(f"❌ {d} is not a Resolve MCP install (src/utils/resolve_bridge_client.py missing). " + SETUP)
    sys.path.insert(0, str(d))
    try:
        from src.utils.resolve_bridge_client import connect as c
    except Exception as e:
        sys.exit(f"❌ cannot load the bridge client ({type(e).__name__}: {e}). Run live.py with that install's own python "
                 f"(profile resolve_live.python = {cfg.get('python')}).")
    try:
        return c(require_enabled=False)
    except Exception as e:
        sys.exit(f"❌ Resolve bridge not reachable: {e}\n   Open Resolve with a project, start the console bridge "
                 "(LIVE_RESOLVE.md step 3), then run `live.py ping` again.")


def connect():
    project = connect_resolve().GetProjectManager().GetCurrentProject()
    if not project:
        sys.exit("❌ no project open in Resolve")
    return project, project.GetMediaPool()


def ping():
    resolve = connect_resolve()
    print("product:", resolve.GetProductName(), resolve.GetVersionString())
    project = resolve.GetProjectManager().GetCurrentProject()
    print("project:", project.GetName() if project else None)
    tl = project.GetCurrentTimeline() if project else None
    print("timeline:", tl.GetName() if tl else None)


def man_path(work):
    return pathlib.Path(work) / "resolve" / "live.json"


def load_man(work):
    p = man_path(work)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"timeline": None, "items": []}


def save_man(work, m):
    man_path(work).parent.mkdir(parents=True, exist_ok=True)
    man_path(work).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


def timeline(project, name):
    for i in range(1, project.GetTimelineCount() + 1):
        tl = project.GetTimelineByIndex(i)
        if tl.GetName() == name:
            return tl
    return None


def live_items(tl):
    out = {}
    for kind in ("video", "audio"):
        for t in range(1, tl.GetTrackCount(kind) + 1):
            for it in tl.GetItemListInTrack(kind, t) or []:
                out[it.GetUniqueId()] = (it.GetStart(), it.GetEnd(), it)
    return out


def setup(work, name):
    project, mp = connect()
    tl = timeline(project, name)
    if not tl:
        for k, v in {"timelineFrameRate": str(FPS), "timelineResolutionWidth": "1080",  # project fps BEFORE the timeline
                     "timelineResolutionHeight": "1920"}.items():                          # (new projects default 24)
            project.SetSetting(k, v)
        tl = mp.CreateEmptyTimeline(name)
        project.SetCurrentTimeline(tl)
        for k, v in {"useCustomSettings": "1", "timelineResolutionWidth": "1080", "timelineResolutionHeight": "1920",
                     "timelineFrameRate": str(FPS)}.items():
            tl.SetSetting(k, v)
        while tl.GetTrackCount("video") < len(V_NAMES):
            tl.AddTrack("video")
        while tl.GetTrackCount("audio") < len(A_NAMES):
            tl.AddTrack("audio", "stereo")
        for i, n in enumerate(V_NAMES, 1):
            tl.SetTrackName("video", i, n)
        for i, n in enumerate(A_NAMES, 1):
            tl.SetTrackName("audio", i, n)
        print(f"created timeline «{name}» 1080x1920@{FPS}")
    project.SetCurrentTimeline(tl)  # the user sees it
    m = load_man(work); m["timeline"] = name; save_man(work, m)
    return tl


def _open(work):
    project, mp = connect()
    m = load_man(work)
    tl = timeline(project, m["timeline"]) if m["timeline"] else None
    if not tl:
        sys.exit("❌ run: live.py setup <work> <timeline> first")
    return project, mp, tl, m


def _remove_ours(tl, m, keep_layer_fn):
    """delete our untouched items of the matching layer(s); report the user's edits and keep them."""
    live = live_items(tl)
    deleted, changed, same = diff(m["items"], {u: v[:2] for u, v in live.items()})
    target = [it for it in m["items"] if keep_layer_fn(it)]
    kill = [live[it["uid"]][2] for it in target if it["uid"] in same]
    for it in changed:
        if keep_layer_fn(it):
            print(f"⚠️ the user changed our {it['layer']} ({it['file']}) {it['start']}-{it['end']} -> {it['now']} — kept, adapt to it")
    if kill:
        tl.DeleteClips(kill, False)
    gone = {it["uid"] for it in target if it["uid"] in same} | {it["uid"] for it in deleted}
    m["items"] = [it for it in m["items"] if it["uid"] not in gone]


def probe_frames(path):
    import subprocess
    d = subprocess.run([_tool("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True).stdout.strip()
    return int(float(d or 0) * FPS)


def _pool_find(mp, path):
    want = path.lower().replace("\\", "/")
    stack = [mp.GetRootFolder()]
    while stack:
        f = stack.pop()
        stack += f.GetSubFolderList() or []
        for c in f.GetClipList() or []:
            if (c.GetClipProperty("File Path") or "").lower().replace("\\", "/") == want:
                return c
    return None


def _place(mp, tl, m, layer, kind, track, file, at, src_in, dur):
    path = str(pathlib.Path(file).resolve()).replace("\\", "/")
    got_items = mp.ImportMedia([path]) or []
    item = got_items[0] if got_items else _pool_find(mp, path)  # Resolve returns [] for a file already in the pool
    if item is None:
        raise RuntimeError(f"ImportMedia failed and not in pool: {path}")
    frames = int(float(item.GetClipProperty("Frames") or 0)) or int(dur * FPS) or probe_frames(path)  # .wav has no "Frames"
    s0 = int(round(src_in * FPS))
    n = int(round(dur * FPS)) if dur else frames - s0
    rec = tl.GetStartFrame() + int(round(at * FPS))
    got = mp.AppendToTimeline([{"mediaPoolItem": item, "startFrame": s0, "endFrame": s0 + n, "trackIndex": track,
                                "recordFrame": rec, "mediaType": 1 if kind == "video" else 2}]) or []
    for it in got:
        m["items"].append({"uid": it.GetUniqueId(), "layer": layer, "track": f"{kind}:{track}", "file": str(file),
                           "start": it.GetStart(), "end": it.GetEnd()})
    return got


def put(work, layer, file, at=0.0, src_in=0.0, dur=0.0):
    project, mp, tl, m = _open(work)
    kind, track = LAYERS[layer]
    if not dur:  # replace only what the new piece covers (a per-beat motion file must not wipe later beats)
        dur = probe_frames(str(pathlib.Path(file).resolve())) / FPS - src_in
    # whole frames, like _place: a float edge (31.7333*30 = 951.999) would wipe the neighbour that ends on frame 952
    lo, hi = tl.GetStartFrame() + round(at * FPS), tl.GetStartFrame() + round(at * FPS) + round(dur * FPS)
    _remove_ours(tl, m, lambda it: it["track"] == f"{kind}:{track}" and it["start"] < hi and it["end"] > lo)
    got = _place(mp, tl, m, layer, kind, track, file, at, src_in, dur)
    save_man(work, m)
    print(f"{'✅' if got else '❌'} {layer} -> {kind} {track} at {at:.2f}s ({pathlib.Path(file).name})")


def sfx(work, cues_path):
    project, mp, tl, m = _open(work)
    _remove_ours(tl, m, lambda it: it["layer"] == "sfx")
    busy = {t: [] for t in SFX_TRACKS}
    ok = 0
    for c in sorted(json.loads(pathlib.Path(cues_path).read_text(encoding="utf-8")), key=lambda c: c["start"]):
        s = c["start"]
        t = next((t for t in SFX_TRACKS if all(e <= s for e in busy[t])), SFX_TRACKS[-1])
        f = c["file"]
        if probe_frames(f) < 3:  # Resolve refuses clips shorter than ~1 frame (e.g. 31 ms clicks): pad to 0.5 s
            import subprocess
            pad = pathlib.Path(work) / "audio_resolve" / (pathlib.Path(f).stem + "_pad.wav")
            pad.parent.mkdir(exist_ok=True)
            if not pad.exists():
                subprocess.run([_tool("ffmpeg"), "-v", "error", "-y", "-i", f, "-af", "apad=whole_dur=0.5", "-ar", "48000", str(pad)], check=True)
            f = str(pad)
        got = _place(mp, tl, m, "sfx", "audio", t, f, s, 0, 0)
        if got:
            ok += 1; busy[t].append(s + probe_frames(f) / FPS)  # proxy GetEnd() can come back None
            gain = c.get("gain_db", c.get("gain"))
            if gain is not None:
                got[0].SetProperties({"AudioVolume": float(gain)})
    save_man(work, m)
    print(f"✅ {ok} SFX cues on A{SFX_TRACKS[0]}-A{SFX_TRACKS[-1]}")


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def zoom_spans(framing, fps=FPS):
    """framing {"segments":[{"s","e","z"[,"ty","tx"]} hold | {"s","e","z0","z1"[,"ty0","ty1","tx0","tx1"]} eased move]}
    -> [(f0, f1, z, ty, tx)], moves = 1 span/frame. ty = vertical offset in px (+ = image UP), tx = horizontal (Pan), default 0."""
    out = []
    for sg in framing["segments"]:
        f0, f1 = round(sg["s"] * fps), round(sg["e"] * fps)
        if f1 <= f0:
            continue
        if "z" in sg:
            out.append((f0, f1, float(sg["z"]), float(sg.get("ty", 0)), float(sg.get("tx", 0))))
        else:
            n, ty0 = f1 - f0, float(sg.get("ty0", sg.get("ty", 0)))
            ty1 = float(sg.get("ty1", ty0))
            tx0 = float(sg.get("tx0", sg.get("tx", 0)))
            tx1 = float(sg.get("tx1", tx0))
            for k in range(n):
                e = ease_io((k + 0.5) / n)
                out.append((f0 + k, f0 + k + 1, sg["z0"] + (sg["z1"] - sg["z0"]) * e, ty0 + (ty1 - ty0) * e,
                            tx0 + (tx1 - tx0) * e))
    merged = []
    for s in out:
        if (merged and merged[-1][1] == s[0] and abs(merged[-1][2] - s[2]) < 1e-4 and abs(merged[-1][3] - s[3]) < 0.05
                and abs(merged[-1][4] - s[4]) < 0.05):
            merged[-1] = (merged[-1][0], *s[1:])
        else:
            merged.append(s)
    return merged


BASE_KEYS = ("ZoomX", "ZoomY", "Pan", "Tilt", "AnchorPointX", "AnchorPointY")


def camera(work, layer, file, framing_path, parallax=1.0, src_in=0.0, tilt_parallax=1.0, grade_path=None):
    """Smooth camera moves IN Resolve (free has no keyframe API): holds = one clip, moves = one clip per frame.
    Base placement (zoom/pan/tilt/anchor set by davinci-background) is read once from the layer's item and stored in the
    manifest, so re-runs keep it. zoom = base × (1 + parallax·(z − 1)) — speaker parallax 1.0, plate ~0.4 for depth;
    Tilt = base + tilt_parallax·ty (speaker 1.0; plate 0 = the wall stays put while he moves up for a SPLIT); Pan = base + tilt_parallax·tx.
    Grade: --grade bg_setup.json re-applies {"grade": {lut_file, node, cdl}} to every new clip (the plate's look).
    Order matters: our old items are removed FIRST, then the spans are laid (never lay clips over occupied frames)."""
    project, mp, tl, m = _open(work)
    kind, track = LAYERS[layer]
    key = f"{kind}:{track}"
    framing = json.loads(pathlib.Path(framing_path).read_text(encoding="utf-8"))
    live = live_items(tl)
    bases = m.setdefault("bases", {})
    if key not in bases:
        mine = sorted((it for it in m["items"] if it["track"] == key and it["uid"] in live), key=lambda it: it["start"])
        props = live[mine[0]["uid"]][2].GetProperties() if mine else {}
        bases[key] = {k: float(props.get(k, 1.0 if k.startswith("Zoom") else 0.0)) for k in BASE_KEYS}
    base = bases[key]
    grade = json.loads(pathlib.Path(grade_path).read_text(encoding="utf-8"))["grade"] if grade_path else None
    _remove_ours(tl, m, lambda it: it["track"] == key)
    left = [it for it in m["items"] if it["track"] == key]
    if left:
        print(f"⚠️ {len(left)} item(s) on {key} were changed by the user and kept — spans may overlap them")
    item = mp.ImportMedia([str(pathlib.Path(file).resolve()).replace("\\", "/")])[0]
    t0, s0 = tl.GetStartFrame(), int(round(src_in * FPS))
    spans = zoom_spans(framing)
    got = mp.AppendToTimeline([{"mediaPoolItem": item, "startFrame": s0 + f0, "endFrame": s0 + f1, "trackIndex": track,
                                "recordFrame": t0 + f0, "mediaType": 1} for f0, f1, *_ in spans]) or []
    if len(got) != len(spans):
        print(f"⚠️ placed {len(got)}/{len(spans)} spans")
    bad = 0
    for it, (_, _, z, ty, tx) in zip(got, spans):
        k = 1 + parallax * (z - 1)
        it.SetProperties({**base, "ZoomX": base["ZoomX"] * k, "ZoomY": base["ZoomY"] * k,
                          "Tilt": base["Tilt"] + tilt_parallax * ty, "Pan": base["Pan"] + tilt_parallax * tx})
        if grade:
            ok = it.GetNodeGraph().SetLUT(int(grade["node"]), grade["lut_file"]) and it.SetCDL(grade["cdl"])
            bad += not ok
    if bad:
        print(f"⚠️ grade failed on {bad} clip(s)")
    for it in got:
        m["items"].append({"uid": it.GetUniqueId(), "layer": layer, "track": key, "file": str(file),
                           "start": it.GetStart(), "end": it.GetEnd()})
    save_man(work, m)
    moves = sum(1 for sg in framing["segments"] if "z0" in sg)
    print(f"✅ {layer}: {len(got)} clips ({moves} smooth moves, parallax {parallax}, tilt parallax {tilt_parallax}) base {base}"
          + (" + grade" if grade else ""))


def state(work):
    project, mp, tl, m = _open(work)
    live = live_items(tl)
    deleted, changed, same = diff(m["items"], {u: v[:2] for u, v in live.items()})
    ours = {it["uid"] for it in m["items"]}
    added = [(u, v[2].GetName(), v[0], v[1]) for u, v in live.items() if u not in ours]
    for it in deleted: print(f"🗑 the user deleted our {it['layer']} {it['file']} ({it['start']}-{it['end']})")
    for it in changed: print(f"✂️ the user moved/trimmed our {it['layer']} {it['file']}: {it['start']}-{it['end']} -> {it['now']}")
    for u, n, s, e in added: print(f"➕ the user added {n} ({s}-{e})")
    if not (deleted or changed or added):
        print("no changes by the user"); return 0
    return 2


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest(); sys.exit()
    sys.stdout.reconfigure(encoding="utf-8")
    opt = lambda k, d=0.0: float(a[a.index(k) + 1]) if k in a else d
    cmd = a[0]
    if cmd == "ping":
        ping()
    elif cmd == "setup":
        setup(a[1], a[2])
    elif cmd == "put":
        put(a[1], a[2], a[3], opt("--at"), opt("--in"), opt("--dur"))
    elif cmd == "sfx":
        sfx(a[1], a[2])
    elif cmd == "camera":
        camera(a[1], a[2], a[3], a[4], opt("--parallax", 1.0), opt("--in"), opt("--tilt-parallax", 1.0),
               a[a.index("--grade") + 1] if "--grade" in a else None)
    elif cmd == "state":
        sys.exit(state(a[1]))
    else:
        sys.exit(__doc__)
