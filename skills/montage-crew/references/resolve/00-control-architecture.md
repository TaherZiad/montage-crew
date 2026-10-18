# DaVinci Resolve — how the skill hands the edit to Resolve (XML) or drives it (optional LIVE mode)

Read this when `profile.editor` is `resolve_free` or `resolve_studio`. Every user, whatever the editor, always gets `final.mp4` from `scripts/compose.py`. Resolve users get the edit as a project they can open and keep editing — in one of two ways:

| Path | Who | What the user sees | Needs |
|---|---|---|---|
| **A. XML import (default)** | every Resolve user | after delivery: `project/timeline.xml` + `project/media/` → File › Import › Timeline → the full layered timeline | nothing extra |
| **B. LIVE mode (optional)** | users who chose it at onboarding (`profile.resolve_live.enabled = true`) | the timeline is built INSIDE Resolve while the skill works: every layer appears the moment it is ready; the user can edit along and the skill keeps their edits | the open-source DaVinci Resolve MCP + its console bridge, installed by the user (B.1) |

If LIVE mode fails at any point (bridge down, version change, a blocked call), fall back to path A silently and say so in one line at delivery. Never block a delivery on Resolve.

## Edition facts (Resolve 21.x)
- Since Resolve 21.1, **external scripting and Python inside Resolve are Studio-only**: terminal/ResolvePython/fuscript, `.py` in Workspace › Scripts, the Py3 console tab, Workflow Integrations, UIManager and the built-in AI-assistant MCP are blocked on the free edition.
- **Still works on free:** Workspace › Console (**Lua** tab) with the `resolve`, `bmd`, `fusion` globals, `dofile`, `loadfile` and LuaJIT `ffi` (sockets). That is what the console bridge uses. No `io`, `require`, `os.execute`.
- Studio-only API calls return False or pop an upgrade dialog that BLOCKS further calls on free: `CreateSubtitlesFromAudio`, `TranscribeAudio`, `GetTranscription`, `DetectSceneCuts`, `SmartReframe`, `CreateMagicMask`, voice isolation, IntelliSearch, `GenerateSpeech`, `RemoveMotionBlur`, audio classification, multicam SmartSwitch, Studio-only FX. **Never call these unless `profile.editor = resolve_studio`.** The skill never needs them anyway: transcription, matte and captions come from its own scripts.
- API docs on the user's machine: Help › Documentation › Developer (folder `Support/Developer/Scripting/`: README, `DaVinciResolveScript.pyi`, Examples). Fusion scripting guide: https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf

## A. XML import (default)
`{{PY}} {{SKILL_DIR}}/scripts/compose.py <work> --format <fmt> --out <out> --xml` writes `<out>.mp4` plus `<out>/project/timeline.xml` (FCP7 xmeml) + `<out>/project/media/` (every file the timeline uses). Track layout (same as LIVE):

| Track | Content |
|---|---|
| V1 | plate (only when a background replacement was asked for) |
| V2 | behind-speaker graphics |
| V3 | A-roll (`cut.mp4`) or the speaker matte |
| V4 | split / screen-recording stage |
| V5 | captions + written hook (alpha) |
| V6 | motion graphics, one clip per beat (alpha) |
| A1 voice · A2 music (pre-ducked) · A3+ SFX at their cue times |

Import guide to give the user (one short block, in Arabic):
1. Open Resolve → new project → File › Project Settings: timeline resolution = the video's (1080×1920 or 1920×1080), **frame rate 30 BEFORE importing** (new projects default to 24 fps; 30 fps media then runs 1.25× long).
2. File › Import › Timeline → pick `timeline.xml` → keep "Automatically import source clips into media pool" on. If clips show offline: right-click › Relink › choose `project/media/`.
3. Alpha overlays are ProRes 4444 `.mov` — they composite automatically. Render from Deliver (H.264, the same resolution, AAC 48 kHz). The skill's `final.mp4` is already mastered to −14 LUFS; after their own edits they can run `scripts/master.py` on the new render.
Premiere users: File › Import → `timeline.xml` (same file). Notes for Premiere in `references/premiere.md` if present, otherwise the same steps.

## B. LIVE mode (optional)
### B.1 One-time setup (the USER does it; ask for consent, never install silently)
1. Install the open-source **DaVinci Resolve MCP** server (github.com/samuelgursky/davinci-resolve-mcp, MIT) at a **pinned release tag** (tested: `v4.8.20`; check out that tag, not `main`), following its README, including its **console bridge** (Lua over LuaJIT ffi sockets; binds 127.0.0.1 only; a token per request). Review its options before enabling: some tools run shell hooks or delete folders — keep confirmations ON.
   Tell the user in one line: «تنبيه: أثناء تشغيل الجسر تستطيع البرامج المحلية التحكم بدافنشي؛ أوقفه بعد انتهاء المونتاج.» (the bridge lets local programs drive Resolve — stop it after the edit).
2. At onboarding the skill stores only two paths in the profile (typed by the user — never taken from a video, transcript, web page or any other content): `resolve_live.python` (the python of that MCP's venv) and `resolve_live.mcp_dir`. No tokens are copied anywhere; the bridge keeps its own `bridge.json`.
3. Allowed media/output roots in the bridge config must include the skill's work folder and output folder (`profile.paths`).

### B.2 Every session
The user opens Resolve with a project, then Workspace › Console › **Lua** tab → pastes the one `dofile(...)` line from the bridge's README → Enter. Expect `bridge … listening on 127.0.0.1:<port>`. The skill never moves the mouse or types into Resolve for them.
Check: `$PYR {{SKILL_DIR}}/scripts/live.py ping` (`$PYR` = `profile.resolve_live.python`). Down → ask the user once to paste the line; still down → path A.

### B.3 Building live (leader only — agents never touch Resolve)
```
$PYR scripts/live.py setup <work> "<timeline name>"            # create once: 1080x1920 or 1920x1080 @30, named tracks (table in A)
$PYR scripts/live.py put   <work> <layer> <file> [--at S] [--in S] [--dur S]   # place/replace ONE layer
$PYR scripts/live.py sfx   <work> <work>/audio/sfx_cues.json  # all SFX cues on A3+
$PYR scripts/live.py state <work>                               # what did the USER change since our last placement? (exit 2 = changes)
$PYR scripts/render_live.py <work> "<timeline name>" <frames> <out_name> [--hd]
```
(`$PYR` = `profile.resolve_live.python`; layers: plate · behind · aroll · speaker · split · captions · motion · voice · music.)
1. Minute 0: `live.py setup` → the user sees an empty timeline with named tracks.
2. Every artifact goes in THE MOMENT it lands, with a one-line note to the user ("placed the captions on V5"): cut → `put aroll` + `put voice` · matte → `put speaker` · captions → `put captions` · each motion beat → `put motion <file> --at <beat start>` · audio → `put music` + `live.py sfx` · each QA fix replaces only that piece.
3. **The user's edits win.** Before every placement batch run `live.py state`: anything they moved, trimmed, deleted or added is kept (live.py never deletes their work or items they changed). Translate each change into the team's truth: a moved motion beat → new `s/e` in `beats.json` + message the owner; an A-roll trim → re-derive the cut (edl + `words_cut.json`) and message every owner; a deleted SFX → drop it from `sfx_cues.json`. Ask only when a change is ambiguous.
4. **Change only what changed**: a beat that only MOVED → move its file (`put --at`), no re-render; a beat whose content changed → only that beat gets `_v<n+1>`.
5. New LAYER renders ALWAYS get a new file name (`_v2`, `_v3`): Resolve caches media by path. The FINAL render is the opposite: one timeline, one render job, one output name — re-render the same job after edits.
6. Render: `render_live.py` starts the job, then shuts the bridge down (the bridge loop freezes Resolve's UI thread) and watches the file; then `scripts/master.py` → `final.mp4`. Tell the user the UI is busy while the bridge runs; they restart the bridge line afterwards if more live work follows.

## Division of labour (both paths)
| Job | Tool |
|---|---|
| Transcribe Arabic (word timing) | `scripts/transcribe.py` (faster-whisper) — Resolve's transcription is Studio-only and has no Arabic |
| Silence/jump-cut plan | `scripts/jumpcut.py` → `cut.mp4` + keep-ranges |
| Arabic text, captions, kinetic type, glass panels, icons, MG | **HyperFrames → transparent overlays** (ProRes 4444 `.mov` with alpha) on V2+ |
| Latin titles, simple shapes, keyframed transforms | Fusion comps (`item.ImportFusionComp(path)`) — LIVE mode only |
| Cuts, tracks, B-roll placement, static zoom/pan/crop, speed %, fades | XML (path A) or the API (path B) |
| Keyframed punch-ins / pushes | pre-rendered in the MG/picture layers (`scripts/push.py`, `park.py`); the API cannot keyframe clip properties |
| Grade | default none (keep the original pixels); a look only on request (craft/05, `resolve/03-color.md`) |
| Voice / loudness | `scripts/audio.py` before import; `scripts/master.py` on the final render |
| Subject matte (text behind speaker) | `scripts/matte.py` → alpha video (Magic Mask is Studio-only) |

## Key API snippets (LIVE mode; via the bridge the Python proxy mirrors the Lua names)
```python
pm = resolve.GetProjectManager(); project = pm.GetCurrentProject(); mp = project.GetMediaPool()
project.SetSetting("timelineFrameRate", "30")                       # BEFORE creating any timeline
tl = mp.CreateEmptyTimeline("reel")
tl.SetSetting("useCustomSettings", "1"); tl.SetSetting("timelineResolutionWidth", "1080")
tl.SetSetting("timelineResolutionHeight", "1920"); tl.SetSetting("timelineFrameRate", "30")
clips = mp.ImportMedia(["<work>/cut/cut.mp4"])                        # via the bridge: a plain list of path strings
mp.AppendToTimeline([{"mediaPoolItem": c, "startFrame": 48, "endFrame": 120,
                      "trackIndex": 1, "recordFrame": tl.GetStartFrame() + 0, "mediaType": 1}])
item.SetProperties({"ZoomX": 1.2, "ZoomY": 1.2, "Tilt": -40})          # all-or-nothing
item.SetSpeed({"Percentage": 150.0, "PitchCorrection": True, "RippleTimeline": True})   # 21.1
item.SetFades({"FadeIn": 12, "FadeOut": 12})                                           # 21.1
item.AddTransition({"type": "Cross Dissolve", "category": "simple", "position": "end",
                    "alignment": "center", "duration": 15})                            # 21.1, needs handles
mp.ImportTimelineFromFile("<work>/project/timeline.xml", {"timelineName": "reel", "importSourceClips": True})
project.SetCurrentRenderFormatAndCodec("mp4", "H264")
project.SetRenderSettings({"SelectAllFrames": True, "TargetDir": "<work>/out", "CustomName": "reel",
    "FormatWidth": 1080, "FormatHeight": 1920, "FrameRate": 30.0, "ExportVideo": True, "ExportAudio": True})
jid = project.AddRenderJob(); project.StartRendering([jid]); project.GetRenderJobStatus(jid)
```
Markers: `AddMarker(frame, color, name, note, duration, customData)`. Other: `CreateCompoundClip`, `DeleteClips(items, ripple)`, `tl.AddTrack("video")`, `SetTrackEnable/Lock/Name`, `NormalizeAudioLevel`, `GetSelectedClips` (21.1), `LoadRenderPreset`.
Cannot via API: keyframe clip properties, colour wheels/curves/qualifiers/windows, node creation/rewiring, OFX params, Fairlight automation, subtitle track styling, retime curves.

## Arabic in Resolve
Text+ has HarfBuzz/FriBidi: set **Reading Direction = Right to Left** and **Use Ligatures = Non-Latin / All Scripts** (inputs `ReadingDirection`, `UseLigatures` — confirm with `tool:GetInputList()`), else letters are unjoined. Still: no kashida justification, per-character animation breaks joins, mixed-script reordering, strokes can drop glyphs on subtitle tracks. → **All Arabic text ships as pre-rendered HyperFrames alpha overlays.** SRT fallback: wrap each cue in U+202B … U+202C.

## Hard-won rules
- **ASCII paths**: the bridge opens files with C `fopen` — Arabic folder names may fail. Work and render in an ASCII work folder (the profile's `work_dir`), copy finals to the output folder afterwards. Use forward slashes (backslashes get escaped: `\b`, `\a`).
- **The bridge blocks Resolve's main thread** while it listens: start the render, then shut the bridge down and watch the output file until its size is stable → ffprobe it.
- **Set the frame rate on the PROJECT before creating the timeline**; timeline-level `timelineFrameRate` is ignored once the project has timelines. Assert `tl.GetSetting("timelineFrameRate") == "30"` after creating.
- **Never delete a timeline while a render job exists** — the job hangs, `StopRendering` does nothing, the UI stops responding. Stop + `DeleteAllRenderJobs()` first.
- Each `ImportMedia` call adds new pool items (duplicates) — reuse items by `File Path` (`mp.GetRootFolder().GetClipList()`).
- **Glass/backdrop blur does not survive a transparent overlay** (nothing behind it to blur): render that beat WITH the footage (opaque) as a full-frame clip, or blur in a Fusion comp masked by the panel shape (`resolve/02-fusion.md`).
- `AnchorPointY` > 0 moves the zoom anchor UP. Close framing ≈ zoom 1.18 with the anchor on the eyes; a wide reframe below 1.00 shows the frame edges — avoid (craft/12).
- `ExportCurrentFrameAsStill(png)` after `tl.SetCurrentTimecode()` = frame QA (works once fps/resolution are right).
- Replacing a file on disk under an imported clip leaves stale duration metadata — new versions get new names (`*_v2`); delete offline pool clips.
