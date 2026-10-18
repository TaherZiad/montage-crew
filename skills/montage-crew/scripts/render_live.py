"""OPTIONAL: render a LIVE Resolve timeline (live.py) from Resolve, then free the bridge.
  $PYR render_live.py <work> "<timeline name>" <frames> <out_name> [--hd]      (4K vertical by default, --hd = 1080x1920;
                                                                               a 16:9 timeline renders at its own size)
Run it with the Resolve MCP install's python (LIVE_RESOLVE.md). After StartRendering it calls bridge_shutdown() (the
bridge blocks Resolve's UI thread while rendering) and watches the file grow; start the bridge again afterwards.
ONE render job and ONE output name per video: pass the same <out_name> every time, edits re-render the same file.
Then: python master.py <work>/out/<out_name>.mp4 <work>/out/final.mp4
"""
import os, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from live import connect_resolve  # noqa: E402


def main(a):
    work, tl_name, frames, name = a[0], a[1], int(a[2]), a[3]
    out_dir = f"{work}/out"
    resolve = connect_resolve()
    project = resolve.GetProjectManager().GetCurrentProject()
    tl = next((project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
               if project.GetTimelineByIndex(i).GetName() == tl_name), None)
    if tl is None:
        sys.exit(f"❌ no timeline named «{tl_name}»")
    project.SetCurrentTimeline(tl)
    tw, th = int(tl.GetSetting("timelineResolutionWidth") or 1080), int(tl.GetSetting("timelineResolutionHeight") or 1920)
    w, h = (tw, th) if "--hd" in a else (tw * 2, th * 2)
    start = tl.GetStartFrame()
    project.SetCurrentRenderFormatAndCodec("mp4", "H264")
    project.SetRenderSettings({"SelectAllFrames": False, "MarkIn": start, "MarkOut": start + frames - 1,
                               "TargetDir": out_dir, "CustomName": name, "FormatWidth": w, "FormatHeight": h,
                               "FrameRate": 30.0, "ExportVideo": True, "ExportAudio": True,
                               "AudioCodec": "aac", "AudioSampleRate": 48000})  # free edition refuses some keys but applies these
    jid = None  # one job per video: reuse ours, drop stale duplicates of the same timeline
    for j in project.GetRenderJobList() or []:
        if j.get("TimelineName") != tl_name:
            continue
        same = j.get("OutputFilename", "").startswith(name)
        rng = (int(j.get("MarkIn", -1)), int(j.get("MarkOut", -1))) == (start, start + frames - 1)
        if same and rng and jid is None:
            jid = j["JobId"]
        else:
            project.DeleteRenderJob(j["JobId"])
    if jid is None:
        jid = project.AddRenderJob()
    path = f"{out_dir}/{name}.mp4"
    if os.path.exists(path):
        os.remove(path)
    project.StartRendering([jid])
    try:
        resolve.bridge_shutdown()
    except Exception as e:
        print("bridge_shutdown:", e)
    last, still = -1, 0
    while still < 20:
        time.sleep(1)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        still = still + 1 if size == last and size > 0 else 0
        last = size
    print("rendered:", path, last)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    main(sys.argv[1:])
